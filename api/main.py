from fastapi import FastAPI, Request, Response, next
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os, getpass

load_dotenv()

app = FastAPI()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OPENAI API KEY: ")

api_key = os.getenv("OPENAI_API_KEY")

# Define cors config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

model = init_chat_model(model="gpt-4o-mini", model_provider="openai")

@app.get('/')
async def root():
    return {"message": "Langchain FastAPI server running"}

@app.post('/chat')
async def chat_endpoint(request: Request):
    pass