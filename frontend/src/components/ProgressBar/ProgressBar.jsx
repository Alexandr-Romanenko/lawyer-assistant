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

export default function ProgressBar({ taskIds, messages }) {
  const [completed, setCompleted] = useState([]);

  useEffect(() => {
    if (!taskIds || taskIds.length === 0) return;

    const relevantIds = new Set(taskIds);
    const completedStatuses = ["done", "already_done", "success"];

    const newCompleted = messages
      .filter(
        (msg) =>
          relevantIds.has(msg.decision_id) &&
          completedStatuses.includes(msg.status)
      )
      .map((msg) => msg.decision_id);

    setCompleted(Array.from(new Set(newCompleted)));
  }, [messages, taskIds]);

  const progress = taskIds?.length
    ? (completed.length / taskIds.length) * 100
    : 0;

  return (
    <Box sx={{ width: "100%", my: 2 }}>
      <Typography variant="h6" gutterBottom>
        Обробка рішень
      </Typography>
      <LinearProgressWithLabel value={progress} />
      <Typography variant="body2" mt={1}>
        {`Виконано ${completed.length} з ${taskIds.length}`}
      </Typography>
    </Box>
  );
}

ProgressBar.propTypes = {
  taskIds: PropTypes.array.isRequired,
  messages: PropTypes.array.isRequired,
};
