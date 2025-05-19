import React, { useState } from "react";

import "./HomePage.css";
import SearchMethodSelector from "../SearchMethodSelector/SearchMethodSelector.jsx";

import AxiosInstance from "../Axios/Axios.jsx";
import Textarea from "@mui/joy/Textarea";
import Box from "@mui/joy/Box";
import { Button, CircularProgress, Alert } from "@mui/material";
import { Container } from "@mui/joy";
import Typography from "@mui/material/Typography";


const HomePage = () => {
  const [search, setSearch] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false); // состояние загрузки
  const [error, setError] = useState(null); // состояние ошибки

  const [method, setMethod] = useState("similarity_search");

  // Handel search request
  const handleSearch = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(""); // очищаем старый результат
    if (!search.trim()) {
      setError("Введіть текст пошуку.");
      return;
    }

    AxiosInstance.post(
      `api/search/`,
      { search },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access")}`,
        },
      }
    )
      .then((res) => {
        console.log("The analysis was successful:", res.data);
        setResult(res.data.search_result);
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
              В полі "Search" потрібно описати ситуацію, тотожність якої
              Ви шукаєте або вказати ключові слова для пошуку
            </p>
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

              {/* Choose type of search*/}
              <Container maxWidth="sm" sx={{ mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Пошук рішень
                </Typography>
                <SearchMethodSelector value={method} onChange={setMethod} />
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSearch}
                  sx={{ mt: 2 }}
                >
                  Знайти
                </Button>
              </Container>
            </form>
          </div>

          {/* Лоадер */}
          {loading && (
            <div style={{ marginTop: "20px" }}>
              <CircularProgress />
              <p>Пошук триває... Зачекайте, будь ласка.</p>
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
                <div
                  key={index}
                  className="result-item"
                  style={{
                    marginBottom: "20px",
                    padding: "15px",
                    border: "1px solid #ccc",
                    borderRadius: "8px",
                  }}
                >
                  <p>
                    <strong>Рішення №{index + 1}</strong>
                  </p>
                  <p>
                    <strong>Decision ID:</strong> {item.decision_id}
                  </p>
                  <p>
                    <strong>Макс. коефіцієнт схожості:</strong>{" "}
                    {item.max_score.toFixed(3)}
                  </p>

                  <div style={{ marginTop: "10px", paddingLeft: "10px" }}>
                    <p>
                      <strong>Схожі фрагменти:</strong>
                    </p>
                    {item.chunks.map((chunk, chunkIndex) => (
                      <div
                        key={chunkIndex}
                        style={{
                          marginBottom: "10px",
                          padding: "10px",
                          backgroundColor: "#f9f9f9",
                          borderRadius: "6px",
                        }}
                      >
                        <p>{chunk.text}</p>
                        <p>
                          <em>
                            Коефіцієнт: {chunk.similarity_score.toFixed(3)}
                          </em>
                        </p>
                        {chunk.metadata?.decision_number && (
                          <p>
                            <em>
                              Номер рішення: {chunk.metadata.decision_number}
                            </em>
                          </p>
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
