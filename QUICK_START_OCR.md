"""
Quick Start Guide - extract_text_from_image Function

Get up and running with receipt text extraction in 5 minutes.
"""

# ============================================================================
# 🚀 QUICK START (5 MINUTES)
# ============================================================================

# STEP 1: Ensure you have the requirements installed
# ───────────────────────────────────────────────────
# pip install -r requirements.txt


# STEP 2: Import the function
# ────────────────────────────
from src.ocr import extract_text_from_image


# STEP 3: Extract text from a receipt
# ────────────────────────────────────
lines = extract_text_from_image("path/to/receipt.png")


# STEP 4: Use the extracted text
# ───────────────────────────────
print(f"Extracted {len(lines)} lines:")
for i, line in enumerate(lines, 1):
    print(f"{i}. {line}")


# ============================================================================
# ⚡ MINIMAL EXAMPLE
# ============================================================================

from src.ocr import extract_text_from_image

try:
    lines = extract_text_from_image("receipt.png")
    print(f"Success! Got {len(lines)} lines")
except FileNotFoundError:
    print("File not found")
except ValueError:
    print("OCR processing failed")


# ============================================================================
# 💡 PRACTICAL EXAMPLES
# ============================================================================

# Example 1: Display extracted text
# ──────────────────────────────────
from src.ocr import extract_text_from_image

lines = extract_text_from_image("receipt.png")
text = "\n".join(lines)
print(text)


# Example 2: Find amounts
# ───────────────────────
import re
from src.ocr import extract_text_from_image

lines = extract_text_from_image("receipt.png")
for line in lines:
    if '$' in line or '€' in line:
        print(f"Amount: {line}")


# Example 3: Extract merchant name
# ─────────────────────────────────
from src.ocr import extract_text_from_image

lines = extract_text_from_image("receipt.png")
# Merchant is usually a longer line at the top
merchant = max((l for l in lines if len(l) > 5), default="Unknown", key=len)
print(f"Merchant: {merchant}")


# Example 4: Batch process multiple receipts
# ───────────────────────────────────────────
from pathlib import Path
from src.ocr import extract_text_from_image

for receipt_file in Path("receipts/").glob("*.png"):
    try:
        lines = extract_text_from_image(str(receipt_file))
        print(f"✅ {receipt_file.name}: {len(lines)} lines")
    except Exception as e:
        print(f"❌ {receipt_file.name}: {e}")


# Example 5: With error handling
# ───────────────────────────────
from src.ocr import extract_text_from_image

try:
    lines = extract_text_from_image("receipt.png")
    if not lines:
        print("No text found in image")
    else:
        print(f"Extracted {len(lines)} lines:")
        for line in lines[:10]:  # Show first 10 lines
            print(f"  {line}")
except FileNotFoundError:
    print("Receipt image not found")
except ValueError as e:
    print(f"OCR failed: {e}")
    print("Try: better lighting, higher resolution, straighter angle")
except Exception as e:
    print(f"Unexpected error: {e}")


# ============================================================================
# 🎯 COMMON TASKS
# ============================================================================

# Task: Extract and categorize expense
# ─────────────────────────────────────
from src.ocr import extract_text_from_image
from src.agents import CategorizerAgent

lines = extract_text_from_image("receipt.png")
merchant = lines[0] if lines else "Unknown"

categorizer = CategorizerAgent()
category = categorizer.categorize(merchant)

print(f"Merchant: {merchant}")
print(f"Category: {category}")


# Task: Save extracted text to file
# ──────────────────────────────────
from src.ocr import extract_text_from_image

lines = extract_text_from_image("receipt.png")
with open("extracted_text.txt", "w") as f:
    for line in lines:
        f.write(line + "\n")

print(f"Saved {len(lines)} lines to extracted_text.txt")


# Task: Filter text by pattern
# ─────────────────────────────
import re
from src.ocr import extract_text_from_image

lines = extract_text_from_image("receipt.png")

# Find date-like patterns
dates = [l for l in lines if re.search(r'\d{1,2}/\d{1,2}', l)]
print(f"Potential dates: {dates}")

# Find amounts
amounts = [l for l in lines if re.search(r'\$[\d.]+', l)]
print(f"Amounts found: {len(amounts)}")


# Task: Get confidence score
# ───────────────────────────
from src.ocr import OCRProcessor

processor = OCRProcessor()
text, confidence = processor.extract_from_image("receipt.png")

print(f"Confidence: {confidence:.1%}")
if confidence < 0.7:
    print("⚠️  Low confidence - consider manual review")


# ============================================================================
# 🔧 TROUBLESHOOTING
# ============================================================================

# Problem: FileNotFoundError
# ──────────────────────────
# Solution: Check file path
from pathlib import Path
from src.ocr import extract_text_from_image

