from sqlalchemy import Column, String, Boolean, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    document_type = Column(String, nullable=False)  # 'photo', 'aadhaar', 'pan'
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    extracted_data = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_status = Column(String, default='pending')  # pending, verified, rejected, under_review
    verification_notes = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    validation_score = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="kyc_documents")

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document_type': self.document_type,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'extracted_data': self.extracted_data,
            'is_verified': self.is_verified,
            'verification_status': self.verification_status,
            'verification_notes': self.verification_notes,
            'ocr_confidence': self.ocr_confidence,
            'validation_score': self.validation_score,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }
