# FinSight AI Dashboard - Troubleshooting & FAQ

**Version:** 1.0.0  
**Status:** ✅ Complete  
**Last Updated:** March 2024

---

## 🆘 Troubleshooting Guide

### Connection Issues

#### ❌ Problem: "Connection refused" when opening dashboard

**Symptoms:**
- Dashboard shows "API Connection Error"
- Can't see any expenses
- Error appears immediately on load

**Causes:**
- API server not running
- Wrong API URL configured
- Port 8000 is blocked

**Solutions:**

✅ **Solution 1: Start API Server**
```bash
# Terminal 1
cd "FinSight AI/backend"
uvicorn main:app --reload --port 8000
```

Wait for: `Uvicorn running on http://127.0.0.1:8000`

✅ **Solution 2: Check API URL**
1. Open dashboard
2. Click gear icon in sidebar
3. Verify URL: `http://localhost:8000/api`
4. Update if incorrect
5. Refresh page (F5)

✅ **Solution 3: Check Firewall**
```bash
# macOS
sudo lsof -i :8000

# If port blocked, use different port:
uvicorn main:app --reload --port 8001
# Then update API URL in sidebar to: http://localhost:8001/api
```

---

#### ❌ Problem: "Port 8501 already in use"

**Symptoms:**
- Error: "Port 8501 is already in use"
- Can't start dashboard

**Causes:**
- Another Streamlit app running
- Previous session not closed
- Port blocked by firewall

**Solutions:**

✅ **Solution 1: Use Different Port**
```bash
streamlit run streamlit_app.py --server.port 8502
```
Then access: `http://localhost:8502`

✅ **Solution 2: Kill Process on Port 8501**
```bash
# macOS/Linux
lsof -ti:8501 | xargs kill -9

# Then start normally
streamlit run streamlit_app.py
```

✅ **Solution 3: Check Active Processes**
```bash
# macOS
ps aux | grep streamlit

# Kill by process ID if needed
kill -9 <PID>
```

---

### Performance Issues

#### ❌ Problem: Dashboard is slow or unresponsive

**Symptoms:**
- Page takes long time to load
- Charts don't render
- Buttons don't respond
- Freezing/lag

**Causes:**
- Too many expenses (slow query)
- Large time period selected
- API is slow
- Computer resources low

**Solutions:**

✅ **Solution 1: Reduce Time Period**
1. Use sidebar "Days to Analyze" slider
2. Start with 7-30 days instead of 365
3. Dashboard should load faster

✅ **Solution 2: Clear Cache**
```
Press R in dashboard to clear cache
Dashboard will reload
```

✅ **Solution 3: Restart Dashboard**
```bash
# In terminal running Streamlit, press Ctrl+C
# Then restart:
streamlit run streamlit_app.py
```

✅ **Solution 4: Check System Resources**
```bash
# macOS
top -n 5
# Look for CPU and memory usage
# If above 80%, close other apps
```

✅ **Solution 5: Restart API Server**
```bash
# Terminal running API, press Ctrl+C
# Restart:
cd backend
uvicorn main:app --reload
```

---

### File Upload Issues

#### ❌ Problem: "File upload failed" or "Unsupported file type"

**Symptoms:**
- Can't upload receipt image
- Error message appears
- File doesn't process

**Causes:**
- Wrong file format (PDF, HEIC, etc.)
- File too large (>10MB)
- Corrupted file
- Missing file extension

**Solutions:**

✅ **Solution 1: Check File Format**

**Supported:** JPG, PNG, GIF, BMP  
**Not Supported:** PDF, HEIC, WebP, TIFF

**To Convert:**
```bash
# macOS - Use Preview app
# 1. Open image in Preview
# 2. File > Export
# 3. Save as JPG or PNG

# Or use command line:
# Install ImageMagick: brew install imagemagick
convert image.pdf image.jpg
convert image.heic image.jpg
```

✅ **Solution 2: Check File Size**
```bash
# macOS/Linux
ls -lh receipt.jpg
# File should be under 10MB
```

**If too large:**
```bash
# Compress using ImageMagick
convert large.jpg -resize 1920x1080 -quality 80 small.jpg

# Or use Preview (macOS)
# 1. Open in Preview
# 2. Tools > Adjust Size
# 3. Reduce dimensions
# 4. Export as JPG
```

✅ **Solution 3: Verify File Integrity**
```bash
# Check if file is valid image
file receipt.jpg
# Should show: JPEG image data

# If corrupted, re-take photo
```

