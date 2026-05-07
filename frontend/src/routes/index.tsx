import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  return (
    <div className="flex flex-col items-center gap-6 py-20 text-center">
      <h1 className="text-4xl font-bold text-gray-900">
        ScopeIQ
      </h1>
      <p className="max-w-xl text-lg text-gray-500">
        Should I build this? Get the answer in 5 minutes.
      </p>
      <p className="text-sm text-gray-400">
        Scaffold ready — auth UI coming in C-PR3.
      </p>
    </div>
  );
}
