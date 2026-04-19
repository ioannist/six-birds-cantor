import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          schema_version: "v1",
          generated_at_utc: "2026-03-19T00:00:00Z",
          datasets: [],
        }),
    });
  });

  it("renders the shell with router", () => {
    render(<App />);
    expect(screen.getByText("Six Birds Cantor")).toBeInTheDocument();
  });

  it("defaults to Overview page", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", { name: "Overview" }),
    ).toBeInTheDocument();
  });
});
