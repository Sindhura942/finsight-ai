# Categorizer Agent - Quick Start Guide

**⏱️ 5-minute quick start** | Full docs: `docs/CATEGORIZER_AGENT.md`

---

## Installation

```bash
pip install -r requirements.txt
```

---

## 60-Second Example

### Keyword-Based (No Setup Required)

```python
from src.agents import categorize_expenses

expenses = [
    {"merchant": "Starbucks", "amount": 8.20},
    {"merchant": "Uber", "amount": 18.00},
    {"merchant": "Amazon", "amount": 42.00}
]

result = categorize_expenses(expenses, use_llm=False)

for item in result:
    print(f"{item['merchant']:20} ${item['amount']:7.2f}  {item['category']}")

# Output:
# Starbucks                8.20  food
# Uber                    18.00  transport
# Amazon                  42.00  shopping
```

---

## Setup Ollama (Optional)

For LLM-based categorization with reasoning:

```bash
# Install Ollama
brew install ollama  # or visit https://ollama.ai

# Start Ollama
ollama serve

# In another terminal, pull a model
ollama pull mistral
```

---

## Use Ollama

```python
from src.agents import CategorizerAgent

agent = CategorizerAgent(model="mistral")

expenses = [
    {"merchant": "Whole Foods Market", "amount": 75.50}
]

result = agent.categorize_expenses(expenses)

for item in result:
    print(f"Merchant: {item.merchant}")
    print(f"Category: {item.category}")
    print(f"Confidence: {item.confidence:.0%}")
    print(f"Reasoning: {item.reasoning}")

# Output:
# Merchant: Whole Foods Market
# Category: groceries
# Confidence: 98%
# Reasoning: High-end grocery store chain
```

---

## Common Tasks

### Task 1: Quick Categorize

```python
from src.agents import categorize_expenses

expenses = [{"merchant": "Netflix", "amount": 15.99}]
result = categorize_expenses(expenses, use_llm=False)
print(result[0]['category'])  # subscriptions
```

### Task 2: With Confidence

```python
result = categorize_expenses(expenses, use_llm=False)
for item in result:
    print(f"{item['merchant']}: {item['category']} ({item['confidence']:.0%})")
```

### Task 3: Batch Processing

```python
expenses = [
    {"merchant": "Starbucks", "amount": 5.50},
    {"merchant": "Subway", "amount": 12.00},
    {"merchant": "Shell", "amount": 45.00},
]

result = categorize_expenses(expenses)

# Group by category
by_cat = {}
for item in result:
    cat = item['category']
    if cat not in by_cat:
        by_cat[cat] = 0
    by_cat[cat] += item['amount']

for cat in sorted(by_cat.keys()):
    print(f"{cat}: ${by_cat[cat]:.2f}")
```

### Task 4: Custom Categories

```python
from src.agents import CategorizerAgent

agent = CategorizerAgent()
agent.add_category("pet", ["vet", "petco", "petsmart"])

expenses = [{"merchant": "Local Vet", "amount": 200}]
result = agent.categorize_expenses(expenses, use_llm=False)
print(result[0].category)  # pet
```

### Task 5: JSON Export

```python
import json

result = categorize_expenses(expenses, use_llm=False)
json_data = json.dumps(
    [item.to_dict() for item in result],
    indent=2
)
print(json_data)
```

### Task 6: Integration with Parser

```python
from src.ocr import parse_receipt
from src.agents import categorize_expenses

# Extract from receipt
text = "Starbucks $8.20\nUber $18\nAmazon $42"
expenses = parse_receipt(text)

# Categorize
result = categorize_expenses(expenses)
```

---

## Available Categories

```python
from src.agents import CategorizerAgent

agent = CategorizerAgent()
print(agent.get_categories())

# ['entertainment', 'food', 'groceries', 'healthcare', 
#  'other', 'shopping', 'subscriptions', 'transport', 'utilities']
```

---

## Modes

### Mode 1: Keyword-Based (Recommended First)

```python
# No setup required
# Fast: < 1ms per expense
# Deterministic: same input = same output
result = categorize_expenses(expenses, use_llm=False)
```

**Good for:** Quick categorization, offline, batch processing

### Mode 2: LLM-Based (Better Accuracy)

```python
# Requires Ollama running
# Slower: 500ms - 2s per expense
# Intelligent: understands context
result = categorize_expenses(expenses, use_llm=True)
```

**Good for:** Complex merchants, need reasoning, non-English text

### Mode 3: Auto (Recommended)

```python
# Uses LLM if available, falls back to keywords
agent = CategorizerAgent(use_fallback=True)
result = agent.categorize_expenses(expenses)
```

**Good for:** Production systems, reliability

---

## Troubleshooting

### "Ollama server not available"

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Start it
ollama serve
```

Or use keyword mode:
```python
result = categorize_expenses(expenses, use_llm=False)
```

### "Model not found"

```bash
# Pull the model
ollama pull mistral

# List available
ollama list
```

### "Invalid category"

The agent defaults to "other" for unknown merchants:

```python
result = categorize_expenses([
    {"merchant": "XYZ Corp", "amount": 100}
], use_llm=False)

# Falls back to "other" category
print(result[0].category)  # other
```

---

## Next Steps

- 📚 **Full Documentation:** `docs/CATEGORIZER_AGENT.md`
- 💻 **Examples:** `examples/categorizer_agent_examples.py`
- 🧪 **Tests:** `src/agents/test_categorizer_agent.py`
- 🔗 **Integration:** See examples with receipt parser

---

## Key Points

✅ Works offline with keyword fallback  
✅ Optional LLM integration with Ollama  
✅ Fast (< 1ms keywords, < 2s LLM)  
✅ Extensible (add custom categories)  
✅ Reliable (graceful degradation)  
✅ Production-ready (tested, documented)  

---

**Ready to use!** Pick a task above and get started. 🚀
