"use client";
import { useState } from "react";

export default function ChatBot() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if(!message) return;
    try {
      setLoading(true);
      setResponse("");

      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: "1" }),
      });

      if (!res.body) {
        setLoading(false);
        console.log("No response body");
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");

      async function readStream() {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const tokens = chunk.split(" ");

          for (let i = 0; i < tokens.length; i++) {
            await new Promise((r) => setTimeout(r, 30)); // typing delay
            setResponse((prev) => prev + tokens[i] + " ");
          }
        }
        setLoading(false);
      }

      // Start reading the stream continuously
      readStream();
    } catch (error) {
      console.error("Streaming error:", error);
      setLoading(false);
    }
  };

  return (
    <section className="flex flex-col h-[95vh] w-[800px] max-w-full mx-auto bg-white shadow-lg rounded-2xl overflow-hidden font-sans border border-gray-200">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-500 to-purple-500 text-white py-4 px-6 text-xl font-semibold uppercase tracking-wide shadow-md">
        ChatMe
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {response ? (
          <div className="bg-indigo-950 text-white p-4 rounded-lg font-sans text-lg whitespace-pre-wrap shadow-inner">
            {response}
            {loading && <span className="animate-pulse">▌</span>}
          </div>
        ) : (
          !loading && (
            <div className="h-full flex flex-col items-center justify-center text-gray-600">
              <p className="text-xl text-center">
                Type your message below to start chatting.
              </p>
            </div>
          )
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-gray-300 p-3 flex items-center gap-2 bg-white shadow-inner">
        <input
          type="text"
          name="chatbox"
          id="chatbox"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 border border-gray-300 rounded-xl py-2 px-4 outline-none focus:ring-2 focus:ring-indigo-400 transition-all duration-200"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-5 py-2 rounded-xl transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer disabled:opacity-50"
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </section>
  );
}
