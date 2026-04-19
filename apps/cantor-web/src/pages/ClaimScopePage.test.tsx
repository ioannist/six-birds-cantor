import { render, screen, waitFor } from "@testing-library/react";
import ClaimScopePage from "./ClaimScopePage";
import type { AnnotationPolicy } from "../data/types";

const MOCK_POLICY: AnnotationPolicy = {
  schema_version: "v1",
  paper_core_positioning: "level3_core_on_audited_shell",
  core_claim_ids: ["continuous_full_loop_lawfulness_theoremlet", "cocycle_pressure_closure_theoremlet"],
  support_only_claim_ids: ["closure_deficit_proxy_support"],
  reserve_claim_ids: ["packaging-completion_broader-class_ambitions"],
  nonclaim_ids: ["no_broader-class_theorem_beyond_the_audited_shell"],
  scope_guards: ["audited shell only", "no broader-class theorem"],
  per_theoremlet_bindings: [],
  claim_classifications: {},
  phrases_to_avoid: ["broader-class theorem", "shell-general result"],
};

beforeEach(() => {
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(MOCK_POLICY),
  });
});

describe("ClaimScopePage", () => {
  it("renders the page", async () => {
    render(<ClaimScopePage />);
    await waitFor(() => {
      expect(screen.getByTestId("claim-scope-page")).toBeInTheDocument();
    });
  });

  it("shows scope guard banner", async () => {
    render(<ClaimScopePage />);
    await waitFor(() => {
      expect(screen.getByTestId("scope-guard-banner")).toBeInTheDocument();
    });
  });

  it("shows core claims as core badges", async () => {
    render(<ClaimScopePage />);
    await waitFor(() => {
      const coreBadges = screen.getAllByTestId("claim-badge-core");
      expect(coreBadges.length).toBe(2);
    });
  });

  it("shows support-only claims with support badge", async () => {
    render(<ClaimScopePage />);
    await waitFor(() => {
      expect(screen.getByTestId("support-claims")).toBeInTheDocument();
    });
  });

  it("shows reserve claims with reserve badge", async () => {
    render(<ClaimScopePage />);
    await waitFor(() => {
      expect(screen.getByTestId("reserve-claims")).toBeInTheDocument();
    });
  });

  it("shows non-claims visually suppressed", async () => {
    render(<ClaimScopePage />);
    await waitFor(() => {
      expect(screen.getByTestId("nonclaim-items")).toBeInTheDocument();
    });
  });

  it("nonclaim badge has nonclaim category", async () => {
    render(<ClaimScopePage />);
    await waitFor(() => {
      const nonclaimBadge = screen.getByTestId("claim-badge-nonclaim");
      expect(nonclaimBadge).toBeInTheDocument();
    });
  });

  it("shows phrases to avoid", async () => {
    render(<ClaimScopePage />);
    await waitFor(() => {
      expect(screen.getByText("broader-class theorem")).toBeInTheDocument();
    });
  });
});
