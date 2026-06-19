import { useEffect, useState } from "react";

export function useWebSocket(projectId) {
  // store the latest alert
  const [alert, setAlert] = useState({});

  // connect to the websocket backend endpoint on load
  useEffect(() => {
    // set up websocket connection
    const ws = new WebSocket(`ws://localhost:8000/ws/${projectId}`);

    // listen for incoming messages
    ws.addEventListener("message", (event) => {
      setAlert(JSON.parse(event.data));
    });

    // close the connection
    return () => {
      ws.close();
    };
  }, [projectId]);

  // send the latest alert received on return
  return alert;
}
