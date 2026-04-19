import { loadIndex, loadTheoremPackage, loadDataset } from "./loadData";
import type { DataIndex, TheoremPackage } from "./types";

// Mock fetch with sample data
const MOCK_INDEX: DataIndex = {
  schema_version: "v1",
  generated_at_utc: "2026-03-19T00:00:00Z",
  datasets: [
    { name: "theorem-package", path: "theorem-package.json" },
    { name: "claim-ledger", path: "claim-ledger.json" },
    { name: "traceability", path: "traceability.json" },
    { name: "figure-manifest", path: "figure-manifest.json" },
    { name: "witnesses", path: "witnesses.json" },
  ],
};

const MOCK_THEOREM_PACKAGE: TheoremPackage = {
  schema_version: "v1",
  package_id: "level3_theorem_package_v1",
  paper_core_positioning: "level3_core_on_audited_shell",
  canonical_object_id: "canonical_hybrid_theorem_object_v1",
  core_class_id: "continuous_full_loop_lawful_kernel_class_shell_stable",
  selected_routes: { lawfulness_route: "deterministic_skew_product_with_budget_feedback" },
  included_theoremlets: [
    {
      theoremlet_id: "continuous_full_loop_lawfulness_theoremlet",
      status: "closed_in_note",
      class_scope: "continuous_full_loop_lawful_kernel_class_shell_stable",
      note: "Test theoremlet.",
    },
  ],
  nonclaims: [],
  reserve_routes: [],
  canonical_hybrid_object: {
    object_id: "canonical_hybrid_theorem_object_v1",
    base_theory_id: "T0_cocycle_pressure_theory",
    extended_theory_id: "T1_hybrid_cocycle_plus_completion_theory",
    decision: "canonical_object_and_intrinsic_extension_closed",
    object_identity_verdict: "t1_objects_finer_than_t0_objects",
    factorization_verdict: "non_factorization_closed_on_audited_shell",
  },
  claim_posture: {
    core_positioning: "level3_core_on_audited_shell",
    core_claim_ids: ["continuous_full_loop_lawfulness_theoremlet"],
    support_only_claim_ids: [],
    reserve_claim_ids: [],
    nonclaim_ids: [],
    manuscript_posture: "test",
    phrases_to_avoid: [],
  },
};

function mockFetch(data: unknown) {
  return vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(data),
  });
}

describe("loadIndex", () => {
  it("parses the index manifest", async () => {
    globalThis.fetch = mockFetch(MOCK_INDEX);
    const index = await loadIndex();
    expect(index.schema_version).toBe("v1");
    expect(index.datasets).toHaveLength(5);
    expect(index.datasets[0].name).toBe("theorem-package");
  });
});

describe("loadTheoremPackage", () => {
  it("parses the theorem package", async () => {
    globalThis.fetch = mockFetch(MOCK_THEOREM_PACKAGE);
    const pkg = await loadTheoremPackage();
    expect(pkg.package_id).toBe("level3_theorem_package_v1");
    expect(pkg.included_theoremlets).toHaveLength(1);
  });
});

describe("loadDataset", () => {
  it("loads a named dataset", async () => {
    globalThis.fetch = mockFetch(MOCK_THEOREM_PACKAGE);
    const data = await loadDataset("theorem-package");
    expect(data).toBeDefined();
  });

  it("rejects unknown dataset names", async () => {
    await expect(
      loadDataset("nonexistent" as never),
    ).rejects.toThrow("Unknown dataset");
  });
});

describe("fetch error handling", () => {
  it("throws on non-ok response", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
    });
    await expect(loadIndex()).rejects.toThrow("Failed to load");
  });
});
