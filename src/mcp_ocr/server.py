"""MCP OCR Server implementation."""

from typing import Any, Optional, Union
import cv2
import numpy as np
import pytesseract
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
import httpx
import os
import urllib.parse
from enum import Enum
import subprocess
import sys
import base64
import re
import asyncio
from pdf2image import convert_from_path, convert_from_bytes
from .install_tesseract import install_tesseract

def check_tesseract():
    """Check if Tesseract is installed and accessible."""
    try:
        subprocess.run(["tesseract", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Tesseract not found. Attempting to install...", file=sys.stderr)
        install_tesseract()

# Check Tesseract installation
check_tesseract()

# Initialize FastMCP server
mcp = FastMCP("ocr")

class OCRInputType(Enum):
    FILE = "file"
    URL = "url"
    BYTES = "bytes"

async def load_image(input_data: Union[str, bytes]) -> np.ndarray:
    """Load image from various sources (file path, URL, base64 string, or bytes).
    
    Args:
        input_data: Can be a file path, URL, base64 encoded string, or image bytes
        
    Returns:
        numpy array of the image
        
    Raises:
        McpError: If image loading fails
    """
    try:
        # Determine input type
        if isinstance(input_data, str):
            # Check if it's a URL
            parsed_url = urllib.parse.urlparse(input_data)
            if parsed_url.scheme in ('http', 'https'):
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(input_data)
                        response.raise_for_status()
                        nparr = np.frombuffer(response.content, np.uint8)
                except httpx.HTTPError as e:
                    raise McpError(
                        ErrorData(
                            code=INTERNAL_ERROR,
                            message=f"Failed to fetch image from URL: {str(e)}"
                        )
                    )
            # Check if it's a file path
            elif os.path.exists(input_data):
                try:
                    nparr = np.fromfile(input_data, np.uint8)
                except Exception as e:
                    raise McpError(
                        ErrorData(
                            code=INTERNAL_ERROR,
                            message=f"Failed to read image file: {str(e)}"
                        )
                    )
            # Check if it's a base64 encoded string
            else:
                try:
                    # Remove potential data URI prefix (e.g., "data:image/jpeg;base64,")
                    base64_data = re.sub(r'^data:image/.+;base64,', '', input_data)
                    # Attempt to decode base64
                    image_bytes = base64.b64decode(base64_data)
                    nparr = np.frombuffer(image_bytes, np.uint8)
                except Exception:
                    raise McpError(
                        ErrorData(
                            code=INVALID_PARAMS,
                            message=f"Invalid input: {input_data[:50]}... is not a valid URL, file path, or base64 string"
                        )
                    )
        else:
            # It's bytes
            nparr = np.frombuffer(input_data, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message="Failed to decode image data"
                )
            )
        return img
            
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Unexpected error loading image: {str(e)}"
            )
        )

@mcp.tool()
async def perform_ocr(
    input_data: str,
    language: str = "eng",
    config: str = "--oem 3 --psm 6"
) -> str:
    """Perform OCR on the provided input.
    
    Args:
        input_data: File path, URL, or base64 encoded image data
        language: Tesseract language code (default: "eng")
        config: Tesseract configuration options (default: "--oem 3 --psm 6")
        
    Returns:
        Extracted text from the image
        
    Usage:
        perform_ocr("/path/to/image.jpg")
        perform_ocr("https://example.com/image.jpg")
        perform_ocr(image_bytes)
    """
    try:
        # Validate language
        available_langs = pytesseract.get_languages()
        if language not in available_langs:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Unsupported language: {language}. Available languages: {', '.join(available_langs)}"
                )
            )
            
        # Load and process image
        img = await load_image(input_data)
        
        try:
            # Perform OCR
            text = pytesseract.image_to_string(img, lang=language, config=config)
            if not text.strip():
                raise McpError(
                    ErrorData(
                        code=INTERNAL_ERROR,
                        message="No text detected in image"
                    )
                )
            return text.strip()
        except Exception as e:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"OCR processing failed: {str(e)}"
                )
            )
            
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Unexpected error during OCR: {str(e)}"
            )
        )

@mcp.tool()
async def get_supported_languages() -> list[str]:
    """Get list of supported OCR languages.
    
    Returns:
        List of supported language codes
        
    Usage:
        get_supported_languages()
    """
    try:
        langs = pytesseract.get_languages()
        if not langs:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message="No supported languages found. Please check Tesseract installation."
                )
            )
        return langs
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to get supported languages: {str(e)}"
            )
        )

@mcp.tool()
async def perform_pdf_ocr(
    input_data: str,
    language: str = "eng",
    pages: Optional[Union[int, list[int]]] = None,
    config: str = "--oem 3 --psm 6"
) -> str:
    """Perform OCR on a PDF file.
    
    Args:
        input_data: File path, URL, or base64 encoded PDF data
        language: Tesseract language code (default: "eng")
        pages: Specific page number or list of page numbers (1-indexed). If None, all pages are processed.
        config: Tesseract configuration options (default: "--oem 3 --psm 6")
        
    Returns:
        Extracted text from the PDF pages, separated by page markers
    """
    try:
        # Load PDF bytes
        pdf_bytes = None
        if urllib.parse.urlparse(input_data).scheme in ('http', 'https'):
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(input_data)
                response.raise_for_status()
                pdf_bytes = response.content
        elif os.path.exists(input_data):
            with open(input_data, 'rb') as f:
                pdf_bytes = f.read()
        else:
            try:
                base64_data = re.sub(r'^data:application/pdf;base64,', '', input_data)
                pdf_bytes = base64.b64decode(base64_data)
            except Exception:
                raise McpError(
                    ErrorData(
                        code=INVALID_PARAMS,
                        message="Invalid input: Must be a valid PDF URL, file path, or base64 string"
                    )
                )

        # Convert PDF to images
        try:
            images = convert_from_bytes(pdf_bytes)
        except Exception as e:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to convert PDF to images: {str(e)}"
                )
            )

        # Filter pages if specified
        if pages is not None:
            if isinstance(pages, int):
                target_pages = [pages]
            else:
                target_pages = pages
            
            selected_images = []
            for p in target_pages:
                if 1 <= p <= len(images):
                    selected_images.append((p, images[p-1]))
                else:
                    print(f"Warning: Page {p} is out of range for PDF with {len(images)} pages", file=sys.stderr)
        else:
            selected_images = list(enumerate(images, 1))

        # Perform OCR on selected pages
        results = []
        for page_num, img in selected_images:
            # Convert PIL Image to OpenCV format (numpy array)
            open_cv_image = np.array(img.convert('RGB'))
            # Convert RGB to BGR (OpenCV uses BGR)
            open_cv_image = open_cv_image[:, :, ::-1].copy()
            
            text = pytesseract.image_to_string(open_cv_image, lang=language, config=config)
            results.append(f"--- Page {page_num} ---\n{text.strip()}")

        return "\n\n".join(results)

    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"PDF OCR failed: {str(e)}"
            )
        )

@mcp.tool()
async def perform_batch_ocr(
    inputs: list[str],
    language: str = "eng",
    config: str = "--oem 3 --psm 6"
) -> list[str]:
    """Perform OCR on multiple images in parallel.
    
    Args:
        inputs: List of file paths, URLs, or base64 encoded image data strings
        language: Tesseract language code (default: "eng")
        config: Tesseract configuration options (default: "--oem 3 --psm 6")
        
    Returns:
        List of extracted text for each input in the same order
    """
    tasks = []
    for input_data in inputs:
        tasks.append(perform_ocr(input_data=input_data, language=language, config=config))
    
    return await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
