import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api/server";
import type { Readiness } from "@/lib/api/types";

async function getReadiness(): Promise<Readiness | null> {
  try {
    const res = await apiFetch("/health/ready");
    return (await res.json()) as Readiness;
  } catch {
    return null;
  }
}

const WIDGETS = [
  { title: "Trending topics", phase: 3 },
  { title: "Emerging discussions", phase: 3 },
  { title: "India vs global", phase: 3 },
  { title: "Trending memes", phase: 5 },
  { title: "Recent recommendations", phase: 6 },
  { title: "Data collection", phase: 2 },
];

export default async function DashboardPage() {
  const readiness = await getReadiness();

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold tracking-tight">Dashboard</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">System status</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {readiness ? (
            Object.entries(readiness.checks).map(([name, status]) => (
              <Badge key={name} variant={status === "ok" ? "default" : "destructive"}>
                {name}: {status}
              </Badge>
            ))
          ) : (
            <Badge variant="destructive">API unreachable</Badge>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {WIDGETS.map((w) => (
          <EmptyState key={w.title} title={w.title}>
            No data yet. Arrives in Phase {w.phase}.
          </EmptyState>
        ))}
      </div>
    </div>
  );
}
