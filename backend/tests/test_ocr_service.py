"""Tests for OCR service"""

import pytest
from pathlib import Path

from app.services.ocr_service import OCRService


@pytest.fixture
def ocr_service():
    """Create OCR service instance"""
    return OCRService()


def test_ocr_service_initialization(ocr_service):
    """Test OCR service can be initialized"""
    assert ocr_service is not None


def test_preprocess_image(ocr_service):
    """Test image preprocessing"""
    from PIL import Image
    
    # Create test image
    img = Image.new('RGB', (50, 50), color='red')
    
    processed = ocr_service._preprocess_image(img)
    
    # Should be resized if too small
    assert processed.width >= 100 or processed.height >= 100
    assert processed.mode == 'RGB'


def test_calculate_confidence(ocr_service):
    """Test confidence calculation"""
    data = {
        'conf': [80, 90, 85, -1, 88]
    }
    
    confidence = ocr_service._calculate_confidence(data)
    
    assert 0 <= confidence <= 1
    assert abs(confidence - 0.8575) < 0.01  # (80+90+85+88)/(100*4)
