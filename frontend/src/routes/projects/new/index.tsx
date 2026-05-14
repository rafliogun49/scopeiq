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
    console.log("✅ Form submitted");
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
      console.error("❌ Error:", err);
      setError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setLoading(false);
    }
  };

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
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6">
            {error && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="name" className="font-geist text-sm font-medium">
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
            </div>

            <div className="space-y-2">
              <Label htmlFor="idea" className="font-geist text-sm font-medium">
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
                name="knownCompetitors"
                type="text"
                placeholder="Notion, Evernote, Bear"
                value={knownCompetitors}
                onChange={(e) => setKnownCompetitors(e.target.value)}
                className="rounded-xl"
              />
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
              disabled={loading || !name || !idea}
              className="rounded-xl font-geist active:scale-[0.98] transition-transform"
            >
              {loading ? "Creating..." : "Create Project"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
