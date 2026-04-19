import Badge from "../ui/Badge";
import type { RejectedRoute } from "../../data/types";

interface RejectedRouteNoticeProps {
  routes: {
    direct_stratumwise_separation: RejectedRoute;
    exact_kl_closure_deficit: RejectedRoute;
  };
}

export default function RejectedRouteNotice({ routes }: RejectedRouteNoticeProps) {
  return (
    <div className="rejected-routes" data-testid="rejected-routes">
      <h3>Rejected / Support-Only Routes</h3>
      <div className="rejected-routes__grid">
        <div className="rejected-routes__item">
          <div className="rejected-routes__header">
            <Badge variant="nonclaim" label="rejected" />
            <span className="rejected-routes__name">Direct stratumwise root separation</span>
          </div>
          <p className="rejected-routes__reason">{routes.direct_stratumwise_separation.reason}</p>
        </div>
        <div className="rejected-routes__item">
          <div className="rejected-routes__header">
            <Badge variant="support" label="support only" />
            <span className="rejected-routes__name">Exact KL closure-deficit</span>
          </div>
          <p className="rejected-routes__reason">{routes.exact_kl_closure_deficit.reason}</p>
        </div>
      </div>
    </div>
  );
}