---

#### ❌ Problem: "OCR extraction failed" or low confidence

**Symptoms:**
- Upload works but extraction fails
- Confidence scores very low (<50%)
- Merchant/amount not extracted

**Causes:**
- Poor image quality
- Blurry photo
- Bad lighting
- Crumpled/torn receipt
- Non-English receipt

**Solutions:**

✅ **Solution 1: Retake Better Photo**
- Good lighting (natural or bright)
- Straight-on angle (not tilted)
- Clear focus on text
- Include full receipt
- No shadows or glare

✅ **Solution 2: Edit Extracted Data**
- If confidence low, edit manually:
  1. Click "Edit" button
  2. Correct merchant name
  3. Verify amount
  4. Select correct category
  5. Confirm date
  6. Save

✅ **Solution 3: Use Manual Entry Instead**
- If OCR fails consistently
- Click "Add Expense" page
- Enter details manually
- Same result, no OCR needed

---

### Form Issues

#### ❌ Problem: "Cannot submit form" or validation errors

**Symptoms:**
- Form won't submit
- Red error messages appear
- Fields marked as invalid

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| "Merchant name required" | Empty merchant field | Enter merchant name |
| "Amount must be > 0" | Amount is $0 or negative | Enter positive amount |
| "Category required" | No category selected | Select a category |
| "Invalid date" | Future date (some systems) | Use past or today's date |

**Solutions:**

✅ **Solution 1: Check All Fields**
```
☐ Date: Valid date (today or earlier)
☐ Merchant: At least 2 characters
☐ Category: One selected
☐ Amount: Greater than $0.00
```

✅ **Solution 2: Review Error Message**
- Read error message carefully
- It tells you which field is wrong
- Fix that specific field
- Try submitting again

✅ **Solution 3: Clear and Retry**
```
1. Click "Clear Form" button
2. Re-enter all data carefully
3. Double-check each field
4. Submit again
```

---

### Data Issues

#### ❌ Problem: "Data not updating" or outdated information

**Symptoms:**
- New expenses don't appear
- Metrics still show old values
- Charts don't update

**Causes:**
- Cache not refreshed
- Page not reloaded
- API not responding
- Database not saved

**Solutions:**

✅ **Solution 1: Clear Cache (Fastest)**
```
Press R in dashboard
Streamlit clears cache and reloads
Data should update
```

✅ **Solution 2: Reload Page**
```
Press F5 or Cmd+R
Browser refreshes
Dashboard reloads
```

✅ **Solution 3: Restart Dashboard**
```bash
# In terminal running Streamlit:
Ctrl+C  # Stop it
streamlit run streamlit_app.py  # Start again
```

✅ **Solution 4: Check Time Period**
1. Look at sidebar "Days to Analyze"
2. If set to 7 days, only shows last 7 days
3. Increase to 30 or 365 days
4. New expenses might be outside period

---

#### ❌ Problem: "Cannot find expense I just added"

**Symptoms:**
- Just added expense
- Not showing in dashboard
- Not in category breakdown
- Cannot find in analytics

**Causes:**
- Submission failed silently
- Category mismatch
- Date filter excludes it
- Page not reloaded

**Solutions:**

✅ **Solution 1: Check Time Period**
```
Expense added today?
→ Sidebar "Days to Analyze" includes today?
→ If "7 days", includes last 7 days?
→ Increase to 30 days to be sure
```

✅ **Solution 2: Check Category**
```
Added to "Food" category?
→ Go to Analytics → Category Analysis
→ Find Food in the table
→ Is expense there?
→ If yes, check pie chart filter
```

✅ **Solution 3: Clear Cache & Reload**
```
1. Press R to clear cache
2. Dashboard reloads
3. Check if expense appears
4. If not, try refresh (F5)
```

✅ **Solution 4: Check Database**
```bash
# In backend directory
sqlite3 finsight.db
> SELECT COUNT(*) FROM expenses;
# Shows total number of expenses
# If count is low, data might not be saving
```

---

### Display Issues

#### ❌ Problem: "Charts not rendering" or showing as blank

**Symptoms:**
- Chart area is empty
- No pie chart, no bar chart
- Only error message shown

**Causes:**
- No data in selected period
- Browser JavaScript disabled
- Plotly library issue
- API returning empty response

**Solutions:**

✅ **Solution 1: Add More Data**
```
No expenses in selected period?
→ Increase "Days to Analyze" slider
→ Include dates with expenses
→ Charts should appear
```

