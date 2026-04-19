import Badge from "../ui/Badge";
import type { T0Theoremlet } from "../../data/types";

interface T0ClassMapProps {
  coreClassId: string;
  shellStable: boolean;
  theoremlets: T0Theoremlet[];
}

export default function T0ClassMap({
  coreClassId,
  shellStable,
  theoremlets,
}: T0ClassMapProps) {
  return (
    <div className="t0-class-map" data-testid="t0-class-map">
      <h3>T0 Object Classes</h3>
      <div className="t0-class-map__class">
        <div className="t0-class-map__header">
          <code className="t0-class-map__id">{coreClassId}</code>
          {shellStable && (
            <span className="t0-class-map__shell-marker" data-testid="shell-stable-marker">
              shell-stable
            </span>
          )}
        </div>
        <ul className="t0-class-map__theoremlets">
          {theoremlets.map((t) => (
            <li key={t.theoremlet_id}>
              <Badge variant="closed" label={t.theoremlet_id.replace(/_/g, " ")} />
              <span className="t0-class-map__status">{t.status.replace(/_/g, " ")}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
