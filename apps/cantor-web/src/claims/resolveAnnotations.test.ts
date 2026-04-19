import {
  classifyClaim,
  resolveClaim,
  isAllowedOnPanel,
  filterAllowedClaims,
  getCoreClaimsOnly,
} from "./resolveAnnotations";
import type { AnnotationPolicy } from "../data/types";

const MOCK_POLICY: AnnotationPolicy = {
  schema_version: "v1",
  paper_core_positioning: "level3_core_on_audited_shell",
  core_claim_ids: [
    "continuous_full_loop_lawfulness_theoremlet",
    "cocycle_pressure_closure_theoremlet",
    "strict_theory_extension_theoremlet",
    "conditional_pressure_disintegration_theoremlet",
  ],
  support_only_claim_ids: ["closure_deficit_proxy_support"],
  reserve_claim_ids: ["packaging-completion_broader-class_ambitions"],
  nonclaim_ids: ["no_broader-class_theorem_beyond_the_audited_shell"],
  scope_guards: ["audited shell only", "no broader-class theorem"],
  per_theoremlet_bindings: [
    {
      theoremlet_id: "strict_theory_extension_theoremlet",
      allowed_claim_ids: ["strict_theory_extension_theoremlet"],
      forbidden_claim_ids: ["no_broader-class_theorem_beyond_the_audited_shell"],
    },
  ],
  claim_classifications: {
    continuous_full_loop_lawfulness_theoremlet: {
      status: "closed_theoremlet",
      allowed_final_paper_use: "core_claim",
      claim_type: "lawfulness",
    },
    closure_deficit_proxy_support: {
      status: "supporting_evidence",
      allowed_final_paper_use: "support_only",
      claim_type: "thermodynamic_consequence",
    },
    "packaging-completion_broader-class_ambitions": {
      status: "reserve",
      allowed_final_paper_use: "reserve_only",
      claim_type: "future_work",
    },
    no_broader_class_theorem_beyond_the_audited_shell: {
      status: "nonclaim",
      allowed_final_paper_use: "nonclaim_only",
      claim_type: "broader_class",
    },
  },
  phrases_to_avoid: ["broader-class theorem"],
};

describe("classifyClaim", () => {
  it("classifies core claims", () => {
    expect(classifyClaim("strict_theory_extension_theoremlet", MOCK_POLICY)).toBe("core");
  });

  it("classifies support-only claims", () => {
    expect(classifyClaim("closure_deficit_proxy_support", MOCK_POLICY)).toBe("support");
  });

  it("classifies reserve claims", () => {
    expect(classifyClaim("packaging-completion_broader-class_ambitions", MOCK_POLICY)).toBe("reserve");
  });

  it("classifies non-claims", () => {
    expect(classifyClaim("no_broader-class_theorem_beyond_the_audited_shell", MOCK_POLICY)).toBe("nonclaim");
  });

  it("returns unknown for unrecognized IDs", () => {
    expect(classifyClaim("nonexistent_claim", MOCK_POLICY)).toBe("unknown");
  });
});

describe("resolveClaim", () => {
  it("resolves a core claim", () => {
    const r = resolveClaim("strict_theory_extension_theoremlet", MOCK_POLICY);
    expect(r.category).toBe("core");
    expect(r.allowed).toBe(true);
  });

  it("marks support claims as allowed", () => {
    const r = resolveClaim("closure_deficit_proxy_support", MOCK_POLICY);
    expect(r.category).toBe("support");
    expect(r.allowed).toBe(true);
  });

  it("marks reserve claims as not allowed", () => {
    const r = resolveClaim("packaging-completion_broader-class_ambitions", MOCK_POLICY);
    expect(r.category).toBe("reserve");
    expect(r.allowed).toBe(false);
  });

  it("marks non-claims as not allowed", () => {
    const r = resolveClaim("no_broader-class_theorem_beyond_the_audited_shell", MOCK_POLICY);
    expect(r.category).toBe("nonclaim");
    expect(r.allowed).toBe(false);
  });
});

describe("isAllowedOnPanel", () => {
  it("allows claim on its own panel", () => {
    expect(
      isAllowedOnPanel(
        "strict_theory_extension_theoremlet",
        "strict_theory_extension_theoremlet",
        MOCK_POLICY,
      ),
    ).toBe(true);
  });

  it("forbids non-claim on panel", () => {
    expect(
      isAllowedOnPanel(
        "no_broader-class_theorem_beyond_the_audited_shell",
        "strict_theory_extension_theoremlet",
        MOCK_POLICY,
      ),
    ).toBe(false);
  });
});

describe("filterAllowedClaims", () => {
  it("filters out unknown IDs", () => {
    const result = filterAllowedClaims(
      ["strict_theory_extension_theoremlet", "nonexistent"],
      MOCK_POLICY,
    );
    expect(result).toHaveLength(1);
  });
});

describe("getCoreClaimsOnly", () => {
  it("returns only core claims", () => {
    const core = getCoreClaimsOnly(MOCK_POLICY);
    expect(core.length).toBe(4);
    for (const c of core) {
      expect(c.category).toBe("core");
    }
  });
});
