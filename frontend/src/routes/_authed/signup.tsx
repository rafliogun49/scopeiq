import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useForm } from "@tanstack/react-form";
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

export const Route = createFileRoute("/_authed/signup")({
  component: SignupPage,
});

interface SignupForm {
  email: string;
  password: string;
  confirmPassword: string;
}

function SignupPage() {
  const navigate = useNavigate();

  const form = useForm<SignupForm>({
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
    validators: {
      onChange: ({ value }) => {
        const errors: Partial<Record<keyof SignupForm, string>> = {};
        if (!value.email) {
          errors.email = "Email is required";
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.email)) {
          errors.email = "Invalid email format";
        }
        if (!value.password) {
          errors.password = "Password is required";
        } else if (value.password.length < 6) {
          errors.password = "Password must be at least 6 characters";
        }
        if (value.confirmPassword && value.password !== value.confirmPassword) {
          errors.confirmPassword = "Passwords do not match";
        }
        return errors;
      },
    },
    onSubmit: async ({ value }) => {
      try {
        const response = await api.post<{ token: string }>("/auth/signup", {
          email: value.email,
          password: value.password,
        });
        setToken(response.token);
        navigate({ to: "/projects" });
      } catch (error) {
        form.setErrorMap({
          form: "Failed to create account. Email may already be in use.",
        });
      }
    },
  });

  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-slate-50 px-4 py-12">
      <Card className="w-full max-w-md rounded-[2rem] border border-slate-200/50 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="font-geist text-2xl font-semibold tracking-tight">
            Create an account
          </CardTitle>
          <CardDescription className="font-satoshi text-slate-600">
            Enter your details to get started
          </CardDescription>
        </CardHeader>
        <form onSubmit={form.handleSubmit}>
          <CardContent className="space-y-4">
            {form.state.errors.form && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {form.state.errors.form}
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
                value={form.state.values.email}
                onChange={(v) => form.setFieldValue("email", v)}
                onBlur={form.handleBlur}
                className="rounded-xl"
              />
              {form.state.fieldMeta.email?.errors && (
                <p className="text-sm text-red-600">
                  {form.state.fieldMeta.email.errors.join(", ")}
                </p>
              )}
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
                value={form.state.values.password}
                onChange={(v) => form.setFieldValue("password", v)}
                onBlur={form.handleBlur}
                className="rounded-xl"
              />
              {form.state.fieldMeta.password?.errors && (
                <p className="text-sm text-red-600">
                  {form.state.fieldMeta.password.errors.join(", ")}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="confirmPassword"
                className="font-geist text-sm font-medium"
              >
                Confirm Password
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="••••••••"
                value={form.state.values.confirmPassword}
                onChange={(v) => form.setFieldValue("confirmPassword", v)}
                onBlur={form.handleBlur}
                className="rounded-xl"
              />
              {form.state.fieldMeta.confirmPassword?.errors && (
                <p className="text-sm text-red-600">
                  {form.state.fieldMeta.confirmPassword.errors.join(", ")}
                </p>
              )}
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button
              type="submit"
              className="w-full rounded-xl font-geist font-medium active:scale-[0.98] transition-transform"
              disabled={form.state.isSubmitting}
            >
              {form.state.isSubmitting
                ? "Creating account..."
                : "Create account"}
            </Button>

            <p className="text-center text-sm text-slate-600">
              Already have an account?{" "}
              <a
                href="/login"
                className="font-medium text-primary hover:underline"
                onClick={(e) => {
                  e.preventDefault();
                  navigate({ to: "/login" });
                }}
              >
                Sign in
              </a>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
