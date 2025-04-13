#!/usr/bin/env python3
"""
Command-line entry point for the MCP OCR Server.
"""

import argparse
from .server import mcp

def main():
    """MCP OCR: Extract text from images using OCR."""
    parser = argparse.ArgumentParser(
        description="Extract text from images using OCR with support for local files, URLs, and image data."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
