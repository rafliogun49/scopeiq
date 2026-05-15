import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";
import type { QueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";

interface RouterContext {
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className="scopeiq-app-bg relative min-h-screen text-slate-950">
      <header className="sticky top-0 z-20 border-b border-slate-200/60 bg-white/35 px-6 py-3 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <a
            href="/"
            className="group inline-flex items-center gap-3 rounded-xl px-2 py-1.5 transition-colors hover:bg-emerald-50/70"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-700 font-geist text-sm font-semibold text-white shadow-[0_12px_28px_-18px_rgba(4,120,87,0.9)]">
              SI
            </span>
            <span className="font-geist text-lg font-semibold tracking-tight text-emerald-800">
              Scope<span className="text-slate-950">IQ</span>
            </span>
          </a>
          <div className="flex items-center gap-2">
            {isAuthenticated && (
              <>
                <a
                  href="/projects"
                  className="hidden rounded-xl px-3 py-2 font-geist text-sm font-medium text-slate-600 transition-colors hover:bg-white/50 hover:text-slate-950 sm:inline-flex"
                >
                  Projects
                </a>
                <Button
                  variant="outline"
                  onClick={() => {
                    logout();
                    window.location.href = "/login";
                  }}
                  size="sm"
                  className="gap-1.5"
                >
                  <LogOut className="h-3.5 w-3.5" strokeWidth={1.9} />
                  <span>Logout</span>
                </Button>
              </>
            )}
          </div>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
