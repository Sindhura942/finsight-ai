# Complete FinSight AI Pipeline Integration Guide

**A comprehensive guide to using all 4 modules together**

---

## 🎯 Overview

This guide shows how to integrate all four FinSight AI modules into a complete end-to-end pipeline:

```
Receipt Image (JPG/PNG)
    ↓
[Module 1] OCR Extraction → Raw Text
    ↓
[Module 2] Receipt Parsing → Structured Items
    ↓
[Module 3] Expense Categorization → Categorized Expenses
    ↓
[Module 4] Financial Analysis → Insights & Recommendations
```

---

## 📚 Module Reference

| Module | Purpose | Input | Output |
|--------|---------|-------|--------|
| **OCR Extractor** | Extract text from images | Image file path | Raw text |
| **Receipt Parser** | Parse text to items | Raw text | List of ExpenseItem |
| **Categorizer** | Assign categories | List of items | List of categorized expenses |
| **Analyzer** | Generate insights | List of expenses | FinancialAnalysis |

---

## 🚀 Quick Integration (5 Minutes)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Pipeline

```python
from src.ocr.processor import OCRExtractor
from src.ocr.receipt_parser import ReceiptParser
from src.agents import ExpenseCategorizer, FinancialAnalyzer
import json

# Initialize modules
ocr = OCRExtractor()
parser = ReceiptParser()
categorizer = ExpenseCategorizer(use_llm=False)
analyzer = FinancialAnalyzer(use_llm=False)

# Process receipt
image_path = "receipt.jpg"

# Step 1: Extract text
text = ocr.extract(image_path)
print(f"Extracted text: {text[:100]}...")

# Step 2: Parse items
items = parser.parse(text)
print(f"Found {len(items)} items")

# Step 3: Categorize expenses
expenses = categorizer.categorize(items)
print(f"Categorized {len(expenses)} expenses")

# Step 4: Analyze spending
analysis = analyzer.analyze(expenses)
print(analysis.summary)

# Export results
results = {
    "raw_text": text,
    "items": [item.__dict__ for item in items],
    "expenses": [exp.to_dict() for exp in expenses],
    "analysis": analysis.to_dict()
}

with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## 🔧 Advanced Integration

### With LLM Enhancement

```python
# Use LLM for better accuracy
parser = ReceiptParser(use_llm=True)
categorizer = ExpenseCategorizer(use_llm=True)
analyzer = FinancialAnalyzer(use_llm=True)

# Process with AI enhancement
text = ocr.extract("receipt.jpg")
items = parser.parse(text)  # Better parsing with LLM
expenses = categorizer.categorize(items)  # Better categorization
analysis = analyzer.analyze(expenses)  # Better recommendations

print("High-quality analysis with LLM enhancement!")
```

### With Budget Checking

```python
# Define budget limits
budgets = {
    "food": 300,
    "transport": 150,
    "shopping": 200,
    "entertainment": 100
}

# Analyze with budget compliance
analysis = analyzer.analyze(expenses, budget_limits=budgets)

# Check for over-budget categories
print("Budget Analysis:")
for cat in analysis.category_breakdown:
    budget = budgets.get(cat.category)
    if budget:
        if cat.amount > budget:
            over = cat.amount - budget
            print(f"⚠️  {cat.category}: ${over:.2f} over budget")
        else:
            under = budget - cat.amount
            print(f"✅ {cat.category}: ${under:.2f} under budget")

# Get recommendations
print("\nTop Recommendations:")
for rec in sorted(analysis.recommendations, 
                  key=lambda x: x.potential_savings, 
                  reverse=True)[:3]:
    print(f"  • {rec.title}")
    print(f"    Save: ${rec.potential_savings:.2f}/month")
```

### Batch Processing Multiple Receipts

```python
import os
from pathlib import Path

# Process all receipts in a folder
receipt_folder = "receipts/"
all_analyses = []
failed_receipts = []

