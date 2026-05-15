import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api, clearToken } from '@/lib/api';
import { qk } from '@/lib/qk';

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export function useAuth() {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery<User | null>({
    queryKey: qk.me(),
    queryFn: () => api.get<User>('/auth/me'),
    retry: false,
  });

  const logout = () => {
    clearToken();
    queryClient.clear();
  };

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    logout,
  };
}
