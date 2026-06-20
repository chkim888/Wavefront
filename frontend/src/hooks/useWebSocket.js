import { useEffect, useState } from "react";

export function useWebSocket(projectId) {
  // store the latest alert
  const [alert, setAlert] = useState({});

  // connect to the websocket backend endpoint on load
  useEffect(() => {
    // do not define websocket if projectId not valid
    if (!projectId) return;

    // set up websocket connection
    const ws = new WebSocket(`ws://localhost:8000/ws/${projectId}`);

    // listen for incoming messages
    const handleMessage = (event) => {
      setAlert(JSON.parse(event.data));
    };
    ws.addEventListener("message", handleMessage);

    // close the connection
    return () => {
      // remove event listener on closing
      ws.removeEventListener("message", handleMessage);
      ws.close();
    };
  }, [projectId]);

  // send the latest alert received on return
  return alert;
}
