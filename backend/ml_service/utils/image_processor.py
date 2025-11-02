import logging
from typing import Union
from io import BytesIO
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Image preprocessing utilities"""
    
    SUPPORTED_FORMATS = {'JPEG', 'PNG', 'BMP', 'GIF', 'TIFF'}
    MAX_SIZE = (2048, 2048)
    
    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
        """
        Load PIL Image from bytes
        
        Args:
            image_bytes: Raw image bytes
        
        Returns:
            PIL Image object
        """
        try:
            image = Image.open(BytesIO(image_bytes))
            
            # Validate format
            if image.format not in ImageProcessor.SUPPORTED_FORMATS:
                logger.warning(f"[v0] Unsupported format: {image.format}, converting to RGB")
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > ImageProcessor.MAX_SIZE[0] or image.size[1] > ImageProcessor.MAX_SIZE[1]:
                logger.info(f"[v0] Resizing image from {image.size} to {ImageProcessor.MAX_SIZE}")
                image.thumbnail(ImageProcessor.MAX_SIZE)
            
            logger.info(f"[v0] Image loaded: {image.size}, format: {image.format}")
            return image
            
        except Exception as e:
            logger.error(f"[v0] Failed to load image: {e}")
            raise
    
    @staticmethod
    def load_image_from_path(path: str) -> Image.Image:
        """Load PIL Image from file path"""
        try:
            image = Image.open(path)
            if image.format not in ImageProcessor.SUPPORTED_FORMATS:
                image = image.convert('RGB')
            return image
        except Exception as e:
            logger.error(f"[v0] Failed to load image from path: {e}")
            raise
    
    @staticmethod
    def convert_to_rgb(image: Image.Image) -> Image.Image:
        """Ensure image is in RGB format"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    
    @staticmethod
    def resize_image(image: Image.Image, size: tuple) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        image.thumbnail(size, Image.Resampling.LANCZOS)
        return image
