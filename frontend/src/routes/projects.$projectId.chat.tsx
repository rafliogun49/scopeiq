import { createFileRoute, useParams } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "@tanstack/react-form";
import { api } from "@/lib/api";
import { qk } from "@/lib/qk";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const Route = createFileRoute("/projects/$projectId/chat")({
  component: ChatPage,
});

interface ChatMessage {
  id: string;
  project_id: string;
  role: "user" | "assistant";
  content: string;
  citations?: string[];
  created_at: string;
}

function ChatPage() {
  const { projectId } = useParams();
  const queryClient = useQueryClient();

  const { data: messages, isLoading } = useQuery<ChatMessage[]>({
    queryKey: qk.messages(projectId),
    queryFn: () =>
      api.get<ChatMessage[]>(`/projects/${projectId}/chat/messages`),
  });

  const sendMessage = useMutation({
    mutationFn: (content: string) =>
      api.post<ChatMessage>(`/projects/${projectId}/chat`, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: qk.messages(projectId) });
    },
  });

  const form = useForm({
    defaultValues: {
      message: "",
    },
    validators: {
      onChange: ({ value }) => ({
        message: !value.message ? "Message is required" : undefined,
      }),
    },
    onSubmit: async ({ value }) => {
      await sendMessage.mutateAsync(value.message);
      form.reset();
    },
  });

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

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-8">
        <h1 className="font-geist text-2xl font-semibold tracking-tight">
          Chat with Research
        </h1>
        <p className="mt-1 font-satoshi text-slate-600">
          Ask follow-up questions about your research
        </p>
      </div>

      {/* Messages List */}
      <Card className="mb-6 rounded-[2rem] border border-slate-200/50 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
        <CardContent className="pt-6">
          <div className="space-y-4 max-h-[60vh] overflow-y-auto">
            {messages && messages.length > 0 ? (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-[2rem] p-4 ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-slate-100 text-slate-900"
                    }`}
                  >
                    <p className="font-satoshi text-sm leading-relaxed">
                      {msg.content}
                    </p>
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {msg.citations.map((citation, i) => (
                          <a
                            key={i}
                            href={citation}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs ${
                              msg.role === "user"
                                ? "bg-blue-500 text-white hover:bg-blue-400"
                                : "bg-white text-slate-600 hover:bg-slate-50"
                            }`}
                          >
                            <svg
                              className="h-3 w-3"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                              />
                            </svg>
                            Source {i + 1}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
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
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
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
                <div className="max-w-[80%] rounded-[2rem] p-4 bg-slate-100">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Chat Input */}
      <form onSubmit={form.handleSubmit}>
        <Card className="rounded-[2rem] border border-slate-200/50 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
          <CardContent className="pt-6">
            <div className="flex gap-3">
              <Textarea
                placeholder="Ask a follow-up question..."
                rows={2}
                value={form.state.values.message}
                onChange={(v) => form.setFieldValue("message", v)}
                onBlur={form.handleBlur}
                disabled={sendMessage.isPending}
                className="rounded-xl resize-none"
              />
              <Button
                type="submit"
                disabled={sendMessage.isPending || !form.state.values.message}
                className="rounded-xl font-geist self-end active:scale-[0.98] transition-transform"
              >
                {sendMessage.isPending ? "Sending..." : "Send"}
              </Button>
            </div>
            {form.state.errors.message && (
              <p className="mt-2 text-sm text-red-600">
                {form.state.errors.message}
              </p>
            )}
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
