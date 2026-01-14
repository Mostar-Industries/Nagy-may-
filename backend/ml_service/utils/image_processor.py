import logging
import io
from typing import Tuple, Optional
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Image preprocessing for YOLO inference"""
    
    SUPPORTED_FORMATS = {'JPEG', 'PNG', 'WEBP', 'BMP', 'GIF'}
    MAX_SIZE = 4096  # Max dimension
    TARGET_SIZE = 640  # YOLO input size
    
    def __init__(self):
        pass
    
    def load_image_from_bytes(self, image_bytes: bytes) -> Image.Image:
        """
        Load and preprocess image from bytes.
        
        Args:
            image_bytes: Raw image bytes
        
        Returns:
            PIL Image ready for inference
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Validate format
            if image.format and image.format.upper() not in self.SUPPORTED_FORMATS:
                logger.warning(f"Unusual format: {image.format}")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if max(image.size) > self.MAX_SIZE:
                image = self._resize_maintain_aspect(image, self.MAX_SIZE)
                logger.info(f"Resized large image to {image.size}")
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise ValueError(f"Invalid image data: {e}")
    
    def load_image_from_path(self, path: str) -> Image.Image:
        """Load image from file path"""
        with open(path, 'rb') as f:
            return self.load_image_from_bytes(f.read())
    
    def _resize_maintain_aspect(self, image: Image.Image, max_dim: int) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        w, h = image.size
        if w > h:
            new_w = max_dim
            new_h = int(h * max_dim / w)
        else:
            new_h = max_dim
            new_w = int(w * max_dim / h)
        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    def preprocess_for_yolo(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess image specifically for YOLO inference.
        
        Returns numpy array in YOLO format.
        """
        # Resize to YOLO input size
        resized = image.resize((self.TARGET_SIZE, self.TARGET_SIZE), Image.Resampling.BILINEAR)
        
        # Convert to numpy
        arr = np.array(resized, dtype=np.float32)
        
        # Normalize to 0-1
        arr = arr / 255.0
        
        # HWC to CHW format
        arr = np.transpose(arr, (2, 0, 1))
        
        # Add batch dimension
        arr = np.expand_dims(arr, 0)
        
        return arr
    
    def get_image_info(self, image: Image.Image) -> dict:
        """Get image metadata"""
        return {
            "width": image.size[0],
            "height": image.size[1],
            "mode": image.mode,
            "format": image.format,
        }
