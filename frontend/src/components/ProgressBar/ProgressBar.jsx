import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { LinearProgress, Box, Typography } from "@mui/material";

function LinearProgressWithLabel({ value }) {
  return (
    <Box display="flex" alignItems="center">
      <Box width="100%" mr={1}>
        <LinearProgress variant="determinate" value={value} />
      </Box>
      <Box minWidth={35}>
        <Typography variant="body2" color="textSecondary">{`${Math.round(
          value
        )}%`}</Typography>
      </Box>
    </Box>
  );
}

LinearProgressWithLabel.propTypes = {
  value: PropTypes.number.isRequired,
};

export default function ProgressBar({ taskIds, userChannelId }) {
  const [completed, setCompleted] = useState([]);

  useEffect(() => {
    if (!taskIds || taskIds.length === 0) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/user/${userChannelId}/`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status === "success" || data.status === "done") {
        setCompleted((prev) => {
          if (!prev.includes(data.decision_id)) {
            return [...prev, data.decision_id];
          }
          return prev;
        });
      }
    };

    return () => {
      ws.close();
    };
  }, [taskIds, userChannelId]);

const progress = taskIds?.length
  ? (completed.length / taskIds.length) * 100
  : 0;

  return (
    <Box sx={{ width: "100%" }}>
      <Typography variant="h6" gutterBottom>
        Обработка решений
      </Typography>
      <LinearProgressWithLabel value={progress} />
      <Typography variant="body2" mt={1}>
        {`Завершено ${completed.length} из ${taskIds.length}`}
      </Typography>
    </Box>
  );
}

ProgressBar.propTypes = {
  taskIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  userChannelId: PropTypes.string.isRequired,
};
