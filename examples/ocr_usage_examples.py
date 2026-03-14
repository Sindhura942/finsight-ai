"""
Practical Usage Guide - OCR Text Extraction Module

This guide shows practical examples of using the extract_text_from_image function
in real-world scenarios.
"""

# ==============================================================================
# EXAMPLE 1: Basic Receipt Text Extraction
# ==============================================================================

def example_basic_extraction():
    """Extract text from a receipt image"""
    from src.ocr import extract_text_from_image
    
    # Path to receipt image
    receipt_path = "path/to/receipt.png"
    
    try:
        # Extract text lines
        lines = extract_text_from_image(receipt_path)
        
        # Display results
        print(f"Extracted {len(lines)} lines from receipt:\n")
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}. {line}")
    
    except FileNotFoundError:
        print("❌ Receipt image not found")
    except ValueError as e:
        print(f"❌ OCR processing failed: {e}")


# ==============================================================================
# EXAMPLE 2: Extract Merchant Name and Amount
# ==============================================================================

def example_extract_merchant_and_amount():
    """Extract key information from receipt"""
    import re
    from src.ocr import extract_text_from_image
    
    lines = extract_text_from_image("receipt.png")
    
    # Merchant name (usually first non-empty line or longest line)
    merchant_lines = sorted(lines, key=len, reverse=True)
    merchant = next((l for l in merchant_lines if len(l) > 5), "Unknown")
    print(f"Merchant: {merchant}")
    
    # Find amount (look for $ followed by numbers)
    amount_pattern = r'\$\s*(\d+\.?\d*)'
    for line in lines:
        match = re.search(amount_pattern, line)
        if match:
            amount = float(match.group(1))
            print(f"Amount: ${amount:.2f}")
            break


# ==============================================================================
# EXAMPLE 3: Extract Items and Prices
# ==============================================================================

def example_extract_items():
    """Extract individual items from receipt"""
    import re
    from src.ocr import extract_text_from_image
    
    lines = extract_text_from_image("receipt.png")
    
    items = []
    
    for line in lines:
        # Look for lines with item description and price
        # Pattern: text followed by amount (e.g., "Coffee $4.99")
        match = re.search(r'(.+?)\s+(\$[\d.]+)$', line)
        if match:
            item_name = match.group(1).strip()
            price = match.group(2)
            items.append({
                'name': item_name,
                'price': price
            })
    
    print("Items:")
    for item in items:
        print(f"  • {item['name']}: {item['price']}")


# ==============================================================================
# EXAMPLE 4: Process Multiple Receipts
# ==============================================================================

def example_batch_processing():
    """Process multiple receipt images"""
    from pathlib import Path
    from src.ocr import extract_text_from_image
    
    # Directory containing receipt images
    receipt_dir = Path("receipts/")
    
    results = {}
    
    for receipt_file in receipt_dir.glob("*.png"):
        try:
            lines = extract_text_from_image(str(receipt_file))
            results[receipt_file.name] = {
                'success': True,
                'line_count': len(lines),
                'content': lines
            }
        except Exception as e:
            results[receipt_file.name] = {
                'success': False,
                'error': str(e)
            }
    
    # Display results
    for filename, result in results.items():
        if result['success']:
            print(f"✅ {filename}: {result['line_count']} lines extracted")
        else:
            print(f"❌ {filename}: {result['error']}")


# ==============================================================================
# EXAMPLE 5: Integration with AI Categorization
# ==============================================================================

def example_with_ai_categorization():
    """Extract text and use AI to categorize expense"""
    from src.ocr import extract_text_from_image
    from src.agents import CategorizerAgent, LLMAgent
    
    # Extract text from receipt
    lines = extract_text_from_image("receipt.png")
    receipt_text = "\n".join(lines)
    
    # Use LLM to extract merchant name
    llm = LLMAgent()
    merchant_prompt = f"Extract the store/merchant name from this receipt:\n{receipt_text}"
    merchant = llm.generate(merchant_prompt)
    
    # Categorize the expense
    categorizer = CategorizerAgent()
    category = categorizer.categorize(merchant)
    
    # Extract amount using LLM
    amount_prompt = f"Extract the total amount from this receipt:\n{receipt_text}"
    amount_str = llm.generate(amount_prompt)
    
    print(f"Merchant: {merchant}")
    print(f"Category: {category}")
    print(f"Amount: {amount_str}")


# ==============================================================================
# EXAMPLE 6: Save Extracted Data to JSON
# ==============================================================================

def example_save_to_json():
    """Extract text and save to JSON file"""
    import json
    from datetime import datetime
    from src.ocr import extract_text_from_image
    
    # Extract text
    lines = extract_text_from_image("receipt.png")
    
    # Create structured data
    receipt_data = {
        'timestamp': datetime.now().isoformat(),
        'image_file': 'receipt.png',
        'extracted_lines': lines,
        'total_lines': len(lines),
        'raw_text': '\n'.join(lines)
    }
    
    # Save to JSON
    with open('extracted_receipt.json', 'w') as f:
        json.dump(receipt_data, f, indent=2)
    
    print(f"Saved extraction results to extracted_receipt.json")


# ==============================================================================
# EXAMPLE 7: Custom Preprocessing for Difficult Images
# ==============================================================================

