import axios from "axios";

// const isDevelopment = import.meta.env.MODE === 'development'
// const BaseUrl = isDevelopment ? import.meta.env.VITE_API_BASE_URL_LOCAL : import.meta.env.VITE_API_BASE_URL_DEPLOY
//
// const AxiosInstance = axios.create({
//     baseURL: BaseUrl,
//     timeout: 5000,
//     headers: {
//         "Content-Type":"application/json",
//         accept: "application/json"
//     }
// });

// Settings for development mode
const baseUrl = "http://127.0.0.1:8000/";
const AxiosInstance = axios.create({
  baseURL: baseUrl,
  //timeout: 5000,
  timeout: 120000, // 2 минуты (в миллисекундах)
  headers: {
    "Content-Type": "application/json",
    accept: "application/json",
  },
});

export default AxiosInstance;