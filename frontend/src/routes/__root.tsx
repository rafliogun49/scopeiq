import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import type { QueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
        <a href="/" className="text-xl font-semibold text-blue-600">
          ScopeIQ
        </a>
        {isAuthenticated && (
          <Button
            variant="outline"
            onClick={() => {
              logout();
              window.location.href = "/login";
            }}
            className="rounded-xl font-geist text-sm"
          >
            Logout
          </Button>
        )}
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}
