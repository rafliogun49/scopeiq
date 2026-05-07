/**
 * Centralized TanStack Query keys — per PRD §15.3.
 * Import from here to avoid string typos.
 */
export const qk = {
  me: () => ["me"] as const,
  projects: () => ["projects"] as const,
  project: (id: string) => ["projects", id] as const,
  runs: (projectId: string) => ["projects", projectId, "runs"] as const,
  run: (id: string) => ["runs", id] as const,
  messages: (projectId: string) => ["projects", projectId, "messages"] as const,
};
