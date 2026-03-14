"""
FinSight AI - Streamlit Dashboard
Modern and clean expense tracking dashboard with AI-powered insights
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import requests
from typing import Dict, List, Tuple
import io
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="FinSight AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    /* Main color scheme */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --danger-color: #d62728;
        --warning-color: #ff9800;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
        padding: 30px;
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5em;
    }
    
    .main-header p {
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card h3 {
        color: #666;
        font-size: 0.9em;
        margin: 0 0 10px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #1f77b4;
    }
    
    /* Category badge */
    .category-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 500;
        margin: 0 5px 5px 0;
    }
    
    .category-food {
        background-color: #ffe5cc;
        color: #ff7f0e;
    }
    
    .category-transport {
        background-color: #cce5ff;
        color: #1f77b4;
    }
    
    .category-shopping {
        background-color: #e5ccff;
        color: #9467bd;
    }
    
    .category-utilities {
        background-color: #ccf0e5;
        color: #2ca02c;
    }
    
    .category-entertainment {
        background-color: #ffcccc;
        color: #d62728;
    }
    
    .category-health {
        background-color: #fff0cc;
        color: #ff9800;
    }
    
    .category-other {
        background-color: #e5e5e5;
        color: #666;
    }
    
    /* Section divider */
    .section-divider {
        margin: 30px 0;
        border-top: 2px solid #e0e0e0;
    }
    
    /* Recommendation card */
    .recommendation-card {
        background: linear-gradient(135deg, #f5f5f5 0%, #fff 100%);
        padding: 20px;
        border-left: 4px solid #ff7f0e;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    
    .recommendation-priority-high {
        border-left-color: #d62728;
        background: linear-gradient(135deg, #fff5f5 0%, #fff 100%);
    }
    
    .recommendation-priority-medium {
        border-left-color: #ff9800;
        background: linear-gradient(135deg, #fffaf0 0%, #fff 100%);
    }
    
    .recommendation-priority-low {
        border-left-color: #2ca02c;
        background: linear-gradient(135deg, #f5fff5 0%, #fff 100%);
    }
    
    .priority-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    
    .priority-badge-high {
        background-color: #ffcccc;
        color: #d62728;
    }
    
    .priority-badge-medium {
        background-color: #ffe5cc;
        color: #ff7f0e;
    }
    
    .priority-badge-low {
        background-color: #ccf0e5;
        color: #2ca02c;
    }
    
    /* Success message */
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000/api"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_category_color(category: str) -> str:
    """Get color for category badge"""
    colors = {
        "food & dining": "#ff7f0e",
        "groceries": "#2ca02c",
        "transportation": "#1f77b4",
        "utilities": "#9467bd",
        "entertainment": "#d62728",
        "shopping": "#ff9800",
        "health": "#17becf",
        "other": "#7f7f7f"
    }
    return colors.get(category.lower(), "#7f7f7f")

def get_category_badge_class(category: str) -> str:
    """Get CSS class for category badge"""
    classes = {
        "food & dining": "category-food",
        "groceries": "category-utilities",
        "transportation": "category-transport",
        "utilities": "category-utilities",
        "entertainment": "category-entertainment",
        "shopping": "category-shopping",
        "health": "category-health",
        "other": "category-other"
    }
    return classes.get(category.lower(), "category-other")

def upload_receipt(uploaded_file) -> Dict:
    """Upload receipt to API"""
    try:
        files = {'file': uploaded_file}
        response = requests.post(
            f"{st.session_state.api_url}/upload-receipt",
            files=files,
            timeout=30
        )
        
        if response.status_code == 201:
            return {'success': True, 'data': response.json()}
        else:
            return {
                'success': False,
                'error': response.json().get('detail', 'Failed to upload receipt')
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def add_expense(date: str, merchant: str, category: str, amount: float, description: str = "") -> Dict:
    """Add expense to API"""
    try:
        params = {
            'date': date,
            'merchant': merchant,
            'category': category,
            'amount': amount,
            'description': description
        }
        response = requests.post(
            f"{st.session_state.api_url}/add-expense",
            params=params,
            timeout=30
        )
        
        if response.status_code == 201:
            return {'success': True, 'data': response.json()}
        else:
            return {
                'success': False,
                'error': response.json().get('detail', 'Failed to add expense')
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_spending_summary(days: int = 30) -> Dict:
    """Get spending summary from API"""
    try:
        response = requests.get(
            f"{st.session_state.api_url}/spending-summary",
            params={'days': days},
            timeout=30
        )
        
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': 'Failed to get spending summary'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_monthly_insights(months: int = 3) -> Dict:
    """Get monthly insights from API"""
    try:
        response = requests.get(
            f"{st.session_state.api_url}/monthly-insights",
            params={'months': months},
            timeout=30
        )
        
        if response.status_code == 200:
            return {'success': True, 'data': response.json()}
        else:
            return {'success': False, 'error': 'Failed to get insights'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================================
# HEADER SECTION
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>💰 FinSight AI</h1>
    <p>Smart Expense Tracking & AI-Powered Financial Insights</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - NAVIGATION & SETTINGS
# ============================================================================

with st.sidebar:
    st.markdown("### 📋 Navigation")
    
    page = st.radio(
        "Choose a page:",
        ["📊 Dashboard", "📸 Upload Receipt", "➕ Add Expense", "📈 Analytics", "💡 AI Insights"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    
    # API Configuration
    with st.expander("🔌 API Settings"):
        api_url = st.text_input(
            "API Base URL",
            value=st.session_state.api_url,
            help="Default: http://localhost:8000/api"
        )
        if api_url != st.session_state.api_url:
            st.session_state.api_url = api_url
    
    # Time period selection
    st.markdown("### 📅 Time Period")
    period_days = st.slider(
        "Analyze last N days",
        min_value=1,
        max_value=365,
        value=30,
        step=7,
        help="Select the number of days to analyze"
    )

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================

if page == "📊 Dashboard":
    st.markdown("### 📊 Dashboard Overview")
    
    # Fetch spending summary
    with st.spinner("Loading dashboard data..."):
        summary = get_spending_summary(period_days)
    
    if summary['success']:
        data = summary['data'].get('data', {})
        summary_info = data.get('summary', {})
        by_category = data.get('by_category', [])
        insights = data.get('insights', [])
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Spending</h3>
                <div class="metric-value">${summary_info.get('total_spending', 0):.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Daily Average</h3>
                <div class="metric-value">${summary_info.get('average_daily_spending', 0):.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Transactions</h3>
                <div class="metric-value">{summary_info.get('transaction_count', 0)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Top Category</h3>
                <div class="metric-value" style="font-size: 1.2em; text-transform: capitalize;">
                    {summary_info.get('highest_category', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Spending by Category - Pie Chart
            if by_category:
                categories = [cat['category'] for cat in by_category]
                amounts = [cat['total'] for cat in by_category]
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=categories,
                    values=amounts,
                    marker=dict(
                        colors=[get_category_color(cat) for cat in categories]
                    ),
                    hovertemplate='<b>%{label}</b><br>$%{value:.2f}<br>%{percent}<extra></extra>'
                )])
                
                fig_pie.update_layout(
                    title="Spending by Category",
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Category Breakdown - Bar Chart
            if by_category:
                df_categories = pd.DataFrame(by_category)
                
                fig_bar = go.Figure(data=[go.Bar(
                    x=df_categories['category'],
                    y=df_categories['total'],
                    marker=dict(
                        color=[get_category_color(cat) for cat in df_categories['category']]
                    ),
                    hovertemplate='<b>%{x}</b><br>$%{y:.2f}<extra></extra>'
                )])
                
                fig_bar.update_layout(
                    title="Spending by Category",
                    xaxis_title="Category",
                    yaxis_title="Amount ($)",
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False
                )
                fig_bar.update_xaxes(tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Category Details
        st.markdown("---")
        st.markdown("### 📋 Category Details")
        
        if by_category:
            for cat in by_category:
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    badge_class = get_category_badge_class(cat['category'])
                    st.markdown(f"""
                    <span class="category-badge {badge_class}">{cat['category'].title()}</span>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.metric("Total", f"${cat['total']:.2f}")
                
                with col3:
                    st.metric("% of Total", f"{cat.get('percentage', 0):.1f}%")
                
                with col4:
                    st.metric("Count", f"{cat.get('transaction_count', 0)}")
                
                with col5:
                    st.metric("Avg", f"${cat.get('average_per_transaction', 0):.2f}")
        
        # Insights
        if insights:
            st.markdown("---")
            st.markdown("### 💡 AI Insights")
            
            for insight in insights:
                st.info(f"💭 {insight}")
    
    else:
        st.error(f"Failed to load dashboard: {summary.get('error', 'Unknown error')}")

