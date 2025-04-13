import pytest
import os
from mcp_ocr.server import perform_ocr, get_supported_languages

@pytest.fixture
def sample_image():
    # Create a simple test image with text
    from PIL import Image, ImageDraw
    
    img = Image.new('RGB', (200, 50), color='white')
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Hello World", fill='black')
    
    # Save to bytes
    import io
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

@pytest.mark.asyncio
async def test_perform_ocr(sample_image):
    """Test OCR on a simple image."""
    result = await perform_ocr(sample_image)
    assert "Hello" in result
    assert "World" in result

@pytest.mark.asyncio
async def test_get_supported_languages():
    """Test getting supported languages."""
    languages = await get_supported_languages()
    assert isinstance(languages, list)
    assert "eng" in languages  # English should always be available

@pytest.mark.asyncio
async def test_perform_ocr_invalid_input():
    """Test OCR with invalid input."""
    with pytest.raises(Exception):
        await perform_ocr(b"invalid image data") 