"""Handle Tesseract installation during package setup."""

import os
import platform
import subprocess
import sys
from typing import Optional

def get_package_manager() -> Optional[str]:
    """Detect the system's package manager."""
    system = platform.system().lower()
    
    if system == "darwin":
        # Check if Homebrew is installed
        if subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
            return "brew"
    elif system == "linux":
        # Check for apt (Debian/Ubuntu)
        if os.path.exists("/usr/bin/apt"):
            return "apt"
        # Check for dnf (Fedora)
        elif os.path.exists("/usr/bin/dnf"):
            return "dnf"
        # Check for pacman (Arch)
        elif os.path.exists("/usr/bin/pacman"):
            return "pacman"
    
    return None

def install_tesseract():
    """Install Tesseract OCR based on the operating system."""
    system = platform.system().lower()
    pkg_manager = get_package_manager()
    
    try:
        if system == "darwin" and pkg_manager == "brew":
            subprocess.run(["brew", "install", "tesseract"], check=True)
            
        elif system == "linux":
            if pkg_manager == "apt":
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "tesseract-ocr"], check=True)
            elif pkg_manager == "dnf":
                subprocess.run(["sudo", "dnf", "install", "-y", "tesseract"], check=True)
            elif pkg_manager == "pacman":
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "tesseract"], check=True)
                
        elif system == "windows":
            print("For Windows users:")
            print("Please download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("After installation, ensure the Tesseract installation directory is in your system PATH.")
            return
            
        print("Tesseract OCR installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing Tesseract: {str(e)}", file=sys.stderr)
        print("Please install Tesseract manually:", file=sys.stderr)
        print("- macOS: brew install tesseract", file=sys.stderr)
        print("- Ubuntu/Debian: sudo apt-get install tesseract-ocr", file=sys.stderr)
        print("- Fedora: sudo dnf install tesseract", file=sys.stderr)
        print("- Arch: sudo pacman -S tesseract", file=sys.stderr)
        print("- Windows: https://github.com/UB-Mannheim/tesseract/wiki", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    install_tesseract() 