import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MotionDetector:
    """Simple motion detection to skip static frames"""
    
    def __init__(self, threshold: float = 0.1):
        """
        Initialize motion detector
        
        Args:
            threshold: Motion threshold (0-1 scale)
        """
        self.threshold = threshold
        self.prev_frame = None
    
    def detect_motion(self, frame: np.ndarray) -> bool:
        """
        Detect if frame has significant motion
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            True if motion detected, False otherwise
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.prev_frame is None:
                self.prev_frame = gray
                return True
            
            # Compute absolute difference
            diff = cv2.absdiff(self.prev_frame, gray)
            
            # Threshold the difference
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            # Calculate motion percentage
            motion_pixels = np.sum(thresh) / (thresh.shape[0] * thresh.shape[1] * 255)
            
            self.prev_frame = gray
            
            has_motion = motion_pixels > self.threshold
            if has_motion:
                logger.debug(f"[MOTION] Detected motion: {motion_pixels:.2%}")
            
            return has_motion
            
        except Exception as e:
            logger.error(f"[MOTION] Error detecting motion: {e}")
            return True  # Default to True for safety
    
    def reset(self):
        """Reset motion detector"""
        self.prev_frame = None
