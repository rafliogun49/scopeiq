import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { api, setToken } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useQueryClient } from "@tanstack/react-query";
import { qk } from "@/lib/qk";

export const Route = createFileRoute("/login")({
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await api.post<{ access_token: string }>("/auth/login", {
        email,
        password,
      });
      setToken(response.access_token);

      // Invalidate auth query so useAuth() re-fetches
      queryClient.invalidateQueries({ queryKey: qk.me() });

      navigate({ to: "/projects" });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Invalid email or password",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[calc(100dvh-5rem)] max-w-6xl items-center justify-center px-6 py-12">
      <Card className="w-full max-w-md rounded-[2rem] border border-slate-200/70 bg-white/95 shadow-[0_28px_80px_-45px_rgba(15,23,42,0.45)]">
        <CardHeader className="border-b border-slate-200/70 px-6 pb-6 pt-6 text-center">
          <p className="font-geist text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
            ScopeIQ access
          </p>
          <CardTitle className="mt-2 font-geist text-3xl font-semibold tracking-tight text-slate-950">
            Welcome back
          </CardTitle>
          <CardDescription className="font-satoshi text-sm text-slate-600">
            Enter your credentials to sign in
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4 px-6 py-6">
            {error && (
              <div className="rounded-2xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email" className="font-geist text-sm font-medium">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rounded-xl"
              />
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="password"
                className="font-geist text-sm font-medium"
              >
                Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="rounded-xl"
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4 border-t border-slate-200/70 bg-white/80 p-6">
            <Button
              type="submit"
              className="w-full"
              disabled={loading || !email || !password}
            >
              {loading ? "Signing in..." : "Sign in"}
            </Button>

            <p className="text-center text-sm text-slate-600">
              Don't have an account?{" "}
              <a
                href="/signup"
                className="font-medium text-emerald-800 hover:underline"
              >
                Sign up
              </a>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
