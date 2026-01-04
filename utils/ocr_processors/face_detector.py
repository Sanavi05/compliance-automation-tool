import cv2
import face_recognition
import numpy as np
import logging
from PIL import Image

# Configure logging
logger = logging.getLogger(__name__)


class FaceDetector:
    """Face detection and matching using OpenCV and face_recognition library"""
    
    def __init__(self):
        """Initialize FaceDetector"""
        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_face_opencv(self, image_path):
        """Detect faces using Haar Cascade
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with detection results
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return {
                    'success': False,
                    'error': 'Could not read image',
                    'faces_detected': 0
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return {
                'success': True,
                'faces_detected': len(faces),
                'face_locations': faces.tolist() if len(faces) > 0 else []
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'faces_detected': 0
            }
    
    def extract_face_encoding(self, image_path):
        """Extract face encoding using face_recognition library
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Face encoding array or None
        """
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) == 0:
                return None
            
            # Return the first face encoding
            return face_encodings[0]
            
        except Exception as e:
            logger.error(f"Error extracting face encoding: {e}")
            return None
    
    def compare_faces(self, image1_path, image2_path, tolerance=0.6):
        """Compare two face images and return match result with confidence
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            tolerance: How much distance between faces to consider a match (default 0.6)
            
        Returns:
            Dictionary with comparison results
        """
        try:
            # Extract face encodings
            encoding1 = self.extract_face_encoding(image1_path)
            encoding2 = self.extract_face_encoding(image2_path)
            
            if encoding1 is None:
                return {
                    'success': False,
                    'error': 'No face detected in first image',
                    'match': False,
                    'confidence': 0.0
                }
            
            if encoding2 is None:
                return {
                    'success': False,
                    'error': 'No face detected in second image',
                    'match': False,
                    'confidence': 0.0
                }
            
            # Compare faces
            matches = face_recognition.compare_faces([encoding1], encoding2, tolerance=tolerance)
            face_distance = face_recognition.face_distance([encoding1], encoding2)[0]
            
            # Calculate confidence score (inverse of distance, normalized to 0-100)
            # Lower distance = higher confidence
            confidence = max(0, (1 - face_distance) * 100)
            
            return {
                'success': True,
                'match': bool(matches[0]),
                'confidence': round(confidence, 2),
                'distance': round(float(face_distance), 4)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'match': False,
                'confidence': 0.0
            }
