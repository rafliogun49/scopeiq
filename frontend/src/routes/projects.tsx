import {
  createFileRoute,
  Link,
  Outlet,
  useRouterState,
} from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";
import { useProjects } from "@/hooks/useProjects";
import { formatDisplayDate } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/projects")({
  component: ProjectsPage,
});

function ProjectsPage() {
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  });
  const normalizedPathname = pathname.replace(/\/+$/, "") || "/";

  if (normalizedPathname !== "/projects") {
    return <Outlet />;
  }

  return <ProjectsIndexPage />;
}

function ProjectsIndexPage() {
  const { data: projects, isLoading } = useProjects();
  const projectCount = projects?.length ?? 0;
  const competitorCount =
    projects?.reduce(
      (total, project) => total + (project.known_competitors?.length ?? 0),
      0,
    ) ?? 0;

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="mt-2 h-4 w-64" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="rounded-[2rem]">
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="mt-2 h-4 w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8 rounded-[2rem] border border-slate-200/70 bg-white/80 p-6 shadow-[0_24px_70px_-40px_rgba(15,23,42,0.32)]">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="mb-2 font-geist text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
              Research workspace
            </p>
            <h1 className="font-geist text-3xl font-semibold tracking-tight text-slate-950">
              Projects
            </h1>
            <p className="mt-2 max-w-2xl font-satoshi text-sm leading-relaxed text-slate-600">
              Track idea validation runs, reports, and follow-up research from
              one focused workspace.
            </p>
          </div>
          <Link to="/projects/new">
            <Button size="lg">New Project</Button>
          </Link>
        </div>
        <div className="mt-6 grid gap-3 border-t border-slate-200/70 pt-5 sm:grid-cols-3">
          <div className="rounded-2xl bg-slate-50/80 px-4 py-3 ring-1 ring-slate-200/70">
            <p className="font-geist text-xs font-medium uppercase tracking-[0.14em] text-slate-500">
              Projects
            </p>
            <p className="mt-2 font-geist text-2xl font-semibold tracking-tight text-slate-950">
              {projectCount}
            </p>
          </div>
          <div className="rounded-2xl bg-emerald-50/70 px-4 py-3 ring-1 ring-emerald-100">
            <p className="font-geist text-xs font-medium uppercase tracking-[0.14em] text-emerald-700">
              Competitors
            </p>
            <p className="mt-2 font-geist text-2xl font-semibold tracking-tight text-slate-950">
              {competitorCount}
            </p>
          </div>
          <div className="rounded-2xl bg-slate-950 px-4 py-3 text-white shadow-[0_22px_55px_-35px_rgba(15,23,42,0.9)]">
            <p className="font-geist text-xs font-medium uppercase tracking-[0.14em] text-slate-300">
              Next run
            </p>
            <p className="mt-2 font-geist text-2xl font-semibold tracking-tight">
              5 min
            </p>
          </div>
        </div>
      </div>

      {!projects || projects.length === 0 ? (
        <Card className="rounded-[2rem] border border-dashed border-slate-200/80 bg-white/92 shadow-[0_24px_70px_-45px_rgba(15,23,42,0.35)]">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
              <svg
                className="h-8 w-8 text-slate-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="font-geist text-lg font-semibold">
              No projects yet
            </h3>
            <p className="mt-1 font-satoshi text-slate-600">
              Create your first research project to get started
            </p>
            <Link to="/projects/new" className="mt-4">
              <Button>Create Project</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {projects.map((project) => (
            <Link
              key={project.id}
              to="/projects/$projectId"
              params={{ projectId: project.id }}
              className="group"
            >
              <Card className="relative min-h-64 cursor-pointer rounded-[1.75rem] border border-slate-200/70 bg-white shadow-[0_24px_70px_-45px_rgba(15,23,42,0.45)] transition-all hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-[0_28px_80px_-45px_rgba(16,185,129,0.35)]">
                <div className="absolute inset-y-5 left-0 w-1 rounded-r-full bg-emerald-600/80 opacity-70 transition-opacity group-hover:opacity-100" />
                <CardHeader className="gap-4 px-6 pt-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <CardTitle className="line-clamp-2 font-geist text-[1.35rem] font-semibold leading-tight tracking-tight text-slate-950">
                        {project.name}
                      </CardTitle>
                      <CardDescription className="mt-2 font-satoshi text-xs font-medium uppercase tracking-[0.12em] text-slate-500">
                        Created {formatDisplayDate(project.created_at)}
                      </CardDescription>
                    </div>
                    <div className="rounded-full bg-emerald-50 px-2.5 py-1 font-geist text-xs font-semibold text-emerald-800 ring-1 ring-emerald-100">
                      Active
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-1 flex-col px-6 pb-6">
                  <p className="line-clamp-3 min-h-[4.5rem] font-satoshi text-[0.95rem] leading-relaxed text-slate-600">
                    {project.idea}
                  </p>

                  <div className="mt-6 border-t border-slate-200/70 pt-4">
                    {project.known_competitors?.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {project.known_competitors
                          .slice(0, 3)
                          .map((competitor) => (
                            <span
                              key={competitor}
                              className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-satoshi font-medium text-slate-600 ring-1 ring-slate-200/70"
                            >
                              {competitor}
                            </span>
                          ))}
                        {project.known_competitors.length > 3 && (
                          <span className="rounded-full bg-white px-2.5 py-1 text-xs font-satoshi font-medium text-slate-500 ring-1 ring-slate-200/70">
                            +{project.known_competitors.length - 3} more
                          </span>
                        )}
                      </div>
                    ) : (
                      <p className="font-satoshi text-xs text-slate-500">
                        No known competitors listed yet
                      </p>
                    )}

                    <div className="mt-5 flex items-center justify-between">
                      <span className="font-geist text-sm font-semibold text-slate-700">
                        Open dossier
                      </span>
                      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-950 text-white transition-transform group-hover:translate-x-0.5">
                        <ArrowRight className="h-4 w-4" strokeWidth={1.8} />
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
