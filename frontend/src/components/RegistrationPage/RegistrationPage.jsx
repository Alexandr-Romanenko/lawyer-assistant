import Alert from "@mui/joy/Alert";
import CircularProgress from "@mui/joy/CircularProgress";
import { useForm } from "react-hook-form";
import AxiosInstance from "../Axios/Axios.jsx";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { Button } from "@mui/material";
import { useState } from "react";
import PasswordField from "../FormFields/PasswordField.jsx";
import InputField from "../FormFields/InputField.jsx";
import Box from "@mui/joy/Box";
import "./RegistrationPage.css";

const schema = yup.object({
  email: yup
    .string()
    .email("Field expects an email")
    .required("Email is a required field"),
  firstName: yup
    .string()
    .required("First name is a required field")
    .max(254)
    .matches(
      /^[A-Za-zА-Яа-яІіЇїЄєҐґ'’\- ]+$/,
      "First name must contain only letters"
    ),
  secondName: yup
    .string()
    .required("Second name is a required field")
    .max(254)
    .matches(
      /^[A-Za-zА-Яа-яІіЇїЄєҐґ'’\- ]+$/,
      "Second name must contain only letters"
    ),
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
  password2: yup
    .string()
    .required("Password confirmation is a required field")
    .oneOf([yup.ref("password"), null], "Passwords must match"),
});

const RegistrationPage = () => {
  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isValid },
  } = useForm({
    resolver: yupResolver(schema),
    mode: "onChange",
    defaultValues: {
      firstName: "",
      secondName: "",
      email: "",
      password: "",
      password2: "",
    },
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState("");

  const onSubmit = (data) => {
    setLoading(true);
    setError(null);
    setSuccessMsg("");

    AxiosInstance.post(`user/register/`, {
      email: data.email,
      first_name: data.firstName,
      second_name: data.secondName,
      password: data.password,
      password2: data.password2,
    })
      .then((res) => {
        console.log("Registration successful:", res.data);
        setSuccessMsg("Реєстрація пройшла успішно!");
        reset();
      })
      .catch((err) => {
        console.error("Registration error:", err);

        if (err.response) {
          const backendErrors = err.response;

          // Получаем первое сообщение об ошибке
          const firstError = Object.values(backendErrors)?.[0]?.[0];

          if (firstError) {
            setError(firstError); // показываем только одну ошибку
          } else {
            setError("Помилка під час реєстрації. Спробуйте ще раз.");
          }
        } else {
          setError("Помилка під час реєстрації. Спробуйте ще раз.");
        }
      })

      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <section>
      <div className="container">
        <div className="registratuion-page-container">
          <div className="hero-section">
            <h1 className="hero-title">User registration</h1>
          </div>

          <form className="registration-form" onSubmit={handleSubmit(onSubmit)}>
            {/* First name */}
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
                id={"firstName"}
                label={"First name"}
                name={"firstName"}
                control={control}
              />
            </Box>

            {/* Second name */}
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
                id={"secondName"}
                label={"Second name"}
                name={"secondName"}
                control={control}
              />
            </Box>

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

            {/* Password2 */}
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
                id={"password2"}
                label={"Confirm password"}
                name={"password2"}
                control={control}
              />
            </Box>

            <Button
              variant="contained"
              type="submit"
              disabled={!isValid || loading}
              sx={{ width: "30%" }}
            >
              {loading ? "Registration..." : "Register"}
            </Button>
          </form>

          {loading && (
            <div style={{ marginTop: "20px" }}>
              <CircularProgress />
              <p>Registration is ongoing...</p>
            </div>
          )}

          {error && (
            <div style={{ marginTop: "20px" }}>
              <Alert severity="error">{error}</Alert>
            </div>
          )}

          {successMsg && (
            <div style={{ marginTop: "20px" }}>
              <Alert severity="success">{successMsg}</Alert>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default RegistrationPage;
