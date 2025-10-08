"use client"
import { useState } from "react";

export default function Chat() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("")

  const sendMessage = async() => {
    try {
     // const backend_url = process.env.NEXT_PUBLIC_API_URL as string
      const response = await fetch(`http://127.0.0.1:8000/chat`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message })
      })

      const data = await response.json();
      setResponse(data.message)
    } catch (error: any) {
      console.log(error.message);
    }
  }

  return (
    <section className="p-2">
      <h2>ChatMe</h2>
      <textarea
        name="chatbox"
        id="chatbox"  
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
        rows={4}
        cols={50}
        className="border"
      ></textarea><br />
      <button onClick={sendMessage} className="bg-green-500 cursor-pointer p-1 px-2 rounded ">Send</button>
      <p><strong>Bot: </strong>{response}</p>
    </section>
  );
}
