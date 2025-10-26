from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain.chat_models import init_chat_model
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain_core.tools import Tool

from langchain_experimental.utilities import PythonREPL
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

load_dotenv()
app = FastAPI()

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.environ.get("OPENAI_API_KEY"):
    raise "OpenAI API KEY not provided"

api_key = os.getenv("OPENAI_API_KEY")


# ~ Define chat request model
class Chatbody(BaseModel):
    message: str


# ~ Define StateGraph
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ~ Build graph
graph_builder = StateGraph(State)

model = init_chat_model(model="gpt-4o-mini", model_provider="openai")

#####
# * Define Tools
#####
wiki_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
)

# ~ Python REPL
python_repl = PythonREPL()
repl_tool = Tool(
    name="python_repl",
    description="Execute python code using this shell. Use print(...) to display results",
    func=python_repl.run,
)

tools = [wiki_tool, repl_tool]

llm_with_tools = model.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

#~ Add tools to the graph
graph_builder.add_node("tools", ToolNode(tools=[wiki_tool, repl_tool]))

#~ Add nodes
# ^ define node with unique name
graph_builder.add_node("chatbot", chatbot)

#~ Add edges
# ^ Add entry point
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
# ^ Add exit point
graph_builder.add_edge("chatbot", END)
# ^ Compile graph
graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}


######
# * GET /
######
@app.get("/")
async def get_home():
    return {"success": True, "message": "Fast API x LangGraph backend"}


#####
# * POST /chat
#####
@app.post("/chat")
async def chat_endpoint(request: Chatbody):
    try:
        question = request.message

        system_message = """
       You are a helpful AI assistant.
    - Use Wikipedia to answer factual questions.
    - Use the Python REPL to execute computations and run short code snippets.
    - Detect which tool (Wikipedia or python_repl) is needed and call it when appropriate.
    - Prefer concise, professional answers; avoid unnecessary exposition.
        """.strip()

        events = graph.stream(
            {"messages": [("user", question), ("system", system_message)]},
            config,
            stream_mode="values",
        )

        def generate_response():
            for event in events:
                response = event["messages"][-1]
                if response.type == "ai":
                    yield response.content + "\n" #~ YIELD- When the function ends, you don't want to exit the function, instead, you want to continue calling the function to generate the next chunk of data(for streaming)
        
        return StreamingResponse(generate_response(), media_type="text/plain")

    #! WE WANT TO STREAM THE RESPONSE INSTEAD OF RETURNING THE WHOLE OF IT AT ONCE
    #         response = ""
    #
    #         for event in events:
    #             response = event["messages"][-1].content
    #         return {"response": response}

    except Exception as e:
        print("An exception occurred: ", e)
