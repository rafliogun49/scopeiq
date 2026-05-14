import { useState, useEffect } from "react";

export interface RunEvent {
  type: "plan" | "agent_started" | "tool_called" | "agent_finished" | "error" | "log";
  agent: "orchestrator" | "scraper" | "social" | "synthesizer" | null;
  payload: Record<string, unknown>;
  timestamp: string;
}

export function useRunStream(runId: string) {
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [status, setStatus] = useState<"connecting" | "streaming" | "complete" | "error">(
    "connecting"
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;

    setStatus("connecting");
    setEvents([]);
    setError(null);

    const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
    const token = localStorage.getItem("access_token");

    const eventSource = new EventSource(`${baseUrl}/runs/${runId}/stream`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    } as EventSourceInit);

    eventSource.onopen = () => {
      setStatus("streaming");
    };

    eventSource.addEventListener("progress", (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents((prev) => [...prev, data]);
      } catch (err) {
        console.error("Failed to parse SSE event:", err);
      }
    });

    eventSource.addEventListener("complete", (event) => {
      try {
        const data = JSON.parse(event.data);
        setStatus(data.status as "complete" | "error");
        eventSource.close();
      } catch (err) {
        console.error("Failed to parse complete event:", err);
      }
    });

    eventSource.onerror = (err) => {
      console.error("SSE Error:", err);
      setStatus("error");
      setError("Connection lost");
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [runId]);

  return {
    events,
    status,
    error,
    isStreaming: status === "streaming" || status === "connecting",
    isComplete: status === "complete",
  };
}
