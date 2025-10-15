"""include memory and tools"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
import json
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

import os, getpass
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI API KEY not found...")
if not os.environ.get("TAVILY_API_KEY"):
    raise EnvironmentError("Tavily API key not provided")

api_key = os.getenv("OPENAI_API_KEY")

tool = TavilySearch(max_results=2)
tools = [tool]
# tool.invoke("What's a node in LangGraph?")


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

llm_with_tools = model.bind_tools(tools)


def chatbot(state: State):
    # state["messages"] - list of messages
    msgs = state["messages"]

    response = llm_with_tools.invoke(msgs)
    return {"messages": [response]}


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)


def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")

# * 3. Add the model to the node
graph_builder.add_node("chatbot", chatbot)

# * 4. Add an entry point to tell the graph where to start its work each time it runs
graph_builder.add_edge(START, "chatbot")

# *5. Add an exit point to tell the graph where to finish execution
graph_builder.add_edge(
    "chatbot", END
)  # tells the graph to terminate after running the chatbot node

# * 6. Compile the graph
graph = graph_builder.compile(checkpointer=memory)

user_input = "My name is Bildad"
user_input2 = "What is my name and age?"

config = {"configurable": {"thread_id": "1"}}


# First conversation
graph.invoke({"messages": [{"role": "user", "content": user_input}]}, config)

# Second conversation in the same thread
output = graph.invoke({"messages": [{"role": "user", "content": user_input2}]}, config)

output["messages"][-1].pretty_print()

# The config is the **second positional argument** to stream() or invoke()!
# graph.stream(
#     {"messages": [{"role": "user", "content": user_input}]},
#     config,
#     stream_mode="values",
# )
#
# user_input2 = "Do you remember my name? "
# events = graph.stream(
#     {"messages": [{"role": "user", "content": user_input2}]},
#     config,
#     stream_mode="values",
# )
#
# for event in events:
#     event["messages"][-1].pretty_print()


"""initial = HumanMessage(
    content="Do you have any memory of previous conversations with me?"
)
state = {"messages": [initial]}

output = graph.invoke(state)
# print(output["messages"][-1].content)
print(output["messages"][-1].content)"""
