import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "outline";
}

export function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonProps) {
  const variantClass =
    variant === "primary"
      ? "bg-primary text-white active:bg-primary-active"
      : "bg-surface text-text-secondary border border-border";

  return (
    <button
      type="button"
      className={`h-[54px] w-full rounded-[14px] text-[16.5px] font-bold tracking-[-0.02em] disabled:opacity-40 ${variantClass} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
