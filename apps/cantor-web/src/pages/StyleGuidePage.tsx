import {
  primitiveColors,
  primitiveLabels,
  theoryColors,
  theoryLabels,
  iconLabels,
} from "../theme/tokens";
import type { BadgeVariant, IconName } from "../theme/tokens";
import Badge from "../components/ui/Badge";
import Icon from "../components/ui/Icon";

const badgeVariants: BadgeVariant[] = ["closed", "support", "reserve", "nonclaim"];
const iconNames: IconName[] = ["saturation", "forcing", "nonfactorization", "macro_obstruction"];

function Swatch({ color, label }: { color: string; label: string }) {
  return (
    <span className="swatch">
      <span className="swatch__dot" style={{ background: color }} data-testid="swatch" />
      <span className="swatch__label">{label}</span>
    </span>
  );
}

export default function StyleGuidePage() {
  return (
    <div className="style-guide" data-testid="style-guide">
      {/* Primitive colors */}
      <section className="style-guide__section">
        <h2>Primitive Colors (P1–P6)</h2>
        <div className="style-guide__row">
          {(Object.keys(primitiveColors) as (keyof typeof primitiveColors)[]).map((key) => (
            <Swatch key={key} color={primitiveColors[key]} label={`${key} — ${primitiveLabels[key]}`} />
          ))}
        </div>
      </section>

      {/* Theory layers */}
      <section className="style-guide__section">
        <h2>Theory Layers</h2>
        <div className="style-guide__row">
          {(Object.keys(theoryColors) as (keyof typeof theoryColors)[]).map((key) => (
            <Swatch key={key} color={theoryColors[key]} label={theoryLabels[key]} />
          ))}
        </div>
      </section>

      {/* Badges */}
      <section className="style-guide__section">
        <h2>Badges</h2>
        <div className="style-guide__row">
          {badgeVariants.map((v) => (
            <Badge key={v} variant={v} />
          ))}
        </div>
      </section>

      {/* Icons */}
      <section className="style-guide__section">
        <h2>Icons</h2>
        <div className="style-guide__row">
          {iconNames.map((name) => (
            <span className="icon-row" key={name}>
              <Icon name={name} />
              <span>{iconLabels[name]}</span>
            </span>
          ))}
        </div>
      </section>

      {/* Example cards */}
      <section className="style-guide__section">
        <h2>Example Cards</h2>
        <div className="style-guide__row">
          <article className="style-guide__card">
            <h3>
              Lawfulness Theoremlet <Badge variant="closed" />
            </h3>
            <p>
              Closed six-primitive lawfulness regime on the shell-stable audited package.
            </p>
            <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.75rem" }}>
              <span className="icon-row"><Icon name="saturation" size={18} /> Saturated</span>
              <span className="icon-row"><Icon name="forcing" size={18} /> Forced</span>
            </div>
          </article>
          <article className="style-guide__card">
            <h3>
              Broader-class Ambition <Badge variant="reserve" />
            </h3>
            <p>
              Reserve route — not included in the paper-core package.
            </p>
            <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.75rem" }}>
              <span className="icon-row"><Icon name="macro_obstruction" size={18} /> Obstructed</span>
            </div>
          </article>
        </div>
      </section>
    </div>
  );
}
