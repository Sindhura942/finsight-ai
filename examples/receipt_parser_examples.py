"""Practical examples for receipt parser"""

from src.ocr import parse_receipt, ReceiptParser, ExpenseItem


def example_simple_parsing():
    """Example: Simple merchant and amount parsing"""
    print("=" * 60)
    print("Example 1: Simple Parsing")
    print("=" * 60)
    
    text = """
    Starbucks $8.20
    Uber $18
    Amazon $42
    """
    
    # Simple parsing returns just merchant and amount
    items = parse_receipt(text, simple=True)
    
    print("Input text:")
    print(text)
    print("\nParsed items:")
    for item in items:
        print(f"  - {item['merchant']}: ${item['amount']:.2f}")


def example_detailed_parsing():
    """Example: Detailed parsing with full item information"""
    print("\n" + "=" * 60)
    print("Example 2: Detailed Parsing")
    print("=" * 60)
    
    text = "Starbucks $8.20"
    
    # Full parsing includes currency, confidence, etc.
    items = parse_receipt(text, simple=False)
    
    print("Input text:", text)
    print("\nFull parsed item:")
    if items:
        item = items[0]
        print(f"  Merchant: {item['merchant']}")
        print(f"  Amount: ${item['amount']:.2f}")
        print(f"  Currency: {item['currency']}")
        print(f"  Confidence: {item['confidence']:.2%}")
        print(f"  Raw text: {item['raw_text']}")


