import { describe, expect, it } from "vitest";

import { NAV, SECTIONS, isActive } from "./nav";

const byLabel = (label: string) => NAV.find((n) => n.label === label)!;

describe("isActive", () => {
  it("matches the dashboard only on /", () => {
    expect(isActive(byLabel("Dashboard"), "/", null)).toBe(true);
    expect(isActive(byLabel("Dashboard"), "/memes", null)).toBe(false);
  });

  it("distinguishes region presets of the trend explorer", () => {
    expect(isActive(byLabel("Trend Explorer"), "/trends", null)).toBe(true);
    expect(isActive(byLabel("Indian Reddit"), "/trends", "IN")).toBe(true);
    expect(isActive(byLabel("Trend Explorer"), "/trends", "IN")).toBe(false);
    expect(isActive(byLabel("Global Reddit"), "/trends", "IN")).toBe(false);
  });
});

describe("SECTIONS", () => {
  it("has a placeholder for every phased page and none for query presets", () => {
    expect(Object.keys(SECTIONS)).toContain("memes");
    expect(Object.keys(SECTIONS).some((k) => k.includes("?"))).toBe(false);
  });
});
