from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain.chat_models import init_chat_model

load_dotenv()
app = FastAPI()

if not os.environ.get("OPENAI_API_KEY"):
    raise "OpenAI API KEY not provided"

api_key = os.getenv("OPENAI_API_KEY")

#~ Define chat request model 
class Chatbody(BaseModel):
    message: str

#~ Define StateGraph
class State(TypedDict):
    messages: Annotated[list, add_messages]

#~ Build graph
graph_builder = StateGraph(State)

model = init_chat_model(model="gpt-4o-mini", model_provider='openai')

def chatbot(state: State):
    return {"messages": [model.invoke(state["messages"])]}

#^ define node with unique name
graph_builder.add_node("chatbot", chatbot)
#^ Add entry point
graph_builder.add_edge(START, "chatbot")
#^ Add exit point
graph_builder.add_edge("chatbot", END)
#^ Compile graph
graph = graph_builder.compile()

######
# * GET /
######
@app.get('/')
async def get_home():
    return {"success": True, 'message': "Fast API x LangGraph backend"}

#####
# * POST /chat
#####
@app.post('/chat')
async def chat(Chatbody):
    pass