receipt_path = "receipt.png"
if not Path(receipt_path).exists():
    print(f"File not found: {receipt_path}")
else:
    lines = extract_text_from_image(receipt_path)


# Problem: OCR returns empty list
# ───────────────────────────────
# Solutions:
# 1. Image is blank
# 2. Image has no text
# 3. Text color matches background
# 4. Resolution is too low

# Fix: Use OCRProcessor to check confidence
from src.ocr import OCRProcessor

processor = OCRProcessor()
text, confidence = processor.extract_from_image("receipt.png")
print(f"Text: {text[:100]}...")
print(f"Confidence: {confidence:.1%}")


# Problem: Poor OCR accuracy
# ──────────────────────────
# Solutions:
# 1. Use higher resolution image (1000+ pixels)
# 2. Ensure good lighting
# 3. Scan straight (not at an angle)
# 4. Use clear, sharp images (not blurry)

# Example: Resize image if too small
from PIL import Image
from src.ocr import extract_text_from_image

image = Image.open("small_receipt.png")
if image.width < 1000:
    ratio = 1000 / image.width
    new_size = (1000, int(image.height * ratio))
    image = image.resize(new_size, Image.Resampling.LANCZOS)
    image.save("receipt_resized.png")

lines = extract_text_from_image("receipt_resized.png")


# ============================================================================
# 📊 INTEGRATION EXAMPLES
# ============================================================================

# Integrate with ReceiptService
# ──────────────────────────────
from src.services import ReceiptService
from src.database import SessionLocal

db = SessionLocal()
service = ReceiptService(db)
result = service.process_receipt("receipt.png")

print(f"Merchant: {result.data.merchant_name}")
print(f"Amount: ${result.data.amount}")
print(f"Confidence: {result.confidence:.1%}")


# Integrate with API endpoint
# ────────────────────────────
# The function is automatically used by:
# POST /api/expenses/upload-receipt/
#
# Just upload a receipt image and the API will:
# 1. Extract text using extract_text_from_image
# 2. Categorize using CategorizerAgent
# 3. Save to database


# ============================================================================
# 📚 MORE INFORMATION
# ============================================================================

# For complete documentation, see:
#
# 📖 docs/OCR_MODULE.md
#    - Full API reference
#    - All parameters and options
#    - Troubleshooting guide
#    - Performance metrics
#
# 🎯 examples/receipt_extraction_demo.py
#    - Interactive demo
#    - Multiple usage modes
#    - Batch processing
#
# 💻 examples/ocr_usage_examples.py
#    - 12 practical examples
#    - Real-world integration
#    - Best practices
#
# ✅ src/ocr/test_processor.py
#    - Test examples
#    - Error scenarios
#    - Edge cases


# ============================================================================
# 🎓 LEARNING PATH
# ============================================================================

# 1. Start here (this file):
#    Get familiar with basic usage

# 2. Try the interactive demo:
#    python examples/receipt_extraction_demo.py receipt.png

# 3. Explore usage examples:
#    python examples/ocr_usage_examples.py

# 4. Read the docs:
#    docs/OCR_MODULE.md

# 5. Look at tests:
#    src/ocr/test_processor.py

# 6. Integrate into your code:
#    from src.ocr import extract_text_from_image
#    lines = extract_text_from_image("image.png")


# ============================================================================
# ❓ FAQ
# ============================================================================

"""
Q: How do I install Tesseract?
A: macOS: brew install tesseract
   Ubuntu: sudo apt-get install tesseract-ocr
   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

Q: What image formats are supported?
A: PNG, JPG, TIFF, BMP (any format Pillow supports)

Q: What's the minimum image resolution?
A: 500x500 pixels, but 1000+ pixels recommended for best accuracy

Q: How accurate is the OCR?
A: 80-95% depending on image quality

Q: Can I process multiple receipts at once?
A: Yes, use a loop or concurrent.futures.ThreadPoolExecutor

Q: How do I improve accuracy?
A: Better lighting, higher resolution, straight angle, sharp focus

Q: Does it work on Tesseract 3 or only 5?
A: Works on both, Tesseract 5+ recommended for better accuracy

Q: Can I use this with other languages?
A: Yes, Tesseract supports 100+ languages
   Configure with: pytesseract configuration parameters
"""


# ============================================================================
# ✅ YOU'RE READY!
# ============================================================================

# Now you can:
# ✅ Extract text from receipt images
# ✅ Process batch receipts
# ✅ Integrate with FinSight AI
# ✅ Build OCR-based applications

# Happy coding! 🚀

if __name__ == "__main__":
    print("✅ Quick Start Guide Ready")
    print("\nNext steps:")
    print("1. Ensure requirements installed: pip install -r requirements.txt")
    print("2. Try the demo: python examples/receipt_extraction_demo.py receipt.png")
    print("3. Read docs: docs/OCR_MODULE.md")
