from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
from pydantic import BaseModel
import os, getpass

load_dotenv()

app = FastAPI()

if not os.environ.get("OPENAI_API_KEY"):
    # os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OPENAI API KEY: ") # Won't work in prod
    raise EnvironmentError("OPENAI API KEY not found...")

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

class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def get_root():
    return {"message": "Langchain FastAPI server running"}


@app.post("/chat")
# async def chat_endpoint(request: Request):
async def chat_endpoint(request_data: ChatRequest):
    """Create chat template with user input"""
    # data = await request.json()
    # user_input = data.get("message")
    chat_template = ChatPromptTemplate(
        [
            ("system", "You are a helpful AI assistant. Answer the questions asked. Be as precise, clear and professional as possible."),
            ("human", "{user_input}")
        ]
    )
    
    temp = chat_template.invoke({"user_input": request_data.message})
    
    result = model.invoke(temp)
    return {"success": True, "message": result.content}
