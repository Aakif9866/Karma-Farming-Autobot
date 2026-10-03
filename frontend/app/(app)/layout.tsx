import { redirect } from "next/navigation";
import { Suspense } from "react";

import { LogoutButton } from "@/components/logout-button";
import { Sidebar } from "@/components/sidebar";
import { apiFetch } from "@/lib/api/server";
import type { UserOut } from "@/lib/api/types";

export default async function AppLayout({ children }: LayoutProps<"/">) {
  const res = await apiFetch("/auth/me");
  if (res.status === 401) redirect("/login");
  if (!res.ok) throw new Error(`API error ${res.status} loading session`);
  const user = (await res.json()) as UserOut;

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="border-b border-sidebar-border bg-sidebar md:sticky md:top-0 md:h-screen md:w-60 md:shrink-0 md:overflow-y-auto md:border-r md:border-b-0">
        <Suspense>
          <Sidebar />
        </Suspense>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-12 items-center justify-end gap-3 border-b border-border px-4 md:px-6">
          <span className="truncate text-sm text-muted-foreground">{user.email}</span>
          <LogoutButton />
        </header>
        <main className="flex-1 px-4 py-6 md:px-6">{children}</main>
      </div>
    </div>
  );
}
