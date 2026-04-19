import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import AppShell from "./AppShell";
import { useAppStore } from "../app/store";
import type { TheoremLayer } from "../app/store";

// Simple test pages that display shared state
function TestPage({ label }: { label: string }) {
  const store = useAppStore();
  return (
    <div data-testid="page-content">
      <span data-testid="page-label">{label}</span>
      <span data-testid="layer">{store.selectedTheoremLayer}</span>
      <span data-testid="witness">{store.selectedWitnessId}</span>
    </div>
  );
}

function renderWithRouter(initialPath = "/") {
  const router = createMemoryRouter(
    [
      {
        element: <AppShell />,
        children: [
          { index: true, element: <TestPage label="Overview" /> },
          { path: "live-substrate", element: <TestPage label="Live substrate" /> },
          { path: "t0-vs-t1", element: <TestPage label="T0 vs T1" /> },
          { path: "extension-certificate", element: <TestPage label="Extension certificate" /> },
          { path: "thermodynamic-consequence", element: <TestPage label="Thermodynamic consequence" /> },
          { path: "primitive-knockouts", element: <TestPage label="Primitive knockouts" /> },
          { path: "claim-scope", element: <TestPage label="Claim scope" /> },
          { path: "style-guide", element: <TestPage label="Style guide" /> },
        ],
      },
    ],
    { initialEntries: [initialPath] },
  );
  return render(<RouterProvider router={router} />);
}

// Reset store between tests
beforeEach(() => {
  useAppStore.setState({
    selectedConfigId: "default",
    selectedWitnessId: "generated.continuous_full_loop_kernel",
    selectedShell: "audited_shell",
    selectedTheoremLayer: "hybrid",
    selectedTimeIndex: 0,
  });
});

describe("AppShell", () => {
  it("renders the shell header", () => {
    renderWithRouter();
    expect(screen.getByText("Six Birds Cantor")).toBeInTheDocument();
  });

  it("renders all 7 main nav labels", () => {
    renderWithRouter();
    const nav = screen.getByRole("navigation", { name: "main navigation" });
    const labels = [
      "Overview",
      "Live substrate",
      "T0 vs T1",
      "Extension certificate",
      "Thermodynamic consequence",
      "Primitive knockouts",
      "Claim scope",
    ];
    for (const label of labels) {
      expect(within(nav).getByText(label)).toBeInTheDocument();
    }
  });

  it("renders style guide link", () => {
    renderWithRouter();
    expect(screen.getByText("Style guide")).toBeInTheDocument();
  });

  it("renders shared controls", () => {
    renderWithRouter();
    const controls = screen.getByRole("complementary", { name: "shared controls" });
    expect(controls).toBeInTheDocument();
    expect(screen.getByText("Theorem layer")).toBeInTheDocument();
    expect(screen.getByLabelText("witness")).toBeInTheDocument();
    expect(screen.getByLabelText("shell")).toBeInTheDocument();
    expect(screen.getByLabelText("time index")).toBeInTheDocument();
  });

  it("defaults to Overview page", () => {
    renderWithRouter();
    expect(screen.getByTestId("page-label")).toHaveTextContent("Overview");
  });

  it("navigates to a different section", async () => {
    const user = userEvent.setup();
    renderWithRouter();

    await user.click(screen.getByRole("link", { name: "Live substrate" }));
    expect(screen.getByTestId("page-label")).toHaveTextContent("Live substrate");
  });

  it("navigating changes the visible section for all routes", async () => {
    const user = userEvent.setup();
    renderWithRouter();

    const routes = [
      { link: "T0 vs T1", label: "T0 vs T1" },
      { link: "Claim scope", label: "Claim scope" },
      { link: "Overview", label: "Overview" },
    ];

    for (const route of routes) {
      await user.click(screen.getByRole("link", { name: route.link }));
      expect(screen.getByTestId("page-label")).toHaveTextContent(route.label);
    }
  });
});

describe("Shared state across navigation", () => {
  it("changing theorem layer on one page is reflected on another", async () => {
    const user = userEvent.setup();
    renderWithRouter();

    // Verify default
    expect(screen.getByTestId("layer")).toHaveTextContent("hybrid");

    // Change to T0
    await user.click(screen.getByLabelText("T0"));
    expect(screen.getByTestId("layer")).toHaveTextContent("T0");

    // Navigate away and verify state persists
    await user.click(screen.getByRole("link", { name: "Live substrate" }));
    expect(screen.getByTestId("page-label")).toHaveTextContent("Live substrate");
    expect(screen.getByTestId("layer")).toHaveTextContent("T0");
  });

  it("changing witness on one page is reflected on another", async () => {
    const user = userEvent.setup();
    renderWithRouter();

    const select = screen.getByLabelText("witness");
    await user.selectOptions(select, "generated.continuous_full_loop_kernel_shell");

    expect(screen.getByTestId("witness")).toHaveTextContent(
      "generated.continuous_full_loop_kernel_shell",
    );

    // Navigate and check
    await user.click(screen.getByRole("link", { name: "T0 vs T1" }));
    expect(screen.getByTestId("witness")).toHaveTextContent(
      "generated.continuous_full_loop_kernel_shell",
    );
  });

  it("state survives full round-trip navigation", async () => {
    const user = userEvent.setup();
    renderWithRouter();

    // Set T1
    await user.click(screen.getByLabelText("T1"));

    // Navigate away
    await user.click(screen.getByRole("link", { name: "Claim scope" }));
    expect(screen.getByTestId("layer")).toHaveTextContent("T1");

    // Navigate back
    await user.click(screen.getByRole("link", { name: "Overview" }));
    expect(screen.getByTestId("layer")).toHaveTextContent("T1");
  });
});
