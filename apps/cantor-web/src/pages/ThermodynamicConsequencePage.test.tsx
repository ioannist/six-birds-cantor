import { render, screen, waitFor } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import ThermodynamicConsequencePage from "./ThermodynamicConsequencePage";
import { useAppStore } from "../app/store";
import { _resetPolicyCache } from "../claims/useAnnotationPolicy";
import type { DisintegrationView } from "../data/types";

const MOCK_POLICY = {
  schema_version: "v1",
  paper_core_positioning: "level3_core_on_audited_shell",
  core_claim_ids: ["conditional_pressure_disintegration_theoremlet"],
  support_only_claim_ids: [],
  reserve_claim_ids: [],
  nonclaim_ids: [],
  scope_guards: [],
  per_theoremlet_bindings: [],
  claim_classifications: {},
  phrases_to_avoid: [],
};

const MOCK_DISINT: DisintegrationView = {
  schema_version: "v1",
  witness_id: "generated.continuous_full_loop_kernel",
  base_theory_id: "T0_cocycle_pressure_theory",
  extended_theory_id: "T1_hybrid_cocycle_plus_completion_theory",
  selected_consequence_object: "weighted_package_conditioned_pressure_gap",
  decision: "conditional_disintegration_closed",
  scope: "audited_shell_only",
  t0_pressure: {
    pressure_route: "fekete_sup_cocycle_route",
    fekete_gap_proxy: 0.6558,
    pressure_profiles: {
      "1.0": { gap_proxy: 0.656, pressure_proxy: 0.006358, sign: 1.0 },
    },
  },
  descriptor_summaries: [
    {
      lens_state: "spectral_lens",
      tau: 0.6,
      gap_bounded_away_from_zero: true,
      closure_deficit_proxy: 5.37e-9,
      pressure_gap: {
        "1.0": { gap: 0.1405, t0_pressure: 0.00636, weighted_conditioned_pressure: -0.1341 },
      },
      fiber_count: 3,
    },
    {
      lens_state: "row_similarity_cluster_lens",
      tau: 0.6,
      gap_bounded_away_from_zero: true,
      closure_deficit_proxy: 3.77e-8,
      pressure_gap: {
        "1.0": { gap: 0.1405, t0_pressure: 0.00636, weighted_conditioned_pressure: -0.1342 },
      },
      fiber_count: 3,
    },
  ],
  config_summary: {
    disintegration_supported: true,
    min_gap: 0.0735,
    max_closure_deficit_proxy: 3.77e-8,
    descriptor_count: 6,
    macro_admissibility_summary: { admissible_count: 0, inadmissible_count: 18 },
  },
  shell_stability: {
    gap_bounded_on_both_witnesses: true,
    macro_failure_aligns: true,
    working_route: "conditional_pressure_disintegration_route",
  },
  rejected_routes: {
    direct_stratumwise_separation: {
      status: "rejected",
      reason: "Direct stratumwise root separation was not closed.",
    },
    exact_kl_closure_deficit: {
      status: "support_only",
      reason: "KL-style closure-deficit proxies are supporting evidence.",
    },
  },
  theoremlet: {
    theoremlet_id: "conditional_pressure_disintegration_theoremlet",
    status: "closed_in_note",
    class_scope: "continuous_full_loop_lawful_kernel_class_shell_stable",
    allowed_claim_ids: ["conditional_pressure_disintegration_theoremlet"],
  },
  claim_binding: {
    theoremlet_id: "conditional_pressure_disintegration_theoremlet",
    allowed_claim_ids: ["conditional_pressure_disintegration_theoremlet"],
    figure_ids: ["tbl_conditional_disintegration"],
  },
};

function renderPage() {
  globalThis.fetch = vi.fn().mockImplementation((url: string) => {
    const data = url.includes("annotation_policy") ? MOCK_POLICY : MOCK_DISINT;
    return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
  });
  const router = createMemoryRouter(
    [{ index: true, element: <ThermodynamicConsequencePage /> }],
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

describe("ThermodynamicConsequencePage", () => {
  it("renders the page", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("disintegration-page")).toBeInTheDocument();
    });
  });

  it("shows scope banner", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("scope-banner")).toBeInTheDocument();
    });
  });

  it("shows global T0 pressure object", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("global-pressure")).toBeInTheDocument();
    });
  });

  it("shows weighted package-conditioned pressure gap", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("pressure-gap")).toBeInTheDocument();
      expect(screen.getByText("Weighted Package-Conditioned Pressure Gap")).toBeInTheDocument();
    });
  });

  it("shows consequence object description", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("consequence-object")).toBeInTheDocument();
    });
  });

  it("shows shell stability summary", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("shell-stability")).toBeInTheDocument();
    });
  });

  it("shows rejected routes notice", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("rejected-routes")).toBeInTheDocument();
      expect(screen.getByText("rejected")).toBeInTheDocument();
      expect(screen.getByText("support only")).toBeInTheDocument();
    });
  });

  it("rejected route is not presented as a core claim", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("disintegration-page")).toBeInTheDocument();
    });
    const rejectedSection = screen.getByTestId("rejected-routes");
    expect(rejectedSection.textContent).toContain("rejected");
    expect(rejectedSection.textContent).toContain("not closed");
  });

  it("shows allowed disintegration claim", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("disintegration-claim")).toBeInTheDocument();
      expect(screen.getByText(/conditional pressure disintegration theoremlet/)).toBeInTheDocument();
    });
  });

  it("loads shell witness when changed", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("disintegration-page")).toBeInTheDocument();
    });

    const shellData = { ...MOCK_DISINT, witness_id: "generated.continuous_full_loop_kernel_shell" };
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
