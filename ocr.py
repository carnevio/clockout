from PIL import ImageGrab, Image
import os
import easyocr
import re
from datetime import datetime, date, timezone, timedelta


path = "clipboard_screenshot.png"
reader = easyocr.Reader(['de'], gpu=False, quantize=False)

def save_clipboard_image():
    img = ImageGrab.grabclipboard()
    if img is None:
        return False
    img.save(path)
    return path

def OCR_clipboard_image(image_path):
    #return os.path.exists(image_path), None
    
    img = Image.open(image_path)
    
    text = reader.readtext(image_path, detail=0)
    text = ' '.join(text)

    text = re.sub(r'[.,;]', ':', text)
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    text = re.sub(r'\s*:\s*', ':', text)

    zeiten = re.findall(r'\b([012]?\d):([0-5]\d)\b', text)
    formatted_zeiten = [f"{h.zfill(2)}:{m}" for h, m in zeiten]

    tz = timezone(timedelta(hours=1))
    heute = date.today()

    formatted_zeiten = [
    datetime.strptime(f"{heute} {zeit}", "%Y-%m-%d %H:%M")
    .replace(tzinfo=tz)
    .isoformat()
    for zeit in formatted_zeiten
    ]
    

    return text, formatted_zeiten

def delete_clipboard_image(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)