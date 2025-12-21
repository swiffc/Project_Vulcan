#!/usr/bin/env python3
"""
AI-CAD Automation: Unified Environment Bootstrap Script
Project Vulcan - SolidWorks / Inventor / Forge / AI Chatbot Integration

Combines all CAD API access, geometry libraries, AI orchestration,
and backend dependencies into a single virtual environment.

Tested for Python >=3.10

Usage:
    python setup_ai_cad_env.py

Then activate:
    Windows: .\ai_cad_env\Scripts\activate
    Linux/Mac: source ai_cad_env/bin/activate
"""

import os
import subprocess
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# 1. Define master dependency list
# ----------------------------------------------------------------------

# Core CAD API Access
CAD_LIBS = [
    "pywin32",          # Windows COM automation
    "pythonnet",        # .NET CLR access
    "clr-loader",       # CLR loader for pythonnet
    "comtypes",         # COM type library wrapper
    # "pyswx",          # SolidWorks Python wrapper (if available)
    "SolidWrap",        # SolidWorks automation wrapper
    # "inventor-api",   # Inventor API (custom)
    # "forge-python-utils",  # Autodesk Forge utilities
]

# Geometry / Modeling
GEOMETRY_LIBS = [
    # "pythonOCC-core", # OpenCASCADE (requires conda)
    "cadquery",         # Parametric CAD scripting
    # "FreeCAD",        # FreeCAD Python bindings (requires separate install)
    "meshio",           # Mesh file I/O
    "trimesh",          # Triangle mesh processing
    "numpy-stl",        # STL file handling
    "shapely",          # 2D geometric operations
]

# Data / Excel / Documents
DATA_LIBS = [
    "pandas",           # Data manipulation
    "numpy",            # Numerical computing
    "scipy",            # Scientific computing
    "openpyxl",         # Excel read/write
    "xlwings",          # Excel automation
    "jinja2",           # Template engine
    "reportlab",        # PDF generation
    "sqlalchemy",       # Database ORM
    "python-docx",      # Word documents
    "PyPDF2",           # PDF manipulation
    "pdf2image",        # PDF to image conversion
    "pytesseract",      # OCR
]

# Simulation / Thermal / Engineering
SIMULATION_LIBS = [
    # "pyansys",        # ANSYS integration (heavy)
    "CoolProp",         # Thermodynamic properties
    # "pyNastran",      # Nastran file handling (large)
    "pint",             # Unit handling
    "uncertainties",    # Error propagation
]

# AI / LLM / Orchestration
AI_LIBS = [
    "langchain",        # LLM orchestration
    "langchain-anthropic",  # Anthropic integration
    "langchain-openai", # OpenAI integration
    "langgraph",        # Graph-based agent workflows
    # "autogen",        # Microsoft AutoGen (optional)
    "crewai",           # Multi-agent framework
    # "semantic-kernel", # Microsoft SK (optional)
    # "vanna-ai",       # SQL AI (optional)
    # "haystack-ai",    # Document AI (optional)
    "transformers",     # Hugging Face models
    "openai",           # OpenAI API
    "anthropic",        # Anthropic API
    "tiktoken",         # Token counting
]

# Backend Frameworks
BACKEND_LIBS = [
    "fastapi",          # Modern API framework
    "uvicorn[standard]", # ASGI server
    "flask",            # Lightweight web framework
    "apscheduler",      # Job scheduling
    # "celery",         # Distributed task queue (requires broker)
    "httpx",            # Async HTTP client
    "websockets",       # WebSocket support
    "python-multipart", # File uploads
]

# Process / System / DevOps
SYSTEM_LIBS = [
    "psutil",           # System monitoring
    "GPUtil",           # GPU monitoring
    "loguru",           # Better logging
    "pytest",           # Testing framework
    "pytest-asyncio",   # Async testing
    "python-dotenv",    # Environment variables
    "pydantic",         # Data validation
    "pydantic-settings", # Settings management
    "watchdog",         # File system monitoring
]

# Visualization / Dashboards
VIZ_LIBS = [
    "dash",             # Plotly dashboards
    # "dash-vtk",       # VTK visualization (heavy)
    "plotly",           # Interactive charts
    # "vtk",            # 3D visualization (heavy)
    # "pythreejs",      # Three.js for Jupyter
    "matplotlib",       # Static plots
    "pillow",           # Image processing
]

# Search / Vector DB / RAG
VECTOR_LIBS = [
    "chromadb",         # Vector database
    # "faiss-cpu",      # Facebook AI similarity search
    "sentence-transformers",  # Embeddings
    # "docarray",       # Document arrays
]

# MCP / Protocol
MCP_LIBS = [
    "mcp",              # Model Context Protocol
]

# Combine all libraries
ALL_LIBS = (
    CAD_LIBS +
    GEOMETRY_LIBS +
    DATA_LIBS +
    SIMULATION_LIBS +
    AI_LIBS +
    BACKEND_LIBS +
    SYSTEM_LIBS +
    VIZ_LIBS +
    VECTOR_LIBS +
    MCP_LIBS
)