# ============================================================================
# PAGE 2: UPLOAD RECEIPT
# ============================================================================

elif page == "📸 Upload Receipt":
    st.markdown("### 📸 Upload Receipt Image")
    st.markdown("Upload a receipt image to automatically extract expense details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📤 Upload Receipt")
        
        uploaded_file = st.file_uploader(
            "Choose a receipt image",
            type=["jpg", "jpeg", "png", "gif", "bmp"],
            help="Upload a receipt image (JPG, PNG, GIF, BMP). Max 10MB."
        )
        
        if uploaded_file:
            # Display image
            image = Image.open(uploaded_file)
            st.image(image, caption="Receipt Image", use_column_width=True)
            
            # Upload button
            if st.button("🔍 Analyze Receipt", key="analyze_receipt"):
                with st.spinner("Analyzing receipt..."):
                    result = upload_receipt(uploaded_file)
                
                if result['success']:
                    expense = result['data'].get('expense', {})
                    confidence = result['data'].get('confidence', 0)
                    
                    st.markdown('<div class="success-message">', unsafe_allow_html=True)
                    st.success("✅ Receipt analyzed successfully!")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display extracted information
                    st.markdown("#### 📋 Extracted Information")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Merchant", expense.get('merchant', 'N/A'))
                    
                    with col2:
                        st.metric("Amount", f"${expense.get('amount', 0):.2f}")
                    
                    with col3:
                        st.metric("Confidence", f"{confidence*100:.0f}%")
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Category:** {expense.get('category', 'N/A')}")
                        st.markdown(f"**Date:** {expense.get('date', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**ID:** {expense.get('id', 'N/A')}")
                        st.markdown(f"**Source:** Receipt Upload")
                else:
                    st.error(f"Failed to analyze receipt: {result.get('error', 'Unknown error')}")
    
    with col2:
        st.markdown("#### ℹ️ Tips for Best Results")
        
        st.info("""
        **For accurate receipt analysis:**
        
        ✓ Use clear, well-lit photos
        ✓ Ensure receipt is fully visible
        ✓ Avoid shadows and glare
        ✓ Keep text readable
        ✓ Supported formats: JPG, PNG, GIF, BMP
        ✓ Maximum file size: 10MB
        
        **What we extract:**
        - Merchant/Store name
        - Purchase amount
        - Expense category
        - Purchase date
        - Confidence score
        """)

