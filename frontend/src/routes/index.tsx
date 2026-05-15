import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        navigate({ to: "/projects" });
      } else {
        navigate({ to: "/login" });
      }
    }
  }, [isAuthenticated, isLoading, navigate]);

  return (
    <div className="flex min-h-[100dvh] items-center justify-center">
      <div className="rounded-[2rem] border border-slate-200/70 bg-white/90 px-8 py-7 text-center shadow-[0_28px_80px_-45px_rgba(15,23,42,0.45)]">
        <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-700 font-geist text-sm font-semibold text-white">
          SI
        </div>
        <h1 className="font-geist text-2xl font-semibold tracking-tight text-slate-950">
          Loading workspace
        </h1>
        <p className="mt-2 font-satoshi text-sm text-slate-600">
          Redirecting you to the dashboard
        </p>
      </div>
    </div>
  );
}
