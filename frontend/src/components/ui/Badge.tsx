import type { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  variant?: "cobalt" | "orange" | "muted" | "weak" | "green" | "cyan" | "violet" | "amber" | "pink";
}

/**
 * Badge — Marginalia style.
 * Sharp corners, 1px hairline border, monospace uppercase text.
 * No pill shapes, no rounded corners.
 */
export function Badge({ children, variant = "muted" }: BadgeProps) {
  const styles: Record<string, string> = {
    cobalt: "color: var(--cobalt); border-color: var(--cobalt-dim);",
    cyan: "color: var(--cobalt); border-color: var(--cobalt-dim);",
    violet: "color: var(--cobalt); border-color: var(--cobalt-dim);",
    green: "color: var(--cobalt); border-color: var(--cobalt-dim);",
    orange: "color: var(--orange); border-color: var(--orange-dim);",
    amber: "color: var(--orange); border-color: var(--orange-dim);",
    pink: "color: var(--orange); border-color: var(--orange-dim);",
    muted: "color: var(--ink-muted); border-color: var(--border);",
    weak: "color: var(--weak-match); border-color: var(--border-muted);",
  };

  return (
    <span
      className="mono-label"
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "1px 5px",
        border: "1px solid",
        borderRadius: "1px",
        fontSize: "0.58rem",
        ...Object.fromEntries(
          styles[variant].split(";").filter(Boolean).map((s) => {
            const [k, v] = s.split(":").map((x) => x.trim());
            return [k.replace(/-([a-z])/g, (_, c: string) => c.toUpperCase()), v];
          })
        ),
      }}
    >
      {children}
    </span>
  );
}
