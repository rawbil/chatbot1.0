from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, io
from pydantic import BaseModel
from typing import Annotated, TypeDict
from PIL import Image

# Langchain and Langgraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
# from langchain_groq import ChatGroq
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import Tools


load_dotenv()
app = FastAPI()

api_key = os.getenv("OPENAI_API_KEY")

model = init_chat_model(model="gpt-4o-mini", model_provider="openai")