def example_custom_preprocessing():
    """Handle difficult images with custom preprocessing"""
    from PIL import Image, ImageEnhance, ImageFilter
    import pytesseract
    
    # Open image
    image = Image.open("blurry_receipt.png")
    
    # Convert to grayscale for better contrast
    image = image.convert('L')
    
    # Extreme contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(3.0)
    
    # Multiple sharpening passes
    for _ in range(3):
        image = image.filter(ImageFilter.SHARPEN)
    
    # Extract text
    text = pytesseract.image_to_string(image)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    return lines


# ==============================================================================
# EXAMPLE 8: Filter Low-Confidence Results
# ==============================================================================

def example_with_confidence_filtering():
    """Filter results based on OCR confidence"""
    from src.ocr import OCRProcessor
    
    processor = OCRProcessor()
    text, confidence = processor.extract_from_image("receipt.png")
    
    print(f"Confidence: {confidence:.1%}")
    
    if confidence < 0.6:
        print("⚠️  Low confidence - consider manual review")
        print("   Image quality may be poor")
        print("   Try: rescanning, improving lighting, higher resolution")
    elif confidence < 0.8:
        print("⚠️  Medium confidence - some errors possible")
    else:
        print("✅ High confidence - results are reliable")


# ==============================================================================
# EXAMPLE 9: Real-time Receipt Processing (Async)
# ==============================================================================

def example_async_processing():
    """Process receipts asynchronously"""
    import asyncio
    from pathlib import Path
    from src.ocr import extract_text_from_image
    
    async def process_receipt_async(receipt_path):
        """Process a single receipt"""
        return extract_text_from_image(str(receipt_path))
    
    async def process_multiple_receipts():
        """Process multiple receipts concurrently"""
        receipt_dir = Path("receipts/")
        receipt_files = list(receipt_dir.glob("*.png"))
        
        # Process all receipts concurrently
        tasks = [process_receipt_async(f) for f in receipt_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    # Run async processing
    # results = asyncio.run(process_multiple_receipts())


# ==============================================================================
# EXAMPLE 10: Integration with Database Storage
# ==============================================================================

def example_save_to_database():
    """Extract text and save to database"""
    from src.ocr import extract_text_from_image
    from src.database import SessionLocal
    from src.database.models import Expense
    from datetime import datetime
    
    # Extract text
    lines = extract_text_from_image("receipt.png")
    
    # Create expense record
    db = SessionLocal()
    expense = Expense(
        merchant_name=lines[0] if lines else "Unknown",
        amount=0.0,
        category="uncategorized",
        date=datetime.now(),
        description="\n".join(lines[:5])  # First 5 lines as description
    )
    
    # Save to database
    db.add(expense)
    db.commit()
    
    print(f"Saved receipt data to database: {expense.id}")


# ==============================================================================
# EXAMPLE 11: Performance Optimization for Bulk Processing
# ==============================================================================

def example_bulk_processing_optimized():
    """Efficiently process large batches of receipts"""
    from pathlib import Path
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from src.ocr import extract_text_from_image
    
    def process_receipt(receipt_path):
        """Process a single receipt"""
        try:
            lines = extract_text_from_image(str(receipt_path))
            return receipt_path.name, True, len(lines)
        except Exception as e:
            return receipt_path.name, False, str(e)
    
    # Get all receipt files
    receipt_dir = Path("receipts/")
    receipt_files = list(receipt_dir.glob("*.png"))
    
    # Process in parallel (4 threads)
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(process_receipt, f): f 
            for f in receipt_files
        }
        
        for future in as_completed(futures):
            filename, success, result = future.result()
            results.append({
                'filename': filename,
                'success': success,
                'result': result
            })
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"Processed {len(results)} receipts: {successful} successful")


# ==============================================================================
# EXAMPLE 12: Quality Assurance - Validate Extracted Text
# ==============================================================================

def example_validate_extracted_text():
    """Validate quality of extracted text"""
    import re
    from src.ocr import extract_text_from_image
    
    lines = extract_text_from_image("receipt.png")
    
    # Validation checks
    issues = []
    
    # Check 1: Are there lines?
    if not lines:
        issues.append("No text extracted")
    
    # Check 2: Do we have a total/amount?
    has_amount = any('$' in line or '€' in line for line in lines)
    if not has_amount:
        issues.append("No currency symbol found")
    
    # Check 3: Do we have a date?
    date_pattern = r'\d{1,2}/\d{1,2}/\d{2,4}'
    has_date = any(re.search(date_pattern, line) for line in lines)
    if not has_date:
        issues.append("No date found")
    
    # Check 4: Is the text coherent?
    avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
    if avg_line_length < 5:
        issues.append(f"Lines very short (avg: {avg_line_length:.0f} chars)")
    
    # Report validation results
    if not issues:
        print("✅ Extraction quality: GOOD")
    else:
        print("⚠️  Extraction quality: POOR")
        for issue in issues:
            print(f"   • {issue}")


if __name__ == "__main__":
    # Run examples (uncomment to try)
    
    # example_basic_extraction()
    # example_extract_merchant_and_amount()
    # example_extract_items()
    # example_batch_processing()
    # example_with_ai_categorization()
    # example_save_to_json()
    # example_with_confidence_filtering()
    # example_save_to_database()
    # example_bulk_processing_optimized()
    # example_validate_extracted_text()
    
    print("✅ OCR Usage Examples Ready")
    print("\nTo run examples, uncomment them in the if __name__ == '__main__' block")
