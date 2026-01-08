import os
from datetime import datetime
from difflib import SequenceMatcher
import logging
from sqlalchemy.orm import Session

from kyc_document import KYCDocument
from kyc_verification import KYCVerification
from utils.ocr_processors.aadhaar_ocr import AadhaarOCR
from utils.ocr_processors.pan_ocr import PANOCR
from utils.ocr_processors.face_detector import FaceDetector
from utils.validators.aadhaar_validator import AadhaarValidator
from utils.validators.pan_validator import PANValidator
from utils.pdf_converter import pdf_to_image, is_pdf_file
from config import TESSERACT_PATH

# Configure logging
logger = logging.getLogger(__name__)


class KYCService:
    """Service class for KYC document processing and verification"""
    
    def __init__(self, tesseract_path=None):
        """Initialize KYC service with OCR processors and validators
        
        Args:
            tesseract_path: Path to tesseract executable (optional)
        """
        # Use provided path, or config path, or None (will use system PATH)
        tesseract = tesseract_path or (TESSERACT_PATH if os.path.exists(TESSERACT_PATH) else None)
        self.aadhaar_ocr = AadhaarOCR(tesseract)
        self.pan_ocr = PANOCR(tesseract)
        self.face_detector = FaceDetector()
        self.aadhaar_validator = AadhaarValidator()
        self.pan_validator = PANValidator()
    
    def process_document(self, db: Session, user_id: str, document_type: str, 
                        file_path: str, file_name: str, file_size: int, mime_type: str):
        """Process uploaded document based on type
        
        Args:
            db: Database session
            user_id: User ID
            document_type: Type of document ('photo', 'aadhaar', 'pan')
            file_path: Path to uploaded file
            file_name: Original filename
            file_size: File size in bytes
            mime_type: MIME type of file
            
        Returns:
            Dictionary with processing result
        """
        try:
            # Extract data based on document type
            extracted_data = None
            ocr_confidence = 0.0
            validation_score = 0.0
            is_verified = False
            verification_status = 'pending'
            verification_notes = ''
            
            if document_type == 'photo':
                # For photo, just check if face is detected
                face_result = self.face_detector.detect_face_opencv(file_path)
                if face_result['success'] and face_result['faces_detected'] > 0:
                    extracted_data = {'faces_detected': face_result['faces_detected']}
                    is_verified = True
                    verification_status = 'verified'
                    validation_score = 100.0
                    ocr_confidence = 100.0
                else:
                    extracted_data = {'error': face_result.get('error', 'No face detected')}
                    verification_status = 'rejected'
                    verification_notes = 'No face detected in photo'
            
            elif document_type == 'aadhaar':
                # Process Aadhaar card
                # Convert PDF to image if needed
                actual_file_path = file_path
                temp_image_path = None
                ocr_result = None
                
                if is_pdf_file(file_path):
                    logger.info("Converting PDF to image for OCR")
                    temp_image_path = pdf_to_image(file_path)
                    if temp_image_path:
                        actual_file_path = temp_image_path
                    else:
                        verification_status = 'rejected'
                        verification_notes = 'Failed to convert PDF to image. Please upload an image file (JPG/PNG) instead.'
                        extracted_data = {'error': 'PDF conversion failed'}
                        ocr_result = {'success': False}
                
                # Process OCR if we haven't already failed
                if ocr_result is None:
                    ocr_result = self.aadhaar_ocr.process_document(actual_file_path)
                
                if ocr_result.get('success'):
                    extracted_data = {
                        'aadhaar_number': ocr_result.get('aadhaar_number'),
                        'name': ocr_result.get('name'),
                        'dob': ocr_result.get('dob'),
                        'gender': ocr_result.get('gender')
                    }
                    ocr_confidence = ocr_result.get('confidence', 0.0)
                    
                    # Validate extracted data
                    validation_result = self.aadhaar_validator.validate_complete_document(extracted_data)
                    validation_score = validation_result['score']
                    
                    if validation_result['valid']:
                        is_verified = True
                        verification_status = 'verified'
                    else:
                        verification_status = 'under_review'
                        verification_notes = '; '.join(validation_result['errors'])
                elif ocr_result is None:
                    # OCR was never called (e.g., PDF conversion failed)
                    verification_status = 'rejected'
                    verification_notes = 'Document processing failed. Please try uploading a clear image file (JPG/PNG).'
                    extracted_data = {'error': 'Processing failed'}
                else:
                    # OCR failed or returned no data
                    error_msg = ocr_result.get('error', 'OCR processing failed')
                    # Include raw text if available for debugging
                    raw_text = ocr_result.get('raw_text', '')
                    if raw_text:
                        logger.info(f"Aadhaar OCR extracted text (but validation failed): {raw_text[:200]}")
                    extracted_data = {'error': error_msg, 'raw_text': raw_text}
                    verification_status = 'rejected'
                    verification_notes = f'OCR failed: {error_msg}. Please ensure the image is clear and readable.'
                    logger.error(f"Aadhaar OCR failed: {error_msg}. Full result: {ocr_result}")
                
                # Clean up temporary image file
                if temp_image_path and os.path.exists(temp_image_path):
                    try:
                        os.remove(temp_image_path)
                    except Exception as e:
                        logger.warning(f"Could not delete temp image: {e}")
            
            elif document_type == 'pan':
                # Process PAN card
                # Convert PDF to image if needed
                actual_file_path = file_path
                temp_image_path = None
                ocr_result = None
                
                if is_pdf_file(file_path):
                    logger.info("Converting PDF to image for OCR")
                    temp_image_path = pdf_to_image(file_path)
                    if temp_image_path:
                        actual_file_path = temp_image_path
                    else:
                        verification_status = 'rejected'
                        verification_notes = 'Failed to convert PDF to image. Please upload an image file (JPG/PNG) instead.'
                        extracted_data = {'error': 'PDF conversion failed'}
                        ocr_result = {'success': False}
                
                # Process OCR if we haven't already failed
                if ocr_result is None:
                    ocr_result = self.pan_ocr.process_document(actual_file_path)
                
                if ocr_result and ocr_result.get('success'):
                    extracted_data = {
                        'pan_number': ocr_result.get('pan_number'),
                        'name': ocr_result.get('name'),
                        'father_name': ocr_result.get('father_name'),
                        'dob': ocr_result.get('dob'),
                        'raw_text': ocr_result.get('raw_text', '')
                    }
                    ocr_confidence = ocr_result.get('confidence', 0.0)
                    
                    # Check if we extracted any meaningful data
                    if not any([extracted_data.get('pan_number'), extracted_data.get('name'), extracted_data.get('dob')]):
                        verification_status = 'rejected'
                        verification_notes = 'OCR completed but could not extract required fields (PAN number, name, or DOB). Please ensure the document is clear and all text is visible.'
                        logger.warning(f"PAN OCR succeeded but extracted no data. Raw text: {extracted_data.get('raw_text', '')[:200]}")
                    else:
                        # Validate extracted data
                        validation_result = self.pan_validator.validate_complete_document(extracted_data)
                        validation_score = validation_result['score']
                        
                        if validation_result['valid']:
                            is_verified = True
                            verification_status = 'verified'
                        else:
                            verification_status = 'under_review'
                            verification_notes = '; '.join(validation_result['errors'])
                else:
                    error_msg = ocr_result.get('error', 'OCR processing failed')
                    # Include raw text if available for debugging
                    raw_text = ocr_result.get('raw_text', '')
                    if raw_text:
                        logger.info(f"PAN OCR extracted text (but validation failed): {raw_text[:200]}")
                    extracted_data = {'error': error_msg, 'raw_text': raw_text}
                    verification_status = 'rejected'
                    verification_notes = f'OCR failed: {error_msg}. Please ensure the image is clear and readable.'
                    logger.error(f"PAN OCR failed: {error_msg}. Full result: {ocr_result}")
                
                # Clean up temporary image file
                if temp_image_path and os.path.exists(temp_image_path):
                    try:
                        os.remove(temp_image_path)
                    except Exception as e:
                        logger.warning(f"Could not delete temp image: {e}")
            
            # Save to database
            kyc_document = KYCDocument(
                user_id=user_id,
                document_type=document_type,
                file_path=file_path,
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type,
                extracted_data=extracted_data,
                is_verified=is_verified,
                verification_status=verification_status,
                verification_notes=verification_notes,
                ocr_confidence=ocr_confidence,
                validation_score=validation_score,
                uploaded_at=datetime.utcnow()
            )
            
            if is_verified:
                kyc_document.verified_at = datetime.utcnow()
            
            db.add(kyc_document)
            db.commit()
            db.refresh(kyc_document)
            
            # Update KYC verification status
            self.update_kyc_verification_status(db, user_id, document_type, is_verified)
            
            return {
                'success': True,
                'document_id': kyc_document.id,
                'document': kyc_document.to_dict(),
                'message': 'Document processed successfully'
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process document'
            }
    
    def update_kyc_verification_status(self, db: Session, user_id: str, 
                                      document_type: str, is_verified: bool):
        """Create or update KYCVerification record
        
        Args:
            db: Database session
            user_id: User ID
            document_type: Type of document
            is_verified: Whether document is verified
        """
        try:
            # Get or create KYCVerification record
            kyc_verification = db.query(KYCVerification).filter(
                KYCVerification.user_id == user_id
            ).first()
            
            if not kyc_verification:
                kyc_verification = KYCVerification(
                    user_id=user_id,
                    kyc_status='in_progress',
                    started_at=datetime.utcnow()
                )
                db.add(kyc_verification)
            
            # Update document-specific verification flags
            if document_type == 'photo':
                kyc_verification.photo_verified = is_verified
            elif document_type == 'aadhaar':
                kyc_verification.aadhaar_verified = is_verified
            elif document_type == 'pan':
                kyc_verification.pan_verified = is_verified
            
            kyc_verification.updated_at = datetime.utcnow()
            
            # Check if all documents are uploaded and verified
            all_uploaded = (
                kyc_verification.photo_verified and 
                kyc_verification.aadhaar_verified and 
                kyc_verification.pan_verified
            )
            
            if all_uploaded:
                # Perform cross-validation
                cross_val_result = self.cross_validate_documents(db, user_id)
                kyc_verification.cross_validation_result = cross_val_result
                
                # Perform face matching
                face_match_result = self.verify_face_match(db, user_id)
                if face_match_result['success']:
                    kyc_verification.face_match_score = face_match_result.get('confidence', 0.0)
                    kyc_verification.face_match_verified = face_match_result.get('match', False)
                
                # Determine final KYC status
                if (cross_val_result.get('name_match', False) and 
                    cross_val_result.get('dob_match', False) and 
                    kyc_verification.face_match_verified):
                    kyc_verification.kyc_status = 'completed'
                    kyc_verification.kyc_level = 'full'
                    kyc_verification.completed_at = datetime.utcnow()
                else:
                    kyc_verification.kyc_status = 'in_progress'
                    kyc_verification.requires_manual_review = True
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating KYC verification status: {e}")
    
    def cross_validate_documents(self, db: Session, user_id: str):
        """Compare name and DOB across Aadhaar and PAN
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with validation result
        """
        try:
            # Get Aadhaar and PAN documents
            aadhaar_doc = db.query(KYCDocument).filter(
                KYCDocument.user_id == user_id,
                KYCDocument.document_type == 'aadhaar',
                KYCDocument.is_verified == True
            ).first()
            
            pan_doc = db.query(KYCDocument).filter(
                KYCDocument.user_id == user_id,
                KYCDocument.document_type == 'pan',
                KYCDocument.is_verified == True
            ).first()
            
            if not aadhaar_doc or not pan_doc:
                return {
                    'success': False,
                    'error': 'Both Aadhaar and PAN documents required',
                    'name_match': False,
                    'dob_match': False
                }
            
            aadhaar_data = aadhaar_doc.extracted_data or {}
            pan_data = pan_doc.extracted_data or {}
            
            # Compare names using SequenceMatcher
            aadhaar_name = (aadhaar_data.get('name') or '').lower().strip()
            pan_name = (pan_data.get('name') or '').lower().strip()
            
            name_similarity = 0.0
            if aadhaar_name and pan_name:
                name_similarity = SequenceMatcher(None, aadhaar_name, pan_name).ratio()
            
            name_match = name_similarity >= 0.8
            
            # Compare DOB
            aadhaar_dob = aadhaar_data.get('dob', '').replace('-', '/').strip()
            pan_dob = pan_data.get('dob', '').replace('-', '/').strip()
            
            dob_match = False
            if aadhaar_dob and pan_dob:
                dob_match = aadhaar_dob == pan_dob
            
            return {
                'success': True,
                'name_match': name_match,
                'name_similarity': round(name_similarity * 100, 2),
                'aadhaar_name': aadhaar_data.get('name'),
                'pan_name': pan_data.get('name'),
                'dob_match': dob_match,
                'aadhaar_dob': aadhaar_dob,
                'pan_dob': pan_dob
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'name_match': False,
                'dob_match': False
            }
    
    def verify_face_match(self, db: Session, user_id: str):
        """Compare uploaded photo with Aadhaar photo
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with match result
        """
        try:
            # Get photo and Aadhaar documents
            photo_doc = db.query(KYCDocument).filter(
                KYCDocument.user_id == user_id,
                KYCDocument.document_type == 'photo',
                KYCDocument.is_verified == True
            ).first()
            
            aadhaar_doc = db.query(KYCDocument).filter(
                KYCDocument.user_id == user_id,
                KYCDocument.document_type == 'aadhaar',
                KYCDocument.is_verified == True
            ).first()
            
            if not photo_doc or not aadhaar_doc:
                return {
                    'success': False,
                    'error': 'Both photo and Aadhaar documents required',
                    'match': False
                }
            
            # Compare faces
            result = self.face_detector.compare_faces(
                photo_doc.file_path,
                aadhaar_doc.file_path,
                tolerance=0.6
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'match': False
            }
    
    def get_kyc_status(self, db: Session, user_id: str):
        """Return complete KYC status with all documents
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with KYC status
        """
        try:
            # Get KYC verification record
            kyc_verification = db.query(KYCVerification).filter(
                KYCVerification.user_id == user_id
            ).first()
            
            # Get all documents
            documents = db.query(KYCDocument).filter(
                KYCDocument.user_id == user_id
            ).order_by(KYCDocument.uploaded_at.desc()).all()
            
            return {
                'success': True,
                'verification': kyc_verification.to_dict() if kyc_verification else None,
                'documents': [doc.to_dict() for doc in documents]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
