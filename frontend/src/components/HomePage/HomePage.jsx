import React, { useState } from "react";
import AxiosInstance from "../Axios/Axios.jsx";
import Textarea from "@mui/joy/Textarea";
import Box from "@mui/joy/Box";
import { Button, CircularProgress, Alert } from "@mui/material";
import "./HomePage.css";

const HomePage = () => {
  const [search, setSearch] = useState("");
  const [input_text, setInputText] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false); // <- состояние загрузки
  const [error, setError] = useState(null); // <- состояние ошибки

  const handleSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(""); // очищаем старый результат
    console.log(input_text);

    AxiosInstance.post(`api/decision_upload/`, {
      input_text,
    })
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

    AxiosInstance.post(`api/search/`, {
      search,
    })
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
      <div key={index} className="result-item" style={{ marginBottom: "15px", padding: "10px", border: "1px solid #ccc", borderRadius: "8px" }}>
        <p><strong>Document №{index + 1}</strong></p>
        <p><strong>Текст:</strong> {item.text}</p>
        <p><strong>Коефіцієнт схожості:</strong> {item.similarity_score.toFixed(3)}</p>
        {item.metadata && (
          <p><strong>Decision ID:</strong> {item.metadata.decision_number}</p>
        )}
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
