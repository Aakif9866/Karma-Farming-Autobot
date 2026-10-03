import { notFound } from "next/navigation";

import { EmptyState } from "@/components/empty-state";
import { SECTIONS } from "@/lib/nav";

// Placeholder for sections that land in later phases; a real app/(app)/<name>/page.tsx overrides it.
export default async function SectionPage({ params }: PageProps<"/[section]">) {
  const item = SECTIONS[(await params).section];
  if (!item) notFound();

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold tracking-tight">{item.label}</h1>
      <EmptyState title="Not built yet">This page arrives in Phase {item.phase}.</EmptyState>
    </div>
  );
}
