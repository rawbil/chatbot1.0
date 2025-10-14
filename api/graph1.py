from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
import os, getpass
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI API KEY not found...")

api_key = os.getenv("OPENAI_API_KEY")


# * 1. Create a state graph - Defines the structure of our chatbot
class State(TypedDict):
    messages: Annotated[
        list, add_messages
    ]  # append message to the list rather than overwriting existing messages


graph_builder = StateGraph(State)

"""each node can receive the current state as input and output  an update to the state."""

# * 2. Add a Node
# ~ A node is a function that takes the state as input and returns update
# ~ It can be a function that takes the message and calls the LLM to generate a response

model = init_chat_model(model="gpt-4o-mini", model_provider="openai")


def chatbot(state: State):
    # state["messages"] - list of messages
    msgs = state["messages"]

    response = model.invoke(msgs)
    return {"messages": [response]}


# * 3. Add the model to the node
graph_builder.add_node("chatbot", chatbot)

# * 4. Add an entry point to tell the graph where to start its work each time it runs
graph_builder.add_edge(START, "chatbot")

# *5. Add an exit point to tell the graph where to finish execution
graph_builder.add_edge(
    "chatbot", END
)  # tells the graph to terminate after running the chatbot node

# * 6. Compile the graph
graph = graph_builder.compile()

initial = HumanMessage(content="What is your name?")
state = {"messages": [initial]}

output = graph.invoke(state)
# print(output["messages"][-1].content)
print(output["messages"][-1].content)
