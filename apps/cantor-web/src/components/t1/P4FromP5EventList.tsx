import type { T1P4FromP5Event } from "../../data/types";
import Icon from "../ui/Icon";

interface P4FromP5EventListProps {
  events: T1P4FromP5Event[];
}

export default function P4FromP5EventList({ events }: P4FromP5EventListProps) {
  return (
    <div className="t1-panel" data-testid="p4-from-p5-events">
      <h3>
        <span style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem" }}>
          <Icon name="forcing" size={18} /> P4&#8592;P5 Lens Feedback Events
        </span>
      </h3>
      {events.length === 0 ? (
        <p className="t1-panel__detail-label">No P4&#8592;P5 events detected.</p>
      ) : (
        <>
          <p className="t1-panel__detail-label">
            {events.length} lens transitions triggered by packaging completion status.
          </p>
          <table className="t1-panel__table">
            <thead>
              <tr>
                <th>Tau</th>
                <th>From</th>
                <th>To</th>
                <th>Trigger</th>
                <th>Packages</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e, i) => (
                <tr key={i}>
                  <td>{e.tau}</td>
                  <td>{e.from_lens.replace(/_/g, " ")}</td>
                  <td>{e.to_lens.replace(/_/g, " ")}</td>
                  <td>{e.trigger_status.replace(/_/g, " ")}</td>
                  <td>{e.package_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
