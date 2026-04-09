from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from get_menus import get_menus
from func import get_end_times
from datetime import datetime, timedelta
from ocr import OCR_clipboard_image
from pydantic import BaseModel
import httpx
import base64


class Item(BaseModel):
    data: str


api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://clockout.ch",
    ],  # Hier dein Frontend erlauben
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
path = "ocr_img.png"
@api.post("/process-img")
async def process_img(item: Item):
    img = base64.b64decode(item.data)
    with open("output_image.png", "wb") as image_file:
        image_file.write(img)
    text, formated_times = OCR_clipboard_image("./output_image.png")
    print(f"Zeiten: {formated_times}")
    end_time= await get_end_times(formated_times,"P0Y0M0DT0H30M0S","P0Y0M0DT8H0M0S")
    return {"end_time": end_time.isoformat(), "times": formated_times}

# Api Endpoint to get menus
@api.get("/menus")
async def menus():
        #Menus holen
        menu_json = {}
        menus = await get_menus()
        for name, desc, sort in menus:
            menu_json[sort]= {"name": name, "desc": desc}
        return menu_json

# API Endpoint to get transport data
@api.get("/transport/{target_location}")
async def get_transport_data(target_location:str, end_time:datetime, walking_time: timedelta | None = 0, minus_time:timedelta | None = 0):
    

    # Verbindungen abfragen
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.get(
            f"https://transport.opendata.ch/v1/connections?from=Buchrain&to={target_location}&time={(end_time + walking_time - minus_time).strftime('%H:%M')}&limit=6"
        )
        data = r.json()
    print()
    print("Nächste Abfahrten ab Buchrain:")
    for verbindung in data.get("connections", []):
        abfahrt = datetime.fromisoformat(verbindung["from"]["departure"])
        
        if verbindung["from"].get("delay") is not None and verbindung["from"].get("delay") > 3:
            print(f"  {abfahrt.strftime('%H:%M')} Uhr (Verspätung: {verbindung['from']['delay']} Min.)")
        else:
            print(f"  {abfahrt.strftime('%H:%M')} Uhr")
