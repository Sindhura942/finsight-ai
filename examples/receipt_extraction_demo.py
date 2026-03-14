"""
Demo script for receipt text extraction using the extract_text_from_image function

This script demonstrates how to use the OCR module to extract text from receipt images.
It shows the complete workflow from image file to extracted text lines.

Usage:
    python examples/receipt_extraction_demo.py path/to/receipt.png

Requirements:
    - Tesseract OCR installed (https://github.com/UB-Mannheim/tesseract/wiki)
    - Python packages: pytesseract, Pillow
    - Install: pip install -r requirements.txt
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr import extract_text_from_image
from src.utils import get_logger

logger = get_logger("ReceiptDemo")


def demo_basic_extraction(image_path: str) -> None:
    """Demonstrate basic text extraction from receipt image
    
    Args:
        image_path: Path to receipt image file
    """
    print("\n" + "=" * 70)
    print("RECEIPT TEXT EXTRACTION - BASIC DEMO")
    print("=" * 70)
    
    try:
        print(f"\n📁 Image Path: {image_path}")
        
        # Extract text lines
        print("\n🔄 Processing image...")
        lines = extract_text_from_image(image_path)
        
        # Display results
        print(f"\n✅ Successfully extracted {len(lines)} lines from receipt\n")
        print("📝 Extracted Text Lines:")
        print("-" * 70)
        
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}. {line}")
        
        print("-" * 70)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"   Please provide a valid image file path")
    except ValueError as e:
        print(f"❌ Processing Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


def demo_with_analysis(image_path: str) -> None:
    """Demonstrate extraction with text analysis
    
    Args:
        image_path: Path to receipt image file
    """
    print("\n" + "=" * 70)
    print("RECEIPT TEXT EXTRACTION - WITH ANALYSIS")
    print("=" * 70)
    
    try:
        # Extract text
        lines = extract_text_from_image(image_path)
        
        print(f"\n📊 Extraction Statistics:")
        print(f"   Total Lines: {len(lines)}")
        print(f"   Total Characters: {sum(len(line) for line in lines)}")
        print(f"   Average Line Length: {sum(len(line) for line in lines) / len(lines):.1f} chars")
        
        # Find potential merchant names (usually longer, uppercase lines)
        print(f"\n🏪 Potential Merchant Names (longer lines):")
        print("-" * 70)
        
        sorted_by_length = sorted(lines, key=len, reverse=True)
        for line in sorted_by_length[:5]:
            if len(line) > 10:
                print(f"   • {line}")
        
        # Find potential amounts (lines with numbers/currency symbols)
        print(f"\n💰 Lines with Numbers (potential amounts):")
        print("-" * 70)
        
        for line in lines:
            if any(char.isdigit() for char in line):
                # Check for currency symbols or decimal points
                if '$' in line or '€' in line or '£' in line or '.' in line:
                    print(f"   • {line}")
        
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_batch_processing(image_paths: list) -> None:
    """Demonstrate batch processing of multiple receipt images
    
    Args:
        image_paths: List of paths to receipt images
    """
    print("\n" + "=" * 70)
    print("BATCH RECEIPT PROCESSING DEMO")
    print("=" * 70)
    
    results = []
    
    for i, image_path in enumerate(image_paths, 1):
        try:
            print(f"\n[{i}/{len(image_paths)}] Processing: {image_path}")
            lines = extract_text_from_image(image_path)
            results.append({
                'path': image_path,
                'success': True,
                'lines': len(lines),
                'text': lines
            })
            print(f"   ✅ Extracted {len(lines)} lines")
        except Exception as e:
            results.append({
                'path': image_path,
                'success': False,
                'error': str(e)
            })
            print(f"   ❌ Failed: {str(e)}")
    
    # Summary
    print("\n" + "-" * 70)
    print("BATCH PROCESSING SUMMARY")
    print("-" * 70)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"Total Files: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed Files:")
        for result in results:
            if not result['success']:
                print(f"  • {result['path']}: {result['error']}")


def main():
    """Main demo function"""
    print("\n" + "=" * 70)
    print("FinSight AI - Receipt Text Extraction Module")
    print("=" * 70)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("\n📚 Usage Examples:")
        print("\n1. Basic Extraction:")
        print("   python examples/receipt_extraction_demo.py path/to/receipt.png")
        print("\n2. With Analysis:")
        print("   python examples/receipt_extraction_demo.py --analyze path/to/receipt.png")
        print("\n3. Batch Processing:")
        print("   python examples/receipt_extraction_demo.py --batch receipt1.png receipt2.png")
        
        print("\n📝 Example Receipt Image:")
        print("   • JPG, PNG, or TIFF format")
        print("   • Recommended resolution: 1000+ pixels width")
        print("   • Best results with clear, well-lit images")
        
        print("\n⚙️ Configuration:")
        print("   • Tesseract path can be set in .env file")
        print("   • Default: Uses system Tesseract installation")
        
        return
    
    # Parse arguments
    if sys.argv[1] == '--analyze':
        if len(sys.argv) < 3:
            print("❌ Error: Image path required")
            return
        demo_with_analysis(sys.argv[2])
    
    elif sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("❌ Error: At least one image path required")
            return
        demo_batch_processing(sys.argv[2:])
    
    else:
        # Basic extraction
        demo_basic_extraction(sys.argv[1])
    
    print("\n" + "=" * 70)
    print("✅ Demo Complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
