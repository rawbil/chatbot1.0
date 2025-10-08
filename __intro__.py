from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

model = init_chat_model("gpt-4o-mini", model_provider="openai")

question = input("Ask your question here...")

template = ChatPromptTemplate(
    [
        ("system", "You are a helpful assistant. Your name is {name}"),
        ("human", question),
    ]
)

invoke_template = template.invoke({"name": "Bildad"})

result = model.invoke(invoke_template)
print(result.content)

# Every request you make is recorded in Langchain. You can see the logs containing the input and the AI response, as well as the latency, no.of tokens used and the price