for receipt_file in os.listdir(receipt_folder):
    if receipt_file.endswith((".jpg", ".png")):
        try:
            receipt_path = os.path.join(receipt_folder, receipt_file)
            
            # Process pipeline
            text = ocr.extract(receipt_path)
            items = parser.parse(text)
            expenses = categorizer.categorize(items)
            analysis = analyzer.analyze(expenses)
            
            all_analyses.append({
                "file": receipt_file,
                "analysis": analysis
            })
            
            print(f"✅ Processed {receipt_file}")
            
        except Exception as e:
            failed_receipts.append((receipt_file, str(e)))
            print(f"❌ Failed to process {receipt_file}: {e}")

# Aggregate results
total_spending = sum(a["analysis"].total_spending for a in all_analyses)
print(f"\nTotal Spending: ${total_spending:.2f}")
print(f"Receipts Processed: {len(all_analyses)}")
print(f"Failed: {len(failed_receipts)}")
```

---

## 📊 Use Cases

### Use Case 1: Personal Expense Tracking

```python
from datetime import datetime
from src.ocr.processor import OCRExtractor
from src.ocr.receipt_parser import ReceiptParser
from src.agents import ExpenseCategorizer, FinancialAnalyzer

def track_weekly_expenses():
    """Track and analyze weekly expenses from receipts."""
    
    ocr = OCRExtractor()
    parser = ReceiptParser(use_llm=False)
    categorizer = ExpenseCategorizer(use_llm=False)
    analyzer = FinancialAnalyzer(use_llm=False)
    
    # Process receipts from the week
    weekly_expenses = []
    for i in range(1, 8):
        receipt_file = f"receipts/day{i}.jpg"
        
        text = ocr.extract(receipt_file)
        items = parser.parse(text)
        expenses = categorizer.categorize(items)
        weekly_expenses.extend(expenses)
    
    # Analyze the week
    analysis = analyzer.analyze(weekly_expenses)
    
    # Generate report
    print(f"Weekly Expense Report")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Total: ${analysis.total_spending:.2f}")
    print()
    print("Category Breakdown:")
    for cat in analysis.category_breakdown:
        print(f"  {cat.category}: ${cat.amount:.2f} ({cat.percentage:.1f}%)")
    print()
    print("Cost-Saving Recommendations:")
    for rec in analysis.recommendations[:3]:
        print(f"  • {rec.title}")
        print(f"    {rec.description}")
```

### Use Case 2: Business Expense Management

```python
def process_business_receipts(employee_id, month):
    """Process business receipts for expense reimbursement."""
    
    ocr = OCRExtractor()
    parser = ReceiptParser(use_llm=True)
    categorizer = ExpenseCategorizer(use_llm=True)
    analyzer = FinancialAnalyzer(use_llm=False)
    
    # Process all receipts for the employee/month
    expenses = []
    for receipt_file in get_employee_receipts(employee_id, month):
        text = ocr.extract(receipt_file)
        items = parser.parse(text)
        categorized = categorizer.categorize(items)
        expenses.extend(categorized)
    
    # Analyze for compliance
    analysis = analyzer.analyze(expenses)
    
    # Check for unusual spending
    for cat in analysis.category_breakdown:
        if cat.amount > 500:  # High threshold
            print(f"⚠️  High spending detected: {cat.category}")
    
    # Generate reimbursement report
    return {
        "employee_id": employee_id,
        "month": month,
        "total_expenses": analysis.total_spending,
        "categories": {
            cat.category: cat.amount 
            for cat in analysis.category_breakdown
        }
    }
