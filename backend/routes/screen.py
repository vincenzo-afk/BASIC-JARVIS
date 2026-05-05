"""
Screen Route - OCR and Screenshot functionality
Handles screen capture and text extraction
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from modules.ocr.screen_capture import ScreenCapture
from modules.ocr.ocr_engine import OCREngine
from modules.utils.logger import logger

router = APIRouter()

# Initialize modules
screen_capture = ScreenCapture()
ocr_engine = OCREngine()


class ScreenRegion(BaseModel):
    """Define a region of the screen"""
    x: int = Field(default=0, ge=0)
    y: int = Field(default=0, ge=0)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)


class ScreenReadRequest(BaseModel):
    """Request to read screen content"""
    region: Optional[ScreenRegion] = None
    monitor: int = Field(default=0, description="Monitor number (0 = all, 1+ = specific)")
    preprocess: bool = Field(default=True, description="Apply preprocessing for better OCR")


class ScreenReadResponse(BaseModel):
    """Response with extracted text"""
    text: str
    image_path: str
    width: int
    height: int
    word_count: int


@router.post("/read", response_model=ScreenReadResponse)
async def read_screen(request: ScreenReadRequest = None):
    """
    Capture the screen and extract text using OCR
    
    - **region**: Optional specific area to capture
    - **monitor**: Which monitor to capture (0 = all)
    - **preprocess**: Apply image preprocessing for better OCR accuracy
    """
    if request is None:
        request = ScreenReadRequest()
    
    logger.info(f"Screen read request: monitor={request.monitor}")
    
    try:
        # Capture screen
        region = None
        if request.region:
            region = {
                "left": request.region.x,
                "top": request.region.y,
                "width": request.region.width,
                "height": request.region.height
            }
        
        image_path, dimensions = screen_capture.capture(
            monitor=request.monitor,
            region=region
        )
        
        # Extract text with OCR
        text = ""
        try:
            text = ocr_engine.extract_text(
                image_path, 
                preprocess=request.preprocess
            )
        except Exception as ocr_error:
            logger.warning(f"OCR failed (Tesseract might be missing): {ocr_error}")
            text = ""
        
        word_count = len(text.split()) if text else 0
        
        logger.info(f"Screen captured: {dimensions}, words={word_count}")
        
        return ScreenReadResponse(
            text=text,
            image_path=image_path,
            width=dimensions["width"],
            height=dimensions["height"],
            word_count=word_count
        )
        
    except Exception as e:
        logger.error(f"Screen read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capture")
async def capture_screen(monitor: int = 0):
    """
    Capture screen without OCR (just screenshot)
    
    Returns the path to the saved screenshot
    """
    try:
        image_path, dimensions = screen_capture.capture(monitor=monitor)
        
        return {
            "image_path": image_path,
            "width": dimensions["width"],
            "height": dimensions["height"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitors")
async def list_monitors():
    """List available monitors"""
    try:
        monitors = screen_capture.list_monitors()
        return {"monitors": monitors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr")
async def ocr_image(image_path: str, preprocess: bool = True):
    """
    Run OCR on an existing image file
    
    - **image_path**: Path to the image file
    - **preprocess**: Apply preprocessing
    """
    try:
        text = ocr_engine.extract_text(image_path, preprocess=preprocess)
        return {
            "text": text,
            "word_count": len(text.split()) if text else 0
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
