"""
Wrapper script to pull engineering standards from external repositories/packages.
This delegates to `pull_external_standards.py` so existing logic stays in one place.
"""

from pull_external_standards import main


if __name__ == "__main__":
    main()
