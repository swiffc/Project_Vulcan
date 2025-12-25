"""
PDF Annotation System

Annotates PDF drawings with validation errors and warnings.
Adds red flags, highlights, and comments to drawings.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Optional imports
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import red, orange, yellow, green
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    logger.warning("reportlab not available - PDF annotation disabled")
    REPORTLAB_AVAILABLE = False

try:
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import Transformation
    PYPDF2_AVAILABLE = True
except ImportError:
    logger.warning("PyPDF2 not available - PDF merging disabled")
    PYPDF2_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available - image annotation disabled")
    PIL_AVAILABLE = False


@dataclass
class Annotation:
    """Annotation to add to PDF."""
    
    page: int  # 0-indexed
    x: float
    y: float
    text: str
    severity: str  # "critical", "error", "warning", "info"
    icon: str = "flag"  # "flag", "circle", "arrow"


class PDFAnnotator:
    """
    Annotates PDF drawings with validation errors.
    
    Example:
        >>> annotator = PDFAnnotator()
        >>> annotations = [
        ...     Annotation(page=0, x=100, y=200, text="Missing datum C", severity="error"),
        ...     Annotation(page=0, x=300, y=400, text="Tight tolerance", severity="warning"),
        ... ]
        >>> annotator.annotate_pdf("drawing.pdf", annotations, "annotated.pdf")
    """
    
    def __init__(self):
        """Initialize PDF annotator."""
        self.available = REPORTLAB_AVAILABLE and PYPDF2_AVAILABLE
        
        if not self.available:
            logger.warning("PDF annotation not available - install reportlab and PyPDF2")
        else:
            logger.info("PDF annotator initialized")
    
    def annotate_pdf(
        self,
        input_path: str,
        annotations: List[Annotation],
        output_path: str,
    ) -> bool:
        """
        Annotate a PDF with validation errors.
        
        Args:
            input_path: Path to original PDF
            annotations: List of annotations to add
            output_path: Path to save annotated PDF
            
        Returns:
            True if successful
        """
        if not self.available:
            logger.error("PDF annotation not available")
            return False
        
        try:
            logger.info(f"Annotating {input_path} with {len(annotations)} annotations")
            
            # Read original PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Create annotations by page
            annotations_by_page = {}
            for ann in annotations:
                if ann.page not in annotations_by_page:
                    annotations_by_page[ann.page] = []
                annotations_by_page[ann.page].append(ann)
            
            # Process each page
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                
                # Add annotations if any for this page
                if page_num in annotations_by_page:
                    # Create overlay with annotations
                    overlay = self._create_annotation_overlay(
                        page.mediabox.width,
                        page.mediabox.height,
                        annotations_by_page[page_num],
                    )
                    
                    if overlay:
                        # Merge overlay with original page
                        overlay_reader = PdfReader(overlay)
                        page.merge_page(overlay_reader.pages[0])
                
                writer.add_page(page)
            
            # Write annotated PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            logger.info(f"Annotated PDF saved to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"PDF annotation failed: {e}", exc_info=True)
            return False
    
    def _create_annotation_overlay(
        self,
        width: float,
        height: float,
        annotations: List[Annotation],
    ) -> Optional[str]:
        """Create a transparent overlay with annotations."""
        import tempfile
        import os
        
        try:
            # Create temporary file for overlay
            temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
            os.close(temp_fd)
            
            # Create canvas
            c = canvas.Canvas(temp_path, pagesize=(width, height))
            c.setPageCompression(0)  # Disable compression for transparency
            
            # Add each annotation
            for ann in annotations:
                self._draw_annotation(c, ann, height)
            
            c.save()
            return temp_path
        
        except Exception as e:
            logger.error(f"Overlay creation failed: {e}")
            return None
    
    def _draw_annotation(
        self,
        c,  # canvas.Canvas when reportlab available
        ann: Annotation,
        page_height: float,
    ) -> None:
        """Draw a single annotation."""
        # Convert coordinates (PDF uses bottom-left origin)
        x = ann.x
        y = page_height - ann.y
        
        # Choose color based on severity
        if ann.severity == "critical":
            color = red
        elif ann.severity == "error":
            color = red
        elif ann.severity == "warning":
            color = orange
        else:
            color = yellow
        
        # Draw flag icon
        c.setFillColor(color)
        c.setStrokeColor(color)
        
        if ann.icon == "flag":
            # Draw flag
            c.rect(x, y, 2, 20, fill=1)  # Pole
            c.polygon(
                [(x + 2, y + 20), (x + 20, y + 15), (x + 2, y + 10)],
                fill=1,
                stroke=0
            )
        
        elif ann.icon == "circle":
            # Draw circle
            c.circle(x, y, 10, fill=0, stroke=1)
        
        elif ann.icon == "arrow":
            # Draw arrow
            c.line(x, y, x + 20, y - 20)
            c.polygon(
                [(x + 20, y - 20), (x + 15, y - 15), (x + 20, y - 15)],
                fill=1
            )
        
        # Add text
        c.setFillColor(red if ann.severity in ["critical", "error"] else orange)
        c.setFont("Helvetica-Bold", 8)
        
        # Draw text with background
        text_width = c.stringWidth(ann.text, "Helvetica-Bold", 8)
        c.setFillColorRGB(1, 1, 0.9, alpha=0.9)  # Light yellow background
        c.rect(x + 25, y - 10, text_width + 10, 15, fill=1, stroke=0)
        
        c.setFillColor(red if ann.severity in ["critical", "error"] else orange)
        c.drawString(x + 30, y - 5, ann.text)


class ImageAnnotator:
    """
    Annotates images (from PDF pages) with validation errors.
    
    Alternative to PDF annotation - creates annotated images.
    """
    
    def __init__(self):
        """Initialize image annotator."""
        self.available = PIL_AVAILABLE
        
        if not self.available:
            logger.warning("Image annotation not available - install Pillow")
        else:
            logger.info("Image annotator initialized")
    
    def annotate_image(
        self,
        image: Image.Image,
        annotations: List[Annotation],
    ) -> Image.Image:
        """
        Annotate an image with validation errors.
        
        Args:
            image: PIL Image to annotate
            annotations: List of annotations
            
        Returns:
            Annotated image
        """
        if not self.available:
            logger.error("Image annotation not available")
            return image
        
        try:
            # Create drawing context
            draw = ImageDraw.Draw(image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            # Draw each annotation
            for ann in annotations:
                x, y = int(ann.x), int(ann.y)
                
                # Choose color
                if ann.severity == "critical":
                    color = (255, 0, 0)  # Red
                elif ann.severity == "error":
                    color = (255, 0, 0)  # Red
                elif ann.severity == "warning":
                    color = (255, 165, 0)  # Orange
                else:
                    color = (255, 255, 0)  # Yellow
                
                # Draw flag
                draw.rectangle([x, y, x + 3, y + 25], fill=color)
                draw.polygon([(x + 3, y), (x + 25, y + 10), (x + 3, y + 15)], fill=color)
                
                # Draw text with background
                bbox = draw.textbbox((x + 30, y), ann.text, font=font)
                draw.rectangle(
                    [bbox[0] - 5, bbox[1] - 2, bbox[2] + 5, bbox[3] + 2],
                    fill=(255, 255, 230, 230)
                )
                draw.text((x + 30, y), ann.text, fill=color, font=font)
            
            return image
        
        except Exception as e:
            logger.error(f"Image annotation failed: {e}")
            return image
    
    def save_annotated_images(
        self,
        images: List[Image.Image],
        annotations_by_page: dict,
        output_dir: str,
    ) -> List[str]:
        """
        Save annotated images to files.
        
        Args:
            images: List of PIL images (one per page)
            annotations_by_page: Dict of page -> annotations
            output_dir: Directory to save annotated images
            
        Returns:
            List of output file paths
        """
        output_paths = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for page_num, image in enumerate(images):
            annotations = annotations_by_page.get(page_num, [])
            
            if annotations:
                annotated = self.annotate_image(image.copy(), annotations)
            else:
                annotated = image
            
            output_file = output_path / f"page_{page_num + 1}_annotated.png"
            annotated.save(output_file, "PNG")
            output_paths.append(str(output_file))
            
            logger.info(f"Saved annotated page {page_num + 1} to {output_file}")
        
        return output_paths
