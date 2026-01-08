"""Utility to convert PDF files to images for OCR processing"""
import os
import logging
from PIL import Image

logger = logging.getLogger(__name__)

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logger.warning("pdf2image not available. PDF files cannot be processed.")


def pdf_to_image(pdf_path, output_dir=None):
    """Convert PDF to image
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save image (optional, uses same dir as PDF)
        
    Returns:
        Path to converted image file, or None if conversion fails
    """
    if not PDF2IMAGE_AVAILABLE:
        logger.error("pdf2image library not available. Install it with: pip install pdf2image")
        return None
    
    try:
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        
        # Convert first page of PDF to image
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
        
        if not images:
            logger.error("No pages found in PDF")
            return None
        
        # Save first page as image
        image_path = os.path.join(output_dir, os.path.splitext(os.path.basename(pdf_path))[0] + '.png')
        images[0].save(image_path, 'PNG')
        
        logger.info(f"Converted PDF to image: {image_path}")
        return image_path
        
    except Exception as e:
        logger.error(f"Error converting PDF to image: {e}")
        return None


def is_pdf_file(file_path):
    """Check if file is a PDF"""
    return file_path.lower().endswith('.pdf') or file_path.lower().endswith('.pdf')
