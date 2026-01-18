# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2026-01-18

### Added
- PDF OCR Support: New `perform_pdf_ocr` tool to extract text from multi-page PDFs using `pdf2image`.
- Batch Processing: New `perform_batch_ocr` tool to process multiple images in parallel using `asyncio.gather`.
- Poppler Support: Installation script updated to handle `poppler-utils` dependency for PDF processing.
 
## [0.1.3] - 2026-01-18

### Added
- Chinese Character Support: Added `chi_sim` and `chi_tra` to auto-installation script and tested support.
- Base64 Input Support: `perform_ocr` now automatically detects and handles base64 encoded image data.

### Fixed
- Resolved `BaseModel.__init__()` error in `perform_ocr` tool by simplifying signature and fixing `ErrorData` keyword arguments.
- Fixed build issues for editable installs by explicitly mapping package structure in `pyproject.toml`.
- Restored missing `subprocess` imports in the server implementation.

## [0.1.2] - 2024-03-21

### Changed
- Improved package structure and imports
- Enhanced error handling in OCR processing
- Updated documentation with usage examples

### Fixed
- Resolved import issues for package installation
- Further improvements to Windows Tesseract PATH handling

## [0.1.1] - 2024-03-21

### Fixed
- Windows CI: Improved Tesseract PATH handling in GitHub Actions workflow
- Fixed package publishing configuration

## [0.1.0] - 2025-04-13

### Added
- Initial release
- Basic OCR functionality with Tesseract
- Support for file, URL, and bytes input
- Automatic Tesseract installation
- Multi-platform support (Windows, macOS, Linux)
- GitHub Actions CI/CD pipeline
- Test suite with coverage reporting

### Fixed
- Windows CI: Fixed Tesseract PATH handling in GitHub Actions workflow 