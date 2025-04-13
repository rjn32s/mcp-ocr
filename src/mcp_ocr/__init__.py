"""MCP OCR: A production-grade OCR server built using MCP (Model Context Protocol)."""

__version__ = "0.1.0"

from .server import mcp, perform_ocr, get_supported_languages

__all__ = ["mcp", "perform_ocr", "get_supported_languages"]
