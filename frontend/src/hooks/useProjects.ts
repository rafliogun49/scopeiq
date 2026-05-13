import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { qk } from "@/lib/qk";

export interface Project {
  id: string;
  name: string;
  idea: string;
  known_competitors: string[];
  archived: boolean;
  created_at: string;
}

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: qk.projects(),
    queryFn: () => api.get<Project[]>("/projects"),
  });
}

export function useProject(id: string) {
  return useQuery<Project>({
    queryKey: qk.project(id),
    queryFn: () => api.get<Project>(`/projects/${id}`),
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; idea: string; known_competitors?: string[] }) =>
      api.post<Project>("/projects", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: qk.projects() });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.delete(`/projects/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: qk.projects() });
    },
  });
}
