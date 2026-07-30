import type { CSSProperties, ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  radius?: number;
  padding?: string;
  style?: CSSProperties;
}

export function Card({
  children,
  className = "",
  radius = 18,
  padding = "20px",
  style,
}: CardProps) {
  return (
    <div
      className={`bg-surface ${className}`}
      style={{ borderRadius: radius, padding, ...style }}
    >
      {children}
    </div>
  );
}
