import re
from datetime import datetime


class PANValidator:
    """Validator for PAN card data"""
    
    def validate_pan_format(self, pan_number):
        """Check format [A-Z]{5}[0-9]{4}[A-Z]
        
        Args:
            pan_number: PAN number string
            
        Returns:
            Boolean indicating if format is valid
        """
        if not pan_number:
            return False
        
        pan = str(pan_number).upper().strip()
        
        # Check format: 5 letters, 4 digits, 1 letter
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        return bool(re.match(pattern, pan))
    
    def validate_pan_structure(self, pan_number):
        """Validate 4th character holder type
        
        The 4th character represents the holder type:
        - P: Individual
        - C: Company
        - H: HUF (Hindu Undivided Family)
        - F: Firm
        - A: Association of Persons (AOP)
        - T: Trust
        - B: Body of Individuals (BOI)
        - L: Local Authority
        - J: Artificial Juridical Person
        - G: Government
        
        Args:
            pan_number: PAN number string
            
        Returns:
            Dictionary with validation result and holder type
        """
        if not self.validate_pan_format(pan_number):
            return {'valid': False, 'error': 'Invalid PAN format'}
        
        pan = str(pan_number).upper().strip()
        
        # Get 4th character (index 3)
        holder_char = pan[3]
        
        # Valid holder types
        holder_types = {
            'P': 'Individual',
            'C': 'Company',
            'H': 'HUF',
            'F': 'Firm',
            'A': 'AOP',
            'T': 'Trust',
            'B': 'BOI',
            'L': 'Local Authority',
            'J': 'Artificial Juridical Person',
            'G': 'Government'
        }
        
        if holder_char in holder_types:
            return {
                'valid': True,
                'holder_type': holder_types[holder_char],
                'holder_code': holder_char
            }
        else:
            return {
                'valid': False,
                'error': f'Invalid holder type character: {holder_char}'
            }
    
    def validate_name(self, name):
        """Validate name format
        
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
        """Validate age (18-120 years for PAN)
        
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
            
            # Check if age is reasonable for PAN (18-120 years)
            if age < 18:
                return {'valid': False, 'error': 'Age must be at least 18 years for PAN'}
            
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
        
        total_fields = 4  # PAN number, name, father_name, dob
        valid_fields = 0
        
        # Validate PAN number
        pan_number = extracted_data.get('pan_number')
        if pan_number:
            format_valid = self.validate_pan_format(pan_number)
            structure = self.validate_pan_structure(pan_number)
            
            if format_valid and structure['valid']:
                valid_fields += 1
                validation_results['field_validations']['pan_number'] = {
                    'valid': True,
                    'holder_type': structure.get('holder_type')
                }
            else:
                validation_results['errors'].append('Invalid PAN number format or structure')
                validation_results['field_validations']['pan_number'] = {
                    'valid': False,
                    'error': structure.get('error', 'Invalid format')
                }
        else:
            validation_results['errors'].append('PAN number not found')
            validation_results['field_validations']['pan_number'] = {'valid': False, 'error': 'Not found'}
        
        # Validate name
        name = extracted_data.get('name')
        name_validation = self.validate_name(name)
        validation_results['field_validations']['name'] = name_validation
        if name_validation['valid']:
            valid_fields += 1
        else:
            validation_results['errors'].append(f"Name validation failed: {name_validation.get('error', 'Unknown error')}")
        
        # Validate father's name (optional but adds to score if present)
        father_name = extracted_data.get('father_name')
        if father_name:
            father_name_validation = self.validate_name(father_name)
            validation_results['field_validations']['father_name'] = father_name_validation
            if father_name_validation['valid']:
                valid_fields += 1
            else:
                validation_results['errors'].append(f"Father's name validation failed: {father_name_validation.get('error', 'Unknown error')}")
        else:
            validation_results['field_validations']['father_name'] = {'valid': False, 'error': 'Not found'}
        
        # Validate DOB
        dob = extracted_data.get('dob')
        if dob:
            dob_validation = self.validate_dob(dob)
            validation_results['field_validations']['dob'] = dob_validation
            if dob_validation['valid']:
                valid_fields += 1
            else:
                validation_results['errors'].append(f"DOB validation failed: {dob_validation.get('error', 'Unknown error')}")
        else:
            validation_results['field_validations']['dob'] = {'valid': False, 'error': 'Not found'}
        
        # Calculate score
        validation_results['score'] = (valid_fields / total_fields) * 100
        validation_results['valid'] = validation_results['score'] >= 75.0
        
        return validation_results
