import aiohttp
import logging
import base64
import cv2
import numpy as np
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class InferenceClient:
    """Client for calling YOLO inference API"""
    
    def __init__(self, api_url: str, timeout: int = 30):
        """
        Initialize inference client
        
        Args:
            api_url: Base URL of YOLO API
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
    
    async def predict(self, frame: np.ndarray) -> Optional[Dict]:
        """
        Run YOLO inference on frame
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            Inference result dict or None on error
        """
        try:
            # Encode frame to JPEG
            _, buffer = cv2.imencode(".jpg", frame)
            frame_b64 = base64.b64encode(buffer).decode("utf-8")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/detect",
                    json={"image_b64": frame_b64},
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status != 200:
                        logger.error(f"[INFERENCE] API error: {response.status}")
                        return None
                    
                    result = await response.json()
                    logger.debug(f"[INFERENCE] Got {len(result.get('detections', []))} detections")
                    return result
        
        except asyncio.TimeoutError:
            logger.error(f"[INFERENCE] Timeout calling {self.api_url}/detect")
            return None
        except Exception as e:
            logger.error(f"[INFERENCE] Error: {e}")
            return None
