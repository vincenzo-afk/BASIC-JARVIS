"""
OCR Engine Module
Text extraction from images using Tesseract
"""
import pytesseract
import cv2
import os
from typing import Optional
from PIL import Image
import numpy as np
from config.settings import TESSERACT_CMD, OCR_LANGUAGE
from modules.utils.logger import logger


class OCREngine:
    """
    OCR (Optical Character Recognition) engine using Tesseract
    
    Features:
    - Image preprocessing for better accuracy
    - Multiple output formats
    - Configurable language support
    """
    
    def __init__(self, tesseract_cmd: str = None, language: str = None):
        self.language = language or OCR_LANGUAGE
        
        # Configure Tesseract path if provided
        if tesseract_cmd or TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd or TESSERACT_CMD
        
        self._verify_tesseract()
    
    def _verify_tesseract(self):
        """Verify Tesseract is installed and accessible"""
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except Exception as e:
            logger.warning(f"Tesseract not found or not configured: {e}")
    
    def extract_text(
        self,
        image_path: str,
        preprocess: bool = True,
        language: str = None
    ) -> str:
        """
        Extract text from an image file
        
        Args:
            image_path: Path to the image file
            preprocess: Apply preprocessing for better accuracy
            language: OCR language (default from settings)
            
        Returns:
            Extracted text string
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        lang = language or self.language
        
        try:
            # Load image
            image = cv2.imread(image_path)
            
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Preprocess if enabled
            if preprocess:
                image = self._preprocess_image(image)
            
            # Run OCR
            text = pytesseract.image_to_string(
                image,
                lang=lang,
                config='--psm 3 --oem 3'  # Fully automatic page segmentation
            )
            
            # Clean up text
            text = self._clean_text(text)
            
            logger.info(f"OCR extracted {len(text)} characters from {image_path}")
            
            return text
            
        except Exception as e:
            logger.error(f"OCR error: {e}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        
        Applies:
        - Grayscale conversion
        - Noise reduction
        - Thresholding
        - Deskewing (if needed)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Adaptive thresholding for text
        # Using Gaussian for smoother results
        binary = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        return binary
    
    def _clean_text(self, text: str) -> str:
        """Clean up OCR output"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                # Remove multiple spaces
                line = ' '.join(line.split())
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_text_with_bounds(
        self,
        image_path: str,
        preprocess: bool = True
    ) -> list:
        """
        Extract text with bounding box information
        
        Returns:
            List of dicts with text, x, y, width, height
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = cv2.imread(image_path)
        
        if preprocess:
            image = self._preprocess_image(image)
        
        # Get detailed data
        data = pytesseract.image_to_data(
            image,
            lang=self.language,
            output_type=pytesseract.Output.DICT
        )
        
        results = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            # Skip empty text
            if int(data['conf'][i]) > 0 and data['text'][i].strip():
                results.append({
                    'text': data['text'][i],
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'confidence': int(data['conf'][i])
                })
        
        return results
    
    def extract_text_from_pil(self, pil_image: Image.Image) -> str:
        """Extract text from a PIL Image object"""
        text = pytesseract.image_to_string(
            pil_image,
            lang=self.language
        )
        return self._clean_text(text)


def extract_text(image_path: str, preprocess: bool = True) -> str:
    """Convenience function for quick OCR"""
    engine = OCREngine()
    return engine.extract_text(image_path, preprocess=preprocess)
