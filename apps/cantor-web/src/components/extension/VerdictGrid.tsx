import type { ExtensionVerdicts } from "../../data/types";
import Icon from "../ui/Icon";

interface VerdictGridProps {
  verdicts: ExtensionVerdicts;
}

const VERDICT_CONFIG: {
  key: keyof ExtensionVerdicts;
  label: string;
  icon: "saturation" | "forcing" | "nonfactorization" | "macro_obstruction";
}[] = [
  { key: "factorization", label: "Non-factorization", icon: "nonfactorization" },
  { key: "saturation", label: "Saturation", icon: "saturation" },
  { key: "forcing", label: "Forcing (P4←P5)", icon: "forcing" },
  { key: "macro_admissibility", label: "Macro-admissibility", icon: "macro_obstruction" },
];

export default function VerdictGrid({ verdicts }: VerdictGridProps) {
  return (
    <div className="verdict-grid" data-testid="verdict-grid">
      <h3>Extension Verdicts</h3>
      <div className="verdict-grid__cards">
        {VERDICT_CONFIG.map((v) => (
          <div key={v.key} className="verdict-grid__card">
            <div className="verdict-grid__card-header">
              <Icon name={v.icon} size={20} />
              <span className="verdict-grid__card-label">{v.label}</span>
            </div>
            <span className="verdict-grid__card-value">
              {verdicts[v.key].replace(/_/g, " ")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