✅ **Solution 2: Check Browser**
```
1. Open Developer Tools (F12)
2. Check Console tab for errors
3. Refresh page (F5)
4. Try different browser
```

✅ **Solution 3: Reinstall Plotly**
```bash
pip install --upgrade plotly
streamlit run streamlit_app.py
```

✅ **Solution 4: Check API Response**
```bash
# Test API directly
curl http://localhost:8000/api/spending-summary?days=30
# Should return JSON with expense data
# If empty or error, API issue
```

---

## ❓ Frequently Asked Questions

### Installation & Setup

#### Q1: Do I need to install Python?
**A:** Yes, Python 3.8+ is required.
- **macOS:** `brew install python@3.9`
- **Windows:** Download from python.org
- **Linux:** `sudo apt install python3`

Check version: `python --version`

#### Q2: What if pip command doesn't work?
**A:** Use `pip3` instead:
```bash
pip3 install -r streamlit_requirements.txt
streamlit run streamlit_app.py
```

#### Q3: Do I need a database?
**A:** The backend creates one automatically (`finsight.db`).

To reset database:
```bash
cd backend
rm finsight.db
# Restart API server to recreate
```

#### Q4: Can I run dashboard on a different computer?
**A:** Yes, if API is accessible.

Change API URL in sidebar:
```
Old: http://localhost:8000/api
New: http://other-computer-ip:8000/api
```

---

### Features & Usage

#### Q5: Can I upload receipts in languages other than English?
**A:** OCR works best with English. Other languages may have lower confidence scores. You can manually edit results.

#### Q6: What file formats are supported for receipts?
**A:** Only JPG, PNG, GIF, BMP. PDF not supported.

To convert PDF to JPG:
```bash
brew install imagemagick  # macOS
convert receipt.pdf receipt.jpg
```

#### Q7: How many expenses can the system handle?
**A:** Tested with 10,000+ expenses. Performance may slow with 100,000+.

Optimize:
- Use smaller time periods
- Archive old expenses
- Delete test data

#### Q8: Can I edit expenses after adding them?
**A:** Current version doesn't support editing. You can:
- Delete from database (manual)
- Add corrected entry with different date
- Request feature update

---

### Data & Privacy

#### Q9: Where is my data stored?
**A:** Locally in `backend/finsight.db` SQLite database.

Database location:
```
/Users/sindhuram/Downloads/FinSight AI/backend/finsight.db
```

#### Q10: Is my data secure?
**A:** Data is stored locally, not sent anywhere. For production:
- Use HTTPS for API
- Add authentication
- Encrypt database
- Regular backups

#### Q11: How do I backup my data?
**A:** Copy the database file:
```bash
cp backend/finsight.db backend/finsight.db.backup
```

To restore:
```bash
rm backend/finsight.db
cp backend/finsight.db.backup backend/finsight.db
```

#### Q12: Can I export my data?
**A:** Currently not built-in. You can:
```bash
# Export to CSV
sqlite3 backend/finsight.db
> .mode csv
> .output expenses.csv
> SELECT * FROM expenses;
> .quit
```

---

### Customization

#### Q13: How do I change the colors?
**A:** Edit `streamlit_app.py`:

```python
def get_category_color(category: str) -> str:
    colors = {
        "food": "#FF9500",        # Orange
        "transport": "#0066CC",   # Blue
        # Change hex codes to your colors
    }
    return colors.get(category.lower(), "#666666")
```

#### Q14: Can I add custom categories?
**A:** Yes, but requires code changes.

Edit category list:
```python
categories = [
    "Food", "Transport", "Shopping",
    "Utilities", "Entertainment",
    "Health", "Other", "YourCategory"  # Add here
]
```

Add color for new category:
```python
"yourcategory": "#ABCDEF"  # Add here
```

#### Q15: How do I change the dashboard title?
**A:** Edit `streamlit_app.py`:

```python
st.set_page_config(
    page_title="Your New Title",  # Change this
    page_icon="💰"
)
```

---

### Performance & Optimization

#### Q16: Dashboard is slow, how do I speed it up?
**A:** Try these:
1. Use smaller time period (7-30 days)
2. Clear cache (press R)
3. Restart dashboard
4. Reduce number of categories
5. Use faster API server

#### Q17: What are recommended system requirements?
**A:** Minimum:
- Python 3.8+
- 2GB RAM
- Modern browser

