"""
Script to scan and extract content from Standards Book PDFs
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    try:
        import PyPDF2
        HAS_PDFPLUMBER = False
    except ImportError:
        print("ERROR: Neither pdfplumber nor PyPDF2 is installed.")
        print("Please install: pip install pdfplumber")
        sys.exit(1)

def extract_text_pdfplumber(pdf_path):
    """Extract text using pdfplumber (better for tables and formatting)"""
    text_content = []
    metadata = {}
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            metadata = {
                'total_pages': len(pdf.pages),
                'title': pdf.metadata.get('Title', 'Unknown'),
                'author': pdf.metadata.get('Author', 'Unknown'),
            }
            
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append({
                        'page': i,
                        'text': text,
                        'tables': page.extract_tables() if page.extract_tables() else []
                    })
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None, None
    
    return text_content, metadata

def extract_text_pypdf2(pdf_path):
    """Extract text using PyPDF2 (fallback)"""
    text_content = []
    metadata = {}
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = {
                'total_pages': len(pdf_reader.pages),
                'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown',
            }
            
            for i, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append({
                        'page': i,
                        'text': text,
                        'tables': []  # PyPDF2 doesn't extract tables
                    })
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None, None
    
    return text_content, metadata

def scan_pdf(pdf_path):
    """Scan a PDF file and return extracted content"""
    print(f"\n{'='*80}")
    print(f"Scanning: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        return None
    
    if HAS_PDFPLUMBER:
        content, metadata = extract_text_pdfplumber(pdf_path)
    else:
        content, metadata = extract_text_pypdf2(pdf_path)
    
    if content is None:
        return None
    
    print(f"Total Pages: {metadata['total_pages']}")
    print(f"Title: {metadata.get('title', 'N/A')}")
    print(f"Author: {metadata.get('author', 'N/A')}")
    
    # Extract first few pages for preview
    print(f"\n--- Preview (First 3 pages) ---")
    for page_data in content[:3]:
        print(f"\nPage {page_data['page']}:")
        print("-" * 60)
        preview = page_data['text'][:1000]  # First 1000 chars
        print(preview)
        if len(page_data['text']) > 1000:
            print("... [truncated]")
    
    # Count tables
    total_tables = sum(len(p.get('tables', [])) for p in content)
    if total_tables > 0:
        print(f"\nTotal tables found: {total_tables}")
    
    return {
        'path': pdf_path,
        'metadata': metadata,
        'content': content,
        'total_tables': total_tables
    }

def main():
    """Main function to scan all PDFs"""
    pdf_files = [
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK I_REV0.pdf",
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK II vol. I_REV0.pdf",
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK II vol. II_REV0.pdf",
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK III_REV0.pdf",
        r"C:\Users\D&E Cornealius\Documents\STANDARDS BOOK IV_REV0.pdf",
    ]
    
    results = []
    
    for pdf_path in pdf_files:
        result = scan_pdf(pdf_path)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SCAN SUMMARY")
    print(f"{'='*80}")
    print(f"Total PDFs scanned: {len(results)}")
    print(f"Total pages: {sum(r['metadata']['total_pages'] for r in results)}")
    print(f"Total tables: {sum(r['total_tables'] for r in results)}")
    
    # Save full content to files for analysis
    output_dir = Path(__file__).parent.parent / "output" / "standards_scan"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for result in results:
        filename = Path(result['path']).stem
        output_file = output_dir / f"{filename}_extracted.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"STANDARDS BOOK EXTRACTION\n")
            f.write(f"{'='*80}\n")
            f.write(f"File: {result['path']}\n")
            f.write(f"Title: {result['metadata'].get('title', 'N/A')}\n")
            f.write(f"Total Pages: {result['metadata']['total_pages']}\n")
            f.write(f"Total Tables: {result['total_tables']}\n")
            f.write(f"{'='*80}\n\n")
            
            for page_data in result['content']:
                f.write(f"\n{'='*60}\n")
                f.write(f"PAGE {page_data['page']}\n")
                f.write(f"{'='*60}\n\n")
                f.write(page_data['text'])
                f.write("\n\n")
                
                # Write tables if available
                if page_data.get('tables'):
                    f.write(f"\n--- TABLES ON PAGE {page_data['page']} ---\n")
                    for idx, table in enumerate(page_data['tables'], 1):
                        f.write(f"\nTable {idx}:\n")
                        for row in table:
                            f.write(str(row) + "\n")
        
        print(f"Saved extraction to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()

