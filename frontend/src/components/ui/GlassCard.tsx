import { motion, type HTMLMotionProps } from "framer-motion";
import { clsx } from "clsx";
import type { ReactNode } from "react";

const spring = { type: "spring" as const, stiffness: 350, damping: 25 };

interface GlassCardProps extends HTMLMotionProps<"div"> {
  children: ReactNode;
  className?: string;
  glow?: boolean;
}

export function GlassCard({ children, className, glow, ...props }: GlassCardProps) {
  return (
    <motion.div
      className={clsx(
        "glass rounded-2xl p-6 shadow-2xl",
        glow && "animate-border-glow",
        className
      )}
      whileHover={{ scale: 1.008, borderColor: "rgba(0, 242, 254, 0.22)" }}
      transition={spring}
      {...props}
    >
      {children}
    </motion.div>
  );
}
