import { render, screen, waitFor } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import ExtensionCertificatePage from "./ExtensionCertificatePage";
import { useAppStore } from "../app/store";
import { _resetPolicyCache } from "../claims/useAnnotationPolicy";
import type { ExtensionView } from "../data/types";

const MOCK_POLICY = {
  schema_version: "v1",
  paper_core_positioning: "level3_core_on_audited_shell",
  core_claim_ids: ["strict_theory_extension_theoremlet"],
  support_only_claim_ids: [],
  reserve_claim_ids: [],
  nonclaim_ids: [],
  scope_guards: [],
  per_theoremlet_bindings: [],
  claim_classifications: {},
  phrases_to_avoid: [],
};

const MOCK_EXT: ExtensionView = {
  schema_version: "v1",
  witness_id: "generated.continuous_full_loop_kernel",
  base_theory_id: "T0_cocycle_pressure_theory",
  extended_theory_id: "T1_hybrid_cocycle_plus_completion_theory",
  base_object_map: {
    map_id: "t0_cocycle_object_map",
    description: "Audited cocycle descriptor quotient on the shell-stable class.",
  },
  extended_object_map: {
    map_id: "t1_packaged_object_map",
    description: "Packaged fixed-point strata induced by the completion endomap.",
  },
  factorization_test: {
    factor_through_T0: false,
    non_factorization_rate: 0.8333,
    multiple_T1_strata_per_T0_class: 10,
    note: "Non-factorization holds on the audited shell.",
  },
  verdicts: {
    factorization: "non_factorization_closed_on_audited_shell",
    object_identity: "t1_objects_finer_than_t0_objects",
    saturation: "saturation_active_on_audited_shell",
    forcing: "forcing_active_with_persistent_new_strata",
    macro_admissibility: "t0_too_coarse_on_canonical_object",
  },
  saturation_summary: { saturated: false, saturated_panel_count: 3, total_panels: 9 },
  forcing_summary: { p4_from_p5_event_count: 36, total_runs: 36 },
  macro_admissibility_summary: { obstruction_count: 36, total_runs: 36 },
  completion_summary: { distinct_strata: 30, fixed_point_runs: 20, cycle_runs: 10, nonconvergent_runs: 6 },
  scope: "audited_shell_only",
  theoremlet: {
    theoremlet_id: "strict_theory_extension_theoremlet",
    status: "closed_in_note",
    class_scope: "continuous_full_loop_lawful_kernel_class_shell_stable",
    allowed_claim_ids: ["strict_theory_extension_theoremlet"],
  },
  claim_binding: {
    theoremlet_id: "strict_theory_extension_theoremlet",
    allowed_claim_ids: ["strict_theory_extension_theoremlet"],
    figure_ids: ["tbl_strict_theory_extension"],
  },
};

function renderPage() {
  globalThis.fetch = vi.fn().mockImplementation((url: string) => {
    const data = url.includes("annotation_policy") ? MOCK_POLICY : MOCK_EXT;
    return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
  });
  const router = createMemoryRouter(
    [{ index: true, element: <ExtensionCertificatePage /> }],
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

describe("ExtensionCertificatePage", () => {
  it("renders the page", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("extension-page")).toBeInTheDocument();
    });
  });

  it("shows scope banner", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("scope-banner")).toBeInTheDocument();
      expect(screen.getByText("audited shell only")).toBeInTheDocument();
    });
  });

  it("shows failed factorization diagram", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("factorization-diagram")).toBeInTheDocument();
    });
  });

  it("shows non-factorization verdict in verdict grid", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("verdict-grid")).toBeInTheDocument();
      expect(screen.getByText("Non-factorization")).toBeInTheDocument();
    });
  });

  it("shows saturation certificate", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("saturation-certificate")).toBeInTheDocument();
    });
  });

  it("shows forcing certificate", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("forcing-certificate")).toBeInTheDocument();
    });
  });

  it("shows macro-admissibility obstruction", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("macro-obstruction")).toBeInTheDocument();
    });
  });

  it("shows allowed extension claim", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("extension-claim")).toBeInTheDocument();
      expect(screen.getByText(/strict theory extension theoremlet/)).toBeInTheDocument();
    });
  });

  it("only renders the strict extension theoremlet claim", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("extension-page")).toBeInTheDocument();
    });
    // The allowed claim section should only contain the strict extension claim
    const claimSection = screen.getByTestId("extension-claim");
    expect(claimSection.textContent).toContain("strict theory extension");
    expect(claimSection.textContent).not.toContain("conditional pressure disintegration");
    expect(claimSection.textContent).not.toContain("packaging-completion");
  });

  it("loads shell witness when changed", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("extension-page")).toBeInTheDocument();
    });

    const shellExt = { ...MOCK_EXT, witness_id: "generated.continuous_full_loop_kernel_shell" };
    globalThis.fetch = vi.fn().mockImplementation((url: string) => {
      const data = url.includes("annotation_policy") ? MOCK_POLICY : shellExt;
      return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
    });
    useAppStore.getState().setWitnessId("generated.continuous_full_loop_kernel_shell");

    await waitFor(() => {
      expect(screen.getByText(/continuous_full_loop_kernel_shell/)).toBeInTheDocument();
    });
  });
});