# ============================================================================
# PAGE 3: ADD EXPENSE
# ============================================================================

elif page == "➕ Add Expense":
    st.markdown("### ➕ Add Expense Manually")
    st.markdown("Enter expense details manually to track your spending")
    
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input(
                "Date",
                value=datetime.now().date(),
                help="Select the expense date"
            )
            
            merchant = st.text_input(
                "Merchant/Store Name",
                placeholder="e.g., Starbucks, Amazon, Whole Foods",
                help="Name of the store or business"
            )
            
            amount = st.number_input(
                "Amount ($)",
                min_value=0.01,
                max_value=10000.00,
                step=0.01,
                help="Expense amount in dollars"
            )
        
        with col2:
            category = st.selectbox(
                "Category",
                [
                    "food & dining",
                    "groceries",
                    "transportation",
                    "utilities",
                    "entertainment",
                    "shopping",
                    "health",
                    "other"
                ],
                help="Select the expense category"
            )
            
            description = st.text_area(
                "Description (Optional)",
                placeholder="Add notes about this expense...",
                help="Optional notes or details",
                max_chars=500,
                height=100
            )
        
        # Submit button
        submitted = st.form_submit_button(
            "✅ Add Expense",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not merchant:
                st.error("❌ Please enter a merchant name")
            elif amount <= 0:
                st.error("❌ Amount must be greater than 0")
            else:
                with st.spinner("Adding expense..."):
                    result = add_expense(
                        date=expense_date.strftime("%Y-%m-%d"),
                        merchant=merchant,
                        category=category,
                        amount=amount,
                        description=description
                    )
                
                if result['success']:
                    expense = result['data'].get('expense', {})
                    st.markdown('<div class="success-message">', unsafe_allow_html=True)
                    st.success("✅ Expense added successfully!")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display confirmation
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Merchant", merchant)
                    with col2:
                        st.metric("Amount", f"${amount:.2f}")
                    with col3:
                        st.metric("Category", category)
                else:
                    st.error(f"❌ Failed to add expense: {result.get('error', 'Unknown error')}")

# ============================================================================
# PAGE 4: ANALYTICS
# ============================================================================

elif page == "📈 Analytics":
    st.markdown("### 📈 Detailed Analytics")
    
    # Fetch spending summary for analytics
    with st.spinner("Loading analytics..."):
        summary = get_spending_summary(period_days)
    
    if summary['success']:
        data = summary['data'].get('data', {})
        by_category = data.get('by_category', [])
        
        # Tab navigation
        tab1, tab2, tab3 = st.tabs(["📊 Category Analysis", "📉 Trends", "🎯 Percentages"])
        
        # Tab 1: Category Analysis
        with tab1:
            st.markdown("#### Category-wise Spending Analysis")
            
            if by_category:
                # Create detailed table
                df_categories = pd.DataFrame(by_category)
                
                # Display summary table
                st.markdown("**Spending Summary:**")
                display_df = df_categories[[
                    'category', 'total', 'percentage', 'transaction_count', 
                    'average_per_transaction'
                ]].copy()
                
                display_df.columns = ['Category', 'Total ($)', '% of Total', 'Count', 'Avg ($)']
                display_df = display_df.round(2)
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Top spending category
                st.markdown("---")
                st.markdown("#### 🏆 Top Spending Category")
                
                if df_categories is not None and len(df_categories) > 0:
                    top_cat = df_categories.loc[df_categories['total'].idxmax()]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Category",
                            top_cat['category'].title(),
                            delta=f"#{df_categories['total'].rank(ascending=False)[df_categories['total'].idxmax()]:.0f}"
                        )
                    
                    with col2:
                        st.metric(
                            "Amount",
                            f"${top_cat['total']:.2f}",
                            delta=f"{top_cat['percentage']:.1f}% of total"
                        )
                    
                    with col3:
                        st.metric(
                            "Transactions",
                            f"{int(top_cat['transaction_count'])}"
                        )
        
        # Tab 2: Trends
        with tab2:
            st.markdown("#### Spending Trends")
            
            if by_category:
                # Sort by amount for better visualization
                df_sorted = pd.DataFrame(by_category).sort_values('total', ascending=True)
                
                fig = go.Figure(data=[
                    go.Bar(
                        y=df_sorted['category'],
                        x=df_sorted['total'],
                        orientation='h',
                        marker=dict(
                            color=df_sorted['total'],
                            colorscale='Viridis'
                        ),
                        hovertemplate='<b>%{y}</b><br>$%{x:.2f}<extra></extra>'
                    )
                ])
                
                fig.update_layout(
                    title="Spending by Category (Sorted)",
                    xaxis_title="Amount ($)",
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Tab 3: Percentages
        with tab3:
            st.markdown("#### Spending Distribution")
            
            if by_category:
                df_pct = pd.DataFrame(by_category).sort_values('percentage', ascending=False)
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=df_pct['category'],
                        y=df_pct['percentage'],
                        marker=dict(
                            color=[get_category_color(cat) for cat in df_pct['category']]
                        ),
                        hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>'
                    )
                ])
                
                fig.update_layout(
                    title="Spending Distribution (%)",
                    xaxis_title="Category",
                    yaxis_title="Percentage (%)",
                    height=400,
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False
                )
                fig.update_xaxes(tickangle=-45)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Create a table
                st.markdown("**Percentage Breakdown:**")
                
                display_pct = df_pct[['category', 'percentage']].copy()
                display_pct.columns = ['Category', 'Percentage (%)']
                display_pct['Percentage (%)'] = display_pct['Percentage (%)'].round(1)
                
                st.dataframe(display_pct, use_container_width=True, hide_index=True)
    
    else:
        st.error(f"Failed to load analytics: {summary.get('error', 'Unknown error')}")

