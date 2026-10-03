"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";

import { cn } from "@/lib/utils";
import { NAV, isActive } from "@/lib/nav";

export function Sidebar() {
  const pathname = usePathname();
  const region = useSearchParams().get("region");

  return (
    <nav aria-label="Main" className="flex flex-col gap-0.5 p-3">
      <Link href="/" className="mb-4 flex items-center gap-2 px-2 py-1">
        <span aria-hidden className="size-2.5 rounded-full bg-primary" />
        <span className="text-sm font-semibold tracking-tight">Karma Farming Autobot</span>
      </Link>
      {NAV.map((item) => {
        const active = isActive(item, pathname, region);
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex items-center justify-between rounded-md px-2 py-1.5 text-sm text-sidebar-foreground transition-colors hover:bg-sidebar-accent focus-visible:outline-2 focus-visible:outline-ring",
              active && "bg-sidebar-accent text-foreground",
            )}
          >
            <span className="flex items-center gap-2">
              <span
                aria-hidden
                className={cn("h-4 w-0.5 rounded-full", active ? "bg-primary" : "bg-transparent")}
              />
              {item.label}
            </span>
            {item.phase && <span className="text-[10px] text-muted-foreground">P{item.phase}</span>}
          </Link>
        );
      })}
    </nav>
  );
}
