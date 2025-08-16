import pytesseract
from PIL import Image
import io

def extract_text_from_image(uploaded_file):
    try:
        image = Image.open(io.BytesIO(uploaded_file.read()))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise RuntimeError(f"Error processing image: {e}")