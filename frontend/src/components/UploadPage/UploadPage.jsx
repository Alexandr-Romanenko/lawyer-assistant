import React, { useEffect, useRef, useState } from "react";

import ProgressBar from "../ProgressBar/ProgressBar.jsx";
import "./UploadPage.css";

import AxiosInstance from "../Axios/Axios.jsx";
import Textarea from "@mui/joy/Textarea";
import Box from "@mui/joy/Box";
import { Button, Alert } from "@mui/material";

const UploadPage = () => {
  const [input_text, setInputText] = useState("");
  const [uploadingResult, setUploadingResult] = useState("");
  const [loading, setLoading] = useState(false); // loading state
  const [error, setError] = useState(null); // error state
  const [messages, setMessages] = useState([]);

  const socketRef = useRef(null); // save socket

  // web-socket
  useEffect(() => {
    const token = localStorage.getItem("access");
    const ws = new WebSocket(`ws://localhost:8000/ws/progress/?token=${token}`);
    socketRef.current = ws;

    ws.onopen = () => {
      setMessages((prev) => [
        ...prev,
        { type: "system", detail: "WebSocket connected" },
      ]);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "progress") {
          setMessages((prev) => [...prev, data]);
        } else if (data.type === "status") {
          setMessages((prev) => [...prev, data]);
        } else {
          setMessages((prev) => [...prev, data]);
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message", err);
      }
    };

    ws.onerror = (err) => {
      setMessages((prev) => [
        ...prev,
        {
          type: "error",
          detail: `WebSocket error: ${err?.message || "Unknown error"}`,
        },
      ]);
    };

    ws.onclose = () => {
      setMessages((prev) => [
        ...prev,
        { type: "system", detail: "WebSocket closed" },
      ]);
    };

    return () => {
      if (ws.readyState === 1) {
        ws.close();
      }
    };
  }, []);

  // Handel load decision request
  const handleLoading = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setUploadingResult(""); // clearing old result
    if (!input_text.trim()) {
      setError("Введіть текст рішення перед завантаженням.");
      setLoading(false);
      return;
    }

    AxiosInstance.post(
      `api/decision_upload/`,
      { input_text }, // тело запроса
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access")}`,
        },
      }
    )
      .then((res) => {
        setUploadingResult(res.data);
      })
      .catch((err) => {
        setError(err);
      })
      .finally(() => {
        setLoading(false); // disable loading indicator
      });
  };

  // Handel clean area
  const handleCleanArea = () => {
    setInputText("");
    setError(null);
  };

  return (
    <section>
      <div className="container">
        <div className="upload-page-container">
          <div className="hero-section">
            <h1 className="hero-title">Upload decisions</h1>
          </div>
          <div className="use-rules-section">
            <h3>Завантаження інформації:</h3>
            <p>
              В поле "Input text" потрібно вставити рішення, які потрібно
              завантажити до векторної БД
            </p>
          </div>

          {/* Form to upload decisions */}
          <div className="upload-form-block">
            <form onSubmit={handleLoading}>
              <div className="upload-form">
                <div className="form-items">
                  <Box
                    sx={{
                      py: 5,
                      display: "grid",
                      gap: 2,
                      alignItems: "center",
                      flexWrap: "wrap",
                    }}
                  >
                    <div className="item-url-input">
                      <Textarea
                        name="Soft"
                        value={input_text}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder="Input text"
                        variant="soft"
                        maxRows={3}
                      />
                    </div>
                  </Box>
                </div>

                {/* Upload button */}
                <Button
                  variant="contained"
                  type="submit"
                  sx={{ width: "10%", marginTop: "30px", marginRight: "30px" }}
                  disabled={loading || !input_text.trim()}
                >
                  {loading ? "Uploading..." : "Upload"}
                </Button>

                {/* Clean area button */}
                <Button
                  variant="contained"
                  type="button"
                  sx={{ width: "10%", marginTop: "30px" }}
                  onClick={handleCleanArea}
                  disabled={!input_text.trim()}
                >
                  Clean
                </Button>
              </div>
            </form>
          </div>

          {/* Progress Bar */}
          {uploadingResult &&
            uploadingResult.ids_array &&
            uploadingResult.user_channel_id && (
              <ProgressBar
                taskIds={uploadingResult.ids_array}
                userChannelId={uploadingResult.user_channel_id}
                socket={socketRef.current}
                messages={messages}
              />
            )}

          {/* WebSocket messages area */}
          <h5 className="header-websocket-area">
            Деталізація системного процесу
          </h5>
          <div
            style={{
              marginTop: "20px",
              maxHeight: "238px",
              overflowY: "auto",
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "10px",
              backgroundColor: "#f5f5f5",
            }}
          >
            {messages.slice(-15).map((msg, index) => (
              <Alert
                key={index}
                severity={
                  msg.type === "error"
                    ? "error"
                    : msg.type === "system"
                    ? "info"
                    : "info"
                }
                style={{ marginBottom: "5px", fontSize: "0.85rem" }}
              >
                {msg.type === "progress" || msg.type === "status"
                  ? `[ID: ${msg.decision_id}] → ${msg.status}: ${msg.detail}`
                  : msg.detail}
              </Alert>
            ))}
          </div>

          {/* Error */}
          {error && (
            <div style={{ marginTop: "20px" }}>
              <Alert severity="error">{error}</Alert>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default UploadPage;
