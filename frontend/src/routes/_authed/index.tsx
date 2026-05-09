import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { useAuth } from "@/hooks/useAuth";

export const Route = createFileRoute("/_authed")({
  component: AuthLayout,
  beforeLoad: async () => {
    // This runs before the route loads
    // We'll do a client-side check in the component
  },
});

function AuthLayout() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    throw redirect({ to: "/login" });
  }

  return <Outlet />;
}
