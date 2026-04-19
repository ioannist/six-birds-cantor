import type { IconName } from "../../theme/tokens";
import { semanticColors } from "../../theme/tokens";

interface IconProps {
  name: IconName;
  size?: number;
}

const color = semanticColors.closed;

function SaturationIcon({ size }: { size: number }) {
  return (
    <svg className="icon-svg" width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke={color} strokeWidth="1.5" />
      <path d="M12 3v18" stroke={color} strokeWidth="1.5" />
      <path d="M12 12h9" stroke={color} strokeWidth="1.5" strokeDasharray="2 2" />
      <circle cx="12" cy="12" r="2.5" fill={color} opacity="0.6" />
    </svg>
  );
}

function ForcingIcon({ size }: { size: number }) {
  const c = semanticColors.support;
  return (
    <svg className="icon-svg" width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M6 18L18 6" stroke={c} strokeWidth="2" strokeLinecap="round" />
      <path d="M13 6h5v5" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M6 12v6h6" stroke={c} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.5" />
    </svg>
  );
}

function NonfactorizationIcon({ size }: { size: number }) {
  const c = semanticColors.nonclaim;
  return (
    <svg className="icon-svg" width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="3" width="18" height="18" rx="3" stroke={c} strokeWidth="1.5" />
      <path d="M5 5l14 14" stroke={c} strokeWidth="2" strokeLinecap="round" />
      <path d="M9 3v18M3 9h18" stroke={c} strokeWidth="1" opacity="0.35" />
    </svg>
  );
}

function MacroObstructionIcon({ size }: { size: number }) {
  const c = semanticColors.reserve;
  return (
    <svg className="icon-svg" width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke={c} strokeWidth="1.5" />
      <path d="M8 12h8" stroke={c} strokeWidth="2" strokeLinecap="round" />
      <path d="M12 8v8" stroke={c} strokeWidth="2" strokeLinecap="round" opacity="0.4" />
      <circle cx="12" cy="12" r="3" stroke={c} strokeWidth="1" strokeDasharray="2 1.5" />
    </svg>
  );
}

const iconMap: Record<IconName, (props: { size: number }) => JSX.Element> = {
  saturation: SaturationIcon,
  forcing: ForcingIcon,
  nonfactorization: NonfactorizationIcon,
  macro_obstruction: MacroObstructionIcon,
};

export default function Icon({ name, size = 24 }: IconProps) {
  const Component = iconMap[name];
  return <Component size={size} />;
}
