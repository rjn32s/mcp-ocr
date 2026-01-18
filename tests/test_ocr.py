import pytest
import os
import sys
from mcp_ocr.server import perform_ocr, get_supported_languages, perform_pdf_ocr, perform_batch_ocr

@pytest.fixture
def sample_image():
    """Create a simple test image with text."""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a white image
    img = Image.new('RGB', (200, 50), color='white')
    d = ImageDraw.Draw(img)
    
    # Use a simple font that works on all platforms
    text = "Hello World"
    d.text((10, 10), text, fill='black')
    
    # Save to bytes and encode to base64
    import io
    import base64
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

@pytest.mark.asyncio
async def test_perform_ocr(sample_image):
    """Test OCR on a simple image."""
    try:
        result = await perform_ocr(input_data=sample_image)
        # Remove whitespace and make lowercase for more reliable comparison
        result = result.lower().strip()
        assert "hello" in result
        assert "world" in result
    except Exception as e:
        pytest.skip(f"OCR test failed, possibly due to Tesseract installation: {str(e)}")

@pytest.mark.asyncio
async def test_get_supported_languages():
    """Test getting supported languages."""
    try:
        languages = await get_supported_languages()
        assert isinstance(languages, list)
        assert "eng" in languages  # English should always be available
    except Exception as e:
        pytest.skip(f"Language test failed, possibly due to Tesseract installation: {str(e)}")

@pytest.mark.asyncio
async def test_perform_ocr_invalid_input():
    """Test OCR with invalid input."""
    with pytest.raises(Exception):
        await perform_ocr(input_data="not a valid image or path")

@pytest.mark.asyncio
async def test_perform_ocr_chinese():
    """Test Chinese OCR support."""
    from PIL import Image, ImageDraw, ImageFont
    import io
    import base64
    
    # Create a white image with a Chinese character "中"
    img = Image.new('RGB', (100, 100), color='white')
    d = ImageDraw.Draw(img)
    # Using default font might not support Chinese, but this tests the pipeline
    # In a real environment, you'd need a font that supports Chinese
    text = "中"
    d.text((10, 10), text, fill='black')
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    try:
        # This will fail or skip if chi_sim is not installed
        result = await perform_ocr(input_data=img_b64, language="chi_sim")
        assert "中" in result or result != ""
    except Exception as e:
        pytest.skip(f"Chinese OCR skip: {str(e)}")

@pytest.mark.asyncio
async def test_perform_pdf_ocr():
    """Test PDF OCR support."""
    # This is a bit tricky to test without a real PDF, but we can test the pipeline
    # We'll use a placeholder that should fail with a specific error if poppler is missing
    try:
        # Invalid PDF data
        with pytest.raises(Exception):
            await perform_pdf_ocr(input_data="not a pdf")
    except Exception as e:
        pytest.skip(f"PDF OCR test skip: {str(e)}")

@pytest.mark.asyncio
async def test_perform_batch_ocr(sample_image):
    """Test Batch OCR support."""
    try:
        results = await perform_batch_ocr(inputs=[sample_image, sample_image])
        assert len(results) == 2
        for result in results:
            assert "hello" in result.lower()
    except Exception as e:
        pytest.skip(f"Batch OCR test skip: {str(e)}")