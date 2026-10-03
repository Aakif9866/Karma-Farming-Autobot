import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";

import { EmptyState } from "./empty-state";

it("renders title and hint", () => {
  render(<EmptyState title="No data">Arrives in Phase 3.</EmptyState>);
  expect(screen.getByText("No data")).toBeInTheDocument();
  expect(screen.getByText("Arrives in Phase 3.")).toBeInTheDocument();
});
