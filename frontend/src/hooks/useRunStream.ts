import { useState, useEffect, useCallback } from "react";
import { openRunStream, type RunEvent } from "@/lib/sse";

export function useRunStream(runId: string) {
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [status, setStatus] = useState<"connecting" | "streaming" | "complete" | "error">(
    "connecting"
  );
  const [error, setError] = useState<string | null>(null);

  const handleEvent = useCallback((event: RunEvent) => {
    setEvents((prev) => [...prev, event]);
  }, []);

  const handleComplete = useCallback(() => {
    setStatus("complete");
  }, []);

  const handleError = useCallback((err: Event) => {
    setStatus("error");
    setError("Failed to connect to run stream");
    console.error("SSE Error:", err);
  }, []);

  useEffect(() => {
    setStatus("connecting");
    setEvents([]);
    setError(null);

    const cleanup = openRunStream(runId, handleEvent, handleComplete, handleError);

    return () => {
      cleanup();
    };
  }, [runId, handleEvent, handleComplete, handleError]);

  return {
    events,
    status,
    error,
    isStreaming: status === "streaming" || status === "connecting",
    isComplete: status === "complete",
  };
}
