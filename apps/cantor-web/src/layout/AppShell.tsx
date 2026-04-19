import { NavLink, Outlet } from "react-router-dom";
import { useAppStore } from "../app/store";
import type { TheoremLayer } from "../app/store";

const NAV_ITEMS = [
  { to: "/", label: "Overview" },
  { to: "/live-substrate", label: "Live substrate" },
  { to: "/t0-vs-t1", label: "T0 vs T1" },
  { to: "/extension-certificate", label: "Extension certificate" },
  { to: "/thermodynamic-consequence", label: "Thermodynamic consequence" },
  { to: "/primitive-knockouts", label: "Primitive knockouts" },
  { to: "/claim-scope", label: "Claim scope" },
] as const;

const THEOREM_LAYERS: TheoremLayer[] = ["T0", "T1", "hybrid"];

const WITNESS_OPTIONS = [
  "generated.continuous_full_loop_kernel",
  "generated.continuous_full_loop_kernel_shell",
];

const SHELL_OPTIONS = ["audited_shell"];

export default function AppShell() {
  const store = useAppStore();

  return (
    <div className="shell">
      <header className="shell__header">
        <span className="shell__title">Six Birds Cantor</span>
        <NavLink to="/style-guide" className="shell__dev-link">
          Style guide
        </NavLink>
      </header>

      <nav className="shell__nav" aria-label="main navigation">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `shell__nav-item${isActive ? " shell__nav-item--active" : ""}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="shell__body">
        <aside className="shell__controls" aria-label="shared controls">
          <fieldset className="control-group">
            <legend>Theorem layer</legend>
            <div className="control-group__options">
              {THEOREM_LAYERS.map((layer) => (
                <label key={layer} className="control-radio">
                  <input
                    type="radio"
                    name="theoremLayer"
                    value={layer}
                    checked={store.selectedTheoremLayer === layer}
                    onChange={() => store.setTheoremLayer(layer)}
                  />
                  {layer}
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset className="control-group">
            <legend>Witness</legend>
            <select
              value={store.selectedWitnessId}
              onChange={(e) => store.setWitnessId(e.target.value)}
              aria-label="witness"
            >
              {WITNESS_OPTIONS.map((w) => (
                <option key={w} value={w}>
                  {w.replace("generated.", "")}
                </option>
              ))}
            </select>
          </fieldset>

          <fieldset className="control-group">
            <legend>Shell</legend>
            <select
              value={store.selectedShell}
              onChange={(e) => store.setShell(e.target.value)}
              aria-label="shell"
            >
              {SHELL_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </fieldset>

          <fieldset className="control-group">
            <legend>Time index</legend>
            <input
              type="number"
              min={0}
              value={store.selectedTimeIndex}
              onChange={(e) => store.setTimeIndex(Number(e.target.value))}
              aria-label="time index"
            />
          </fieldset>
        </aside>

        <main className="shell__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
