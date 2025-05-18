import React from "react";
import IconButton from "@mui/material/IconButton";
import OutlinedInput from "@mui/material/OutlinedInput";
import InputLabel from "@mui/material/InputLabel";
import InputAdornment from "@mui/material/InputAdornment";
import FormControl from "@mui/material/FormControl";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { FormHelperText } from "@mui/material";
import { Controller } from "react-hook-form";

export default function PasswordField(props) {
  const [showPassword, setShowPassword] = React.useState(false);
  const { id, label, name, control } = props;

  const getAutoComplete = (name) => {
    if (name === "password") return "new-password";
    if (name === "password2") return "new-password"; // для подтверждения пароля
    return "off";
  };

  const handleClickShowPassword = () => setShowPassword((show) => !show);

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  return (
    <Controller
      id={id || name}
      name={name}
      control={control}
      render={({ field: { onChange, value }, fieldState: { error } }) => (
        <FormControl variant="outlined" className={"myForm"}>
          <InputLabel htmlFor={id || name}>{label}</InputLabel>
          <OutlinedInput
            id={id || name}
            name={name}
            autoComplete={getAutoComplete(name)} // добавляем autoComplete
            onChange={onChange}
            value={value}
            error={!!error}
            type={showPassword ? "text" : "password"}
            endAdornment={
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={handleClickShowPassword}
                  onMouseDown={handleMouseDownPassword}
                  edge="end"
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            }
            label={label}
          />
          <FormHelperText sx={{ color: "#d32f2f" }}>
            {error?.message}
          </FormHelperText>
        </FormControl>
      )}
    />
  );
}

// export default function PasswordField(props) {
//   const [showPassword, setShowPassword] = React.useState(false);
//   const { id, label, name, control} = props
//   const inputId = id || name;
//
//   const handleClickShowPassword = () => setShowPassword((show) => !show);
//
//   const handleMouseDownPassword = (event) => {
//     event.preventDefault();
//   };
//
//   return (
//     <Controller
//         id={id || name}
//         name = {name}
//         control = {control}
//         render = {({
//             field:{onChange, value},
//             fieldState : {error},
//             formState,
//         }) =>(
//
//           <FormControl variant="outlined" className={"myForm"}>
//           <InputLabel htmlFor={inputId}>{label}</InputLabel>
//           <OutlinedInput
//             id={inputId}
//             name={name}
//             autoComplete={name}
//             onChange={onChange}
//             value={value}
//             error = {!!error}
//             type={showPassword ? 'text' : 'password'}
//             endAdornment={
//               <InputAdornment position="end">
//                 <IconButton
//                   aria-label="toggle password visibility"
//                   onClick={handleClickShowPassword}
//                   onMouseDown={handleMouseDownPassword}
//                   edge="end"
//                 >
//                   {showPassword ? <VisibilityOff /> : <Visibility />}
//                 </IconButton>
//               </InputAdornment>
//             }
//             label={label}
//           />
//         <FormHelperText sx={{color:"#d32f2f"}}> {error?.message} </FormHelperText>
//         </FormControl>
//     )
//   }
//  />
//   );
// }
