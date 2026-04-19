import { createHashRouter } from "react-router-dom";
import AppShell from "../layout/AppShell";
import OverviewPage from "../pages/OverviewPage";
import LiveSubstratePage from "../pages/LiveSubstratePage";
import T0VsT1Page from "../pages/T0VsT1Page";
import ExtensionCertificatePage from "../pages/ExtensionCertificatePage";
import ThermodynamicConsequencePage from "../pages/ThermodynamicConsequencePage";
import PrimitiveKnockoutsPage from "../pages/PrimitiveKnockoutsPage";
import ClaimScopePage from "../pages/ClaimScopePage";
import StyleGuidePage from "../pages/StyleGuidePage";

export const router = createHashRouter([
  {
    element: <AppShell />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: "live-substrate", element: <LiveSubstratePage /> },
      { path: "t0-vs-t1", element: <T0VsT1Page /> },
      { path: "extension-certificate", element: <ExtensionCertificatePage /> },
      { path: "thermodynamic-consequence", element: <ThermodynamicConsequencePage /> },
      { path: "primitive-knockouts", element: <PrimitiveKnockoutsPage /> },
      { path: "claim-scope", element: <ClaimScopePage /> },
      { path: "style-guide", element: <StyleGuidePage /> },
    ],
  },
]);
