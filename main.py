import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

VAPI_TOKEN = os.environ.get("VAPI_TOKEN")          # Render'da env var qilib qo'yasiz
ASSISTANT_ID = os.environ.get("ASSISTANT_ID")      # Render'da env var qilib qo'yasiz

app = FastAPI(title="Vapi Telegram WebRTC Link Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/create-call")
def create_call():
    if not VAPI_TOKEN:
        raise HTTPException(status_code=500, detail="Missing env var: VAPI_TOKEN")
    if not ASSISTANT_ID:
        raise HTTPException(status_code=500, detail="Missing env var: ASSISTANT_ID")

    r = requests.post(
        "https://api.vapi.ai/call",
        headers={
            "Authorization": f"Bearer {VAPI_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "type": "webCall",
            "assistantId": ASSISTANT_ID,
        },
        timeout=30,
    )

    if not r.ok:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    data = r.json()

    # Vapi response may differ by version; try common fields
    join_url = (
        data.get("webCallUrl")
        or data.get("joinUrl")
        or data.get("url")
        or data.get("webCall", {}).get("url")
        or data.get("webCall", {}).get("webCallUrl")
    )

    return {
        "joinUrl": join_url,
        "call": data,  # debugging uchun: kerak bo'lsa keyin shu JSON'dan aniq fieldni topamiz
    }
