import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useProject } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const Route = createFileRoute("/projects/$projectId/runs/new")({
  component: StartRunPage,
});

interface CreateRunResponse {
  run_id: string;
  status: string;
}

function StartRunPage() {
  const { projectId } = Route.useParams();
  const navigate = useNavigate();
  const { data: project, isLoading, error } = useProject(projectId);

  const startRun = useMutation({
    mutationFn: () =>
      api.post<CreateRunResponse>(`/projects/${projectId}/runs`, {}),
    onSuccess: (data) => {
      navigate({
        to: "/projects/$projectId/runs/$runId",
        params: { projectId, runId: data.run_id },
      });
    },
  });

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10">
        <div className="mb-8">
          <Link to="/projects/$projectId" params={{ projectId }}>
            <Button variant="outline" className="rounded-xl font-geist">
              ← Back to Project
            </Button>
          </Link>
        </div>
        <Skeleton className="h-8 w-64 mb-8" />
        <Card className="rounded-[2rem]">
          <CardContent className="pt-6">
            <Skeleton className="h-4 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-10 text-center">
        <h1 className="font-geist text-2xl font-semibold">Project not found</h1>
        <p className="mt-2 font-satoshi text-slate-600">
          {error instanceof Error
            ? error.message
            : "The project you're looking for doesn't exist."}
        </p>
        <Link to="/projects">
          <Button variant="outline" className="mt-4 rounded-xl">
            Back to Projects
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Card className="rounded-[2rem] border border-slate-200/70 bg-white/95 shadow-[0_28px_80px_-45px_rgba(15,23,42,0.45)]">
        <CardHeader className="border-b border-slate-200/70 px-6 pb-6 pt-6">
          <p className="font-geist text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
            Agent workflow
          </p>
          <CardTitle className="mt-2 font-geist text-3xl font-semibold tracking-tight text-slate-950">
            Start Research
          </CardTitle>
          <CardDescription className="font-satoshi text-sm text-slate-600">
            AI agents will research your idea and generate a report
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6 px-6 py-6">
          <div>
            <h3 className="font-geist text-sm font-semibold mb-2">Project</h3>
            <p className="font-satoshi text-slate-600">{project.name}</p>
          </div>

          <div>
            <h3 className="font-geist text-sm font-semibold mb-2">
              What happens next?
            </h3>
            <ul className="space-y-2 font-satoshi text-sm text-slate-600">
              <li className="flex items-start gap-2">
                <span className="text-emerald-700">1.</span>
                <span>
                  <strong>Orchestrator</strong> plans the research strategy
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-700">2.</span>
                <span>
                  <strong>Scraper agent</strong> fetches competitor websites
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-700">3.</span>
                <span>
                  <strong>Social agent</strong> mines HN, Stack Exchange for
                  user complaints
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-700">4.</span>
                <span>
                  <strong>Synthesizer</strong> writes the final report with
                  citations
                </span>
              </li>
            </ul>
          </div>

          <div className="rounded-2xl border border-slate-200/70 bg-slate-50/80 p-4">
            <h3 className="font-geist text-sm font-semibold mb-2">Estimated</h3>
            <div className="grid grid-cols-2 gap-4 font-satoshi text-sm">
              <div>
                <span className="text-slate-500">Time:</span>{" "}
                <span className="font-medium">~5 minutes</span>
              </div>
              <div>
                <span className="text-slate-500">Cost:</span>{" "}
                <span className="font-medium">~$0.22</span>
              </div>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex flex-col-reverse gap-3 border-t border-slate-200/70 bg-white/70 p-6 sm:flex-row sm:justify-between">
          <Button
            variant="outline"
            onClick={() =>
              navigate({ to: "/projects/$projectId", params: { projectId } })
            }
          >
            Cancel
          </Button>
          <Button
            onClick={() => startRun.mutate()}
            disabled={startRun.isPending}
          >
            {startRun.isPending ? "Starting..." : "Start Research"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
