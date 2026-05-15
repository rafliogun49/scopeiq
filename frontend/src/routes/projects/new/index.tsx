import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
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

export const Route = createFileRoute("/projects/new/")({
  component: CreateProjectPage,
});

function CreateProjectPage() {
  const navigate = useNavigate();
  const createProject = useCreateProject();
  const [name, setName] = useState("");
  const [idea, setIdea] = useState("");
  const [knownCompetitors, setKnownCompetitors] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!name) {
      setError("Project name is required");
      return;
    }

    if (!idea || idea.length < 20) {
      setError("Idea description is required (min 20 characters)");
      return;
    }

    setLoading(true);

    try {
      const competitors = knownCompetitors
        ? knownCompetitors
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean)
        : [];

      const project = await createProject.mutateAsync({
        name,
        idea,
        known_competitors: competitors,
      });

      navigate({
        to: "/projects/$projectId",
        params: { projectId: project.id },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <Card className="rounded-[2rem] border border-slate-200/70 bg-white/95 shadow-[0_28px_80px_-45px_rgba(15,23,42,0.45)]">
        <CardHeader className="border-b border-slate-200/70 px-6 pb-6 pt-6">
          <p className="font-geist text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
            New research dossier
          </p>
          <CardTitle className="mt-2 font-geist text-3xl font-semibold tracking-tight text-slate-950">
            Create project
          </CardTitle>
          <CardDescription className="max-w-2xl font-satoshi text-sm leading-relaxed text-slate-600">
            Describe the idea clearly enough for the agents to find competing
            products, pricing signals, user complaints, and market gaps.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6 px-6 py-6">
            {error && (
              <div className="rounded-2xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="rounded-2xl border border-slate-200/70 bg-slate-50/60 p-4">
              <div className="space-y-2">
                <Label
                  htmlFor="name"
                  className="font-geist text-sm font-medium"
                >
                  Project Name *
                </Label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="off"
                  placeholder="e.g., AI Receipt Scanner"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="rounded-xl"
                />
                <p className="font-satoshi text-xs text-slate-500">
                  Use a short working name, like “AI Receipt Scanner”.
                </p>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200/70 bg-white p-4 shadow-[0_18px_50px_-42px_rgba(15,23,42,0.5)]">
              <div className="space-y-2">
                <Label
                  htmlFor="idea"
                  className="font-geist text-sm font-medium"
                >
                  Your Idea *
                </Label>
                <Textarea
                  id="idea"
                  name="idea"
                  placeholder="AI-powered receipt scanner for freelancers..."
                  rows={5}
                  value={idea}
                  onChange={(e) => setIdea(e.target.value)}
                  className="rounded-xl resize-none"
                />
                <p className="font-satoshi text-xs text-slate-500">
                  Include target users, workflow, pricing guess, or pain point.
                  Minimum 20 characters.
                </p>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200/70 bg-slate-50/60 p-4">
              <div className="space-y-2">
                <Label
                  htmlFor="knownCompetitors"
                  className="font-geist text-sm font-medium"
                >
                  Known Competitors (optional)
                </Label>
                <Input
                  id="knownCompetitors"
                  name="knownCompetitors"
                  type="text"
                  placeholder="Notion, Evernote, Bear"
                  value={knownCompetitors}
                  onChange={(e) => setKnownCompetitors(e.target.value)}
                  className="rounded-xl"
                />
                <p className="font-satoshi text-xs text-slate-500">
                  Separate names with commas. Leave blank if unknown.
                </p>
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col-reverse gap-3 border-t border-slate-200/70 bg-white/80 p-6 sm:flex-row sm:justify-between">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate({ to: "/projects" })}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading || !name || !idea}>
              {loading ? "Creating..." : "Create Project"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
