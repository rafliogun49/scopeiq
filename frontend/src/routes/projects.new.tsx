import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useForm } from "@tanstack/react-form";
import { useCreateProject } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const Route = createFileRoute("/projects/new")({
  component: CreateProjectPage,
});

function CreateProjectPage() {
  const navigate = useNavigate();
  const createProject = useCreateProject();

  const form = useForm({
    defaultValues: {
      name: "",
      idea: "",
      knownCompetitors: "",
    },
    validators: {
      onChange: ({ value }) => {
        const errors: Partial<Record<keyof typeof value, string>> = {};
        if (!value.name) {
          errors.name = "Project name is required";
        }
        if (!value.idea) {
          errors.idea = "Idea description is required";
        } else if (value.idea.length < 20) {
          errors.idea = "Please provide at least 20 characters";
        }
        return errors;
      },
    },
    onSubmit: async ({ value }) => {
      const knownCompetitors = value.knownCompetitors
        ? value.knownCompetitors
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean)
        : [];

      try {
        const project = await createProject.mutateAsync({
          name: value.name,
          idea: value.idea,
          known_competitors: knownCompetitors,
        });
        navigate({
          to: "/projects/$projectId",
          params: { projectId: project.id },
        });
      } catch (error) {
        form.setErrorMap({
          form: "Failed to create project. Please try again.",
        });
      }
    },
  });

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Card className="rounded-[2rem] border border-slate-200/50 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
        <CardHeader>
          <CardTitle className="font-geist text-2xl font-semibold tracking-tight">
            Create New Project
          </CardTitle>
          <CardDescription className="font-satoshi text-slate-600">
            Describe your product idea and we'll research the market
          </CardDescription>
        </CardHeader>
        <form onSubmit={form.handleSubmit}>
          <CardContent className="space-y-6">
            {form.state.errors.form && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {form.state.errors.form}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="name" className="font-geist text-sm font-medium">
                Project Name
              </Label>
              <Input
                id="name"
                placeholder="e.g., AI Receipt Scanner"
                value={form.state.values.name}
                onChange={(v) => form.setFieldValue("name", v)}
                onBlur={form.handleBlur}
                className="rounded-xl"
              />
              {form.state.fieldMeta.name?.errors && (
                <p className="text-sm text-red-600">
                  {form.state.fieldMeta.name.errors.join(", ")}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="idea" className="font-geist text-sm font-medium">
                Your Idea
              </Label>
              <Textarea
                id="idea"
                placeholder="AI-powered receipt scanner for freelancers that automatically categorizes expenses and generates tax reports..."
                rows={5}
                value={form.state.values.idea}
                onChange={(v) => form.setFieldValue("idea", v)}
                onBlur={form.handleBlur}
                className="rounded-xl resize-none"
              />
              {form.state.fieldMeta.idea?.errors && (
                <p className="text-sm text-red-600">
                  {form.state.fieldMeta.idea.errors.join(", ")}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="knownCompetitors"
                className="font-geist text-sm font-medium"
              >
                Known Competitors (optional)
              </Label>
              <Input
                id="knownCompetitors"
                placeholder="Notion, Evernote, Bear (comma-separated)"
                value={form.state.values.knownCompetitors}
                onChange={(v) => form.setFieldValue("knownCompetitors", v)}
                onBlur={form.handleBlur}
                className="rounded-xl"
              />
              <p className="font-satoshi text-xs text-slate-500">
                Enter competitor names separated by commas
              </p>
            </div>
          </CardContent>

          <CardFooter className="flex justify-between">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate({ to: "/projects" })}
              className="rounded-xl font-geist"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={
                form.state.isSubmitting ||
                !form.state.values.name ||
                !form.state.values.idea
              }
              className="rounded-xl font-geist active:scale-[0.98] transition-transform"
            >
              {form.state.isSubmitting ? "Creating..." : "Create Project"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
