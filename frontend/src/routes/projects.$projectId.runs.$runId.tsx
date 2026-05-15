import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useRunStream } from "@/hooks/useRunStream";
import { useProject } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";
import {
  AlertCircle,
  Bot,
  CheckCircle2,
  Circle,
  ClipboardList,
  FileText,
  Wrench,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const Route = createFileRoute("/projects/$projectId/runs/$runId")({
  component: RunProgressPage,
});

function RunProgressPage() {
  const { projectId, runId } = Route.useParams();
  const navigate = useNavigate();
  const { data: project } = useProject(projectId);
  const { events, status, error, isComplete } = useRunStream(runId);

  const getStatusColor = () => {
    switch (status) {
      case "connecting":
        return "bg-slate-100 text-slate-700 ring-1 ring-slate-200";
      case "streaming":
        return "bg-emerald-50 text-emerald-800 ring-1 ring-emerald-100";
      case "complete":
        return "bg-emerald-100 text-emerald-800 ring-1 ring-emerald-200";
      case "error":
        return "bg-red-50 text-red-700 ring-1 ring-red-200";
      default:
        return "bg-slate-100 text-slate-700 ring-1 ring-slate-200";
    }
  };

  const getEventIcon = (type: string) => {
    const iconClass = "h-5 w-5";

    switch (type) {
      case "plan":
        return <ClipboardList className={iconClass} strokeWidth={1.8} />;
      case "agent_started":
        return <Bot className={iconClass} strokeWidth={1.8} />;
      case "tool_called":
        return <Wrench className={iconClass} strokeWidth={1.8} />;
      case "agent_finished":
        return <CheckCircle2 className={iconClass} strokeWidth={1.8} />;
      case "error":
        return <AlertCircle className={iconClass} strokeWidth={1.8} />;
      case "log":
        return <FileText className={iconClass} strokeWidth={1.8} />;
      default:
        return <Circle className="h-3 w-3" strokeWidth={1.8} />;
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const seconds = Math.floor(
      (Date.now() - new Date(timestamp).getTime()) / 1000,
    );
    if (seconds < 5) return "just now";
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ago`;
  };

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-8 rounded-[2rem] border border-slate-200/70 bg-white/85 p-6 shadow-[0_24px_70px_-45px_rgba(15,23,42,0.38)]">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <Link to="/projects/$projectId" params={{ projectId }}>
              <Button variant="outline" className="mb-4">
                ← Back to Project
              </Button>
            </Link>
            <p className="mb-2 font-geist text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
              Live agent run
            </p>
            <h1 className="font-geist text-3xl font-semibold tracking-tight text-slate-950">
              Research in Progress
            </h1>
            <p className="mt-2 font-satoshi text-sm text-slate-600">
              {project?.name || "Loading project..."}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-geist text-sm font-medium">$0.00</div>
              <div className="font-satoshi text-xs text-slate-500">
                Est. ~$0.22 total
              </div>
            </div>
            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${getStatusColor()}`}
            >
              {status === "connecting" && "Connecting..."}
              {status === "streaming" && "Running"}
              {status === "complete" && "Complete"}
              {status === "error" && "Error"}
            </span>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <Card className="mb-8 rounded-[2rem] border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="font-satoshi text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Complete State */}
      {isComplete && (
        <Card className="mb-8 rounded-[2rem] border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-geist text-lg font-semibold text-green-800">
                  Research Complete!
                </h3>
                <p className="font-satoshi text-sm text-green-700">
                  Your report is ready to view
                </p>
              </div>
              <Button
                onClick={() =>
                  navigate({
                    to: "/projects/$projectId/report",
                    params: { projectId },
                  })
                }
              >
                View Report
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Events Timeline */}
      <Card className="rounded-[2rem] border border-slate-200/70 bg-white/95 shadow-[0_24px_70px_-45px_rgba(15,23,42,0.38)]">
        <CardHeader className="border-b border-slate-200/70 px-6 pb-5 pt-6">
          <CardTitle className="font-geist text-lg font-semibold">
            Live Progress
          </CardTitle>
          <CardDescription className="font-satoshi text-slate-600">
            Watching agent activity in real-time
          </CardDescription>
        </CardHeader>
        <CardContent className="px-6 py-6">
          {events.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 ring-1 ring-emerald-100">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-emerald-700 border-t-transparent" />
              </div>
              <p className="font-satoshi text-slate-600">
                Waiting for agent to start...
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {events.map((event, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 rounded-lg border border-slate-100 p-4"
                >
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-600">
                    {getEventIcon(event.type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-geist text-sm font-medium capitalize">
                        {event.type.replace(/_/g, " ")}
                      </span>
                      {event.agent && (
                        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-satoshi text-slate-600">
                          {event.agent}
                        </span>
                      )}
                      <span className="text-xs text-slate-400">
                        {formatTimeAgo(event.timestamp)}
                      </span>
                    </div>
                    {Object.keys(event.payload).length > 0 && (
                      <pre className="mt-2 text-xs font-mono text-slate-600 bg-slate-50 p-2 rounded overflow-x-auto">
                        {JSON.stringify(event.payload, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
