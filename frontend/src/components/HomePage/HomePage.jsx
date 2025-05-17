import React, {useEffect, useRef, useState} from "react";
import AxiosInstance from "../Axios/Axios.jsx";
import Textarea from "@mui/joy/Textarea";
import Box from "@mui/joy/Box";
import { Button, CircularProgress, Alert } from "@mui/material";
import "./HomePage.css";

const HomePage = () => {
  const [search, setSearch] = useState("");
  const [input_text, setInputText] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false); // состояние загрузки
  const [error, setError] = useState(null); // состояние ошибки
  //const [progress, setProgress] = useState(null); // прогресс загрузки/анализа
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

    // Добавим новое сообщение в список
    setMessages((prev) => [...prev, data]);
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
            if (ws.readyState === 1) {ws.close();}
            }
  }, []);

 const handleSubmit = (event) => {
  event.preventDefault();
  setLoading(true);
  setError(null);
  setResult(""); // очищаем старый результат
  console.log(input_text);

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
      setResult(res.data.result);
    })
    .catch((err) => {
      console.error("Errors as a result of analysing the decision:", err);
      setError("Помилка під час аналізу. Спробуйте ще раз.");
    })
    .finally(() => {
      setLoading(false); // отключаем индикатор загрузки
    });
  };

    const handleSearch = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(""); // очищаем старый результат
    console.log(search);

    AxiosInstance.post(`api/search/`,
      {search},
        {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access")}`,
      },
    }
    )
      .then((res) => {
        console.log("The analysis was successful:", res.data);
        setResult(res.data.result);
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
        <div className="home-page-container">
          <div className="hero-section">
            <h1 className="hero-title">Court decision analyzer</h1>
          </div>
          <div className="use-rules-section">
            <h3>Використання додатку:</h3>
            <p>
              1. В полі "Situation" потрібно описати ситуацію, тотожність якої
              Ви шукаєте
            </p>
            <p>2. В полі "Url" потрібно ввести посилання на рішення суду</p>
            <p>
              3. В полі "Question" Ви можете поставити будь яке питання щодо
              судового рішення, яке Ви надали для аналізу
            </p>
          </div>

          {/* Form to upload decisions */}
          <div className="form-block">
            <form onSubmit={handleSubmit}>
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



          {/* Form to search decisions */}
          <div className="form-block">
            <form onSubmit={handleSearch}>
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
                    <div className="item-text-input">
                      <Textarea
                        name="Soft"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search"
                        variant="soft"
                        maxRows={8}
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
                  {loading ? "Searching..." : "Search"}
                </Button>
              </div>
            </form>
          </div>

{/* WebSocket messages area */}
<div style={{
  marginTop: "20px",
  maxHeight: "300px",
  overflowY: "auto",
  border: "1px solid #ddd",
  borderRadius: "8px",
  padding: "10px",
  backgroundColor: "#f5f5f5"
}}>
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
              <p>Аналіз триває... Зачекайте, будь ласка.</p>
            </div>
          )}

          {/* Ошибка */}
          {error && (
            <div style={{ marginTop: "20px" }}>
              <Alert severity="error">{error}</Alert>
            </div>
          )}

          {/* Результат */}
{result && Array.isArray(result) && result.length > 0 && !loading && (
  <div className="result-block" style={{ marginTop: "20px" }}>
    <h3>Результат пошуку:</h3>
    {result.map((item, index) => (
      <div key={index} className="result-item" style={{ marginBottom: "20px", padding: "15px", border: "1px solid #ccc", borderRadius: "8px" }}>
        <p><strong>Рішення №{index + 1}</strong></p>
        <p><strong>Decision ID:</strong> {item.decision_id}</p>
        <p><strong>Макс. коефіцієнт схожості:</strong> {item.max_score.toFixed(3)}</p>

        <div style={{ marginTop: "10px", paddingLeft: "10px" }}>
          <p><strong>Схожі фрагменти:</strong></p>
          {item.chunks.map((chunk, chunkIndex) => (
            <div key={chunkIndex} style={{ marginBottom: "10px", padding: "10px", backgroundColor: "#f9f9f9", borderRadius: "6px" }}>
              <p>{chunk.text}</p>
              <p><em>Коефіцієнт: {chunk.similarity_score.toFixed(3)}</em></p>
              {chunk.metadata?.decision_number && (
                <p><em>Номер рішення: {chunk.metadata.decision_number}</em></p>
              )}
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
)}
        </div>
      </div>
    </section>
  );
};

export default HomePage;
