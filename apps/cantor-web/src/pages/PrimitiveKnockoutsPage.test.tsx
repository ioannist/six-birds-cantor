import { render, screen, waitFor } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import PrimitiveKnockoutsPage from "./PrimitiveKnockoutsPage";
import { useAppStore } from "../app/store";
import { _resetPolicyCache } from "../claims/useAnnotationPolicy";
import type { KnockoutsView } from "../data/types";

const MOCK_POLICY = {
  schema_version: "v1",
  paper_core_positioning: "level3_core_on_audited_shell",
  core_claim_ids: ["continuous_full_loop_lawfulness_theoremlet"],
  support_only_claim_ids: [],
  reserve_claim_ids: [],
  nonclaim_ids: [],
  scope_guards: [],
  per_theoremlet_bindings: [],
  claim_classifications: {},
  phrases_to_avoid: [],
};

const MOCK_KO: KnockoutsView = {
  schema_version: "v1",
  witness_id: "generated.continuous_full_loop_kernel",
  scope: "audited_shell_only",
  full_loop: {
    lens_switch_count: 249,
    packaging_switch_count: 249,
    tau_switch_count: 7,
    budget_min: 2.714,
    budget_max: 12.0,
    tau_min: 0.6,
    tau_max: 0.982,
    mean_variation: 0.178,
    closure_defect_proxy: 0.12,
  },
  knockouts: [
    {
      removed: "P1",
      material_degradation: true,
      material_reasons: ["tau switching collapsed"],
      closure_defect_proxy: 0.15,
      summary: { lens_switch_count: 249, packaging_switch_count: 249, tau_switch_count: 1, budget_min: 2.71, budget_max: 12.0, tau_min: 0.6, tau_max: 0.98, mean_variation: 0.16 },
    },
    {
      removed: "P2",
      material_degradation: true,
      material_reasons: ["stabilization regime changed", "tau switching collapsed"],
      closure_defect_proxy: 0.087,
      summary: { lens_switch_count: 249, packaging_switch_count: 249, tau_switch_count: 0, budget_min: 2.74, budget_max: 12.0, tau_min: 0.6, tau_max: 0.98, mean_variation: 0.1 },
    },
    {
      removed: "P3",
      material_degradation: true,
      material_reasons: ["lens switching collapsed", "packaging switching collapsed", "tau switching collapsed"],
      closure_defect_proxy: 0.046,
      summary: { lens_switch_count: 0, packaging_switch_count: 0, tau_switch_count: 0, budget_min: 2.73, budget_max: 12.0, tau_min: 0.6, tau_max: 0.98, mean_variation: 0.04 },
    },
    {
      removed: "P4",
      material_degradation: true,
      material_reasons: ["lens switching collapsed"],
      closure_defect_proxy: 0.195,
      summary: { lens_switch_count: 0, packaging_switch_count: 249, tau_switch_count: 7, budget_min: 2.62, budget_max: 12.0, tau_min: 0.6, tau_max: 0.98, mean_variation: 0.2 },
    },
    {
      removed: "P5",
      material_degradation: true,
      material_reasons: ["packaging switching collapsed", "tau switching collapsed", "budget range collapsed"],
      closure_defect_proxy: 0.038,
      summary: { lens_switch_count: 249, packaging_switch_count: 0, tau_switch_count: 2, budget_min: 2.19, budget_max: 3.86, tau_min: 0.6, tau_max: 0.98, mean_variation: 0.05 },
    },
    {
      removed: "P6",
      material_degradation: true,
      material_reasons: ["budget range collapsed"],
      closure_defect_proxy: 0.169,
      summary: { lens_switch_count: 249, packaging_switch_count: 249, tau_switch_count: 7, budget_min: 2.5, budget_max: 2.5, tau_min: 0.6, tau_max: 0.98, mean_variation: 0.18 },
    },
  ],
  theoremlet: {
    theoremlet_id: "continuous_full_loop_lawfulness_theoremlet",
    status: "closed_in_note",
    allowed_claim_ids: ["continuous_full_loop_lawfulness_theoremlet"],
  },
  claim_binding: {
    theoremlet_id: "continuous_full_loop_lawfulness_theoremlet",
    allowed_claim_ids: ["continuous_full_loop_lawfulness_theoremlet"],
    figure_ids: ["fig_primitive_knockout_closure"],
  },
};

function renderPage() {
  globalThis.fetch = vi.fn().mockImplementation((url: string) => {
    const data = url.includes("annotation_policy") ? MOCK_POLICY : MOCK_KO;
    return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
  });
  const router = createMemoryRouter(
    [{ index: true, element: <PrimitiveKnockoutsPage /> }],
    { initialEntries: ["/"] },
  );
  return render(<RouterProvider router={router} />);
}

beforeEach(() => {
  _resetPolicyCache();
  useAppStore.setState({
    selectedWitnessId: "generated.continuous_full_loop_kernel",
    selectedTheoremLayer: "hybrid",
    selectedTimeIndex: 0,
    selectedShell: "audited_shell",
    selectedConfigId: "default",
  });
});

describe("PrimitiveKnockoutsPage", () => {
  it("renders the page", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("knockouts-page")).toBeInTheDocument();
    });
  });

  it("shows full loop reference card", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("full-loop-card")).toBeInTheDocument();
    });
  });

  it("shows all 6 knockout labels", async () => {
    renderPage();
    await waitFor(() => {
      for (const p of ["P1", "P2", "P3", "P4", "P5", "P6"]) {
        expect(screen.getByTestId(`knockout-${p}`)).toBeInTheDocument();
      }
    });
  });

  it("shows degradation badges", async () => {
    renderPage();
    await waitFor(() => {
      const badges = screen.getAllByText("degraded");
      expect(badges.length).toBe(6);
    });
  });

  it("shows side-by-side metrics", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("knockout-grid")).toBeInTheDocument();
    });
  });

  it("P5 knockout shows material degradation reasons", async () => {
    renderPage();
    await waitFor(() => {
      const p5 = screen.getByTestId("knockout-P5");
      expect(p5.textContent).toContain("packaging switching collapsed");
      expect(p5.textContent).toContain("budget range collapsed");
    });
  });

  it("shows allowed claim", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("knockout-claim")).toBeInTheDocument();
    });
  });

  it("loads shell witness when changed", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("knockouts-page")).toBeInTheDocument();
    });

    const shellData = { ...MOCK_KO, witness_id: "generated.continuous_full_loop_kernel_shell" };
    globalThis.fetch = vi.fn().mockImplementation((url: string) => {
      const data = url.includes("annotation_policy") ? MOCK_POLICY : shellData;
      return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
    });
    useAppStore.getState().setWitnessId("generated.continuous_full_loop_kernel_shell");

    await waitFor(() => {
      expect(screen.getByText(/continuous_full_loop_kernel_shell/)).toBeInTheDocument();
    });
  });
});
