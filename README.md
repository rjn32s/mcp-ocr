# MCP OCR Server
[![PyPI](https://img.shields.io/pypi/v/mcp-ocr)](https://pypi.org/project/mcp-ocr/)
[![Downloads](https://static.pepy.tech/personalized-badge/mcp-ocr?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/mcp-ocr)

A production-grade OCR server built using MCP (Model Context Protocol) that provides OCR capabilities through a simple interface.

## Features

- Extract text from images using Tesseract OCR
- Support for multiple input types:
  - Local image files
  - Image URLs
  - Raw image bytes
- Automatic Tesseract installation
- Support for multiple languages
- Production-ready error handling

## Installation

```bash
# Using pip
pip install mcp-ocr

# Using uv
uv pip install mcp-ocr
```

Tesseract will be installed automatically on supported platforms:
- macOS (via Homebrew)
- Linux (via apt, dnf, or pacman)
- Windows (manual installation instructions provided)

## Usage

### As an MCP Server

1. Start the server:
```bash
python -m mcp_ocr
```

2. Configure Claude for Desktop:
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
    "mcpServers": {
        "ocr": {
            "command": "python",
            "args": ["-m", "mcp_ocr"]
        }
    }
}
```

### Available Tools

#### perform_ocr
Extract text from images:
```python
# From file
perform_ocr("/path/to/image.jpg")

# From URL
perform_ocr("https://example.com/image.jpg")

# From bytes
perform_ocr(image_bytes)
```

#### get_supported_languages
List available OCR languages:
```python
get_supported_languages()
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/rjn32s/mcp-ocr.git
cd mcp-ocr
```

2. Set up development environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

3. Run tests:
```bash
pytest
```


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

- Never commit API tokens or sensitive credentials
- Use environment variables or secure credential storage
- Follow GitHub's security best practices

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Model Context Protocol](https://modelcontextprotocol.io)
