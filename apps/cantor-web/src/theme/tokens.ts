/** Shared design tokens for the cantor-web visual grammar. */

// --- Primitive colors (P1–P6) ---

export const primitiveColors = {
  P1: "#e05252", // rewrite
  P2: "#e89b3e", // gating
  P3: "#e8d44d", // timescale adaptation
  P4: "#4db882", // lens competition
  P5: "#4a90d9", // packaging competition
  P6: "#9b6fd4", // budget dynamics
} as const;

export const primitiveLabels: Record<keyof typeof primitiveColors, string> = {
  P1: "Rewrite",
  P2: "Gating",
  P3: "Timescale",
  P4: "Lens",
  P5: "Packaging",
  P6: "Budget",
};

// --- Theory layer colors ---

export const theoryColors = {
  T0: "#4a90d9", // base cocycle pressure theory
  T1: "#d97a4a", // hybrid cocycle + completion theory
} as const;

export const theoryLabels: Record<keyof typeof theoryColors, string> = {
  T0: "Base Theory (T0)",
  T1: "Extended Theory (T1)",
};

// --- Semantic colors ---

export const semanticColors = {
  closed: "#3ec97a",
  support: "#e8a73e",
  reserve: "#7a8ba8",
  nonclaim: "#c95454",
} as const;

// --- Neutral palette ---

export const neutralColors = {
  bg: "#0a0f1f",
  surface: "rgba(248, 245, 238, 0.08)",
  surfaceBorder: "rgba(248, 245, 238, 0.12)",
  text: "#f8f5ee",
  textMuted: "rgba(248, 245, 238, 0.6)",
  textSecondary: "rgba(248, 245, 238, 0.8)",
  border: "rgba(255, 255, 255, 0.12)",
  accent: "#f4b860",
} as const;

// --- Badge variant config ---

export type BadgeVariant = "closed" | "support" | "reserve" | "nonclaim";

export const badgeConfig: Record<
  BadgeVariant,
  { label: string; color: string; bg: string }
> = {
  closed: {
    label: "Closed",
    color: semanticColors.closed,
    bg: "rgba(62, 201, 122, 0.16)",
  },
  support: {
    label: "Support-only",
    color: semanticColors.support,
    bg: "rgba(232, 167, 62, 0.16)",
  },
  reserve: {
    label: "Reserve",
    color: semanticColors.reserve,
    bg: "rgba(122, 139, 168, 0.16)",
  },
  nonclaim: {
    label: "Non-claim",
    color: semanticColors.nonclaim,
    bg: "rgba(201, 84, 84, 0.16)",
  },
};

// --- Icon names ---

export type IconName =
  | "saturation"
  | "forcing"
  | "nonfactorization"
  | "macro_obstruction";

export const iconLabels: Record<IconName, string> = {
  saturation: "Saturation",
  forcing: "Forcing",
  nonfactorization: "Non-factorization",
  macro_obstruction: "Macro-admissibility obstruction",
};
