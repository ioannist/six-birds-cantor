import { render, screen } from "@testing-library/react";
import StyleGuidePage from "./StyleGuidePage";

describe("StyleGuidePage", () => {
  beforeEach(() => {
    render(<StyleGuidePage />);
  });

  it("renders the style guide container", () => {
    expect(screen.getByTestId("style-guide")).toBeInTheDocument();
  });

  it("shows all 6 primitive labels", () => {
    const primitives = ["P1", "P2", "P3", "P4", "P5", "P6"];
    for (const p of primitives) {
      expect(screen.getByText(new RegExp(`^${p} —`))).toBeInTheDocument();
    }
  });

  it("shows T0 and T1 theory labels", () => {
    expect(screen.getByText("Base Theory (T0)")).toBeInTheDocument();
    expect(screen.getByText("Extended Theory (T1)")).toBeInTheDocument();
  });

  it("renders all 4 badge variants", () => {
    const badges = screen.getAllByText(/^(Closed|Support-only|Reserve|Non-claim)$/);
    const labels = badges.map((el) => el.textContent);
    expect(labels).toContain("Closed");
    expect(labels).toContain("Support-only");
    expect(labels).toContain("Reserve");
    expect(labels).toContain("Non-claim");
  });

  it("renders all 4 icon variants with labels", () => {
    expect(screen.getByText("Saturation")).toBeInTheDocument();
    expect(screen.getByText("Forcing")).toBeInTheDocument();
    expect(screen.getByText("Non-factorization")).toBeInTheDocument();
    expect(screen.getByText("Macro-admissibility obstruction")).toBeInTheDocument();
  });

  it("renders swatches with color dots", () => {
    const swatches = screen.getAllByTestId("swatch");
    // 6 primitives + 2 theory = 8 swatches
    expect(swatches.length).toBe(8);
  });

  it("renders example cards", () => {
    expect(screen.getByText("Lawfulness Theoremlet")).toBeInTheDocument();
    expect(screen.getByText(/Broader-class Ambition/)).toBeInTheDocument();
  });
});
