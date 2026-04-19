import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import LiveSubstratePage from "./LiveSubstratePage";
import { useAppStore } from "../app/store";
import type { ContinuousTrajectory } from "../data/types";

function buildMockTrajectory(
  witnessId: string,
  steps: number,
  dim: number,
): ContinuousTrajectory {
  const timeline = Array.from({ length: steps }, (_, i) => ({
    step: i + 1,
    variation: 0.1 + Math.sin(i / 10) * 0.05,
    tau: 0.9 + i * 0.0001,
    budget: 3.0 + i * 0.005,
    lens: i % 3 === 0 ? "spectral_lens" : "row_similarity_cluster_lens",
    packaging:
      i % 4 === 0
        ? "partition_cluster_packaging"
        : "return_core_packaging",
    action_weights: {
      P1: 0.15,
      P2: 0.1,
      P3: 0.25,
      P4: 0.15,
      P5: 0.2,
      P6: 0.15,
    },
    primitive_activity: {
      P1: true,
      P2: true,
      P3: true,
      P4: true,
      P5: true,
      P6: true,
    },
  }));

  const kernel = Array.from({ length: dim }, (_, i) =>
    Array.from({ length: dim }, (_, j) =>
      i === j ? 0.5 : 0.5 / (dim - 1),
    ),
  );

  const kernelSnapshots = [
    { step: 1, kernel },
    { step: 11, kernel },
    { step: steps, kernel },
  ];

  return {
    schema_version: "v1",
    witness_id: `generated.${witnessId}`,
    config: { steps, kernel_dim: dim, seed: 17 },
    total_steps: steps,
    kernel_snapshot_interval: 10,
    kernel_snapshots: kernelSnapshots,
    timeline,
  };
}

const MOCK_KERNEL = buildMockTrajectory("continuous_full_loop_kernel", 100, 4);
const MOCK_SHELL = buildMockTrajectory(
  "continuous_full_loop_kernel_shell",
  60,
  5,
);

function mockFetchForWitness(witnessId: string) {
  return vi.fn().mockImplementation((url: string) => {
    let data: ContinuousTrajectory;
    if (url.includes("kernel_shell")) {
      data = MOCK_SHELL;
    } else {
      data = MOCK_KERNEL;
    }
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(data),
    });
  });
}

function renderPage() {
  const router = createMemoryRouter(
    [{ index: true, element: <LiveSubstratePage /> }],
    { initialEntries: ["/"] },
  );
  return render(<RouterProvider router={router} />);
}

beforeEach(() => {
  useAppStore.setState({
    selectedConfigId: "default",
    selectedWitnessId: "generated.continuous_full_loop_kernel",
    selectedShell: "audited_shell",
    selectedTheoremLayer: "hybrid",
    selectedTimeIndex: 0,
  });
  globalThis.fetch = mockFetchForWitness("continuous_full_loop_kernel");
});

describe("LiveSubstratePage", () => {
  it("renders the page", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("live-substrate-page")).toBeInTheDocument();
    });
  });

  it("shows the kernel heatmap", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("kernel-heatmap")).toBeInTheDocument();
    });
  });

  it("shows lens and packaging state cards", async () => {
    renderPage();
    await waitFor(() => {
      expect(
        screen.getByTestId("state-card-active-lens"),
      ).toBeInTheDocument();
      expect(
        screen.getByTestId("state-card-active-packaging"),
      ).toBeInTheDocument();
    });
  });

  it("shows budget and tau state cards", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("state-card-budget")).toBeInTheDocument();
      expect(screen.getByTestId("state-card-tau")).toBeInTheDocument();
    });
  });

  it("shows budget and tau sparklines", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("sparkline-budget")).toBeInTheDocument();
      expect(screen.getByTestId("sparkline-tau")).toBeInTheDocument();
    });
  });

  it("shows primitive activity row", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("primitive-activity")).toBeInTheDocument();
    });
  });

  it("shows timeline scrubber", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("timeline-scrubber")).toBeInTheDocument();
    });
  });

  it("moving time index updates state card values", async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId("live-substrate-page")).toBeInTheDocument();
    });

    // Change time index in store
    useAppStore.getState().setTimeIndex(50);

    // The budget value should change (mock data varies with step)
    await waitFor(() => {
      const budgetCard = screen.getByTestId("state-card-budget");
      // step 50 budget = 3.0 + 50 * 0.005 = 3.25
      expect(budgetCard.textContent).toContain("3.25");
    });
  });

  it("loads shell witness when witness is changed", async () => {
    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId("live-substrate-page")).toBeInTheDocument();
    });

    // Switch to shell witness
    globalThis.fetch = mockFetchForWitness("continuous_full_loop_kernel_shell");
    useAppStore.getState().setWitnessId("generated.continuous_full_loop_kernel_shell");

    await waitFor(() => {
      expect(screen.getByText(/continuous_full_loop_kernel_shell/)).toBeInTheDocument();
    });
  });
});
