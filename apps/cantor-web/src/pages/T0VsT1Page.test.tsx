import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import T0VsT1Page from "./T0VsT1Page";
import { useAppStore } from "../app/store";
import type { T0View, T1View } from "../data/types";

const MOCK_T0: T0View = {
  schema_version: "v1",
  witness_id: "generated.continuous_full_loop_kernel",
  theory_id: "T0_cocycle_pressure_theory",
  core_class_id: "continuous_full_loop_lawful_kernel_class_shell_stable",
  shell_stable: true,
  t0_object_map: {
    map_id: "t0_cocycle_object_map",
    description: "Audited cocycle descriptor quotient on the shell-stable class.",
  },
  theoremlets: [
    {
      theoremlet_id: "continuous_full_loop_lawfulness_theoremlet",
      status: "closed_in_note",
      class_scope: "continuous_full_loop_lawful_kernel_class_shell_stable",
      assumptions_used: ["continuous_operator_substrate"],
      allowed_claim_ids: ["continuous_full_loop_lawfulness_theoremlet"],
    },
    {
      theoremlet_id: "cocycle_pressure_closure_theoremlet",
      status: "closed_in_note",
      class_scope: "continuous_full_loop_lawful_kernel_class_shell_stable",
      assumptions_used: ["continuous_operator_substrate"],
      allowed_claim_ids: ["cocycle_pressure_closure_theoremlet"],
    },
  ],
  claim_bindings: [
    {
      theoremlet_id: "cocycle_pressure_closure_theoremlet",
      allowed_claim_ids: ["cocycle_pressure_closure_theoremlet"],
      figure_ids: ["tbl_pressure_closure_support"],
    },
  ],
  pressure_object: {
    pressure_route: "fekete_sup_cocycle_route",
    observable_family: "selector_weighted_operator_growth_observable",
    fekete_gap_proxy: 0.6558,
    growth_bound_proxy: 0.2557,
    pressure_profiles: {
      "1.0": { gap_proxy: 0.656, pressure_proxy: 0.006358, sign: 1.0 },
    },
    budget_range: [2.714, 12.0],
    tau_range: [0.6, 0.982],
    shell_exit_count: 0,
    min_lens_margin: 0.437,
    min_packaging_margin: 0.692,
    all_six_primitives_active: true,
  },
  shell_uniform_bounds: {
    budget_range: [2.714, 12.0],
    tau_range: [0.6, 0.982],
    lens_margin_min: 0.433,
    packaging_margin_min: 0.672,
  },
  t1_comparison: {
    _scope: "comparison_only",
    object_identity_verdict: "t1_objects_finer_than_t0_objects",
    factorization_verdict: "non_factorization_closed_on_audited_shell",
    macro_admissibility_verdict: "t0_too_coarse_on_canonical_object",
  },
};

const MOCK_T1: T1View = {
  schema_version: "v1",
  witness_id: "generated.continuous_full_loop_kernel",
  theory_id: "T1_hybrid_cocycle_plus_completion_theory",
  extended_object_map: {
    map_id: "t1_packaged_object_map",
    description: "Packaged fixed-point strata induced by the completion endomap plus forcing structure.",
  },
  completion_config: {
    tau_values: [0.6, 0.75, 0.9],
    lens_states: ["spectral_lens", "row_similarity_cluster_lens", "audit_flow_quantile_lens"],
    initial_distribution_count: 4,
    kernel_dim: 16,
  },
  fixed_point_strata: {
    distinct_count: 30,
    signatures: [[0.1, 0.2], [0.3, 0.4]],
  },
  saturation: {
    saturated: false,
    saturated_panel_count: 3,
    total_panels: 9,
    panel_summaries: [
      { tau: 0.6, lens_state: "spectral_lens", distinct_fixed_points: 4, saturated: true },
      { tau: 0.75, lens_state: "spectral_lens", distinct_fixed_points: 3, saturated: false },
    ],
  },
  run_summaries: [
    {
      tau: 0.6,
      lens_state: "spectral_lens",
      initial_index: 0,
      status: "fixed_point",
      iterations: 12,
      residual: 0.0,
      final_signature_hash: 12345678,
      macro_admissible: true,
    },
  ],
  p4_from_p5_events: [
    {
      tau: 0.6,
      from_lens: "spectral_lens",
      to_lens: "row_similarity_cluster_lens",
      trigger_status: "fixed_point",
      package_count: 3,
    },
  ],
  packaging_identity_changes: [
    {
      tau: 0.6,
      lens_state: "spectral_lens",
      packaging_name: "completion_spectral_packaging",
      packaging_score: 0.52,
      group_count: 2,
    },
    {
      tau: 0.6,
      lens_state: "row_similarity_cluster_lens",
      packaging_name: "completion_cluster_packaging",
      packaging_score: 0.48,
      group_count: 3,
    },
  ],
  t0_comparison: {
    _scope: "comparison_only",
    base_theory_id: "T0_cocycle_pressure_theory",
    base_object_map_id: "t0_cocycle_object_map",
    object_identity_verdict: "t1_objects_finer_than_t0_objects",
    macro_admissibility_verdict: "t0_too_coarse_on_canonical_object",
  },
};