# ----------------------------------------------------------------------
# 2. Virtual Environment Management
# ----------------------------------------------------------------------

ENV_NAME = "ai_cad_env"
ENV_PATH = Path.cwd() / ENV_NAME


def create_env():
    """Create a new virtual environment."""
    if ENV_PATH.exists():
        print(f"Environment already exists at: {ENV_PATH}")
        response = input("Delete and recreate? (y/N): ").strip().lower()
        if response != 'y':
            print("Using existing environment.")
            return
        import shutil
        shutil.rmtree(ENV_PATH)

    subprocess.run([sys.executable, "-m", "venv", str(ENV_PATH)], check=True)
    print(f"Virtual environment created at: {ENV_PATH}")


def get_pip():
    """Get the pip executable path for the virtual environment."""
    if os.name == "nt":  # Windows
        return ENV_PATH / "Scripts" / "pip.exe"
    else:  # Unix/Linux/Mac
        return ENV_PATH / "bin" / "pip"


def pip_install(packages: list, batch_size: int = 10):
    """Install packages in batches to handle failures gracefully."""
    pip = str(get_pip())

    # First upgrade pip itself
    print("Upgrading pip...")
    subprocess.run([pip, "install", "--upgrade", "pip"], check=False)

    failed = []

    for i in range(0, len(packages), batch_size):
        batch = packages[i:i + batch_size]
        print(f"\nInstalling batch {i // batch_size + 1}: {', '.join(batch)}")

        for pkg in batch:
            result = subprocess.run(
                [pip, "install", "--upgrade", pkg],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"  Failed: {pkg}")
                failed.append(pkg)
            else:
                print(f"  Installed: {pkg}")

    return failed


def install_special_packages():
    """Install packages that need special handling."""
    pip = str(get_pip())

    # pythonOCC requires conda or special build
    print("\nNote: pythonOCC-core requires conda installation:")
    print("  conda install -c conda-forge pythonocc-core")

    # FreeCAD requires separate installation
    print("\nNote: FreeCAD requires separate installation from freecad.org")

    # pyansys is heavy and optional
    print("\nNote: pyansys is optional and heavy - install manually if needed:")
    print("  pip install pyansys")


def generate_requirements():
    """Generate a requirements.txt file."""
    req_file = Path.cwd() / "requirements-ai-cad.txt"

    with open(req_file, "w") as f:
        f.write("# AI-CAD Automation Requirements\n")
        f.write("# Generated by setup_ai_cad_env.py\n\n")

        f.write("# CAD API Access\n")
        for pkg in CAD_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# Geometry / Modeling\n")
        for pkg in GEOMETRY_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# Data / Documents\n")
        for pkg in DATA_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# Simulation / Engineering\n")
        for pkg in SIMULATION_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# AI / LLM / Orchestration\n")
        for pkg in AI_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# Backend Frameworks\n")
        for pkg in BACKEND_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# System / DevOps\n")
        for pkg in SYSTEM_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# Visualization\n")
        for pkg in VIZ_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# Vector DB / RAG\n")
        for pkg in VECTOR_LIBS:
            f.write(f"{pkg}\n")

        f.write("\n# MCP Protocol\n")
        for pkg in MCP_LIBS:
            f.write(f"{pkg}\n")

    print(f"\nRequirements file generated: {req_file}")


# ----------------------------------------------------------------------
# 3. Main Entry Point
# ----------------------------------------------------------------------

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║       Project Vulcan - AI-CAD Environment Setup              ║
    ║  SolidWorks / Inventor / Forge / AI Chatbot Integration      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    print("This script will:")
    print("  1. Create a virtual environment (ai_cad_env)")
    print("  2. Install all CAD, AI, and automation packages")
    print("  3. Generate a requirements file for future use")
    print()

    response = input("Continue? (Y/n): ").strip().lower()
    if response == 'n':
        print("Aborted.")
        return

    print("\n" + "=" * 60)
    print("Step 1: Creating virtual environment...")
    print("=" * 60)
    create_env()

    print("\n" + "=" * 60)
    print("Step 2: Installing packages...")
    print("=" * 60)
    failed = pip_install(ALL_LIBS)

    print("\n" + "=" * 60)
    print("Step 3: Special packages...")
    print("=" * 60)
    install_special_packages()

    print("\n" + "=" * 60)
    print("Step 4: Generating requirements file...")
    print("=" * 60)
    generate_requirements()

    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)

    if failed:
        print(f"\nFailed packages ({len(failed)}):")
        for pkg in failed:
            print(f"  - {pkg}")
        print("\nYou may need to install these manually.")

    print(f"""
Activate the environment:
  Windows:   .\\{ENV_NAME}\\Scripts\\activate
  Linux/Mac: source {ENV_NAME}/bin/activate

Then start coding:
  from agents.cad_agent import cad_orchestrator
  from langchain.agents import initialize_agent
  import pandas as pd
    """)


if __name__ == "__main__":
    main()