Recommended:
- Python 3.9+
- 4GB RAM
- Chrome/Firefox
- SSD storage

#### Q18: Can I run dashboard on mobile?
**A:** Dashboard responsive on mobile but limited features.

Mobile issues:
- Sidebar collapses
- Charts may be cramped
- File upload harder
- Better on desktop/tablet

---

### API & Integration

#### Q19: What if I want to use a different API?
**A:** Edit utility functions in `streamlit_app.py`:

```python
def get_spending_summary(days: int = 30) -> dict:
    url = f"{API_URL}/spending-summary?days={days}"
    # Modify this function for your API
```

#### Q20: Can I run the dashboard without the backend?
**A:** No, API required for all features.

Dashboard needs API for:
- Adding expenses
- Uploading receipts
- Getting metrics
- AI recommendations

---

### Advanced Topics

#### Q21: How do I deploy to production?
**A:** Multiple options:

**Option 1: Streamlit Cloud**
```bash
git push to GitHub
Deploy from share.streamlit.io
Free hosting
```

**Option 2: Docker**
```bash
docker build -t finsight .
docker run -p 8501:8501 finsight
```

**Option 3: Self-hosted**
```bash
Ubuntu server + Nginx + systemd
See STREAMLIT_SETUP_GUIDE.md
```

#### Q22: How do I add authentication?
**A:** Streamlit doesn't have built-in auth. Use:
- **Streamlit Cloud:** Built-in auth
- **Self-hosted:** Add with Nginx + OpenID
- **Simple:** Use API key header

#### Q23: How do I monitor logs?
**A:** View in terminal:
```bash
# Increase log verbosity
streamlit run streamlit_app.py --logger.level=debug

# Check API logs
cd backend
# Logs appear in terminal running API
```

---

### Still Need Help?

#### No solution found?

1. **Check these files:**
   - `STREAMLIT_SETUP_GUIDE.md` - Detailed setup
   - `DASHBOARD_FEATURES.md` - Feature documentation
   - `QUICK_START.md` - Quick reference

2. **Review error messages:**
   - Read full error message
   - Note exact error text
   - Search documentation

3. **Try basic troubleshooting:**
   - Restart dashboard
   - Restart API
   - Clear cache
   - Reload page
   - Use different time period

4. **Check system:**
   - Verify Python version
   - Check port availability
   - Verify dependencies installed
   - Check internet connection

5. **Debug API:**
   - Test API directly: `curl http://localhost:8000/docs`
   - Check API logs
   - Verify database exists
   - Restart API server

---

## 📊 Debug Checklist

Before reporting issue, check:

### Connection
- [ ] API server running on port 8000?
- [ ] Dashboard running on port 8501?
- [ ] Can access http://localhost:8000/docs?
- [ ] Can access http://localhost:8501?

### Dependencies
- [ ] Python 3.8+ installed?
- [ ] All packages from requirements.txt installed?
- [ ] No conflicts with other versions?

### Data
- [ ] Database file exists: backend/finsight.db?
- [ ] Added at least one expense?
- [ ] Expense within selected time period?
- [ ] Correct category selected?

### Performance
- [ ] Sufficient RAM (check with `top`)?
- [ ] CPU usage normal (< 80%)?
- [ ] Disk space available?
- [ ] Network connection stable?

### Browser
- [ ] Using modern browser (Chrome/Firefox)?
- [ ] Cookies/cache cleared?
- [ ] JavaScript enabled?
- [ ] No browser extensions blocking?

---

## 🎯 Quick Solutions

| Problem | Quick Fix |
|---------|-----------|
| Blank dashboard | Clear cache (press R) |
| "Connection refused" | Start API server |
| "Port in use" | Use `--server.port 8502` |
| Slow dashboard | Reduce days to analyze |
| Data not updating | Reload page (F5) |
| Upload failed | Check file format (JPG/PNG) |
| Form won't submit | Check all fields filled |
| Wrong API URL | Update in sidebar settings |

---

## ✅ Summary

Most issues can be resolved by:
1. **Restarting** - Dashboard and/or API
2. **Clearing Cache** - Press R
3. **Reloading** - Press F5
4. **Checking Setup** - Verify all running correctly
5. **Reviewing Logs** - Check error messages

**Still stuck?** Check the detailed troubleshooting section above!

---

**Version:** 1.0.0  
**Status:** ✅ Complete  
**Last Updated:** March 2024

**Happy troubleshooting! 🚀**