function mockFetch() {
  return vi.fn().mockImplementation((url: string) => {
    const data = url.includes("_t1.json") ? MOCK_T1 : MOCK_T0;
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(data),
    });
  });
}

function renderPage() {
  globalThis.fetch = mockFetch();
  const router = createMemoryRouter(
    [{ index: true, element: <T0VsT1Page /> }],
    { initialEntries: ["/"] },
  );
  return render(<RouterProvider router={router} />);
}

beforeEach(() => {
  useAppStore.setState({
    selectedWitnessId: "generated.continuous_full_loop_kernel",
    selectedTheoremLayer: "hybrid",
    selectedTimeIndex: 0,
    selectedShell: "audited_shell",
    selectedConfigId: "default",
  });
});

describe("T0VsT1Page", () => {
  it("renders the page with view toggle", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
      expect(screen.getByTestId("view-toggle")).toBeInTheDocument();
    });
  });

  it("defaults to T0 view", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-content")).toBeInTheDocument();
    });
  });

  it("shows T0 object map and shell-stable marker", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-object-map")).toBeInTheDocument();
      expect(screen.getByTestId("shell-stable-marker")).toBeInTheDocument();
    });
  });

  it("shows cocycle pressure object on T0 view", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("pressure-object")).toBeInTheDocument();
    });
  });
});

describe("T1 view", () => {
  it("switches to T1 view when T1 Object button is clicked", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "T1 Object" }));
    expect(screen.getByTestId("t1-content")).toBeInTheDocument();
  });

  it("shows T1 object map", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "T1 Object" }));

    expect(screen.getByTestId("t1-object-map")).toBeInTheDocument();
    expect(screen.getByText("t1_packaged_object_map")).toBeInTheDocument();
  });

  it("shows fixed-point strata", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "T1 Object" }));

    expect(screen.getByTestId("fixed-point-strata")).toBeInTheDocument();
    expect(screen.getByText("30")).toBeInTheDocument();
  });

  it("shows saturation status", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "T1 Object" }));

    expect(screen.getByTestId("saturation-card")).toBeInTheDocument();
  });

  it("shows P4←P5 events", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "T1 Object" }));

    expect(screen.getByTestId("p4-from-p5-events")).toBeInTheDocument();
  });

  it("shows packaging identity changes", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "T1 Object" }));

    expect(screen.getByTestId("packaging-identity")).toBeInTheDocument();
  });

  it("T0 comparison on T1 view is labeled comparison only", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "T1 Object" }));

    const section = screen.getByTestId("t0-comparison");
    expect(section).toBeInTheDocument();
    expect(section.textContent).toContain("comparison only");
  });

  it("T1 is presented as its own object, not just comparison", async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });
    await user.click(screen.getByRole("button", { name: "T1 Object" }));

    // T1 has its own object map, strata, saturation — not just a comparison card
    expect(screen.getByTestId("t1-object-map")).toBeInTheDocument();
    expect(screen.getByTestId("fixed-point-strata")).toBeInTheDocument();
    expect(screen.getByTestId("saturation-card")).toBeInTheDocument();
    expect(screen.getByTestId("p4-from-p5-events")).toBeInTheDocument();
    expect(screen.getByTestId("packaging-identity")).toBeInTheDocument();
  });

  it("loads shell witness when witness changes", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("t0-vs-t1-page")).toBeInTheDocument();
    });

    const shellT0 = { ...MOCK_T0, witness_id: "generated.continuous_full_loop_kernel_shell" };
    const shellT1 = { ...MOCK_T1, witness_id: "generated.continuous_full_loop_kernel_shell" };
    globalThis.fetch = vi.fn().mockImplementation((url: string) => {
      const data = url.includes("_t1.json") ? shellT1 : shellT0;
      return Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
    });
    useAppStore.getState().setWitnessId("generated.continuous_full_loop_kernel_shell");

    await waitFor(() => {
      expect(screen.getByText(/continuous_full_loop_kernel_shell/)).toBeInTheDocument();
    });
  });
});
