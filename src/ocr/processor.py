"""OCR processing using Tesseract"""

import io
from pathlib import Path
from typing import Tuple, List

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

from src.config import get_settings
from src.utils import get_logger

logger = get_logger("OCR")


class OCRProcessor:
    """Optical Character Recognition processor"""

    def __init__(self, tesseract_path: str = None):
        """Initialize OCR processor
        
        Args:
            tesseract_path: Path to tesseract executable
        """
        self.settings = get_settings()
        
        if tesseract_path or self.settings.tesseract_path:
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path or self.settings.tesseract_path

    def extract_from_image(self, image_path: str) -> Tuple[str, float]:
        """Extract text from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (text, confidence)
        """
        try:
            logger.info(f"Extracting text from: {image_path}")
            
            # Open image
            image = Image.open(image_path)
            image = self._preprocess(image)
            
            # Extract text
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            text = pytesseract.image_to_string(image)
            
            # Calculate confidence
            confidence = self._calculate_confidence(data)
            
            logger.info(f"Extraction complete. Confidence: {confidence:.2f}")
            
            return text.strip(), confidence
        
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise

    def extract_from_bytes(self, image_bytes: bytes) -> Tuple[str, float]:
        """Extract text from image bytes
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            Tuple of (text, confidence)
        """
        try:
            logger.info("Extracting text from image bytes")
            
            image = Image.open(io.BytesIO(image_bytes))
            image = self._preprocess(image)
            
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            text = pytesseract.image_to_string(image)
            confidence = self._calculate_confidence(data)
            
            logger.info(f"Extraction complete. Confidence: {confidence:.2f}")
            
            return text.strip(), confidence
        
        except Exception as e:
            logger.error(f"OCR extraction from bytes failed: {str(e)}")
            raise

    @staticmethod
    def _preprocess(image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image
        """
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too small
        if image.width < 100 or image.height < 100:
            factor = max(100 / image.width, 100 / image.height)
            new_size = (int(image.width * factor), int(image.height * factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Scale up for better OCR accuracy
        if image.width < 1000:
            scale_factor = 1000 / image.width
            new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)
        
        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)
        
        return image

    @staticmethod
    def _calculate_confidence(data: dict) -> float:
        """Calculate confidence from OCR data
        
        Args:
            data: Tesseract output data
            
        Returns:
            Confidence score (0-1)
        """
        confidences = []
        for conf in data.get('conf', []):
            if conf != -1:  # -1 means no text
                confidences.append(conf / 100.0)
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)


def extract_text_from_image(image_path: str) -> List[str]:
    """Extract text lines from receipt image using pytesseract
    
    Preprocesses the image for better OCR accuracy, extracts text line by line,
    and removes empty lines. Handles errors gracefully.
    
    Args:
        image_path: Path to receipt image file
        
    Returns:
        List of non-empty text lines extracted from the image
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be processed
        
    Example:
        >>> lines = extract_text_from_image("receipt.png")
        >>> for line in lines:
        ...     print(line)
    """
    try:
        logger.info(f"Extracting text lines from: {image_path}")
        
        # Validate file exists
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Open and preprocess image
        try:
            image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Cannot open image file: {str(e)}")
        
        image = OCRProcessor._preprocess(image)
        
        # Extract text with line information
        try:
            # Get detailed data including position and confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {str(e)}")
            raise ValueError(f"OCR processing failed: {str(e)}")
        
        # Extract lines by grouping text by block
        lines = []
        current_block = -1
        current_line_text = []
        
        for i, word in enumerate(data['text']):
            # Skip empty words
            if not word.strip():
                continue
            
            block_num = data['block_num'][i]
            
            # New block or line detected
            if block_num != current_block:
                # Save previous line if exists
                if current_line_text:
                    line = ' '.join(current_line_text).strip()
                    if line:  # Only add non-empty lines
                        lines.append(line)
                    current_line_text = []
                
                current_block = block_num
            
            current_line_text.append(word)
        
        # Add last line
        if current_line_text:
            line = ' '.join(current_line_text).strip()
            if line:
                lines.append(line)
        
        logger.info(f"Extracted {len(lines)} non-empty lines from image")
        
        return lines
    
    except FileNotFoundError as e:
        logger.error(f"File error: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Processing error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during text extraction: {str(e)}")
        raise ValueError(f"Failed to extract text from image: {str(e)}")
