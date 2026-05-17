import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "@/lib/api";
import { qk } from "@/lib/qk";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  ArrowUpRight,
  ChevronLeft,
  MessageSquare,
  Sparkles,
} from "lucide-react";

export const Route = createFileRoute("/projects/$projectId/chat")({
  component: ChatPage,
});

interface ChatMessage {
  id: string;
  project_id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  created_at: string;
}

interface Citation {
  chunk: string;
  source_url: string;
  score: number;
}

interface ChatResponse {
  assistant_message: string;
  citations: Citation[];
}

function ChatPage() {
  const { projectId } = Route.useParams();
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [message, setMessage] = useState("");
  const [pendingContent, setPendingContent] = useState<string | null>(null);

  const {
    data: messages,
    isLoading,
    error,
  } = useQuery<ChatMessage[]>({
    queryKey: qk.messages(projectId),
    queryFn: () => api.get<ChatMessage[]>(`/projects/${projectId}/messages`),
  });

  const sendMessage = useMutation({
    mutationFn: (message: string) =>
      api.post<ChatResponse>(`/projects/${projectId}/chat`, { message }),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: qk.messages(projectId) });
    },
  });

  const pendingUserMessage = useMemo(() => {
    if (!sendMessage.isPending || !pendingContent) {
      return null;
    }

    return {
      id: "pending-user-message",
      project_id: projectId,
      role: "user" as const,
      content: pendingContent,
      citations: [],
      created_at: new Date().toISOString(),
    };
  }, [pendingContent, projectId, sendMessage.isPending]);

  const displayedMessages = useMemo(() => {
    if (!pendingUserMessage) {
      return messages ?? [];
    }

    return [...(messages ?? []), pendingUserMessage];
  }, [messages, pendingUserMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [displayedMessages, sendMessage.isPending]);

  const messageError = message.trim() ? "" : "Message is required";

  const submitMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || sendMessage.isPending) return;
    setPendingContent(trimmed);
    setMessage("");
    await sendMessage.mutateAsync(trimmed);
    setPendingContent(null);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    await submitMessage(message);
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <div className="mb-8">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="mt-2 h-4 w-64" />
        </div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-20 w-full rounded-[2rem]" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <Card className="rounded-[2rem] border border-red-200/70 bg-red-50/80 shadow-none">
          <CardContent className="px-6 py-6">
            <h1 className="font-geist text-lg font-semibold text-red-900">
              Chat unavailable
            </h1>
            <p className="mt-2 font-satoshi text-sm leading-relaxed text-red-700">
              {error instanceof Error
                ? error.message
                : "The chat history could not be loaded."}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <Link
          to="/projects/$projectId"
          params={{ projectId }}
          className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 font-geist text-sm font-medium text-slate-600 shadow-[0_14px_40px_-30px_rgba(15,23,42,0.45)] transition-colors hover:text-emerald-800"
        >
          <ChevronLeft className="h-4 w-4" strokeWidth={1.8} />
          Back to project
        </Link>
        <Link
          to="/projects"
          className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 font-geist text-sm font-medium text-slate-600 shadow-[0_14px_40px_-30px_rgba(15,23,42,0.45)] transition-colors hover:text-emerald-800"
        >
          Projects
        </Link>
      </div>

      <div className="mb-8 rounded-[2rem] border border-slate-200/70 bg-white/85 p-6 shadow-[0_24px_70px_-45px_rgba(15,23,42,0.38)]">
        <p className="mb-2 font-geist text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
          Research assistant
        </p>
        <h1 className="font-geist text-3xl font-semibold tracking-tight text-slate-950">
          Chat with Research
        </h1>
        <p className="mt-2 font-satoshi text-sm text-slate-600">
          Ask follow-up questions about your research
        </p>
      </div>

      {/* Messages List */}
      <Card className="mb-6 rounded-[2rem] border border-slate-200/70 bg-white/90 shadow-[0_24px_70px_-45px_rgba(15,23,42,0.38)]">
        <CardContent className="px-5 py-5">
          <div className="max-h-[60vh] space-y-4 overflow-y-auto pr-1">
            {displayedMessages.length > 0 ? (
              displayedMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-[2rem] p-4 ${
                      msg.role === "user"
                        ? "bg-slate-950 text-white shadow-[0_18px_45px_-30px_rgba(15,23,42,0.9)]"
                        : "bg-slate-100/90 text-slate-900 ring-1 ring-slate-200/70"
                    }`}
                  >
                    {msg.role === "assistant" ? (
                      <div className="prose prose-sm prose-slate max-w-none font-satoshi prose-headings:font-geist prose-headings:tracking-tight prose-p:leading-relaxed prose-a:text-emerald-800">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            a: ({ href, children }) => (
                              <a
                                href={href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-emerald-800 hover:underline"
                              >
                                {children}
                                <ArrowUpRight
                                  className="h-3.5 w-3.5"
                                  strokeWidth={1.8}
                                />
                              </a>
                            ),
                            p: ({ children }) => (
                              <p className="mb-3 font-satoshi text-sm leading-relaxed text-inherit last:mb-0">
                                {children}
                              </p>
                            ),
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="font-satoshi text-sm leading-relaxed">
                        {msg.content}
                      </p>
                    )}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <div
                          className={`flex items-center gap-2 text-[11px] font-geist font-semibold uppercase tracking-[0.14em] ${
                            msg.role === "user"
                              ? "text-white/70"
                              : "text-slate-500"
                          }`}
                        >
                          <Sparkles className="h-3.5 w-3.5" strokeWidth={1.8} />
                          Sources
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {msg.citations.map((citation, i) => (
                            <a
                              key={`${citation.source_url}-${i}`}
                              href={citation.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs ${
                                msg.role === "user"
                                  ? "bg-white/10 text-white hover:bg-white/15"
                                  : "bg-white text-emerald-800 ring-1 ring-slate-200/70 hover:bg-emerald-50"
                              }`}
                              title={citation.chunk}
                            >
                              <ArrowUpRight
                                className="h-3 w-3"
                                strokeWidth={1.8}
                              />
                              Source {i + 1}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
                  <MessageSquare
                    className="h-8 w-8 text-slate-400"
                    strokeWidth={1.6}
                  />
                </div>
                <h3 className="font-geist text-lg font-semibold">
                  Start a conversation
                </h3>
                <p className="mt-1 font-satoshi text-slate-600">
                  Ask questions about your research findings
                </p>
              </div>
            )}

            {sendMessage.isPending && (
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-[2rem] bg-slate-100 p-4 ring-1 ring-slate-200/70">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </CardContent>
      </Card>

      {/* Chat Input */}
      <form onSubmit={handleSubmit}>
        <Card className="rounded-[2rem] border border-slate-200/70 bg-white/95 shadow-[0_24px_70px_-45px_rgba(15,23,42,0.38)]">
          <CardContent className="p-5">
            <div className="flex gap-3">
              <Textarea
                placeholder="Ask a follow-up question..."
                rows={2}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    submitMessage(message);
                  }
                }}
                disabled={sendMessage.isPending}
                className="rounded-xl resize-none"
              />
              <Button
                type="submit"
                disabled={sendMessage.isPending || !message.trim()}
                className="self-end"
              >
                {sendMessage.isPending ? "Sending..." : "Send"}
              </Button>
            </div>
            {sendMessage.isError && (
              <p className="mt-3 text-sm text-red-600">
                {sendMessage.error instanceof Error
                  ? sendMessage.error.message
                  : "Message could not be sent."}
              </p>
            )}
            {!!message && !!messageError && (
              <p className="mt-2 text-sm text-red-600">{messageError}</p>
            )}
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