# ============================================================================
# PAGE 5: AI INSIGHTS
# ============================================================================

elif page == "💡 AI Insights":
    st.markdown("### 💡 AI-Powered Insights & Recommendations")
    st.markdown("Get personalized recommendations to optimize your spending")
    
    # Fetch monthly insights
    with st.spinner("Analyzing spending patterns..."):
        insights = get_monthly_insights(months=3)
    
    if insights['success']:
        data = insights['data'].get('data', {})
        monthly_data = data.get('monthly_data', [])
        trends = data.get('trends', {})
        recommendations = data.get('recommendations', [])
        budget_alerts = data.get('budget_alerts', [])
        
        # Tabs for different insights
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Trends", "💰 Recommendations", "⚠️ Budget Alerts", "📅 Monthly Data"])
        
        # Tab 1: Trends
        with tab1:
            st.markdown("#### 📊 Spending Trends")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                trend = trends.get('overall_trend', 'stable')
                trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
                st.metric(
                    "Overall Trend",
                    trend.title(),
                    delta=trend_emoji,
                    delta_color="off"
                )
            
            with col2:
                st.metric(
                    "Spending Stability",
                    f"{trends.get('spending_stability', 0)*100:.0f}%",
                    help="Higher is more stable"
                )
            
            with col3:
                st.metric(
                    "Fastest Growing",
                    trends.get('fastest_growing_category', 'N/A').title()
                )
            
            st.markdown("---")
            
            # Trend description
            if trends.get('trend_description'):
                st.info(f"📈 {trends.get('trend_description')}")
        
        # Tab 2: Recommendations
        with tab2:
            st.markdown("#### 💰 Cost-Saving Recommendations")
            
            if recommendations:
                # Sort by priority
                high_priority = [r for r in recommendations if r.get('priority') == 'high']
                medium_priority = [r for r in recommendations if r.get('priority') == 'medium']
                low_priority = [r for r in recommendations if r.get('priority') == 'low']
                
                # High Priority
                if high_priority:
                    st.markdown("**🔴 High Priority**")
                    for rec in high_priority:
                        st.markdown(f"""
                        <div class="recommendation-card recommendation-priority-high">
                            <span class="priority-badge priority-badge-high">HIGH</span>
                            <h4>{rec.get('category', 'General').title()}</h4>
                            <p><b>{rec.get('suggestion', '')}</b></p>
                            <p style="color: green; font-weight: bold;">
                                💰 Potential savings: ${rec.get('potential_savings', 0):.2f} ({rec.get('savings_percentage', 0):.1f}%)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Medium Priority
                if medium_priority:
                    st.markdown("**🟠 Medium Priority**")
                    for rec in medium_priority:
                        st.markdown(f"""
                        <div class="recommendation-card recommendation-priority-medium">
                            <span class="priority-badge priority-badge-medium">MEDIUM</span>
                            <h4>{rec.get('category', 'General').title()}</h4>
                            <p><b>{rec.get('suggestion', '')}</b></p>
                            <p style="color: green; font-weight: bold;">
                                💰 Potential savings: ${rec.get('potential_savings', 0):.2f} ({rec.get('savings_percentage', 0):.1f}%)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Low Priority
                if low_priority:
                    st.markdown("**🟢 Low Priority**")
                    for rec in low_priority:
                        st.markdown(f"""
                        <div class="recommendation-card recommendation-priority-low">
                            <span class="priority-badge priority-badge-low">LOW</span>
                            <h4>{rec.get('category', 'General').title()}</h4>
                            <p><b>{rec.get('suggestion', '')}</b></p>
                            <p style="color: green; font-weight: bold;">
                                💰 Potential savings: ${rec.get('potential_savings', 0):.2f} ({rec.get('savings_percentage', 0):.1f}%)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No recommendations available at this time.")
        
        # Tab 3: Budget Alerts
        with tab3:
            st.markdown("#### ⚠️ Budget Alerts")
            
            if budget_alerts:
                for alert in budget_alerts:
                    status = alert.get('status', 'normal')
                    
                    if status == 'over_budget':
                        alert_type = "error"
                        emoji = "🔴"
                    elif status == 'near_budget':
                        alert_type = "warning"
                        emoji = "🟡"
                    else:
                        alert_type = "success"
                        emoji = "🟢"
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.metric(
                            f"{emoji} {alert['category'].title()}",
                            f"${alert.get('current_spending', 0):.2f}",
                            delta=f"Budget: ${alert.get('suggested_budget', 0):.2f}",
                            delta_color="off"
                        )
                    
                    with col2:
                        if status == 'over_budget':
                            excess = alert.get('excess_amount', 0)
                            st.warning(
                                f"Over budget by ${excess:.2f}. Consider reducing spending in {alert['category']}."
                            )
                        elif status == 'near_budget':
                            st.info(
                                f"Approaching budget limit. Current: ${alert.get('current_spending', 0):.2f} / Limit: ${alert.get('suggested_budget', 0):.2f}"
                            )
                        else:
                            st.success(
                                f"Within budget. Current: ${alert.get('current_spending', 0):.2f} / Limit: ${alert.get('suggested_budget', 0):.2f}"
                            )
            else:
                st.info("No budget alerts at this time. Keep up the good work! 🎉")
        
        # Tab 4: Monthly Data
        with tab4:
            st.markdown("#### 📅 Monthly Breakdown")
            
            if monthly_data:
                for month_data in monthly_data:
                    with st.expander(f"📆 {month_data.get('month', 'N/A')}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "Total Spending",
                                f"${month_data.get('total_spending', 0):.2f}"
                            )
                        
                        with col2:
                            st.metric(
                                "Transactions",
                                f"{month_data.get('transaction_count', 0)}"
                            )
                        
                        with col3:
                            st.metric(
                                "Daily Average",
                                f"${month_data.get('average_daily', 0):.2f}"
                            )
                        
                        # Month-over-month comparison
                        if month_data.get('vs_previous_month'):
                            vs = month_data['vs_previous_month']
                            change = vs.get('change_percentage', 0)
                            
                            st.markdown("---")
                            
                            if change > 0:
                                st.warning(f"📈 Spending increased by {abs(change):.1f}% compared to previous month")
                            elif change < 0:
                                st.success(f"📉 Spending decreased by {abs(change):.1f}% compared to previous month")
                            else:
                                st.info("➡️ Spending unchanged compared to previous month")
                        
                        # Top categories
                        if month_data.get('top_categories'):
                            st.markdown("**Top Spending Categories:**")
                            for cat in month_data['top_categories'][:3]:
                                st.write(f"• {cat['category'].title()}: ${cat['amount']:.2f} ({cat['percentage']:.1f}%)")
    
    else:
        st.error(f"Failed to load insights: {insights.get('error', 'Unknown error')}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 30px;">
    <p>💰 <b>FinSight AI</b> - Smart Expense Tracking Dashboard</p>
    <p>Version 1.0.0 | <a href="http://localhost:8000/docs">API Documentation</a></p>
</div>
""", unsafe_allow_html=True)
