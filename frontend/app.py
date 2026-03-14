"""FinSight AI - Streamlit Frontend Application"""

import os
from pathlib import Path

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="FinSight AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def check_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health/", timeout=2)
        return response.status_code == 200
    except:
        return False


def upload_receipt(file):
    """Upload receipt file to backend"""
    try:
        files = {"file": file}
        response = requests.post(f"{API_BASE_URL}/api/expenses/upload", files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None


def get_expenses(skip=0, limit=100):
    """Fetch expenses from backend"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/expenses/",
            params={"skip": skip, "limit": limit},
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch expenses: {str(e)}")
        return []


def get_spending_summary(days=30):
    """Get spending summary from backend"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/insights/spending-summary",
            params={"days": days},
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch spending summary: {str(e)}")
        return None


def get_spending_trends(days=30):
    """Get spending trends from backend"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/insights/trends",
            params={"days": days},
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch trends: {str(e)}")
        return []


def get_recommendations(days=30):
    """Get cost-saving recommendations from backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/insights/recommendations",
            json={"days": days},
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch recommendations: {str(e)}")
        return None


# Main app
def main():
    # Header
    st.title("💰 FinSight AI")
    st.markdown("### AI-Powered Financial Assistant")

    # Check API health
    if not check_api_health():
        st.error(
            "⚠️ Backend API is not running. Please start the backend server at "
            f"{API_BASE_URL}"
        )
        st.stop()

    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Upload Receipt", "Expenses", "Analytics", "Recommendations"],
    )

    # Period selector in sidebar
    days = st.sidebar.slider("Analysis Period (days)", 1, 365, 30)

    if page == "Dashboard":
        show_dashboard(days)
    elif page == "Upload Receipt":
        show_upload_page()
    elif page == "Expenses":
        show_expenses_page()
    elif page == "Analytics":
        show_analytics_page(days)
    elif page == "Recommendations":
        show_recommendations_page(days)


def show_dashboard(days):
    """Display main dashboard"""
    st.header("Dashboard")

    # Get data
    summary = get_spending_summary(days)
    trends = get_spending_trends(days)

    if not summary:
        st.warning("No expense data available")
        return

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Spending", f"${summary['total_spending']:.2f}")

    with col2:
        st.metric("Transactions", summary['transaction_count'])

    with col3:
        st.metric("Average Transaction", f"${summary['average_transaction']:.2f}")

    with col4:
        st.metric("Top Category", summary['highest_category'])

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Category breakdown
        categories = summary['categories']
        if categories:
            df = pd.DataFrame(categories)
            fig = px.pie(
                df,
                values='total_amount',
                names='category',
                title='Spending by Category',
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Spending trend
        if trends:
            df = pd.DataFrame(trends)
            df['date'] = pd.to_datetime(df['date'])
            fig = px.line(
                df,
                x='date',
                y='amount',
                title='Spending Trend',
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)


def show_upload_page():
    """Display receipt upload page"""
    st.header("Upload Receipt")
    st.markdown("Upload a receipt image to automatically extract expense information")

    uploaded_file = st.file_uploader(
        "Choose receipt image",
        type=["jpg", "jpeg", "png", "gif", "bmp"],
    )

    if uploaded_file is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)

        with col2:
            st.info("Processing receipt...")

            expense = upload_receipt(uploaded_file)

            if expense:
                st.success("✅ Receipt processed successfully!")

                st.markdown("### Extracted Information")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Merchant:** {expense['merchant_name']}")
                    st.markdown(f"**Amount:** ${expense['amount']:.2f}")

                with col2:
                    st.markdown(f"**Category:** {expense['category']}")
                    st.markdown(f"**Confidence:** {expense['confidence_score']:.1%}")

                st.markdown(f"**Date:** {expense['date']}")

                if expense['description']:
                    st.markdown(f"**Description:** {expense['description'][:200]}...")


def show_expenses_page():
    """Display expenses list page"""
    st.header("Expense List")

    expenses = get_expenses()

    if not expenses:
        st.info("No expenses found")
        return

    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)

    # Display as table
    st.dataframe(
        df[['merchant_name', 'amount', 'category', 'date', 'confidence_score']],
        use_container_width=True,
    )

    st.markdown(f"**Total Records:** {len(df)}")


def show_analytics_page(days):
    """Display analytics page"""
    st.header("Spending Analytics")

    summary = get_spending_summary(days)

    if not summary:
        st.warning("No data available")
        return

    # Category breakdown
    st.subheader("Spending by Category")

    categories = summary['categories']
    if categories:
        df = pd.DataFrame(categories)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                df,
                x='category',
                y='total_amount',
                title='Total by Category',
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                df,
                x='category',
                y='transaction_count',
                title='Transaction Count by Category',
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)


def show_recommendations_page(days):
    """Display recommendations page"""
    st.header("Cost-Saving Recommendations")

    recommendations = get_recommendations(days)

    if not recommendations:
        st.warning("Could not generate recommendations")
        return

    st.subheader(f"Analysis: {recommendations['analysis_period']}")
    st.metric("Total Potential Savings", f"${recommendations['total_potential_savings']:.2f}")

    st.divider()

    suggestions = recommendations['suggestions']
    if not suggestions:
        st.info("No recommendations available")
        return

    for i, suggestion in enumerate(suggestions, 1):
        with st.expander(f"{i}. {suggestion['title']}", expanded=i==1):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(suggestion['description'])
                st.markdown(f"**Category:** {suggestion['category']}")

            with col2:
                st.markdown(f"**Savings:** ${suggestion['potential_savings']:.2f}")
                priority_color = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢",
                }
                st.markdown(f"**Priority:** {priority_color.get(suggestion['priority'], '❓')} {suggestion['priority'].title()}")


if __name__ == "__main__":
    main()