```

### Use Case 3: Financial Planning

```python
def analyze_spending_trends():
    """Analyze spending trends across multiple months."""
    
    ocr = OCRExtractor()
    parser = ReceiptParser(use_llm=False)
    categorizer = ExpenseCategorizer(use_llm=False)
    analyzer = FinancialAnalyzer(use_llm=False)
    
    # Budget limits for the year
    budgets = {
        "food": 300,
        "transport": 150,
        "shopping": 200,
        "entertainment": 100,
        "subscriptions": 50
    }
    
    monthly_analyses = {}
    
    # Process each month
    for month in range(1, 13):
        month_expenses = []
        
        for day in range(1, 31):
            receipt_file = f"receipts/{month:02d}/{day:02d}.jpg"
            if os.path.exists(receipt_file):
                try:
                    text = ocr.extract(receipt_file)
                    items = parser.parse(text)
                    expenses = categorizer.categorize(items)
                    month_expenses.extend(expenses)
                except:
                    pass
        
        # Analyze month
        if month_expenses:
            analysis = analyzer.analyze(month_expenses, budget_limits=budgets)
            monthly_analyses[month] = analysis
    
    # Generate trends report
    print("Annual Spending Trends:")
    print()
    
    for month, analysis in monthly_analyses.items():
        print(f"Month {month}: ${analysis.total_spending:.2f}")
        
        # Show highest spending category
        if analysis.highest_spending_category:
            print(f"  Top: {analysis.highest_spending_category.title()}")
    
    # Calculate average monthly spending
    avg_spending = sum(a.total_spending for a in monthly_analyses.values()) / len(monthly_analyses)
    print(f"\nAverage Monthly: ${avg_spending:.2f}")
    
    # Show recommendations
    print("\nKey Recommendations:")
    all_recs = []
    for analysis in monthly_analyses.values():
        all_recs.extend(analysis.recommendations)
    
    # Get most common high-priority recommendations
    for rec in sorted(all_recs, key=lambda x: x.potential_savings, reverse=True)[:5]:
        print(f"  • {rec.title}: Save ${rec.potential_savings:.2f}/month")
```

---

## 🔌 API Server Integration

### Flask Example

```python
from flask import Flask, request, jsonify
from src.ocr.processor import OCRExtractor
from src.ocr.receipt_parser import ReceiptParser
from src.agents import ExpenseCategorizer, FinancialAnalyzer
import os

app = Flask(__name__)

# Initialize modules
ocr = OCRExtractor()
parser = ReceiptParser(use_llm=False)
categorizer = ExpenseCategorizer(use_llm=False)
analyzer = FinancialAnalyzer(use_llm=False)

@app.route("/analyze-receipt", methods=["POST"])
def analyze_receipt():
    """Upload a receipt and get analysis."""
    
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    
    try:
        # Save temp file
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)
        
        # Process pipeline
        text = ocr.extract(temp_path)
        items = parser.parse(text)
        expenses = categorizer.categorize(items)
        analysis = analyzer.analyze(expenses)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify(analysis.to_dict())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze-expenses", methods=["POST"])
