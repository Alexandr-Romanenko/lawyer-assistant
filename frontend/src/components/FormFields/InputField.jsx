import React from "react";
import { TextField } from "@mui/material";
import { Controller } from 'react-hook-form';

export default function InputField(props) {
  const { id, label, name, control } = props;

  const getAutoComplete = (name) => {
    switch (name) {
      case 'firstName':
        return 'given-name';
      case 'secondName':
        return 'family-name';
      case 'email':
        return 'email';
      default:
        return 'off'; // Для других полей можно использовать 'off'
    }
  };

  return (
    <Controller
      name={name}
      control={control}
      render={({ field: { onChange, value }, fieldState: { error } }) => (
        <TextField
          id={id || name}
          name={name}
          autoComplete={getAutoComplete(name)} // добавляем autoComplete
          onChange={onChange}
          value={value}
          label={label}
          variant="outlined"
          className="myForm"
          error={!!error}
          helperText={error?.message}
          fullWidth
        />
      )}
    />
  );
}

// export default function InputField(props) {
//   const { id, label, name, control } = props;
//   const inputId = id || name;
//
//   return (
//     <Controller
//       name={name}
//       control={control}
//       render={({ field: { onChange, value }, fieldState: { error } }) => (
//         <TextField
//           id={inputId}
//           name={name}
//           autoComplete={name}
//           onChange={onChange}
//           value={value}
//           label={label}
//           variant="outlined"
//           className="myForm"
//           error={!!error}
//           helperText={error?.message}
//           fullWidth
//         />
//       )}
//     />
//   );
// }
