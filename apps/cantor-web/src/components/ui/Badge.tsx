import type { BadgeVariant } from "../../theme/tokens";
import { badgeConfig } from "../../theme/tokens";

interface BadgeProps {
  variant: BadgeVariant;
  label?: string;
}

export default function Badge({ variant, label }: BadgeProps) {
  const config = badgeConfig[variant];
  return (
    <span className={`badge badge--${variant}`} data-variant={variant}>
      {label ?? config.label}
    </span>
  );
}
