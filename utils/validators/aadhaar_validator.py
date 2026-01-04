import re
from datetime import datetime


class AadhaarValidator:
    """Validator for Aadhaar card data with Verhoeff algorithm"""
    
    # Verhoeff algorithm multiplication table
    MULTIPLICATION_TABLE = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    
    # Verhoeff algorithm permutation table
    PERMUTATION_TABLE = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    
    def validate_aadhaar_format(self, aadhaar_number):
        """Check 12-digit format
        
        Args:
            aadhaar_number: Aadhaar number string
            
        Returns:
            Boolean indicating if format is valid
        """
        if not aadhaar_number:
            return False
        
        # Remove spaces
        aadhaar = str(aadhaar_number).replace(' ', '')
        
        # Check if it's exactly 12 digits
        if len(aadhaar) != 12:
            return False
        
        # Check if all characters are digits
        if not aadhaar.isdigit():
            return False
        
        return True
    
    def validate_aadhaar_checksum(self, aadhaar_number):
        """Implement Verhoeff algorithm for checksum validation
        
        Args:
            aadhaar_number: Aadhaar number string
            
        Returns:
            Boolean indicating if checksum is valid
        """
        if not self.validate_aadhaar_format(aadhaar_number):
            return False
        
        # Remove spaces
        aadhaar = str(aadhaar_number).replace(' ', '')
        
        try:
            # Verhoeff algorithm
            c = 0
            for i, digit in enumerate(reversed(aadhaar)):
                c = self.MULTIPLICATION_TABLE[c][self.PERMUTATION_TABLE[(i + 1) % 8][int(digit)]]
            
            return c == 0
        except (IndexError, ValueError):
            return False
    
    def validate_name(self, name):
        """Validate name (min 3 chars, only letters and spaces)
        
        Args:
            name: Name string
            
        Returns:
            Dictionary with validation result
        """
        if not name:
            return {'valid': False, 'error': 'Name is required'}
        
        name = name.strip()
        
        if len(name) < 3:
            return {'valid': False, 'error': 'Name must be at least 3 characters'}
        
        # Check if name contains only letters and spaces
        if not re.match(r'^[a-zA-Z\s]+$', name):
            return {'valid': False, 'error': 'Name must contain only letters and spaces'}
        
        return {'valid': True}
    
    def validate_dob(self, dob_string):
        """Validate date format and reasonable age (0-120 years)
        
        Args:
            dob_string: Date of birth string (DD/MM/YYYY or DD-MM-YYYY)
            
        Returns:
            Dictionary with validation result
        """
        if not dob_string:
            return {'valid': False, 'error': 'Date of birth is required'}
        
        try:
            # Try parsing with different formats
            dob = None
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']:
                try:
                    dob = datetime.strptime(dob_string, fmt)
                    break
                except ValueError:
                    continue
            
            if dob is None:
                return {'valid': False, 'error': 'Invalid date format. Use DD/MM/YYYY or DD-MM-YYYY'}
            
            # Calculate age
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Check if age is reasonable (0-120 years)
            if age < 0:
                return {'valid': False, 'error': 'Date of birth cannot be in the future'}
            
            if age > 120:
                return {'valid': False, 'error': 'Age cannot be more than 120 years'}
            
            return {'valid': True, 'age': age}
            
        except Exception as e:
            return {'valid': False, 'error': f'Error validating date: {str(e)}'}
    
    def validate_complete_document(self, extracted_data):
        """Validate all fields and return validation score
        
        Args:
            extracted_data: Dictionary with extracted data
            
        Returns:
            Dictionary with validation results and score
        """
        validation_results = {
            'valid': True,
            'score': 0.0,
            'errors': [],
            'field_validations': {}
        }
        
        total_fields = 4
        valid_fields = 0
        
        # Validate Aadhaar number
        aadhaar_number = extracted_data.get('aadhaar_number')
        if aadhaar_number:
            format_valid = self.validate_aadhaar_format(aadhaar_number)
            checksum_valid = self.validate_aadhaar_checksum(aadhaar_number)
            
            if format_valid and checksum_valid:
                valid_fields += 1
                validation_results['field_validations']['aadhaar_number'] = {'valid': True}
            else:
                validation_results['errors'].append('Invalid Aadhaar number format or checksum')
                validation_results['field_validations']['aadhaar_number'] = {
                    'valid': False,
                    'error': 'Invalid format or checksum'
                }
        else:
            validation_results['errors'].append('Aadhaar number not found')
            validation_results['field_validations']['aadhaar_number'] = {'valid': False, 'error': 'Not found'}
        
        # Validate name
        name = extracted_data.get('name')
        name_validation = self.validate_name(name)
        validation_results['field_validations']['name'] = name_validation
        if name_validation['valid']:
            valid_fields += 1
        else:
            validation_results['errors'].append(f"Name validation failed: {name_validation.get('error', 'Unknown error')}")
        
        # Validate DOB
        dob = extracted_data.get('dob')
        dob_validation = self.validate_dob(dob)
        validation_results['field_validations']['dob'] = dob_validation
        if dob_validation['valid']:
            valid_fields += 1
        else:
            validation_results['errors'].append(f"DOB validation failed: {dob_validation.get('error', 'Unknown error')}")
        
        # Validate gender
        gender = extracted_data.get('gender')
        if gender and gender.lower() in ['male', 'female']:
            valid_fields += 1
            validation_results['field_validations']['gender'] = {'valid': True}
        else:
            validation_results['errors'].append('Gender not found or invalid')
            validation_results['field_validations']['gender'] = {'valid': False, 'error': 'Not found or invalid'}
        
        # Calculate score
        validation_results['score'] = (valid_fields / total_fields) * 100
        validation_results['valid'] = validation_results['score'] >= 75.0
        
        return validation_results
