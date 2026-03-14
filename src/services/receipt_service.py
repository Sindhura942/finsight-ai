"""Receipt processing service"""

from pathlib import Path

from sqlalchemy.orm import Session

from src.ocr import OCRProcessor
from src.agents import CategorizerAgent
from src.schemas import ExpenseCreate, ReceiptProcessingResult, ReceiptData
from src.utils import get_logger
from src.prompts import get_prompt, format_prompt
from src.agents import LLMAgent

logger = get_logger("ReceiptService")


class ReceiptService:
    """Service for processing receipts"""

    def __init__(self, db: Session):
        """Initialize receipt service
        
        Args:
            db: Database session
        """
        self.db = db
        self.ocr = OCRProcessor()
        self.categorizer = CategorizerAgent()
        self.llm = LLMAgent(temperature=0.1)
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    def process_receipt(self, image_path: str) -> ReceiptProcessingResult:
        """Process a receipt image
        
        Args:
            image_path: Path to receipt image
            
        Returns:
            Receipt processing result
        """
        try:
            logger.info(f"Processing receipt: {image_path}")
            
            # Extract text from image
            text, confidence = self.ocr.extract_from_image(image_path)
            logger.info(f"OCR extraction complete. Confidence: {confidence:.2f}")
            
            # Extract merchant and amount
            prompt_template = get_prompt("extract_receipt")
            if not prompt_template:
                logger.error("Receipt extraction prompt not found")
                return ReceiptProcessingResult(
                    success=False,
                    error="Prompt not found",
                    confidence=0,
                )
            
            prompt = format_prompt(prompt_template, text=text)
            response = self.llm.generate_json(prompt)
            
            merchant_name = response.get("merchant_name", "Unknown")
            amount = float(response.get("amount", 0.0))
            
            logger.info(f"Extracted: {merchant_name} - ${amount}")
            
            # Return result
            receipt_data = ReceiptData(
                merchant_name=merchant_name,
                amount=amount,
                items=[text[:200]],  # Store excerpt of receipt
            )
            
            return ReceiptProcessingResult(
                success=True,
                data=receipt_data,
                confidence=confidence,
            )
        
        except Exception as e:
            logger.error(f"Receipt processing failed: {str(e)}")
            return ReceiptProcessingResult(
                success=False,
                error=str(e),
                confidence=0,
            )

    def create_expense_from_receipt(
        self,
        image_path: str,
        receipt_data: ReceiptData,
        confidence: float,
    ) -> ExpenseCreate:
        """Create expense from receipt data
        
        Args:
            image_path: Path to receipt image
            receipt_data: Extracted receipt data
            confidence: OCR confidence score
            
        Returns:
            Expense create schema
        """
        # Categorize expense
        category = self.categorizer.categorize(receipt_data.merchant_name)
        
        return ExpenseCreate(
            merchant_name=receipt_data.merchant_name,
            amount=receipt_data.amount,
            category=category,
            image_path=image_path,
            confidence_score=confidence,
            description=None,
        )
