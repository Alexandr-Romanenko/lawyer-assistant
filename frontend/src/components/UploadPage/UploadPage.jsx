import React, { useEffect, useRef, useState } from "react";

import "./HomePage.css";
import ProgressBar from "../ProgressBar/ProgressBar.jsx";

import AxiosInstance from "../Axios/Axios.jsx";
import Textarea from "@mui/joy/Textarea";
import Box from "@mui/joy/Box";
import { Button, CircularProgress, Alert } from "@mui/material";

const UploadPage = () => {

  const [input_text, setInputText] = useState("");
  const [uploadingResult, setUploadingResult] = useState("");
  const [loading, setLoading] = useState(false); // состояние загрузки
  const [error, setError] = useState(null); // состояние ошибки
  const [messages, setMessages] = useState([]);

  const socketRef = useRef(null); // сохраняем сокет

  // web-socket
  useEffect(() => {
    const token = localStorage.getItem("access");
    const ws = new WebSocket(`ws://localhost:8000/ws/progress/?token=${token}`);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    console.log("WebSocket message:", data);

    // Разделяем по типу сообщения
    if (data.type === "progress") {
      // Можно передать в прогрессбар через setProgress(data)
      // или просто тоже пушить в messages
      setMessages((prev) => [...prev, data]);
    } else if (data.type === "status") {
      setMessages((prev) => [...prev, data]);
    } else {
      setMessages((prev) => [...prev, data]); // общий случай
    }
  } catch (err) {
    console.error("Failed to parse WebSocket message", err);
  }
};

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
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
    setUploadingResult(""); // очищаем старый результат
    if (!input_text.trim()) {
      setError("Введіть текст рішення перед завантаженням.");
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
        console.log("The analysis was successful:", res.data);
        setUploadingResult(res.data);
      })
      .catch((err) => {
        console.error("Errors as a result of analysing the decision:", err);
        setError("Помилка під час аналізу. Спробуйте ще раз.");
      })
      .finally(() => {
        setLoading(false); // отключаем индикатор загрузки
      });
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
              В поле "Input text" потрібно вставити рішення, які потрібно завантажити до векторної БД
            </p>
          </div>

          {/* Form to upload decisions */}
          <div className="form-block">
            <form onSubmit={handleLoading}>
              <div className="create-quiz-form">
                <div className="form-items">
                  <Box
                    sx={{
                      py: 2,
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
                        maxRows={1}
                      />
                    </div>
                  </Box>
                </div>
                <Button
                  variant="contained"
                  type="submit"
                  sx={{ width: "10%" }}
                  disabled={loading}
                >
                  {loading ? "Uploading..." : "Upload"}
                </Button>
              </div>
            </form>
          </div>

          {/* Progress Bar */}
          {uploadingResult && uploadingResult.ids_array && uploadingResult.user_channel_id && (
  <ProgressBar
  taskIds={uploadingResult.ids_array}
  userChannelId={uploadingResult.user_channel_id}
  socket={socketRef.current}
  messages={messages}
/>
)}

          {/* WebSocket messages area */}
          <div
            style={{
              marginTop: "20px",
              maxHeight: "300px",
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
                severity="info"
                style={{ marginBottom: "5px", fontSize: "0.85rem" }}
              >
                [ID: {msg.decision_id}] → {msg.status}: {msg.detail}
              </Alert>
            ))}
          </div>

          {/* Лоадер */}
          {loading && (
            <div style={{ marginTop: "20px" }}>
              <CircularProgress />
              <p>Завантаження триває... Зачекайте, будь ласка.</p>
            </div>
          )}

          {/* Ошибка */}
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