def example_multi_line_receipt():
    """Example: Parsing multi-line receipt format"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Line Receipt")
    print("=" * 60)
    
    text = """
    Joe's Coffee Shop
    Espresso             $4.50
    Cappuccino           $5.25
    Pastry               $3.75
    Tax                  $0.82
    """
    
    parser = ReceiptParser()
    items = parser.parse_receipt_text(text)
    
    print("Input text:")
    print(text)
    print(f"\nParsed {len(items)} items:")
    for item in items:
        print(f"  - {item.merchant}: ${item.amount:.2f} (confidence: {item.confidence:.0%})")


def example_various_separators():
    """Example: Handling different separator formats"""
    print("\n" + "=" * 60)
    print("Example 4: Various Separator Formats")
    print("=" * 60)
    
    test_cases = [
        ("Dots separator", "Coffee Shop.......................12.50"),
        ("Multiple spaces", "Gas Station            25.99"),
        ("Tab separator", "Restaurant\t$45.50"),
        ("Colon", "Pharmacy: $23.99"),
        ("Dash", "Hotel - $189.00"),
    ]
    
    parser = ReceiptParser()
    
    for name, text in test_cases:
        items = parser.parse_receipt_text(text)
        if items:
            print(f"{name:20} -> {items[0].merchant:20} ${items[0].amount:7.2f}")


def example_currency_handling():
    """Example: Handling different currencies"""
    print("\n" + "=" * 60)
    print("Example 5: Currency Handling")
    print("=" * 60)
    
    test_cases = [
        ("USD", "Store $100.00"),
        ("EUR", "Shop €50.00"),
        ("GBP", "Market £75.50"),
        ("JPY", "Restaurant ¥5000"),
    ]
    
    parser = ReceiptParser()
    
    print(f"{'Currency':10} {'Merchant':20} {'Amount':10} {'Symbol':5}")
    print("-" * 50)
    
    for currency_name, text in test_cases:
        items = parser.parse_receipt_text(text)
        if items:
            item = items[0]
            symbol = text.split()[1][0] if len(text.split()) > 1 else ''
            print(f"{currency_name:10} {item.merchant:20} {item.amount:10.2f} {symbol:5}")


def example_restaurant_receipt():
    """Example: Real-world restaurant receipt"""
    print("\n" + "=" * 60)
    print("Example 6: Restaurant Receipt")
    print("=" * 60)
    
    text = """
    MARIO'S ITALIAN RESTAURANT
    123 Main Street
    
    Spaghetti Carbonara      $18.95
    Caesar Salad              $9.50
    Breadsticks               $4.00
    House Wine (glass)        $8.00
    
    Subtotal                 $40.45
    Tax (8.5%)                $3.44
    Tip (18%)                 $7.28
    
    TOTAL                    $51.17
    
    Thank you for your visit!
    """
    
    parser = ReceiptParser()
    items = parser.parse_receipt_text(text)
    
    print("Input text (abbreviated):")
    print(text[:200] + "...\n")
    
    print(f"Parsed {len(items)} line items:")
    total = 0
    for item in items:
        if item.amount > 0:  # Only positive amounts
            print(f"  {item.merchant:30} ${item.amount:7.2f}")
            total += item.amount
    
    print(f"  {'Total':30} ${total:7.2f}")


def example_amazon_style():
    """Example: E-commerce order format"""
    print("\n" + "=" * 60)
    print("Example 7: E-Commerce (Amazon Style)")
    print("=" * 60)
    
    text = """
    Amazon.com Order
    
    Wireless Keyboard                   $24.99
    USB-C Cable (2-pack)                $12.99
    Phone Case - Blue                   $15.50
    
    Subtotal                            $53.48
    Shipping                            FREE
    Tax                                 $4.27
    
    TOTAL                               $57.75
    """
    
    parser = ReceiptParser()
    items = parser.parse_simple(text)
    
    print("Input text:")
    print(text)
    print("\nParsed items (simple format):")
    for item in items:
        print(f"  {item['merchant']:40} ${item['amount']:7.2f}")


def example_bulk_processing():
    """Example: Processing multiple receipts"""
    print("\n" + "=" * 60)
    print("Example 8: Bulk Receipt Processing")
    print("=" * 60)
    
    receipts = [
        ("Starbucks", "Starbucks $8.20"),
        ("Uber", "Uber $18.50"),
        ("Grocery", "Whole Foods $45.67"),
        ("Restaurant", "Joe's Pizza $32.99"),
        ("Gas", "Shell Gas Station $52.00"),
    ]
    
    parser = ReceiptParser()
    
    print(f"{'Merchant':20} {'Amount':10} {'Category':15} {'Confidence':12}")
    print("-" * 60)
    
    total = 0
    for category, text in receipts:
        items = parser.parse_receipt_text(text)
        if items:
            item = items[0]
            confidence = f"{item.confidence:.0%}"
            print(f"{item.merchant:20} ${item.amount:9.2f} {category:15} {confidence:>11}")
            total += item.amount
    
    print("-" * 60)
    print(f"{'TOTAL':20} ${total:9.2f}")


def example_error_handling():
    """Example: Error handling and edge cases"""
    print("\n" + "=" * 60)
    print("Example 9: Error Handling & Edge Cases")
    print("=" * 60)
    
    test_cases = [
        ("Empty string", ""),
        ("No amounts", "Starbucks\nCoffee Shop"),
        ("Just amount", "$25.99"),
        ("Normal", "Store $25.99"),
        ("Whitespace", "   \n\n   "),
    ]
    
    parser = ReceiptParser()
    
    print(f"{'Test Case':20} {'Input':30} {'Parsed Items':15}")
    print("-" * 70)
    
    for name, text in test_cases:
        items = parser.parse_receipt_text(text)
        input_repr = repr(text[:25])
        item_count = f"{len(items)} items"
        print(f"{name:20} {input_repr:30} {item_count:15}")


def example_confidence_filtering():
    """Example: Filtering by confidence score"""
    print("\n" + "=" * 60)
    print("Example 10: Confidence-Based Filtering")
    print("=" * 60)
    
    text = """
    Starbucks $8.20
    S $5
    Well-Known Store $25.99
    X $10
    """
    
    parser = ReceiptParser()
    items = parser.parse_receipt_text(text)
    
    print("All parsed items:")
    for item in items:
        print(f"  {item.merchant:25} ${item.amount:7.2f} (confidence: {item.confidence:.0%})")
    
    # Filter by confidence
    high_confidence = [item for item in items if item.confidence >= 0.6]
    
    print(f"\nHigh confidence items (>= 60%):")
    for item in high_confidence:
        print(f"  {item.merchant:25} ${item.amount:7.2f}")


def example_merchant_cleanup():
    """Example: Merchant name cleanup"""
    print("\n" + "=" * 60)
    print("Example 11: Merchant Name Cleanup")
    print("=" * 60)
    
    test_cases = [
        "starbucks coffee shop",
        "whole   foods   market",
        "McDonald's #1234",
        "AMAZON.COM PURCHASE",
        "  restaurant  (branch 5)  ",
    ]
    
    parser = ReceiptParser()
    
    print(f"{'Raw Name':40} {'Cleaned':40}")
    print("-" * 85)
    
    for raw_name in test_cases:
        cleaned = parser._clean_merchant_name(raw_name)
        print(f"{raw_name:40} {cleaned:40}")


def example_custom_parser_config():
    """Example: Custom parser configuration"""
    print("\n" + "=" * 60)
    print("Example 12: Custom Parser Configuration")
    print("=" * 60)
    
    # Standard parser
    parser_standard = ReceiptParser(strict_mode=False)
    
    # Strict parser
    parser_strict = ReceiptParser(strict_mode=True)
    
    text = "S $5"  # Very short merchant name
    
    items_standard = parser_standard.parse_receipt_text(text)
    items_strict = parser_strict.parse_receipt_text(text)
    
    print(f"Input text: '{text}'")
    print(f"Standard mode items: {len(items_standard)}")
    print(f"Strict mode items: {len(items_strict)}")
    
    if items_standard:
        print(f"\nStandard parsing confidence: {items_standard[0].confidence:.0%}")


# Run all examples
if __name__ == "__main__":
    example_simple_parsing()
    example_detailed_parsing()
    example_multi_line_receipt()
    example_various_separators()
    example_currency_handling()
    example_restaurant_receipt()
    example_amazon_style()
    example_bulk_processing()
    example_error_handling()
    example_confidence_filtering()
    example_merchant_cleanup()
    example_custom_parser_config()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
