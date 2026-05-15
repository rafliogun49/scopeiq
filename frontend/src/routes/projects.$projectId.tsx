import {
  createFileRoute,
  Link,
  Outlet,
  useRouterState,
  useNavigate,
} from "@tanstack/react-router";
import { useProject, useDeleteProject } from "@/hooks/useProjects";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ArrowRight,
  ChevronLeft,
  FileText,
  MessageSquare,
  PlayCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/projects/$projectId")({
  component: ProjectDetailPage,
});

function ProjectDetailPage() {
  const { projectId } = Route.useParams();
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  });
  const normalizedPathname = pathname.replace(/\/+$/, "") || "/";

  if (normalizedPathname !== `/projects/${projectId}`) {
    return <Outlet />;
  }

  return <ProjectDetailContent projectId={projectId} />;
}

function ProjectDetailContent({ projectId }: { projectId: string }) {
  const navigate = useNavigate();
  const { data: project, isLoading, error } = useProject(projectId);
  const deleteProject = useDeleteProject();

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8">
          <Link to="/projects">
            <Button variant="outline" className="rounded-xl font-geist">
              ← Back to Projects
            </Button>
          </Link>
        </div>
        <Skeleton className="h-8 w-64 mb-8" />
        <Card className="rounded-[2rem]">
          <CardHeader>
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="mt-2 h-4 w-2/3" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10 text-center">
        <h1 className="font-geist text-2xl font-semibold">Project not found</h1>
        <p className="mt-2 font-satoshi text-slate-600">
          {error instanceof Error
            ? error.message
            : "The project you're looking for doesn't exist."}
        </p>
        <Link to="/projects">
          <Button variant="outline" className="mt-4">
            Back to Projects
          </Button>
        </Link>
      </div>
    );
  }

  const createdDate = project.created_at
    ? new Date(project.created_at).toLocaleDateString()
    : "Unknown date";

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-6">
        <Link
          to="/projects"
          className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 font-geist text-sm font-medium text-slate-600 shadow-[0_14px_40px_-30px_rgba(15,23,42,0.45)] transition-colors hover:text-emerald-800"
        >
          <ChevronLeft className="h-4 w-4" strokeWidth={1.8} />
          Projects
        </Link>
      </div>

      <div className="mb-8 rounded-[2rem] border border-slate-200/70 bg-white/85 p-6 shadow-[0_24px_70px_-40px_rgba(15,23,42,0.32)]">
        <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="mb-2 font-geist text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
              Project dossier
            </p>
            <h1 className="font-geist text-3xl font-semibold tracking-tight text-slate-950">
              {project.name}
            </h1>
            <p className="mt-2 font-satoshi text-sm text-slate-600">
              Created {createdDate}
            </p>
          </div>
          <Button
            variant="destructive"
            onClick={() => {
              if (confirm("Are you sure you want to delete this project?")) {
                deleteProject.mutate(projectId, {
                  onSuccess: () => {
                    navigate({ to: "/projects" });
                  },
                });
              }
            }}
          >
            Delete
          </Button>
        </div>
      </div>

      <Card className="mb-8 rounded-[2rem] border border-slate-200/70 bg-white/90 shadow-[0_24px_70px_-45px_rgba(15,23,42,0.38)]">
        <CardHeader className="px-6 pt-6">
          <CardTitle className="font-geist text-lg font-semibold">
            Idea Description
          </CardTitle>
        </CardHeader>
        <CardContent className="px-6 pb-6">
          <p className="max-w-3xl font-satoshi text-slate-600 leading-relaxed">
            {project.idea}
          </p>
        </CardContent>
      </Card>

      {project.known_competitors && project.known_competitors.length > 0 && (
        <Card className="rounded-[2rem] border border-slate-200/70 bg-white/75">
          <CardHeader className="px-6 pt-6">
            <CardTitle className="font-geist text-lg font-semibold">
              Known Competitors
            </CardTitle>
          </CardHeader>
          <CardContent className="px-6 pb-6">
            <div className="flex flex-wrap gap-2">
              {project.known_competitors.map((competitor) => (
                <span
                  key={competitor}
                  className="rounded-full bg-slate-100 px-3 py-1.5 text-sm font-satoshi text-slate-700 ring-1 ring-slate-200/70"
                >
                  {competitor}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="mt-8">
        <h2 className="font-geist text-lg font-semibold mb-4">Next Steps</h2>
        <div className="grid gap-4 md:grid-cols-[minmax(0,1.4fr)_minmax(280px,0.8fr)]">
          <Link to="/projects/$projectId/runs/new" params={{ projectId }}>
            <Card className="h-full cursor-pointer rounded-[2rem] border border-emerald-200/70 bg-emerald-50/60 shadow-[0_20px_40px_-15px_rgba(16,185,129,0.16)] transition-transform hover:-translate-y-0.5">
              <CardContent className="flex h-full flex-col justify-between gap-8 p-6">
                <div>
                  <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-full bg-emerald-600 text-white">
                    <PlayCircle className="h-5 w-5" strokeWidth={1.8} />
                  </div>
                  <h3 className="font-geist text-xl font-semibold tracking-tight">
                    Start research run
                  </h3>
                  <p className="mt-2 max-w-xl text-sm font-satoshi leading-relaxed text-slate-700">
                    Launch the agent workflow to collect competitor pricing,
                    social complaints, citations, and report material.
                  </p>
                </div>
                <div className="inline-flex items-center gap-2 font-geist text-sm font-medium text-emerald-800">
                  Run market research
                  <ArrowRight className="h-4 w-4" strokeWidth={1.8} />
                </div>
              </CardContent>
            </Card>
          </Link>

          <div className="divide-y divide-slate-200 rounded-[2rem] border border-slate-200/70 bg-white">
            <Link
              to="/projects/$projectId/report"
              params={{ projectId }}
              className="group flex items-center justify-between gap-4 p-5"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-700">
                  <FileText className="h-5 w-5" strokeWidth={1.8} />
                </div>
                <div>
                  <h3 className="font-geist font-semibold">View report</h3>
                  <p className="mt-1 text-sm font-satoshi text-slate-600">
                    Read the latest generated findings
                  </p>
                </div>
              </div>
              <ArrowRight
                className="h-4 w-4 text-slate-400 transition-transform group-hover:translate-x-0.5"
                strokeWidth={1.8}
              />
            </Link>

            <Link
              to="/projects/$projectId/chat"
              params={{ projectId }}
              className="group flex items-center justify-between gap-4 p-5"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-700">
                  <MessageSquare className="h-5 w-5" strokeWidth={1.8} />
                </div>
                <div>
                  <h3 className="font-geist font-semibold">Ask follow-ups</h3>
                  <p className="mt-1 text-sm font-satoshi text-slate-600">
                    Query the collected research sources
                  </p>
                </div>
              </div>
              <ArrowRight
                className="h-4 w-4 text-slate-400 transition-transform group-hover:translate-x-0.5"
                strokeWidth={1.8}
              />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
