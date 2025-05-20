import React, { useState } from "react";

import "./SearchPage.css";
import SearchMethodSelector from "../SearchMethodSelector/SearchMethodSelector.jsx";

import AxiosInstance from "../Axios/Axios.jsx";
import Textarea from "@mui/joy/Textarea";
import Box from "@mui/joy/Box";
import { Button, CircularProgress, Alert } from "@mui/material";
import Typography from "@mui/material/Typography";

const SearchPage = () => {
  const [search, setSearch] = useState("");
  const [method, setMethod] = useState("similarity_search");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handel search request
  const handleSearch = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult("");
    if (!search.trim()) {
      setError("Введіть текст пошуку.");
      setLoading(false);
      return;
    }

    AxiosInstance.post(
      `api/search/`,
      { search, method },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access")}`,
        },
      }
    )
      .then((res) => {
        setResult(res.data.search_result);
      })
      .catch((err) => {
        const message = err.response?.data?.error || "Щось пішло не так";
        setError(message);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  // Handel clean field
  const handleCleanField = () => {
    setSearch("");
    setError(null);
    setResult(""); // To think it is necessary here
  };

  return (
    <section>
      <div className="container">
        <div className="search-page-container">
          <div className="hero-section">
            <h1 className="hero-title">Search assistant</h1>
          </div>
          <div className="use-rules-section">
            <h3>Використання додатку:</h3>
            <div className="use-rules-description">
              <p>
                В полі "Search" потрібно описати ситуацію, тотожність якої Ви
                шукаєте або вказати ключові слова для пошуку
              </p>
              <p>Доступні наступні методи пошуку:</p>
              <div className="use-rules-items">
                <p>
                  1. Пошук за схожістю (за замовчуванням) - здійснює пошук за
                  ключовими словами{" "}
                </p>
                <p>
                  2. Пошук за вектором без оцінки релевантності - шукає за
                  змістом, не надаючи оцінку подібності
                </p>
                <p>
                  3. Пошук за вектором з оцінкою релевантності - шукає за
                  змістом та надає оцінку подібності
                </p>
              </div>
            </div>
          </div>

          {/* Form to search decisions */}
          <div className="form-block">
            <form onSubmit={handleSearch}>
              <div className="search-form-block">
                {/* Choose type of search*/}
                <Box maxWidth="sm" sx={{ mt: 4 }}>
                  <Typography variant="h5" gutterBottom>
                    Пошук рішень
                  </Typography>
                  <SearchMethodSelector value={method} onChange={setMethod} />
                </Box>

                {/* Search field */}
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

                {/* Search button */}
                <Button
                  variant="contained"
                  type="submit"
                  sx={{ width: "10%", marginTop: "30px", marginRight: "30px" }}
                  disabled={loading || !search.trim()}
                >
                  {loading ? "Searching..." : "Search"}
                </Button>

                {/* Clean field button */}
                <Button
                  variant="contained"
                  type="button"
                  sx={{ width: "10%", marginTop: "30px" }}
                  onClick={handleCleanField}
                  disabled={!search.trim()}
                >
                  Clean
                </Button>
              </div>
            </form>
          </div>

          {/* Loader */}
          {loading && (
            <div style={{ marginTop: "20px" }}>
              <CircularProgress />
              <p>Пошук триває... Зачекайте, будь ласка.</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{ marginTop: "20px" }}>
              <Alert severity="error">{error}</Alert>
            </div>
          )}

          {/* Result */}
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

export default SearchPage;
