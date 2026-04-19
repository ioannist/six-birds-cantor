import type { T1PackagingIdentityChange } from "../../data/types";

interface PackagingIdentityPanelProps {
  changes: T1PackagingIdentityChange[];
}

export default function PackagingIdentityPanel({ changes }: PackagingIdentityPanelProps) {
  return (
    <div className="t1-panel" data-testid="packaging-identity">
      <h3>Packaging Identity Changes</h3>
      <p className="t1-panel__detail-label">
        {changes.length} distinct packaging configurations across tau/lens combinations.
      </p>
      <table className="t1-panel__table">
        <thead>
          <tr>
            <th>Tau</th>
            <th>Lens</th>
            <th>Packaging</th>
            <th>Score</th>
            <th>Groups</th>
          </tr>
        </thead>
        <tbody>
          {changes.map((c, i) => (
            <tr key={i}>
              <td>{c.tau}</td>
              <td>{c.lens_state.replace(/_/g, " ")}</td>
              <td>{c.packaging_name.replace(/_/g, " ")}</td>
              <td>{c.packaging_score.toFixed(4)}</td>
              <td>{c.group_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
