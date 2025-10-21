"use client";
import { useState } from "react";
import ChatBot from "./chatbot/page";
import { useRouter } from "next/navigation";

export default function Chat() {
  const router = useRouter()
  return (
    <>
      <div className="relative h-[98vh]">
        <section className="absolute bottom-0 right-2 flex flex-col items-center cursor-pointer" onClick={() => router.push('/chatbot')}>
          <p className="font-medium">Chat with us</p>
          <section className="absolute bottom-6">
            <div className="bg-[royalblue] w-10 h-10 rounded-full animate-pulse"></div>{" "}
            <p className="absolute bg-green-500 w-5 h-5 rounded-full top-0 -right-2 z-10 animate-bounce"></p>
            <p className="absolute bg-green-500 w-5 h-5 rounded-full top-0 -left-2 z-10 animate-bounce"></p>
          </section>
        </section>
      </div>
    </>
  );
}
