/**
 * SSE types — mirrors backend/app/schemas/events.py (contract §7.2).
 * Lock by Day 3 (pair: A + C).
 */

export type EventType =
  | "plan"
  | "agent_started"
  | "tool_called"
  | "agent_finished"
  | "error"
  | "log";

export type AgentName = "orchestrator" | "scraper" | "social" | "synthesizer" | null;

export interface RunEvent {
  type: EventType;
  agent: AgentName;
  payload: Record<string, unknown>;
  timestamp: string; // ISO8601
}

export interface RunCompleteEvent {
  run_id: string;
  status: "completed" | "failed" | "cancelled";
}

/**
 * Opens an SSE connection to /runs/:runId/stream.
 * Returns a cleanup function.
 *
 * TODO (C-PR5): use this in the useRunStream hook.
 */
export function openRunStream(
  runId: string,
  onEvent: (event: RunEvent) => void,
  onComplete: (event: RunCompleteEvent) => void,
  onError?: (err: Event) => void
): () => void {
  const url = `${import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1"}/runs/${runId}/stream`;
  const es = new EventSource(url);

  es.addEventListener("progress", (e: MessageEvent) => {
    onEvent(JSON.parse(e.data) as RunEvent);
  });

  es.addEventListener("complete", (e: MessageEvent) => {
    onComplete(JSON.parse(e.data) as RunCompleteEvent);
    es.close();
  });

  if (onError) es.onerror = onError;

  return () => es.close();
}