def analyze_expenses():
    """Analyze pre-categorized expenses."""
    
    expenses = request.json.get("expenses", [])
    budget_limits = request.json.get("budget_limits")
    
    try:
        analysis = analyzer.analyze(expenses, budget_limits=budget_limits)
        return jsonify(analysis.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

### Usage with curl

```bash
# Analyze a receipt image
curl -X POST -F "file=@receipt.jpg" http://localhost:5000/analyze-receipt

# Analyze expenses
curl -X POST http://localhost:5000/analyze-expenses \
  -H "Content-Type: application/json" \
  -d '{
    "expenses": [
      {"merchant": "Starbucks", "amount": 8.20, "category": "food"},
      {"merchant": "Uber", "amount": 18.00, "category": "transport"}
    ],
    "budget_limits": {"food": 300, "transport": 150}
  }'
```

---

## 💾 Database Integration

### SQLite Example

```python
import sqlite3
import json
from datetime import datetime
from src.ocr.processor import OCRExtractor
from src.ocr.receipt_parser import ReceiptParser
from src.agents import ExpenseCategorizer, FinancialAnalyzer

class ExpenseDatabase:
    def __init__(self, db_path="expenses.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Receipts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY,
                filename TEXT,
                raw_text TEXT,
                processed_date TIMESTAMP
            )
        """)
        
        # Expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                receipt_id INTEGER,
                merchant TEXT,
                amount REAL,
                category TEXT,
                processed_date TIMESTAMP,
                FOREIGN KEY (receipt_id) REFERENCES receipts(id)
            )
        """)
        
        # Analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY,
                analysis_data TEXT,
                analysis_date TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def process_and_store_receipt(self, image_path):
        """Process receipt and store in database."""
        
        ocr = OCRExtractor()
        parser = ReceiptParser(use_llm=False)
        categorizer = ExpenseCategorizer(use_llm=False)
        analyzer = FinancialAnalyzer(use_llm=False)
        
        # Process
        text = ocr.extract(image_path)
        items = parser.parse(text)
        expenses = categorizer.categorize(items)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store receipt
        cursor.execute(
            "INSERT INTO receipts (filename, raw_text, processed_date) VALUES (?, ?, ?)",
            (image_path, text, datetime.now())
        )
        receipt_id = cursor.lastrowid
        
        # Store expenses
        for exp in expenses:
            cursor.execute(
                """INSERT INTO expenses 
                   (receipt_id, merchant, amount, category, processed_date) 
                   VALUES (?, ?, ?, ?, ?)""",
                (receipt_id, exp.merchant, exp.amount, exp.category, datetime.now())
            )
        
        conn.commit()
        
        # Analyze and store analysis
        analysis = analyzer.analyze(expenses)
        cursor.execute(
            "INSERT INTO analyses (analysis_data, analysis_date) VALUES (?, ?)",
            (json.dumps(analysis.to_dict()), datetime.now())
        )
        
        conn.commit()
        conn.close()
        
        return analysis
    
    def get_monthly_analysis(self, month, year):
        """Get aggregated analysis for a month."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(amount) as total, category
            FROM expenses
            WHERE strftime('%m', processed_date) = ? AND strftime('%Y', processed_date) = ?
            GROUP BY category
        """, (f"{month:02d}", f"{year}"))
        
        results = cursor.fetchall()
        conn.close()
        
        return {row[1]: row[0] for row in results}
```

---

## 🔄 Error Handling & Recovery

### Robust Pipeline with Error Recovery

```python
from src.ocr.processor import OCRExtractor
from src.ocr.receipt_parser import ReceiptParser
from src.agents import ExpenseCategorizer, FinancialAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustPipeline:
    def __init__(self):
        self.ocr = OCRExtractor()
        self.parser = ReceiptParser(use_llm=False)
        self.categorizer = ExpenseCategorizer(use_llm=False)
        self.analyzer = FinancialAnalyzer(use_llm=False)
    
    def process_receipt(self, image_path, max_retries=3):
        """Process receipt with error recovery."""
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Step 1: OCR
                logger.info(f"Extracting text from {image_path}")
                text = self.ocr.extract(image_path)
                
                if not text.strip():
                    logger.warning("No text extracted, may be blank receipt")
                    return None
                
                # Step 2: Parse
                logger.info("Parsing receipt text")
                items = self.parser.parse(text)
                
                if not items:
                    logger.warning("No items found in receipt")
                    return None
                
                # Step 3: Categorize
                logger.info(f"Categorizing {len(items)} items")
                expenses = self.categorizer.categorize(items)
                
                # Step 4: Analyze
                logger.info("Analyzing expenses")
                analysis = self.analyzer.analyze(expenses)
                
                logger.info("✅ Receipt processed successfully")
                return analysis
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Error processing receipt: {e}")
                
                if retry_count < max_retries:
                    logger.info(f"Retrying ({retry_count}/{max_retries})...")
                    continue
                else:
                    logger.error(f"Failed after {max_retries} retries")
                    return None
        
        return None
    
    def process_batch(self, image_paths):
        """Process multiple receipts with progress tracking."""
        
        results = {
            "successful": [],
            "failed": [],
            "summary": None
        }
        
        all_expenses = []
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"Processing {i+1}/{len(image_paths)}: {image_path}")
            
            analysis = self.process_receipt(image_path)
            
            if analysis:
                results["successful"].append({
                    "path": image_path,
                    "analysis": analysis
                })
                # Collect expenses for overall analysis
                # (We'd need the original expenses here)
            else:
                results["failed"].append(image_path)
        
        logger.info(f"Batch complete: {len(results['successful'])} successful, {len(results['failed'])} failed")
        
        return results
```

---

## 📊 Configuration

### Environment-Based Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OCR settings
    OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() == "true"
    
    # LLM settings
    USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Budget limits
    BUDGET_LIMITS = {
        "food": float(os.getenv("BUDGET_FOOD", "300")),
        "transport": float(os.getenv("BUDGET_TRANSPORT", "150")),
        "shopping": float(os.getenv("BUDGET_SHOPPING", "200")),
        "entertainment": float(os.getenv("BUDGET_ENTERTAINMENT", "100")),
        "subscriptions": float(os.getenv("BUDGET_SUBSCRIPTIONS", "50"))
    }
    
    # Paths
    RECEIPTS_FOLDER = os.getenv("RECEIPTS_FOLDER", "./receipts/")
    OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "./output/")

