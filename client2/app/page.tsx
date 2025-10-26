"use client";
import { useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState("");

  const submitRequest = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!message) return;
    try {
      setLoading(true);
      setResponse("");
      // console.log("Model running...");

      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        body: JSON.stringify({ message }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        setLoading(false);
        console.log(response.status);
        throw new Error(`Error Status: ${response.status}`);
      }

      if (response.body) {
        // Allows streaming of the response body
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        async function readStream() {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const tokens = chunk.split(" "); // convert the chunk to an array

            // loop through the array
            for (let i = 0; i < tokens.length; i++) {
              await new Promise((r) => setTimeout(r, 30)); // 30ms delay for every token
              setResponse((response) => response + tokens[i] + " ");
            }
          }
          setLoading(false);
        }

        await readStream();
      }
    } catch (error: any) {
      setLoading(false);
      throw new Error(error.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <>
      <form className="p-2 pt-10" onSubmit={submitRequest}>
        <input
          type="text"
          placeholder="enter text here"
          className="border p-1.5 mx-4"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button className="bg-white text-slate-900 p-1.5 cursor-pointer">
          Send
        </button>
      </form>
      <div className="border w-[800px] mx-6 overflow-y-auto h-[50vh] p-2 text-white">
        {response && loading ? (
          <div>{response + " ..."}</div>
        ) : !loading && !response ? (
          <p>Response will appear here...</p>
        ) : loading && !response ? (<p>Thinking...</p>) :(
          <p>{response}</p>
        )}
      </div>
    </>
  );
}
