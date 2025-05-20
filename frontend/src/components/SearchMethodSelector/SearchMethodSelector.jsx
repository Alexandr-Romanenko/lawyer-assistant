import React from "react";
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";

const methodDescriptions = {
  similarity_search: "Пошук за схожістю",
  similarity_search_by_vector: "Пошук за вектором без оцінки релевантності",
  similarity_search_by_vector_with_relevance_scores:
    "Пошук за вектором з оцінкою релевантності",
};

export default function SearchMethodSelector({ value, onChange }) {
  const handleChange = (event) => {
    onChange(event.target.value);
  };

  return (
    <FormControl fullWidth variant="outlined" margin="normal">
      <InputLabel id="search-method-label">Метод пошуку</InputLabel>
      <Select
        labelId="search-method-label"
        value={value}
        onChange={handleChange}
        label="Метод пошуку"
      >
        {Object.entries(methodDescriptions).map(([key, label]) => (
          <MenuItem key={key} value={key}>
            <Typography variant="body2">{label}</Typography>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
