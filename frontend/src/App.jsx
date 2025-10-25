import { useState, useRef, useEffect } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!question.trim()) return;
    setMessages((prev) => [...prev, { sender: "user", text: question }]);
    setQuestion("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/ask", { question });
      setMessages((prev) => [...prev, { sender: "bot", text: response.data.answer }]);
    } catch {
      setMessages((prev) => [...prev, { sender: "bot", text: "Server error" }]);
    }
  };

  const enterSend = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{ minHeight: "100vh", background: "#f0f2f5" }}
    >
      <div
        className="shadow bg-white rounded p-3"
        style={{
          width: "100%",
          maxWidth: "500px",
          height: "75vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h5 className="text-center mb-3 fw-bold">NGP College Chatbot</h5>

        <div
          className="p-3 mb-3 overflow-auto rounded flex-grow-1"
          style={{
            background: "#f7f7f7",
            border: "1px solid #ddd",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`p-2 my-1 rounded-3 ${
                msg.sender === "user"
                  ? "bg-primary text-white align-self-end"
                  : "bg-secondary text-white align-self-start"
              }`}
              style={{
                maxWidth: "80%",
                wordWrap: "break-word",
              }}
            >
              {msg.text}
            </div>
          ))}
          <div ref={chatEndRef}></div>
        </div>

        <div className="input-group">
          <input
            className="form-control"
            placeholder="Ask about NGP College..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={enterSend}
          />
          <button className="btn btn-primary" onClick={sendMessage}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
