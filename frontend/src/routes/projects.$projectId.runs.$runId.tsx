import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useRunStream } from "@/hooks/useRunStream";
import { useProject } from "@/hooks/useProjects";
import { Button } from "@/components/ui/button";
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
        return "bg-blue-100 text-blue-700";
      case "streaming":
        return "bg-yellow-100 text-yellow-700";
      case "complete":
        return "bg-green-100 text-green-700";
      case "error":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case "plan":
        return "📋";
      case "agent_started":
        return "🤖";
      case "tool_called":
        return "🔧";
      case "agent_finished":
        return "✅";
      case "error":
        return "❌";
      case "log":
        return "📝";
      default:
        return "•";
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
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <Link to="/projects/$projectId" params={{ projectId }}>
              <Button variant="outline" className="rounded-xl font-geist mb-4">
                ← Back to Project
              </Button>
            </Link>
            <h1 className="font-geist text-2xl font-semibold tracking-tight">
              Research in Progress
            </h1>
            <p className="mt-1 font-satoshi text-slate-600">
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
                className="rounded-xl bg-green-600 font-geist hover:bg-green-700 active:scale-[0.98] transition-transform"
              >
                View Report
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Events Timeline */}
      <Card className="rounded-[2rem] border border-slate-200/50 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
        <CardHeader>
          <CardTitle className="font-geist text-lg font-semibold">
            Live Progress
          </CardTitle>
          <CardDescription className="font-satoshi text-slate-600">
            Watching agent activity in real-time
          </CardDescription>
        </CardHeader>
        <CardContent>
          {events.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
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
                  <div className="text-xl">{getEventIcon(event.type)}</div>
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
