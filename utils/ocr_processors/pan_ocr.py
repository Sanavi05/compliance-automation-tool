import cv2
import pytesseract
import re
import numpy as np
import logging
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)


class PANOCR:
    """OCR processor for PAN card documents"""
    
    def __init__(self, tesseract_path=None):
        """Initialize PANOCR processor
        
        Args:
            tesseract_path: Path to tesseract executable (optional)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def preprocess_image(self, image_path):
        """Preprocess PAN card image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
            
            return denoised
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            # Return original image if preprocessing fails
            img = cv2.imread(image_path)
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img is not None else None
    
    def extract_pan_number(self, text):
        """Extract PAN number using regex pattern [A-Z]{5}[0-9]{4}[A-Z]
        
        Args:
            text: OCR extracted text
            
        Returns:
            PAN number or None
        """
        # Clean text - fix common OCR errors
        text_upper = text.upper()
        # Replace common OCR mistakes: 0->O, 1->I, 5->S (but be careful with digits)
        # We'll try both original and cleaned versions
        
        # Pattern: 5 letters, 4 digits, 1 letter
        pattern = r'\b[A-Z0-9]{5}[0-9]{4}[A-Z0-9]\b'
        matches = re.findall(pattern, text_upper)
        
        for match in matches:
            # Try to fix OCR errors in the match
            # First 5 should be letters (fix 0->O, 1->I)
            first_five = match[:5]
            middle_four = match[5:9]
            last_one = match[9]
            
            # Fix common OCR errors
            first_five = first_five.replace('0', 'O').replace('1', 'I')
            last_one = last_one.replace('0', 'O').replace('1', 'I')
            
            # Check if it's valid PAN format
            if (first_five.isalpha() and len(first_five) == 5 and
                middle_four.isdigit() and len(middle_four) == 4 and
                last_one.isalpha() and len(last_one) == 1):
                return first_five + middle_four + last_one
        
        # Try strict pattern on cleaned text
        pattern_strict = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
        matches_strict = re.findall(pattern_strict, text_upper)
        if matches_strict:
            return matches_strict[0]
        
        return None
    
    def _clean_name(self, name):
        """Clean and normalize name extracted from OCR
        
        Args:
            name: Raw name string
            
        Returns:
            Cleaned name string
        """
        if not name:
            return None
        
        # Remove special characters except spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        name = name.strip()
        
        # Fix common OCR mistakes
        # In names, 0 is often O, 1 is often I
        cleaned = []
        for char in name:
            if char == '0' and (not cleaned or cleaned[-1].isalpha()):
                cleaned.append('O')
            elif char == '1' and (not cleaned or cleaned[-1].isalpha()):
                cleaned.append('I')
            elif char == '5' and (not cleaned or cleaned[-1].isalpha()):
                cleaned.append('S')
            else:
                cleaned.append(char)
        
        name = ''.join(cleaned)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Must have at least 3 letters
        if sum(1 for c in name if c.isalpha()) < 3:
            return None
        
        return name if len(name) > 2 else None
    
    def extract_name(self, text):
        """Extract name in capital letters
        
        Args:
            text: OCR extracted text
            
        Returns:
            Extracted name or None
        """
        # Clean text first
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        lines = text.split('\n')
        
        # Look for lines with name
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines and very short lines
            if len(line_stripped) < 3:
                continue
            
            # Look for lines after "Name" keyword
            if 'name' in line.lower():
                if ':' in line:
                    name = line.split(':', 1)[1].strip()
                    name = self._clean_name(name)
                    if name:
                        return name
                elif i + 1 < len(lines):
                    name = lines[i + 1].strip()
                    name = self._clean_name(name)
                    if name:
                        return name
        
        # Fallback: look for lines with mostly uppercase letters
        for line in lines:
            line = line.strip()
            # Check if line has mostly uppercase letters
            if len(line) > 5:
                upper_count = sum(1 for c in line if c.isupper())
                if upper_count / len(line) > 0.6:
                    # Skip if it contains common keywords
                    if not any(keyword in line.upper() for keyword in ['INCOME', 'TAX', 'INDIA', 'GOVERNMENT', 'PERMANENT', 'ACCOUNT', 'NUMBER', 'PAN', 'CARD']):
                        name = self._clean_name(line)
                        if name:
                            return name
        
        return None
    
    def extract_father_name(self, text):
        """Extract father's name
        
        Args:
            text: OCR extracted text
            
        Returns:
            Father's name or None
        """
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Look for "Father" or "Father's Name" keywords
            if 'father' in line_lower:
                if ':' in line:
                    name = line.split(':', 1)[1].strip()
                    name = self._clean_name(name)
                    if name:
                        return name
                elif i + 1 < len(lines):
                    name = lines[i + 1].strip()
                    name = self._clean_name(name)
                    if name:
                        return name
        
        return None
    
    def extract_dob(self, text):
        """Extract date of birth
        
        Args:
            text: OCR extracted text
            
        Returns:
            Date of birth string or None
        """
        # Pattern: DD/MM/YYYY or DD-MM-YYYY
        pattern = r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b'
        matches = re.findall(pattern, text)
        
        if matches:
            return matches[0]
        
        # Also look for DOB: or Birth keywords
        lines = text.split('\n')
        for line in lines:
            if 'birth' in line.lower() or 'dob' in line.lower():
                match = re.search(pattern, line)
                if match:
                    return match.group(1)
        
        return None
    
    def process_document(self, image_path):
        """Main processing method for PAN card
        
        Args:
            image_path: Path to the PAN card image
            
        Returns:
            Dictionary with extracted data and confidence score
        """
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            if processed_img is None:
                return {
                    'success': False,
                    'error': 'Failed to preprocess image',
                    'confidence': 0.0
                }
            
            # Perform OCR with English and get confidence in one call
            custom_config = r'--oem 3 --psm 6'
            details = pytesseract.image_to_data(processed_img, lang='eng', config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Extract text from details
            text = ' '.join([str(word) for word in details['text'] if word]).strip()
            
            # Check if we got any text
            if not text or len(text) < 10:
                logger.warning(f"OCR extracted very little or no text: '{text[:50]}'")
                return {
                    'success': False,
                    'error': 'OCR extracted no readable text. Please ensure the image is clear, well-lit, and contains visible text.',
                    'raw_text': text,
                    'confidence': 0.0
                }
            
            # Get confidence score
            confidences = [int(conf) for conf in details['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.info(f"PAN OCR extracted text length: {len(text)}, confidence: {avg_confidence:.2f}")
            
            # Extract information
            pan_number = self.extract_pan_number(text)
            name = self.extract_name(text)
            father_name = self.extract_father_name(text)
            dob = self.extract_dob(text)
            
            return {
                'success': True,
                'pan_number': pan_number,
                'name': name,
                'father_name': father_name,
                'dob': dob,
                'raw_text': text,
                'confidence': round(avg_confidence, 2)
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"PAN OCR error: {error_msg}")
            # Check if it's a Tesseract error
            if 'tesseract' in error_msg.lower() or 'TesseractNotFoundError' in str(type(e)):
                error_msg = "Tesseract OCR not found. Please install Tesseract OCR and ensure it's in your PATH."
            return {
                'success': False,
                'error': error_msg,
                'confidence': 0.0
            }