# Usage
from src.ocr.processor import OCRExtractor
from src.agents import FinancialAnalyzer

config = Config()

analyzer = FinancialAnalyzer(
    use_llm=config.USE_LLM,
    ollama_host=config.OLLAMA_HOST,
    model=config.OLLAMA_MODEL
)

analysis = analyzer.analyze(expenses, budget_limits=config.BUDGET_LIMITS)
```

### .env Example

```
OCR_ENABLED=true
USE_LLM=false
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
BUDGET_FOOD=300
BUDGET_TRANSPORT=150
BUDGET_SHOPPING=200
BUDGET_ENTERTAINMENT=100
BUDGET_SUBSCRIPTIONS=50
RECEIPTS_FOLDER=./receipts/
OUTPUT_FOLDER=./output/
```

---

## 🧪 Testing the Pipeline

### Integration Test

```python
def test_complete_pipeline():
    """Test complete pipeline with sample receipt."""
    
    from src.ocr.processor import OCRExtractor
    from src.ocr.receipt_parser import ReceiptParser
    from src.agents import ExpenseCategorizer, FinancialAnalyzer
    
    # Initialize
    ocr = OCRExtractor()
    parser = ReceiptParser(use_llm=False)
    categorizer = ExpenseCategorizer(use_llm=False)
    analyzer = FinancialAnalyzer(use_llm=False)
    
    # Use a test receipt
    image_path = "tests/fixtures/sample_receipt.jpg"
    
    # Step 1: Extract
    text = ocr.extract(image_path)
    assert text, "OCR should extract text"
    assert len(text) > 0, "Extracted text should not be empty"
    
    # Step 2: Parse
    items = parser.parse(text)
    assert items, "Parser should find items"
    assert len(items) > 0, "Should find at least one item"
    
    # Step 3: Categorize
    expenses = categorizer.categorize(items)
    assert expenses, "Categorizer should return expenses"
    assert len(expenses) > 0, "Should categorize at least one expense"
    assert all(hasattr(e, 'category') for e in expenses), "All expenses should have categories"
    
    # Step 4: Analyze
    analysis = analyzer.analyze(expenses)
    assert analysis, "Analyzer should return analysis"
    assert analysis.total_spending > 0, "Total spending should be calculated"
    assert analysis.category_breakdown, "Should have category breakdown"
    assert analysis.highest_spending_category, "Should identify highest spending"
    
    print("✅ Complete pipeline test passed!")
    return analysis
```

---

## 📚 Related Documentation

- **Quick Starts:** See individual `QUICK_START_*.md` files
- **API References:** See `docs/` directory
- **Implementation Details:** See `*_SUMMARY.md` files
- **Examples:** See `examples/` directory

---

**Ready to build with FinSight AI!** 🚀
