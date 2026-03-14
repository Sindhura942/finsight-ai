"""LangGraph workflow for receipt processing"""

from typing import TypedDict, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from src.ocr import OCRProcessor
from src.agents import CategorizerAgent
from src.database import get_db
from src.database.repository import ExpenseRepository
from src.schemas import ExpenseCreate
from src.utils import get_logger

logger = get_logger("langgraph_flow")


class ReceiptProcessingState(TypedDict):
    """State for receipt processing workflow"""
    
    image_path: str
    extracted_text: str
    ocr_confidence: float
    merchant_name: str
    amount: float
    category: str
    expense_data: Optional[ExpenseCreate]
    error: Optional[str]


def extract_text_node(state: ReceiptProcessingState) -> ReceiptProcessingState:
    """Extract text from receipt image
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with extracted text
    """
    try:
        logger.info(f"Extracting text from {state['image_path']}")
        
        ocr = OCRProcessor()
        text, confidence = ocr.extract_from_image(state["image_path"])
        
        state["extracted_text"] = text
        state["ocr_confidence"] = confidence
        
        logger.info(f"Extracted text. Confidence: {confidence:.2f}")
        return state
    
    except Exception as e:
        logger.error(f"Text extraction failed: {str(e)}")
        state["error"] = str(e)
        return state


def parse_details_node(state: ReceiptProcessingState) -> ReceiptProcessingState:
    """Parse merchant and amount from extracted text
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with parsed details
    """
    if state.get("error"):
        return state
    
    try:
        logger.info("Parsing receipt details")
        
        from src.agents import LLMAgent
        from src.prompts import get_prompt, format_prompt
        
        llm = LLMAgent(temperature=0.1)
        
        # Extract merchant and amount
        prompt_template = get_prompt("extract_receipt")
        if not prompt_template:
            raise ValueError("Receipt extraction prompt not found")
        
        prompt = format_prompt(prompt_template, text=state["extracted_text"])
        response = llm.generate_json(prompt)
        
        state["merchant_name"] = response.get("merchant_name", "Unknown")
        state["amount"] = float(response.get("amount", 0.0))
        
        logger.info(f"Parsed: {state['merchant_name']} - ${state['amount']}")
        return state
    
    except Exception as e:
        logger.error(f"Detail parsing failed: {str(e)}")
        state["error"] = str(e)
        return state


def categorize_node(state: ReceiptProcessingState) -> ReceiptProcessingState:
    """Categorize the expense
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with category
    """
    if state.get("error"):
        return state
    
    try:
        logger.info(f"Categorizing {state['merchant_name']}")
        
        categorizer = CategorizerAgent()
        category = categorizer.categorize(state["merchant_name"])
        
        state["category"] = category
        
        logger.info(f"Category: {category}")
        return state
    
    except Exception as e:
        logger.error(f"Categorization failed: {str(e)}")
        state["error"] = str(e)
        return state


def create_expense_node(state: ReceiptProcessingState) -> ReceiptProcessingState:
    """Create expense in database
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with created expense
    """
    if state.get("error"):
        return state
    
    try:
        logger.info("Creating expense in database")
        
        # Create expense data
        expense_data = ExpenseCreate(
            merchant_name=state["merchant_name"],
            amount=state["amount"],
            category=state["category"],
            image_path=state["image_path"],
            confidence_score=state["ocr_confidence"],
            description=None,
            date=datetime.utcnow(),
        )
        
        state["expense_data"] = expense_data
        
        logger.info(f"Expense created: {expense_data.merchant_name}")
        return state
    
    except Exception as e:
        logger.error(f"Expense creation failed: {str(e)}")
        state["error"] = str(e)
        return state


def error_handler_node(state: ReceiptProcessingState) -> ReceiptProcessingState:
    """Handle errors in workflow
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    if state.get("error"):
        logger.error(f"Workflow error: {state['error']}")
    
    return state


def process_receipt_workflow(image_path: str, db: Session) -> ReceiptProcessingState:
    """Execute receipt processing workflow
    
    Args:
        image_path: Path to receipt image
        db: Database session
        
    Returns:
        Final workflow state
    """
    logger.info(f"Starting receipt processing workflow for {image_path}")
    
    # Initialize state
    state: ReceiptProcessingState = {
        "image_path": image_path,
        "extracted_text": "",
        "ocr_confidence": 0.0,
        "merchant_name": "",
        "amount": 0.0,
        "category": "",
        "expense_data": None,
        "error": None,
    }
    
    # Execute workflow nodes
    state = extract_text_node(state)
    
    if not state.get("error"):
        state = parse_details_node(state)
    
    if not state.get("error"):
        state = categorize_node(state)
    
    if not state.get("error"):
        state = create_expense_node(state)
    
    if state.get("error"):
        state = error_handler_node(state)
    
    logger.info("Receipt processing workflow completed")
    
    return state


# For integration with FastAPI, provide convenience function
async def async_process_receipt_workflow(
    image_path: str,
    db: Session = None,
) -> ReceiptProcessingState:
    """Async wrapper for receipt processing
    
    Args:
        image_path: Path to receipt image
        db: Database session (optional, will be created if not provided)
        
    Returns:
        Final workflow state
    """
    if db is None:
        db = next(get_db())
    
    return process_receipt_workflow(image_path, db)
