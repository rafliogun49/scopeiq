import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { qk } from "@/lib/qk";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";

export const Route = createFileRoute("/projects/$projectId/report")({
  component: ReportPage,
});

interface Report {
  id: string;
  project_id: string;
  report_md: string;
  created_at: string;
}

function ReportPage() {
  const { projectId } = Route.useParams();

  const { data: report, isLoading } = useQuery<Report>({
    queryKey: qk.report(projectId),
    queryFn: () => api.get<Report>(`/projects/${projectId}/report`),
  });

  const handleDownload = () => {
    if (!report?.report_md) return;
    const blob = new Blob([report.report_md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `scopeiq-report-${projectId}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-64" />
            <Skeleton className="mt-2 h-4 w-48" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        <Card className="rounded-[2rem]">
          <CardContent className="pt-6">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="mt-4 h-4 w-full" />
            <Skeleton className="mt-4 h-4 w-3/4" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!report || !report.report_md) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10 text-center">
        <Card className="rounded-[2rem] border-dashed">
          <CardContent className="pt-16">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 mx-auto">
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="font-geist text-lg font-semibold">No report yet</h3>
            <p className="mt-1 font-satoshi text-slate-600">
              Run research to generate a report
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-geist text-2xl font-semibold tracking-tight">
            Research Report
          </h1>
          <p className="mt-1 font-satoshi text-slate-600">
            Generated {new Date(report.created_at).toLocaleDateString()}
          </p>
        </div>
        <Button onClick={handleDownload}>Download .md</Button>
      </div>

      <Card className="rounded-[2rem] border border-slate-200/50 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
        <CardContent className="prose prose-slate max-w-none pt-6">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {children}
                </a>
              ),
              img: ({ src, alt }) => (
                <img
                  src={src}
                  alt={alt}
                  className="max-w-full h-auto rounded-lg"
                />
              ),
              h2: ({ children }) => (
                <h2 className="font-geist text-xl font-semibold tracking-tight mt-8 mb-4">
                  {children}
                </h2>
              ),
              p: ({ children }) => (
                <p className="font-satoshi text-slate-700 leading-relaxed mb-4">
                  {children}
                </p>
              ),
            }}
          >
            {report.report_md}
          </ReactMarkdown>
        </CardContent>
      </Card>
    </div>
  );
}
