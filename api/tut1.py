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
from langchain_core.tools import Tool


load_dotenv()
app = FastAPI()

api_key = os.getenv("OPENAI_API_KEY")

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



#########################################
# *  Define chat schema
#########################################
class ChatRequest(BaseModel):
    message: str
    session_id: str


######################################
# * Define tools
#######################################

# Wikipedia tool
wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
)

# python repl tool
python_repl = PythonREPL()
repl_tool = Tool(
    name="python_repl",
    description="Execute python code using this shell. Use print(...) to display results",
    func=python_repl.run
)

tools = [wiki_tool, repl_tool]

################################
#* Initialize chat model
################################
model = init_chat_model(model="gpt-4o-mini", model_provider="openai")

# Add tools to the model
llm_with_tools = model.bind_tools(tools)