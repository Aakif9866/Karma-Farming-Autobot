export type NavItem = { href: string; label: string; phase?: number };

export const NAV: NavItem[] = [
  { href: "/", label: "Dashboard" },
  { href: "/daily", label: "Daily Trends", phase: 4 },
  { href: "/trends", label: "Trend Explorer", phase: 3 },
  { href: "/trends?region=IN", label: "Indian Reddit", phase: 3 },
  { href: "/trends?region=GLOBAL", label: "Global Reddit", phase: 3 },
  { href: "/memes", label: "Meme Intelligence", phase: 5 },
  { href: "/opinions", label: "Opinion Explorer", phase: 4 },
  { href: "/subreddits", label: "Subreddits", phase: 2 },
  { href: "/opportunities", label: "Opportunities", phase: 6 },
  { href: "/studio", label: "Content Studio", phase: 7 },
  { href: "/agents", label: "Agent Monitor", phase: 2 },
  { href: "/settings", label: "Settings", phase: 2 },
];

/** Placeholder sections served by app/(app)/[section] until their phase replaces them. */
export const SECTIONS: Record<string, NavItem> = Object.fromEntries(
  NAV.filter((n) => n.phase && !n.href.includes("?")).map((n) => [n.href.slice(1), n]),
);

export function isActive(item: NavItem, pathname: string, region: string | null): boolean {
  const [path, query] = item.href.split("?");
  if (path === "/") return pathname === "/";
  if (pathname !== path) return false;
  const itemRegion = query ? new URLSearchParams(query).get("region") : null;
  return itemRegion === region;
}
