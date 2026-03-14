# FinSight AI Dashboard - Feature Documentation

**Version:** 1.0.0  
**Status:** ✅ Complete  
**Last Updated:** March 2024

---

## 📖 Table of Contents

1. [Dashboard Overview](#dashboard-overview)
2. [Receipt Upload](#receipt-upload)
3. [Add Expense](#add-expense)
4. [Analytics](#analytics)
5. [AI Insights](#ai-insights)
6. [Customization](#customization)

---

## 📊 Dashboard Overview

The **Dashboard** page provides a comprehensive overview of your spending habits with key metrics and visual charts.

### Key Features

#### 1. **Key Metrics Row**
Four essential metrics displayed at the top:

| Metric | Description | Example |
|--------|-------------|---------|
| 📊 **Total Spending** | Sum of all expenses in selected period | $1,250.50 |
| 📈 **Daily Average** | Average spending per day | $41.68/day |
| 💬 **Transactions** | Total number of expenses | 30 |
| 🏆 **Top Category** | Highest spending category | Food (35%) |

**Usage:** Click any metric card to view drill-down details

#### 2. **Spending Distribution Pie Chart**
Visual representation of spending by category.

**Features:**
- 7 color-coded categories
- Hover for exact amounts and percentages
- Click legend to toggle categories
- Zoom and pan available

**Interpretation:**
- Large slices = High spending categories
- Small slices = Lower spending categories
- Hover to see exact breakdown

#### 3. **Category Comparison Bar Chart**
Bar chart showing spending by category in descending order.

**Features:**
- Sorted from highest to lowest
- Color-coded by category
- Hover for exact amounts
- Responsive to time period changes

**Interpretation:**
- Taller bars = More spending
- Identify top spending categories instantly
- Compare relative spending amounts

#### 4. **Category Details Table**
Detailed breakdown of each category.

**Columns:**
| Column | Description |
|--------|-------------|
| **Category** | Category name (Food, Transport, etc.) |
| **Total** | Sum of all expenses in category |
| **Percentage** | Percentage of total spending |
| **Count** | Number of transactions |
| **Average** | Average transaction amount |

**Usage:**
- Sort by clicking column headers
- Identify spending patterns
- Find categories to optimize

#### 5. **AI Insights Preview**
Quick preview of top AI recommendations.

**Shows:**
- Top 3 recommendations
- Priority level (High/Medium/Low)
- Suggested savings amount
- Category affected

**Actions:**
- Click "View All" to go to AI Insights page
- Prioritize high-priority recommendations

### Time Period Controls
Located in the sidebar:
- Slider from 1-365 days
- Default: Last 30 days
- Dashboard updates instantly
- All metrics recalculate

---

## 📸 Receipt Upload

The **Upload Receipt** page enables automatic expense extraction from receipt images using OCR (Optical Character Recognition).

### How to Use

#### Step 1: Upload Image
```
1. Click the file upload area
2. Select a JPG, PNG, GIF, or BMP file
3. File must be under 10MB
4. Preview appears in sidebar
```

#### Step 2: Analyze Receipt
```
1. Click "Analyze Receipt" button
2. System processes the image
3. Extracts merchant, amount, date, and category
4. Shows confidence score for accuracy
```

#### Step 3: Review & Confirm
```
1. Review extracted information
2. Verify merchant name
3. Check amount and currency
4. Confirm category classification
5. Click "Confirm & Save" if correct
```

### Extracted Information

The system extracts:

| Field | Example | Confidence |
|-------|---------|------------|
| **Merchant** | "Whole Foods Market" | 95% |
| **Amount** | $45.32 | 92% |
| **Date** | 2024-03-15 | 88% |
| **Category** | Food | 85% |
| **Items** | Groceries | Optional |

### Confidence Scores

- **90-100%** ✅ High confidence - Use as-is
- **70-89%** ⚠️ Medium confidence - Review before saving
- **Below 70%** ❌ Low confidence - Edit before saving

### Best Practices

✅ **Good Receipts:**
- Clear, well-lit photos
- Straight-on angle
- Merchant name visible
- Total amount clear
- Date visible

❌ **Poor Receipts:**
- Blurry or dark photos
- Angled or tilted
- Crumpled or torn
- Faded text
- Missing key information

### Supported Formats

- ✅ **JPG/JPEG** - Best for photos
- ✅ **PNG** - Best for clarity
- ✅ **GIF** - Supported
- ✅ **BMP** - Supported
- ❌ **PDF** - Not supported
- ❌ **HEIC** - Not supported

### Tips for Better Results

1. **Take Clear Photos**
   - Use good lighting
   - Keep straight angle
   - Focus on text
   - Include full receipt

2. **Upload Promptly**
   - Upload same day as expense
   - Memory is fresh for review
   - Better categorization
   - More accurate amounts

3. **Verify Results**
   - Always check merchant name
   - Confirm correct amount
   - Verify date accuracy
   - Check category classification

---

## ➕ Add Expense

The **Add Expense** page allows manual entry of expenses for situations where receipts are unavailable.

### Form Fields

#### 1. **Date**
```
Type: Date Picker
Default: Today's date
Range: Any past or future date
Required: Yes
```

**How to Use:**
- Click date field
- Calendar popup appears
- Select date
- Or type in MM/DD/YYYY format

#### 2. **Merchant Name**
```
Type: Text input
Placeholder: "Where did you spend?"
Max Length: 100 characters
Required: Yes
```

**Examples:**
- "Starbucks Coffee"
- "Amazon.com"
- "Shell Gas Station"
- "CVS Pharmacy"

**Validation:**
- Cannot be empty
- At least 2 characters
- Shows error if blank

#### 3. **Category**
```
Type: Dropdown selector
Default: None
Required: Yes
```

**Available Categories:**
1. 🍔 **Food** - Restaurants, groceries, delivery
2. 🚗 **Transport** - Gas, transit, maintenance
3. 🛍️ **Shopping** - Clothing, online, stores
4. ⚡ **Utilities** - Electric, water, internet
5. 🎬 **Entertainment** - Movies, games, subs
6. 🏥 **Health** - Medical, fitness, wellness
7. 📝 **Other** - Anything else

**How to Choose:**
- Select best fit category
- Affects analytics and recommendations
- Can be changed later
- Consistent categorization improves insights

#### 4. **Amount**
```
Type: Number input
Currency: USD ($)
Decimals: 2 (e.g., $12.50)
Required: Yes
```

**Validation:**
- Must be greater than $0.00
- Automatically formatted
- Shows error if zero or negative
- Maximum 7 digits

**Examples:**
- $5.50
- $125.00
- $0.99

#### 5. **Description**
```
Type: Text area
Max Length: 500 characters
Required: No
Placeholder: "Add details or notes..."
```

**Use Cases:**
- Store additional details
- Record what was purchased
- Note special occasions
- Track split expenses
- Remember reasons for expense

**Examples:**
- "Weekly groceries with family"
- "Uber to airport, round trip"
- "Gift for sister's birthday"
- "Monthly gym membership"

### Form Validation

| Field | Rules | Error Message |
|-------|-------|---------------|
| Date | Valid date, past or future | Invalid date |
| Merchant | 2-100 characters, required | Merchant name required |
| Category | Must select one | Category required |
| Amount | > $0.00 | Amount must be greater than 0 |

### Submission Process

```
1. Fill all required fields
   ↓
2. Review entered information
   ↓
3. Click "Add Expense" button
   ↓
4. System validates form
   ↓
5. Shows success or error message
   ↓
6. Form clears if successful
```

### Success Feedback

When expense is added successfully:
- ✅ Green success message appears
- Shows expense details
- Expense added to system
- Dashboard updates automatically
- Form clears for next entry

### Error Handling

If validation fails:
- ❌ Red error message appears
- Points out missing field
- Prevents submission
- Allows correction

---

## 📈 Analytics

The **Analytics** page provides detailed analysis of your spending patterns through multiple visualizations.

### Tab 1: Category Analysis

**Purpose:** Detailed breakdown of spending by category

**Components:**

1. **Summary Metrics**
   ```
   Total Spending: $1,250.50
   Number of Categories: 7
   Average per Category: $178.64
   ```

2. **Top Category Highlight**
   ```
   Name: Food
   Total: $437.68
   Count: 15 transactions
   Average: $29.18
   Percentage: 35%
   ```

3. **Full Category Table**

   | Category | Total | % of Total | Count | Average |
   |----------|-------|-----------|-------|---------|
   | Food | $437.68 | 35.0% | 15 | $29.18 |
   | Transport | $312.50 | 25.0% | 8 | $39.06 |
   | Shopping | $225.00 | 18.0% | 5 | $45.00 |
   | Utilities | $150.00 | 12.0% | 3 | $50.00 |
   | Entertainment | $75.00 | 6.0% | 2 | $37.50 |
   | Health | $50.00 | 4.0% | 1 | $50.00 |
   | Other | $0.00 | 0.0% | 0 | $0.00 |

**Actions:**
- Sort by clicking column headers
- Click category for drill-down
- Identify spending patterns
- Compare categories

**Insights:**
- Food is highest spending (35%)
- 7 categories tracked
- Transport is second at 25%
- Other category has no expenses

### Tab 2: Spending Trends

**Purpose:** Visualize spending trends over selected time period

**Chart Type:** Horizontal Bar Chart

**Features:**
- Sorted from highest to lowest spending
- Color-coded by category
- Amount labels on bars
- Hover for exact values

**Interpretation:**
```
Food     ████████████████████ $437.68
Transport ████████████ $312.50
Shopping ████████ $225.00
Utilities ██████ $150.00
Entertainment ███ $75.00
Health ██ $50.00
Other  $0.00
```

**Use Cases:**
- Identify top spending categories
- Compare relative spending
- Track changes over time
- Spot unusual spending patterns

**Example Insights:**
- "Food spending is 40% of total budget"
- "Transport is second highest at 25%"
- "Entertainment and health are minimal"

### Tab 3: Percentage Distribution

**Purpose:** Show percentage breakdown of spending

**Chart Type:** Vertical Bar Chart

**Components:**

1. **Percentage Chart**
   - Bars show percentage of total
   - All bars together = 100%
   - Color-coded by category
   - Hover for exact percentages

2. **Detailed Table**

   | Category | Percentage | Visual |
   |----------|-----------|--------|
   | Food | 35% | ███████ |
   | Transport | 25% | █████ |
   | Shopping | 18% | ███ |
   | Utilities | 12% | ██ |
   | Entertainment | 6% | █ |
   | Health | 4% | • |
   | Other | 0% | • |

**Insights:**
- Identify spending proportions
- See allocation at a glance
- Identify budget areas
- Plan adjustments

**Example Analysis:**
- "Food is taking 35% of budget - could reduce?"
- "Transport is 25% - consider alternatives?"
- "Entertainment only 6% - increase budget?"

---

## 💡 AI Insights

The **AI Insights** page provides intelligent analysis and personalized recommendations based on your spending patterns.

### Tab 1: Trends

**Purpose:** Understand your overall spending direction

**Components:**

1. **Overall Trend**
   - **Increasing** 📈 - Spending is going up
   - **Decreasing** 📉 - Spending is going down
   - **Stable** 📊 - Spending is consistent

2. **Spending Stability**
   ```
   Stability Score: 75%
   
   0-33%   = Very volatile
   34-66%  = Somewhat stable
   67-100% = Very stable
   ```

3. **Fastest Growing Category**
   ```
   Category: Food
   Previous: $400
   Current: $438
   Growth: +9.5%
   ```

4. **Trend Description**
   ```
   "Your spending has increased by 12% 
    over the last 30 days. Food category 
    is driving the increase with +9.5% growth. 
    Consider reviewing restaurant spending 
    to align with budget."
   ```

**Interpretation:**
- Green = Positive trend
- Red = Concerning trend
- Yellow = Neutral trend
- Use for budget planning

### Tab 2: Recommendations

**Purpose:** AI-powered cost-saving suggestions

**Features:**

1. **Priority Filtering**
   - **High Priority** 🔴 - Immediate action needed
   - **Medium Priority** 🟠 - Should consider
   - **Low Priority** 🟢 - Nice to have

2. **Recommendation Card Structure**
   ```
   ┌─────────────────────────────────┐
   │ 🔴 High Priority               │
   │ Reduce food spending            │
   │                                 │
   │ Your food expenses are 40% of   │
   │ budget. Consider:               │
   │ - Cook at home more             │
   │ - Use grocery store instead     │
   │   of restaurants                │
   │                                 │
   │ 💰 Potential Savings: $50/month │
   └─────────────────────────────────┘
   ```

3. **Savings Calculation**
   - Based on category trends
   - Realistic reduction targets
   - Monthly savings estimate
   - Annual savings potential

**Examples:**

| Priority | Category | Recommendation | Savings |
|----------|----------|-----------------|---------|
| High | Food | Reduce restaurant visits | $50/mo |
| High | Transport | Carpool 2x/week | $40/mo |
| Medium | Shopping | Skip unnecessary purchases | $25/mo |
| Medium | Entertainment | Cancel unused subscriptions | $15/mo |
| Low | Health | No changes needed | $0 |

**Action Items:**

✅ **High Priority Recommendations:**
1. Review and acknowledge
2. Create action plan
3. Implement changes
4. Track progress

⚠️ **Medium Priority Recommendations:**
1. Consider impact
2. Plan if feasible
3. Implement gradually
4. Monitor results

ℹ️ **Low Priority Recommendations:**
1. Review for interest
2. Implement if wanted
3. Monitor if implemented

### Tab 3: Budget Alerts

**Purpose:** Monitor category-specific budget status

**Alert Status Indicators:**

| Status | Color | Meaning |
|--------|-------|---------|
| 🟢 Normal | Green | Within budget, all good |
| 🟡 Near Budget | Yellow | Approaching limit |
| 🔴 Over Budget | Red | Exceeded budget |

**Budget Alert Structure:**
```
┌────────────────────────────────┐
│ Food                      🔴   │
│                                │
│ Current Spending: $438         │
│ Suggested Budget: $400         │
│                                │
│ ⚠️ Over by $38                │
│ Reduce food spending to $400   │
│ to stay within budget          │
└────────────────────────────────┘
```

**Alert Examples:**

**High Alert (Over Budget):**
```
🔴 Food - Over budget by $38
• Current: $438 | Budget: $400
• Action: Reduce spending by $38/month
```

**Medium Alert (Near Budget):**
```
🟡 Transport - Near budget at $390
• Current: $390 | Budget: $400
• Action: Limit spending to stay under
```

**Low Alert (Healthy):**
```
🟢 Entertainment - $75 of $150
• Current: $75 | Budget: $150
• Status: On track, 50% remaining
```

**How to Use Alerts:**
1. Review alert status regularly
2. Identify over-budget categories
3. Take corrective action
4. Plan preventative measures
5. Adjust budgets as needed

### Tab 4: Monthly Data

**Purpose:** Track spending across months with comparisons

**Structure:**

**Expandable Month Sections:**
```
▼ March 2024
  Total Spending: $1,250.50
  Number of Transactions: 30
  Daily Average: $41.68
  
  Month-over-Month Change: +12.5%
  (Up from $1,112.44 in February)
  
  Top Categories:
  1. Food - $437.68 (35%)
  2. Transport - $312.50 (25%)
  3. Shopping - $225.00 (18%)
```

**Monthly Comparison:**

| Metric | This Month | Last Month | Change |
|--------|-----------|-----------|--------|
| Total | $1,250.50 | $1,112.44 | +12.5% ↑ |
| Transactions | 30 | 28 | +7.1% |
| Daily Avg | $41.68 | $37.08 | +12.4% ↑ |
| Top Category | Food | Food | Same |

**Year-to-Date Summary:**
```
Q1 2024 Spending:
January:   $1,050.00
February:  $1,112.44
March:     $1,250.50
─────────────────────
Total:     $3,412.94
Average:   $1,137.65
```

**Trend Analysis:**
- Identify seasonal patterns
- Track monthly growth
- Spot anomalies
- Plan budget adjustments

---

## 🎨 Customization

### Color Customization

The dashboard uses a 7-color category scheme:

| Category | Color | Hex Code |
|----------|-------|----------|
| Food | Orange | #FF9500 |
| Transport | Blue | #0066CC |
| Shopping | Purple | #9933FF |
| Utilities | Green | #00BB00 |
| Entertainment | Red | #EE4444 |
| Health | Cyan | #00CCFF |
| Other | Gray | #666666 |

**To Change Colors:**

Edit `streamlit_app.py`:
```python
def get_category_color(category: str) -> str:
    colors = {
        "food": "#FF9500",        # Change this
        "transport": "#0066CC",   # Change this
        # ... etc
    }
    return colors.get(category.lower(), "#666666")
```

### Category Customization

**To Add New Category:**

1. Update category list in Add Expense form:
```python
categories = [
    "Food", "Transport", "Shopping",
    "Utilities", "Entertainment", 
    "Health", "Other", "YOUR_NEW_CATEGORY"  # Add here
]
```

2. Add color mapping:
```python
def get_category_color(category: str) -> str:
    colors = {
        # ... existing
        "your_new_category": "#AABBCC"  # Add color
    }
```

### API URL Customization

**Change Default API:**

Edit `streamlit_app.py`:
```python
DEFAULT_API_URL = "http://localhost:8000/api"  # Change this

# Or use environment variable:
API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000/api")
```

### Theme Customization

**Change Dashboard Theme:**

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## 📚 Feature Comparison

| Feature | Dashboard | Upload | Add Expense | Analytics | Insights |
|---------|-----------|--------|------------|-----------|----------|
| View spending | ✅ | - | - | ✅ | - |
| Add expenses | - | ✅ | ✅ | - | - |
| View charts | ✅ | - | - | ✅ | - |
| Time periods | ✅ | - | - | ✅ | ✅ |
| Recommendations | - | - | - | - | ✅ |
| Budget alerts | - | - | - | - | ✅ |
| Category details | ✅ | - | - | ✅ | - |

---

## 🎯 Common Use Cases

### Case 1: Daily Expense Tracking
```
1. Open "Add Expense" page
2. Enter daily purchases
3. Review on Dashboard
4. Track in Analytics
```

### Case 2: Receipt Organization
```
1. Open "Upload Receipt" page
2. Upload receipt images
3. Verify extracted data
4. Expenses saved automatically
```

### Case 3: Budget Review
```
1. Go to "AI Insights"
2. Check budget alerts
3. Review recommendations
4. Plan spending adjustments
```

### Case 4: Trend Analysis
```
1. Open Analytics page
2. View spending trends
3. Compare categories
4. Identify patterns
```

---

## ✅ Summary

The FinSight AI Dashboard provides comprehensive expense tracking with:
- ✅ Real-time metrics and charts
- ✅ Receipt OCR processing
- ✅ Manual expense entry
- ✅ Detailed analytics
- ✅ AI recommendations
- ✅ Budget alerts
- ✅ Professional design

**Next Step:** Start using the dashboard to track your expenses!

---

**Version:** 1.0.0  
**Status:** ✅ Complete  
**Last Updated:** March 2024
