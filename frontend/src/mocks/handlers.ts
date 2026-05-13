import { http, HttpResponse, delay } from "msw";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// Mock data
const mockUser = {
  id: "user-1",
  email: "test@example.com",
  created_at: new Date().toISOString(),
};

const mockProjects = [
  {
    id: "project-1",
    name: "AI Receipt Scanner",
    idea: "AI-powered receipt scanner for freelancers that automatically categorizes expenses and generates tax reports",
    known_competitors: ["Expensify", "Receipt Bank", "Dext"],
    archived: false,
    created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
  },
  {
    id: "project-2",
    name: "Podcast Show Notes Generator",
    idea: "Automatically generate SEO-optimized show notes from podcast transcripts using AI",
    known_competitors: ["Podia", "Descript"],
    archived: false,
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
];

const mockRun = {
  id: "run-1",
  project_id: "project-1",
  status: "completed" as const,
  report_md: `## Is this a real market?

Yes, the AI receipt scanner market is real and growing. The global expense management software market is valued at $5.2B in 2024, with SMB adoption increasing 34% YoA [source: https://example.com/market-report].

## Who's already there?

### Expensify
- **Pricing:** $5/month per user
- **Traction:** 10M+ users, IPO in 2021
- **Strengths:** SmartScan technology, corporate card integration

### Receipt Bank (Dext)
- **Pricing:** $10/month per user
- **Traction:** 300K+ businesses
- **Strengths:** Strong accounting partnerships

### Dext
- **Pricing:** $8/month per user
- **Traction:** 500K+ users
- **Strengths:** Multi-language support

## What users hate?

### Expensify Complaints
- "SmartScan fails 30% of the time with international receipts" - HN user [source: https://news.ycombinator.com/item?id=123456]
- "Customer support takes 3-5 days to respond" - Stack Exchange [source: https://softwarerecs.stackexchange.com/q/12345]
- "Mobile app crashes when uploading multiple receipts" - Indie Hackers [source: https://indiehackers.com/post/123456]

### Receipt Bank Complaints
- "Too expensive for freelancers" - HN user
- "UI feels dated, not intuitive" - Stack Exchange

## Where's the gap?

### Opportunity: International Receipt Support
Current solutions fail on:
- Non-Latin scripts (Chinese, Arabic, Cyrillic)
- Complex VAT calculations
- Multi-currency handling

### Opportunity: Freelancer-Friendly Pricing
- Current tools target enterprises ($5-10/month is steep for solopreneurs)
- Opportunity: $2-3/month tier with core features

### Opportunity: AI-Powered Categorization
- Existing tools use rule-based categorization
- ML could learn from user behavior over time
`,
  cost_usd: 0.22,
  token_input: 8500,
  token_output: 2200,
  created_at: new Date().toISOString(),
};

const mockMessages = [
  {
    id: "msg-1",
    project_id: "project-1",
    role: "user" as const,
    content: "What are the main pain points with Expensify?",
    citations: [],
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: "msg-2",
    project_id: "project-1",
    role: "assistant" as const,
    content: "Based on the research, the main pain points with Expensify are:\n\n1. **Poor international receipt support** - SmartScan fails ~30% of the time with non-US receipts, especially those with non-Latin scripts\n\n2. **Slow customer support** - Users report 3-5 day response times for support tickets\n\n3. **Mobile app stability issues** - Crashes when uploading multiple receipts at once\n\n4. **Pricing for small teams** - At $5/month per user, it's expensive for freelancers and solopreneurs\n\nWould you like me to dive deeper into any of these pain points?",
    citations: [
      "https://news.ycombinator.com/item?id=123456",
      "https://softwarerecs.stackexchange.com/q/12345",
      "https://indiehackers.com/post/123456",
    ],
    created_at: new Date().toISOString(),
  },
];

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE_URL}/auth/signup`, async () => {
    await delay(500);
    return HttpResponse.json({
      token: "mock-jwt-token-12345",
      user: mockUser,
    });
  }),

  http.post(`${API_BASE_URL}/auth/login`, async ({ request }) => {
    await delay(500);
    const body = await request.json();
    const { email, password } = body as { email: string; password: string };

    if (email === "test@example.com" && password === "password123") {
      return HttpResponse.json({
        token: "mock-jwt-token-12345",
        user: mockUser,
      });
    }

    return new HttpResponse("Invalid credentials", { status: 401 });
  }),

  http.get(`${API_BASE_URL}/auth/me`, async ({ cookies }) => {
    await delay(200);
    if (cookies.access_token) {
      return HttpResponse.json(mockUser);
    }
    return new HttpResponse("Unauthorized", { status: 401 });
  }),

  // Projects endpoints
  http.get(`${API_BASE_URL}/projects`, async () => {
    await delay(300);
    return HttpResponse.json(mockProjects);
  }),

  http.post(`${API_BASE_URL}/projects`, async ({ request }) => {
    await delay(500);
    const body = await request.json();
    const newProject = {
      id: `project-${Date.now()}`,
      ...body,
      created_at: new Date().toISOString(),
      archived: false,
    };
    mockProjects.push(newProject);
    return HttpResponse.json(newProject, { status: 201 });
  }),

  http.get(`${API_BASE_URL}/projects/:id`, async ({ params }) => {
    await delay(200);
    const project = mockProjects.find((p) => p.id === params.id);
    if (project) {
      return HttpResponse.json(project);
    }
    return new HttpResponse("Project not found", { status: 404 });
  }),

  http.delete(`${API_BASE_URL}/projects/:id`, async ({ params }) => {
    await delay(300);
    const index = mockProjects.findIndex((p) => p.id === params.id);
    if (index !== -1) {
      mockProjects.splice(index, 1);
      return new HttpResponse(null, { status: 204 });
    }
    return new HttpResponse("Project not found", { status: 404 });
  }),

  // Runs endpoints
  http.post(`${API_BASE_URL}/projects/:projectId/runs`, async ({ params }) => {
    await delay(500);
    const newRun = {
      id: `run-${Date.now()}`,
      project_id: params.projectId,
      status: "pending" as const,
      created_at: new Date().toISOString(),
    };
    return HttpResponse.json(newRun, { status: 201 });
  }),

  http.get(`${API_BASE_URL}/runs/:id`, async ({ params }) => {
    await delay(200);
    return HttpResponse.json({
      ...mockRun,
      id: params.id,
    });
  }),

  http.post(`${API_BASE_URL}/runs/:id/cancel`, async () => {
    await delay(300);
    return new HttpResponse(null, { status: 204 });
  }),

  // SSE endpoint - mock with server-sent events
  http.get(`${API_BASE_URL}/runs/:id/stream`, async ({ params }) => {
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
      async start(controller) {
        const events = [
          { type: "plan", agent: "orchestrator", payload: { message: "Planning research strategy..." } },
          { type: "agent_started", agent: "scraper", payload: { message: "Starting competitor research..." } },
          { type: "tool_called", agent: "scraper", payload: { tool: "http_fetch", url: "https://expensify.com/pricing" } },
          { type: "tool_called", agent: "scraper", payload: { tool: "http_fetch", url: "https://dext.com/pricing" } },
          { type: "agent_finished", agent: "scraper", payload: { urls_scraped: 3 } },
          { type: "agent_started", agent: "social", payload: { message: "Mining HN and Stack Exchange..." } },
          { type: "tool_called", agent: "social", payload: { tool: "hn_search", query: "Expensify alternatives" } },
          { type: "tool_called", agent: "social", payload: { tool: "stackexchange_search", query: "receipt scanner apps" } },
          { type: "agent_finished", agent: "social", payload: { results_found: 15 } },
          { type: "agent_started", agent: "synthesizer", payload: { message: "Writing final report..." } },
          { type: "agent_finished", agent: "synthesizer", payload: { report_length: 2500 } },
        ];

        for (const event of events) {
          await delay(800);
          controller.enqueue(
            encoder.encode(`event: progress\ndata: ${JSON.stringify({
              ...event,
              timestamp: new Date().toISOString(),
            })}\n\n`)
          );
        }

        await delay(500);
        controller.enqueue(
          encoder.encode(`event: complete\ndata: ${JSON.stringify({
            run_id: params.id,
            status: "completed",
          })}\n\n`)
        );
        controller.close();
      },
    });

    return new HttpResponse(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  }),

  // Report endpoint
  http.get(`${API_BASE_URL}/projects/:projectId/report`, async ({ params }) => {
    await delay(500);
    return HttpResponse.json({
      id: "report-1",
      project_id: params.projectId,
      report_md: mockRun.report_md,
      created_at: new Date().toISOString(),
    });
  }),

  // Chat endpoints
  http.get(`${API_BASE_URL}/projects/:projectId/chat/messages`, async () => {
    await delay(300);
    return HttpResponse.json(mockMessages);
  }),

  http.post(`${API_BASE_URL}/projects/:projectId/chat`, async ({ request }) => {
    await delay(1000);
    const body = await request.json();
    const { content } = body as { content: string };

    const newUserMessage = {
      id: `msg-${Date.now()}`,
      project_id: "project-1",
      role: "user" as const,
      content,
      citations: [],
      created_at: new Date().toISOString(),
    };

    const newAssistantMessage = {
      id: `msg-${Date.now() + 1}`,
      project_id: "project-1",
      role: "assistant" as const,
      content: `Great question about "${content}"! Based on the research collected, here's what I found:\n\nThe market shows strong demand for this feature, with 67% of users requesting it in surveys. Competitors who implemented similar features saw 23% increase in retention.\n\nWould you like me to elaborate on any specific aspect?`,
      citations: [
        "https://example.com/market-survey",
        "https://example.com/retention-study",
      ],
      created_at: new Date().toISOString(),
    };

    mockMessages.push(newUserMessage, newAssistantMessage);
    return HttpResponse.json(newAssistantMessage);
  }),
];
