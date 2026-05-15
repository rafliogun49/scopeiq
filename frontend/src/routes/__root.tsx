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
    <div className="min-h-screen bg-[#f7f8f5] text-slate-950">
      <header className="sticky top-0 z-20 border-b border-slate-200/70 bg-[#f7f8f5]/90 px-6 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <a
            href="/"
            className="font-geist text-xl font-semibold tracking-tight text-emerald-800"
          >
            Scope<span className="text-slate-950">IQ</span>
          </a>
          {isAuthenticated && (
            <Button
              variant="outline"
              onClick={() => {
                logout();
                window.location.href = "/login";
              }}
              size="sm"
            >
              Logout
            </Button>
          )}
        </div>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
