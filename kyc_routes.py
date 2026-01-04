import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from database import get_db
from auth import get_current_user
from kyc_service import KYCService
from kyc_document import KYCDocument

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
KYC_UPLOAD_FOLDER = 'uploads/kyc'
KYC_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
KYC_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Initialize router
kyc_bp = APIRouter(prefix="/api/kyc", tags=["KYC"])

# Initialize KYC service
kyc_service = KYCService()


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed
    
    Args:
        filename: Name of the file
        
    Returns:
        Boolean indicating if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in KYC_ALLOWED_EXTENSIONS


@kyc_bp.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Upload KYC document
    
    Args:
        file: Uploaded file
        document_type: Type of document ('photo', 'aadhaar', 'pan')
        db: Database session
        current_user: Current user ID from JWT
        
    Returns:
        Processing result
    """
    try:
        # Validate document type
        if document_type not in ['photo', 'aadhaar', 'pan']:
            raise HTTPException(
                status_code=400,
                detail="Invalid document type. Must be 'photo', 'aadhaar', or 'pan'"
            )
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(KYC_ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check file size
        if file_size > KYC_MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {KYC_MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Create user directory
        user_folder = os.path.join(KYC_UPLOAD_FOLDER, current_user)
        os.makedirs(user_folder, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = secure_filename(file.filename)
        filename = f"{document_type}_{timestamp}_{safe_filename}"
        file_path = os.path.join(user_folder, filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Process document
        result = kyc_service.process_document(
            db=db,
            user_id=current_user,
            document_type=document_type,
            file_path=file_path,
            file_name=filename,
            file_size=file_size,
            mime_type=file.content_type or 'application/octet-stream'
        )
        
        if result['success']:
            return {
                "message": "Document uploaded and processed successfully",
                "document": result['document']
            }
        else:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=result.get('message', 'Processing failed'))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@kyc_bp.get("/status")
def get_kyc_status(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get KYC verification status
    
    Args:
        db: Database session
        current_user: Current user ID from JWT
        
    Returns:
        Complete KYC status
    """
    try:
        result = kyc_service.get_kyc_status(db, current_user)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Failed to get KYC status'))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting KYC status: {str(e)}")


@kyc_bp.get("/documents")
def get_kyc_documents(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get all KYC documents for current user
    
    Args:
        db: Database session
        current_user: Current user ID from JWT
        
    Returns:
        List of documents
    """
    try:
        documents = db.query(KYCDocument).filter(
            KYCDocument.user_id == current_user
        ).order_by(KYCDocument.uploaded_at.desc()).all()
        
        return {
            "success": True,
            "documents": [doc.to_dict() for doc in documents]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")


@kyc_bp.post("/verify")
def trigger_verification(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Manually trigger full verification
    
    Args:
        db: Database session
        current_user: Current user ID from JWT
        
    Returns:
        Verification result
    """
    try:
        # Check if all documents are uploaded
        photo = db.query(KYCDocument).filter(
            KYCDocument.user_id == current_user,
            KYCDocument.document_type == 'photo',
            KYCDocument.is_verified == True
        ).first()
        
        aadhaar = db.query(KYCDocument).filter(
            KYCDocument.user_id == current_user,
            KYCDocument.document_type == 'aadhaar',
            KYCDocument.is_verified == True
        ).first()
        
        pan = db.query(KYCDocument).filter(
            KYCDocument.user_id == current_user,
            KYCDocument.document_type == 'pan',
            KYCDocument.is_verified == True
        ).first()
        
        if not all([photo, aadhaar, pan]):
            raise HTTPException(
                status_code=400,
                detail="All documents (photo, Aadhaar, PAN) must be uploaded and verified"
            )
        
        # Trigger verification
        kyc_service.update_kyc_verification_status(db, current_user, 'photo', True)
        
        # Get updated status
        result = kyc_service.get_kyc_status(db, current_user)
        
        return {
            "message": "Verification process completed",
            "status": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering verification: {str(e)}")


@kyc_bp.post("/resubmit/{document_id}")
async def resubmit_document(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Resubmit rejected document
    
    Args:
        document_id: ID of document to resubmit
        file: New file to upload
        db: Database session
        current_user: Current user ID from JWT
        
    Returns:
        Processing result
    """
    try:
        # Get existing document
        existing_doc = db.query(KYCDocument).filter(
            KYCDocument.id == document_id,
            KYCDocument.user_id == current_user
        ).first()
        
        if not existing_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document_type = existing_doc.document_type
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(KYC_ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check file size
        if file_size > KYC_MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {KYC_MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Create user directory
        user_folder = os.path.join(KYC_UPLOAD_FOLDER, current_user)
        os.makedirs(user_folder, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = secure_filename(file.filename)
        filename = f"{document_type}_{timestamp}_{safe_filename}"
        file_path = os.path.join(user_folder, filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Delete old file
        if os.path.exists(existing_doc.file_path):
            try:
                os.remove(existing_doc.file_path)
            except OSError as e:
                logger.warning(f"Could not delete old file: {e}")
        
        # Delete old document record
        db.delete(existing_doc)
        db.commit()
        
        # Process new document
        result = kyc_service.process_document(
            db=db,
            user_id=current_user,
            document_type=document_type,
            file_path=file_path,
            file_name=filename,
            file_size=file_size,
            mime_type=file.content_type or 'application/octet-stream'
        )
        
        if result['success']:
            return {
                "message": "Document resubmitted and processed successfully",
                "document": result['document']
            }
        else:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=result.get('message', 'Processing failed'))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resubmitting document: {str(e)}")
