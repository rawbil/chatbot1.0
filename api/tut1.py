from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, io
from pydantic import BaseModel
from typing import Annotated, TypedDict
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


# try:
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
    func=python_repl.run,
)

tools = [wiki_tool, repl_tool]

################################
# * Initialize chat model
################################
model = init_chat_model(model="gpt-4o-mini", model_provider="openai")

# Add tools to the model
llm_with_tools = model.bind_tools(tools)

##############################
# * Create a State Graph
# - To define the structure of our chat
##############################


class State(TypedDict):
    messages: Annotated[list, add_messages]


#############################
# * Build Langgraph workflow
#############################
graph_builder = StateGraph(State)


def chatbot(state: State):
    msgs = state["messages"]
    response = llm_with_tools.invoke(msgs)
    return {"messages": [response]}


################################
# * Add tools to the graph
################################
graph_builder.add_node("tools", ToolNode(tools=[wiki_tool, repl_tool]))

###############################
# * Add graph edges
###############################
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("chatbot", END)

###################################
# * Compile the graph
###################################
graph = graph_builder.compile()
# except Exception as e:
#     print("An error occured: ", e)


# * /
@app.get("/")
async def home():
    return {"success": True, "message": "Welcome Home!"}


###################################
# * chat route
###################################
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        question = request.message

        # ~System message
        system_message = """
    You are a helpful AI assistant.
    - Use Wikipedia to answer factual questions.
    - Use the Python REPL to execute computations and run short code snippets.
    - Detect which tool (Wikipedia or python_repl) is needed and call it when appropriate.
    - Prefer concise, professional answers; avoid unnecessary exposition.
        """.strip()

        events = graph.stream(
            {"messages": [("system", system_message), ("user", question)]},
            stream_mode="values",
        )

        response = ""
        for event in events:
            response = event["messages"][-1].pretty_print()
        return {"response": response}

        ###END of fn
    except Exception as e:
        print("An exception occurred:", e)
        return {"success": False, "error": str(e)}
