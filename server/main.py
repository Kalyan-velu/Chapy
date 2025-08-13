import os
from typing import Union, List, Dict, Any, Coroutine
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llama_index.llms.gemini import Gemini

from api.routers.documents import router as documents_router
from api.routers.chat import router as chat_router
from app_logging import setup_logging, install_observability, log_registered_routes

GOOGLE_API_KEY ="AIzaSyBgryLDVFMEG0OqBkCS1LVCnfO9c6rmTJ0"
print("API_KEY",GOOGLE_API_KEY)
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize app and logging
setup_logging()
app = FastAPI()
install_observability(app)

# Basic CORS (can be refined using env/config)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(documents_router)
app.include_router(chat_router)



@app.get("/")
async def read_root():
        completion = Gemini(api_key=os.getenv("GOOGLE_API_KEY")).complete("Paul Graham is ")
        return {"completion": completion}

@app.get('/complete')
async def get_llm_completion(prompt: str):
    completion =  Gemini().complete(prompt)
    return completion


