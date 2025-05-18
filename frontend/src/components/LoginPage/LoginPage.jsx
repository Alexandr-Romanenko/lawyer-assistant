import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { Button } from "@mui/material";
import Alert from "@mui/joy/Alert";
import CircularProgress from "@mui/joy/CircularProgress";
import Box from "@mui/joy/Box";
import { Link, useNavigate } from "react-router-dom";

import AxiosInstance from "../Axios/Axios.jsx";
import InputField from "../FormFields/InputField.jsx";
import PasswordField from "../FormFields/PasswordField.jsx";

import "./LoginPage.css";

const schema = yup.object({
  email: yup
    .string()
    .email("Field expects an email")
    .required("Email is a required field"),
  password: yup
    .string()
    .required("Password is a required field")
    .min(8, "Password must be at least 8 characters")
    .matches(/[A-Z]/, "Password must contain at least one uppercase letter")
    .matches(/[a-z]/, "Password must contain at least one lower case letter")
    .matches(/[0-9]/, "Password must contain at least one number")
    .matches(
      /[!@#$%^&*(),.?":;{}|<>+]/,
      "Password must contain at least one special character"
    ),
});

const LoginPage = () => {
  const navigate = useNavigate();
  const {
    handleSubmit,
    control,
    reset,
    formState: { errors, isValid },
  } = useForm({
    resolver: yupResolver(schema),
    mode: "onChange",
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState("");

  const onSubmit = (data) => {
    setLoading(true);
    setError(null);
    setSuccessMsg("");

    AxiosInstance.post("user/login/", {
      email: data.email,
      password: data.password,
    })
      .then((response) => {
        setSuccessMsg("Вхід успішний!");
        localStorage.setItem("access", response.data.access);
        localStorage.setItem("refresh", response.data.refresh);
        reset();
        navigate("/home");
      })
      .catch((err) => {
        console.error("Login error:", err);
        setError("Login failed. Please check your credentials.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <section>
      <div className="container">
        <div className="login-page-container">
          <div className="hero-section">
            <h1 className="hero-title">Login</h1>
          </div>

          <form className="login-form" onSubmit={handleSubmit(onSubmit)}>
            {/* Email */}
            <Box
              className={"itemBox"}
              sx={{
                py: 2,
                display: "grid",
                gap: 2,
                alignItems: "center",
                flexWrap: "wrap",
              }}
            >
              <InputField
                id={"email"}
                label={"Email"}
                name={"email"}
                control={control}
              />
            </Box>

            {/* Password */}
            <Box
              className={"itemBox"}
              sx={{
                py: 2,
                display: "grid",
                gap: 2,
                alignItems: "center",
                flexWrap: "wrap",
              }}
            >
              <PasswordField
                id={"password"}
                label={"Password"}
                name={"password"}
                control={control}
              />
            </Box>

            <Button
              variant="contained"
              type="submit"
              disabled={!isValid || loading}
              sx={{ width: "30%" }}
            >
              {loading ? "Logging in..." : "Login"}
            </Button>
          </form>

          {/* Loading */}
          {loading && (
            <div style={{ marginTop: "20px" }}>
              <CircularProgress />
              <p>Login is ongoing...</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{ marginTop: "20px" }}>
              <Alert severity="error">{error}</Alert>
            </div>
          )}

          {/* Success */}
          {successMsg && (
            <div style={{ marginTop: "20px" }}>
              <Alert severity="success">{successMsg}</Alert>
            </div>
          )}

          {/* Links */}
          <Box className={"itemBox links"} sx={{ flexDirection: "column" }}>
            <div className="link-item">
              No account yet? Please <Link to="/register">register</Link>
            </div>
            <div className="link-item">
              Password forgotten? Click{" "}
              <Link to="/request/password_reset">here</Link>
            </div>
          </Box>
        </div>
      </div>
    </section>
  );
};

export default LoginPage;
