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
      <div className="text-center">
        <h1 className="font-geist text-2xl font-semibold">Loading...</h1>
        <p className="mt-2 font-satoshi text-slate-600">
          Redirecting you to the dashboard
        </p>
      </div>
    </div>
  );
}
