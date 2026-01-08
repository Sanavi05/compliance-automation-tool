import cv2
import pytesseract
import re
import numpy as np
import logging
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)


class AadhaarOCR:
    """OCR processor for Aadhaar card documents"""
    
    def __init__(self, tesseract_path=None):
        """Initialize AadhaarOCR processor
        
        Args:
            tesseract_path: Path to tesseract executable (optional)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def preprocess_image(self, image_path):
        """Enhance image quality using OpenCV
        
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
    
    def extract_aadhaar_number(self, text):
        """Extract 12-digit Aadhaar number using regex
        
        Args:
            text: OCR extracted text
            
        Returns:
            Aadhaar number or None
        """
        # Clean text - remove common OCR errors
        text = text.replace('O', '0').replace('o', '0').replace('I', '1').replace('l', '1')
        
        # Pattern: 12 digits with optional spaces/dashes (4-4-4 format)
        # Try multiple patterns
        patterns = [
            r'\b\d{4}\s?[-]?\s?\d{4}\s?[-]?\s?\d{4}\b',  # With spaces/dashes
            r'\b\d{12}\b',  # 12 consecutive digits
            r'\d{4}\s+\d{4}\s+\d{4}',  # Space-separated
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Remove spaces and dashes, keep only digits
                aadhaar = re.sub(r'[^\d]', '', matches[0])
                if len(aadhaar) == 12 and aadhaar.isdigit():
                    return aadhaar
        
        # Fallback: find any sequence of 12 digits
        digits_only = re.sub(r'[^\d]', '', text)
        if len(digits_only) >= 12:
            # Try to find valid 12-digit sequences
            for i in range(len(digits_only) - 11):
                candidate = digits_only[i:i+12]
                if candidate.isdigit():
                    return candidate
        
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
        
        # Remove common OCR artifacts
        name = re.sub(r'[^\w\s]', ' ', name)  # Keep only alphanumeric and spaces
        name = re.sub(r'\s+', ' ', name)  # Normalize spaces
        name = name.strip()
        
        # Remove common OCR mistakes in names
        replacements = {
            '0': 'O',  # Zero to O in names
            '1': 'I',  # One to I in names
            '5': 'S',  # Sometimes 5 is read as S
        }
        
        # Only replace if it makes sense (not in the middle of words that could be numbers)
        cleaned = []
        for char in name:
            if char in replacements and (not cleaned or cleaned[-1].isalpha()):
                cleaned.append(replacements[char])
            else:
                cleaned.append(char)
        
        name = ''.join(cleaned)
        
        # Final cleanup
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Must have at least 3 letters
        if sum(1 for c in name if c.isalpha()) < 3:
            return None
        
        return name if len(name) > 2 else None
    
    def extract_name(self, text):
        """Extract name from OCR text
        
        Args:
            text: OCR extracted text
            
        Returns:
            Extracted name or None
        """
        # Clean text - normalize spaces and remove special characters that OCR might misread
        text = re.sub(r'[^\w\s]', ' ', text)  # Replace special chars with space
        text = re.sub(r'\s+', ' ', text)  # Normalize multiple spaces
        
        lines = text.split('\n')
        
        # Look for lines that might contain name
        # Usually appears after "Name" or similar keywords
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if 'name' in line_lower or 'naam' in line_lower or 'नाम' in line:
                # Name might be on same line or next line
                if ':' in line:
                    name = line.split(':', 1)[1].strip()
                    name = self._clean_name(name)
                    if name and len(name) > 2:
                        return name
                elif i + 1 < len(lines):
                    name = lines[i + 1].strip()
                    name = self._clean_name(name)
                    if name and len(name) > 2:
                        return name
        
        # Fallback: look for lines with mostly letters
        for line in lines:
            line = line.strip()
            if len(line) > 3 and sum(c.isalpha() or c.isspace() for c in line) / len(line) > 0.7:
                # Skip if it contains keywords
                if not any(keyword in line.lower() for keyword in ['aadhaar', 'government', 'india', 'dob', 'male', 'female']):
                    return line
        
        return None
    
    def extract_dob(self, text):
        """Extract date of birth using regex pattern
        
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
    
    def extract_gender(self, text):
        """Extract gender (Male/Female)
        
        Args:
            text: OCR extracted text
            
        Returns:
            Gender string or None
        """
        text_lower = text.lower()
        
        if 'male' in text_lower:
            if 'female' in text_lower:
                # Both present, check which comes first in context
                male_idx = text_lower.find('male')
                female_idx = text_lower.find('female')
                if female_idx < male_idx:
                    return 'Female'
                else:
                    # Check if it's actually 'female' not 'male'
                    if text_lower[female_idx:female_idx+6] == 'female':
                        return 'Female'
                    return 'Male'
            else:
                return 'Male'
        elif 'female' in text_lower:
            return 'Female'
        
        return None
    
    def process_document(self, image_path):
        """Main processing method for Aadhaar card
        
        Args:
            image_path: Path to the Aadhaar card image
            
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
            
            # Perform OCR with English and Hindi and get confidence in one call
            # Try eng+hin first, fallback to eng if Hindi not available
            custom_config = r'--oem 3 --psm 6'
            try:
                details = pytesseract.image_to_data(processed_img, lang='eng+hin', config=custom_config, output_type=pytesseract.Output.DICT)
            except Exception as lang_error:
                logger.warning(f"eng+hin language failed, trying eng only: {lang_error}")
                # Fallback to English only
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
            
            logger.info(f"Aadhaar OCR extracted text length: {len(text)}, confidence: {avg_confidence:.2f}")
            
            # Extract information
            aadhaar_number = self.extract_aadhaar_number(text)
            name = self.extract_name(text)
            dob = self.extract_dob(text)
            gender = self.extract_gender(text)
            
            return {
                'success': True,
                'aadhaar_number': aadhaar_number,
                'name': name,
                'dob': dob,
                'gender': gender,
                'raw_text': text,
                'confidence': round(avg_confidence, 2)
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Aadhaar OCR error: {error_msg}")
            # Check if it's a Tesseract error
            if 'tesseract' in error_msg.lower() or 'TesseractNotFoundError' in str(type(e)):
                error_msg = "Tesseract OCR not found. Please install Tesseract OCR and ensure it's in your PATH."
            return {
                'success': False,
                'error': error_msg,
                'confidence': 0.0
            }
