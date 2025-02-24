import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import React from "react";

type Message = {
  content: string;
  role: "user" | "assistant";
};

function ChatMessage({ message }: { message: Message }) {
  return (
    <div
      className={`p-3 w-full flex ${
        message.role === "assistant" ? "justify-start" : "justify-end"
      }`}
    >
      <div className="flex items-start space-x-3">
        {message.role === "assistant" && (
          <div className="chat-avatar assistant">A</div>
        )}

        <div
          className={`chat-card ${
            message.role === "assistant" ? "assistant" : "user"
          }`}
        >
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {message.role === "user" && (
          <div className="chat-avatar user">U</div>
        )}
      </div>
    </div>
  );
}

function Prep() {
  const [input, setInput] = useState<string>("");
  const [botState, setBotState] = useState<object>({});
  const [history, setHistory] = useState<Message[]>([
    {
      content:
        "Welcome! Please provide the job description to generate relevant interview questions.",
      role: "assistant",
    },
  ]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  async function chatRequest(history: Message[], botState: object) {
    try {
      const response = await fetch("http://localhost:4000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages: history, state: botState }),
      });

      const content: { botResponse: Message; newState: object } =
        await response.json();

      setHistory([...history, content.botResponse]);
      setBotState(content.newState);
    } catch (error) {
      console.error("Failed to send chat history:", error);
    }
  }

  return (
    <div className="app-container">
      <div className="chat-container">
        <div className="chat-messages">
          {history.map((message, idx) => (
            <ChatMessage message={message} key={idx} />
          ))}
          <div ref={chatEndRef}></div>
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && input.trim()) {
                const newMessage: Message = {
                  content: input,
                  role: "user",
                };
                setHistory([...history, newMessage]);
                setInput("");
                chatRequest([...history, newMessage], botState);
              }
            }}
          />
          <button
            className="chat-send-btn"
            onClick={() => {
              if (input.trim()) {
                const newMessage: Message = {
                  content: input,
                  role: "user",
                };
                setHistory([...history, newMessage]);
                setInput("");
                chatRequest([...history, newMessage], botState);
              }
            }}
          >
            Send
          </button>
        </div>
      </div>

      {/* Embedded CSS */}
      <style>
        {`
        /* App Container */
        .app-container {
          display: flex;
          height: 100vh;
          justify-content: center;
          align-items: center;
          background-color: #f4f4f9;
        }

        /* Chat Container (Now Wider) */
        .chat-container {
          display: flex;
          flex-direction: column;
          width: 80%;
          max-width: 900px;
          height: 80vh;
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }

        /* Chat Messages */
        .chat-messages {
          flex-grow: 1;
          overflow-y: auto;
          padding: 12px;
        }

        /* Chat Message Card (Now Wider) */
        .chat-card {
          background: white;
          border-radius: 12px;
          padding: 14px 18px;
          max-width: 85%;
          word-wrap: break-word;
          border: 1px solid #ddd;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        /* Assistant Message */
        .chat-card.assistant {
          border-left: 6px solid #4f46e5;
        }

        /* User Message */
        .chat-card.user {
          border-left: 6px solid #9333ea;
        }

        /* Avatar */
        .chat-avatar {
          width: 45px;
          height: 45px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          color: white;
        }

        /* Assistant Avatar */
        .chat-avatar.assistant {
          background-color: #4f46e5;
        }

        /* User Avatar */
        .chat-avatar.user {
          background-color: #9333ea;
        }

        /* Chat Input Container */
        .chat-input-container {
          display: flex;
          margin-top: 12px;
          background: white;
          border-radius: 8px;
          padding: 10px;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }

        /* Chat Input */
        .chat-input {
          flex-grow: 1;
          border: none;
          padding: 12px;
          font-size: 16px;
          border-radius: 8px;
          outline: none;
        }

        /* Chat Send Button */
        .chat-send-btn {
          background-color: #4f46e5;
          color: white;
          padding: 12px 18px;
          border-radius: 8px;
          border: none;
          margin-left: 10px;
          cursor: pointer;
        }

        .chat-send-btn:hover {
          background-color: #4338ca;
        }
        `}
      </style>
    </div>
  );
}

export default Prep;
