"""OCR service for extracting text from images"""

import io
from pathlib import Path
from typing import Optional, Tuple

import pytesseract
from PIL import Image

from app.core.constants import OCR_CONFIDENCE_THRESHOLD
from app.core.logger import app_logger


class OCRService:
    """Service for optical character recognition"""

    def __init__(self, tesseract_path: Optional[str] = None):
        """Initialize OCR service
        
        Args:
            tesseract_path: Path to tesseract executable (optional)
        """
        if tesseract_path:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
        self.logger = app_logger

    def extract_text_from_image(self, image_path: str) -> Tuple[str, float]:
        """Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            self.logger.info(f"Extracting text from image: {image_path}")
            
            # Open and preprocess image
            image = Image.open(image_path)
            image = self._preprocess_image(image)
            
            # Extract text with confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            text = pytesseract.image_to_string(image)
            
            # Calculate average confidence
            confidence = self._calculate_confidence(data)
            
            self.logger.info(f"Successfully extracted text. Confidence: {confidence:.2f}")
            
            return text.strip(), confidence
        
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {str(e)}")
            raise

    def extract_from_bytes(self, image_bytes: bytes) -> Tuple[str, float]:
        """Extract text from image bytes
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            self.logger.info("Extracting text from image bytes")
            
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            image = self._preprocess_image(image)
            
            # Extract text
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            text = pytesseract.image_to_string(image)
            confidence = self._calculate_confidence(data)
            
            self.logger.info(f"Successfully extracted text from bytes. Confidence: {confidence:.2f}")
            
            return text.strip(), confidence
        
        except Exception as e:
            self.logger.error(f"OCR extraction from bytes failed: {str(e)}")
            raise

    @staticmethod
    def _preprocess_image(image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too small
        if image.width < 100 or image.height < 100:
            factor = max(100 / image.width, 100 / image.height)
            new_size = (int(image.width * factor), int(image.height * factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image

    @staticmethod
    def _calculate_confidence(data: dict) -> float:
        """Calculate average confidence from OCR data
        
        Args:
            data: Tesseract output data
            
        Returns:
            Average confidence score (0-1)
        """
        confidences = []
        for conf in data.get('conf', []):
            if conf != -1:  # -1 means no text detected
                confidences.append(conf / 100.0)
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)
