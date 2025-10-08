"""typing module is mainly used with generic data types, eg, dicts, lists(that have internal types)"""
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel # Python library for data validation

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None # None makes the value optional
    options: list[str] = [] # defaults to an empty list


@app.get("/")
async def read_root():
    return {"success": True, "message": "Welcome to the home page"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None): # str | None=None
    return {"item_id": item_id, "q": q}

@app.put('/items/{item_id}')
async def update_item(item_id: int, item: Item):
    return {"item":item, "item_id": item_id}

# Other parameters in the function that are not in the path parameters are automatically interpreted as query parameters for the request.

"""Streaming"""
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import asyncio

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model setup
model = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai",
    api_key=os.getenv("OPENAI_API_KEY")
)

class ChatRequest(BaseModel):
    message: str


# ✅ Custom streaming callback
class StreamHandler(BaseCallbackHandler):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.queue.put(token)

    async def on_llm_end(self, *args, **kwargs):
        # Signal the end of stream
        await self.queue.put(None)


@app.post("/chat/stream")
async def chat_stream(request_data: ChatRequest):
    chat_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Respond clearly and concisely."),
        ("human", "{user_input}")
    ])
    temp = chat_template.invoke({"user_input": request_data.message})

    queue = asyncio.Queue()
    handler = StreamHandler(queue)
    streaming_model = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True,
        callbacks=[handler],
    )

    async def event_generator():
        await asyncio.sleep(0.1)
        asyncio.create_task(streaming_model.ainvoke(temp))
        while True:
            token = await queue.get()
            if token is None:
                break
            yield f"data: {token}\n\n"
        yield "data: [END]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

"""

"""
import { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]); // all messages
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    let botMessage = { sender: "bot", text: "" };
    setMessages((prev) => [...prev, botMessage]);

    const res = await fetch("http://127.0.0.1:8000/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });

    if (!res.body) {
      console.error("No stream found!");
      setLoading(false);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let done = false;
    let accumulatedText = "";

    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      const chunkValue = decoder.decode(value);
      const tokens = chunkValue.split("data: ").filter(Boolean);

      for (let token of tokens) {
        token = token.trim();
        if (token === "[END]") continue;
        accumulatedText += token;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { sender: "bot", text: accumulatedText };
          return updated;
        });
      }
    }

    setLoading(false);
  };

  return (
    <div className="chat-container">
      <h2 className="title">💬 LangChain Chatbot</h2>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.sender}`}>
            {msg.text || (msg.sender === "bot" && loading ? <TypingDots /> : "")}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}

// ⌨️ Typing animation component
function TypingDots() {
  return (
    <span className="typing">
      <span>.</span>
      <span>.</span>
      <span>.</span>
    </span>
  );
}

export default App;


<!--CSS--!>
body {
  font-family: 'Inter', sans-serif;
  background: #f4f5f7;
  margin: 0;
  padding: 0;
}

.chat-container {
  max-width: 600px;
  margin: 3rem auto;
  background: #fff;
  border-radius: 16px;
  padding: 1rem 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.title {
  text-align: center;
  margin-bottom: 1rem;
  color: #333;
}

.chat-box {
  height: 60vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 10px;
  background: #fafafa;
}

.message {
  padding: 10px 15px;
  border-radius: 12px;
  max-width: 80%;
  word-wrap: break-word;
  animation: fadeIn 0.3s ease;
}

.message.user {
  align-self: flex-end;
  background: #0078ff;
  color: white;
}

.message.bot {
  align-self: flex-start;
  background: #e5e5ea;
  color: #111;
}

.input-box {
  display: flex;
  margin-top: 1rem;
  gap: 10px;
}

.input-box input {
  flex: 1;
  padding: 10px 15px;
  border-radius: 10px;
  border: 1px solid #ccc;
  font-size: 1rem;
}

.input-box button {
  background: #0078ff;
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 500;
}

.input-box button:disabled {
  background: #aaa;
  cursor: not-allowed;
}

/* Typing dots animation */
.typing span {
  animation: blink 1.5s infinite;
  font-size: 1.5rem;
  opacity: 0.5;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

"""