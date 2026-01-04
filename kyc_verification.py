from sqlalchemy import Column, String, Boolean, Integer, Float, Text, JSON, DateTime, ForeignKey
from database import Base
from datetime import datetime


class KYCVerification(Base):
    __tablename__ = "kyc_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), unique=True, nullable=False)
    kyc_status = Column(String, default='not_started')  # not_started, in_progress, completed, rejected
    kyc_level = Column(String, default='none')  # none, basic, full
    photo_verified = Column(Boolean, default=False)
    aadhaar_verified = Column(Boolean, default=False)
    pan_verified = Column(Boolean, default=False)
    face_match_score = Column(Float, nullable=True)
    face_match_verified = Column(Boolean, default=False)
    cross_validation_result = Column(JSON, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, default='low')  # low, medium, high
    requires_manual_review = Column(Boolean, default=False)
    reviewed_by = Column(String, ForeignKey("users.user_id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'kyc_status': self.kyc_status,
            'kyc_level': self.kyc_level,
            'photo_verified': self.photo_verified,
            'aadhaar_verified': self.aadhaar_verified,
            'pan_verified': self.pan_verified,
            'face_match_score': self.face_match_score,
            'face_match_verified': self.face_match_verified,
            'cross_validation_result': self.cross_validation_result,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'requires_manual_review': self.requires_manual_review,
            'reviewed_by': self.reviewed_by,
            'review_notes': self.review_notes,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
