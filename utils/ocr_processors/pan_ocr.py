import cv2
import pytesseract
import re
import numpy as np
from PIL import Image


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
            print(f"Error preprocessing image: {e}")
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
        # Pattern: 5 letters, 4 digits, 1 letter
        pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
        matches = re.findall(pattern, text.upper())
        
        if matches:
            return matches[0]
        
        return None
    
    def extract_name(self, text):
        """Extract name in capital letters
        
        Args:
            text: OCR extracted text
            
        Returns:
            Extracted name or None
        """
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
                    if name and len(name) > 2:
                        return name
                elif i + 1 < len(lines):
                    name = lines[i + 1].strip()
                    if name and len(name) > 2:
                        return name
        
        # Fallback: look for lines with mostly uppercase letters
        for line in lines:
            line = line.strip()
            # Check if line has mostly uppercase letters
            if len(line) > 5:
                upper_count = sum(1 for c in line if c.isupper())
                if upper_count / len(line) > 0.6:
                    # Skip if it contains common keywords
                    if not any(keyword in line.upper() for keyword in ['INCOME', 'TAX', 'INDIA', 'GOVERNMENT', 'PERMANENT', 'ACCOUNT', 'NUMBER']):
                        return line
        
        return None
    
    def extract_father_name(self, text):
        """Extract father's name
        
        Args:
            text: OCR extracted text
            
        Returns:
            Father's name or None
        """
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Look for "Father" or "Father's Name" keywords
            if 'father' in line_lower:
                if ':' in line:
                    name = line.split(':', 1)[1].strip()
                    if name and len(name) > 2:
                        return name
                elif i + 1 < len(lines):
                    name = lines[i + 1].strip()
                    if name and len(name) > 2:
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
            
            # Perform OCR with English
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(processed_img, lang='eng', config=custom_config)
            
            # Get confidence score
            details = pytesseract.image_to_data(processed_img, lang='eng', output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in details['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
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
            return {
                'success': False,
                'error': str(e),
                'confidence': 0.0
            }
