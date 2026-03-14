# FinSight AI Dashboard - Quick Start Card

## ⚡ 5-Minute Setup

### Terminal 1: Start API Server
```bash
cd "FinSight AI/backend"
uvicorn main:app --reload
```
✅ API running on `http://localhost:8000`

### Terminal 2: Install & Run Dashboard
```bash
cd "FinSight AI"
pip install -r streamlit_requirements.txt
streamlit run streamlit_app.py
```
✅ Dashboard running on `http://localhost:8501`

---

## 🎯 Dashboard Navigation

| Page | Icon | Purpose |
|------|------|---------|
| 📊 **Dashboard** | 📈 | View metrics, charts, and overview |
| 📸 **Upload Receipt** | 🖼️ | Upload receipt images for OCR analysis |
| ➕ **Add Expense** | ✏️ | Manually enter expenses |
| 📈 **Analytics** | 📊 | Detailed category and trend analysis |
| 💡 **AI Insights** | 🤖 | Get recommendations and budget alerts |

---

## 🎨 Dashboard Features at a Glance

### 📊 Dashboard Page
- **4 Metrics:** Total Spending, Daily Average, Transactions, Top Category
- **Pie Chart:** Spending by category
- **Bar Chart:** Category breakdown
- **Category Table:** Detailed breakdown

### 📸 Upload Receipt Page
1. Click file uploader
2. Select JPG/PNG/GIF/BMP image
3. Click "Analyze Receipt"
4. Review extracted data (merchant, amount, category, date)
5. Automatically saved ✅

### ➕ Add Expense Page
1. Select date (defaults to today)
2. Enter merchant name
3. Choose category
4. Enter amount
5. Add optional description
6. Click "Add Expense" ✅

### 📈 Analytics Page
- **Category Analysis:** All categories with totals and percentages
- **Spending Trends:** Bar chart sorted by amount
- **Percentage Distribution:** Breakdown of spending percentages

### 💡 AI Insights Page
- **Trends:** Spending direction and stability
- **Recommendations:** Cost-saving suggestions by priority
- **Budget Alerts:** Budget status per category
- **Monthly Data:** Month-by-month breakdown with comparisons

---

## 🛠️ Common Tasks

### Change API URL
1. Click gear icon in sidebar
2. Enter new API URL
3. Click Update
4. Done! ✅

### View Different Time Period
1. Use "Days to Analyze" slider in sidebar (1-365 days)
2. Dashboard updates automatically

### Clear All Data
```bash
# Delete database and restart
rm backend/finsight.db
```

### Check API Health
```bash
curl http://localhost:8000/api/health
```

---

## ⚠️ Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Connection refused"** | Start API: `uvicorn main:app --reload` |
| **"Port already in use"** | `streamlit run streamlit_app.py --server.port 8502` |
| **"Module not found"** | `pip install -r streamlit_requirements.txt` |
| **Dashboard blank** | Press `R` to clear cache |
| **Images not uploading** | Ensure file is JPG/PNG/GIF/BMP, under 10MB |

---

## 📱 UI Tips

- **Click metric cards** for drill-down details
- **Hover over charts** for detailed information
- **Use sidebar slider** to change time period
- **Press R key** to refresh/clear cache
- **Sidebar collapses** on mobile for more space

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| Dashboard | `http://localhost:8501` |
| API | `http://localhost:8000` |
| API Docs | `http://localhost:8000/docs` |
| API Redoc | `http://localhost:8000/redoc` |

---

## 📊 Expense Categories

1. **Food** 🍔 - Restaurants, groceries, food delivery
2. **Transport** 🚗 - Gas, public transit, car maintenance
3. **Shopping** 🛍️ - Clothing, online purchases, stores
4. **Utilities** ⚡ - Electricity, water, internet, phone
5. **Entertainment** 🎬 - Movies, games, subscriptions
6. **Health** 🏥 - Medical, fitness, wellness
7. **Other** 📝 - Everything else

---

## 💡 Pro Tips

✅ **Upload receipts immediately** after purchases for accurate data  
✅ **Use consistent merchant names** for better analytics  
✅ **Review recommendations weekly** to adjust spending  
✅ **Monitor budget alerts** to stay within budget  
✅ **Check trends monthly** to identify patterns  

---

## 🚀 Next Steps

1. ✅ Dashboard is running
2. ✅ Upload first receipt or add expense
3. ✅ View dashboard metrics
4. ✅ Check analytics page
5. ✅ Review AI recommendations
6. ✅ Adjust budget based on insights

---

## 📞 Need Help?

- **Full Setup Guide:** `STREAMLIT_SETUP_GUIDE.md`
- **API Documentation:** `http://localhost:8000/docs`
- **Dashboard Logs:** Check terminal output
- **Issues:** Review troubleshooting section above

---

**Status:** ✅ Ready to Use  
**Version:** 1.0.0  
**Last Updated:** March 2024

🎉 **Start tracking your expenses now!**
