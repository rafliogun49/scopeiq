import {
  createFileRoute,
  Link,
  Outlet,
  useRouterState,
} from "@tanstack/react-router";
import { useProject, useDeleteProject } from "@/hooks/useProjects";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/projects/$projectId")({
  component: ProjectDetailPage,
});

function ProjectDetailPage() {
  const { projectId } = Route.useParams();
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  });

  if (pathname !== `/projects/${projectId}`) {
    return <Outlet />;
  }

  return <ProjectDetailContent projectId={projectId} />;
}

function ProjectDetailContent({ projectId }: { projectId: string }) {
  const { data: project, isLoading } = useProject(projectId);
  const deleteProject = useDeleteProject();

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10">
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

  if (!project) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10 text-center">
        <h1 className="font-geist text-2xl font-semibold">Project not found</h1>
        <Link to="/projects">
          <Button variant="outline" className="mt-4 rounded-xl">
            Back to Projects
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="font-geist text-2xl font-semibold tracking-tight">
            {project.name}
          </h1>
          <p className="mt-1 font-satoshi text-slate-600">
            Created {new Date(project.created_at).toLocaleDateString()}
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => {
            if (confirm("Are you sure you want to delete this project?")) {
              deleteProject.mutate(projectId);
            }
          }}
          className="rounded-xl font-geist text-red-600 hover:text-red-700"
        >
          Delete
        </Button>
      </div>

      <Card className="mb-8 rounded-[2rem] border border-slate-200/50 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
        <CardHeader>
          <CardTitle className="font-geist text-lg font-semibold">
            Idea Description
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="font-satoshi text-slate-600 leading-relaxed">
            {project.idea}
          </p>
        </CardContent>
      </Card>

      {project.known_competitors && project.known_competitors.length > 0 && (
        <Card className="rounded-[2rem] border border-slate-200/50">
          <CardHeader>
            <CardTitle className="font-geist text-lg font-semibold">
              Known Competitors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {project.known_competitors.map((competitor) => (
                <span
                  key={competitor}
                  className="rounded-full bg-slate-100 px-3 py-1.5 text-sm font-satoshi text-slate-700"
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
        <div className="grid gap-4 md:grid-cols-3">
          <Link to="/projects/$projectId/runs/new" params={{ projectId }}>
            <Card className="cursor-pointer rounded-[2rem] border border-slate-200/50 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                  <svg
                    className="h-5 w-5 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <h3 className="font-geist font-semibold">Start Research</h3>
                <p className="mt-1 text-sm font-satoshi text-slate-600">
                  Run AI-powered market research
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link to="/projects/$projectId/report" params={{ projectId }}>
            <Card className="cursor-pointer rounded-[2rem] border border-slate-200/50 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-green-100">
                  <svg
                    className="h-5 w-5 text-green-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <h3 className="font-geist font-semibold">View Report</h3>
                <p className="mt-1 text-sm font-satoshi text-slate-600">
                  Read research findings
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link to="/projects/$projectId/chat" params={{ projectId }}>
            <Card className="cursor-pointer rounded-[2rem] border border-slate-200/50 hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-purple-100">
                  <svg
                    className="h-5 w-5 text-purple-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                </div>
                <h3 className="font-geist font-semibold">Chat</h3>
                <p className="mt-1 text-sm font-satoshi text-slate-600">
                  Ask questions about research
                </p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  );
}
