import { motion } from "framer-motion";
import { clsx } from "clsx";
import type { ReactNode, ComponentPropsWithoutRef } from "react";

type GlowButtonProps = Omit<ComponentPropsWithoutRef<"button">, "onDrag" | "onDragEnd" | "onDragStart" | "onAnimationStart"> & {
  children: ReactNode;
  variant?: "primary" | "ghost";
  loading?: boolean;
  className?: string;
};

export function GlowButton({ children, variant = "primary", loading, className, ...props }: GlowButtonProps) {
  return (
    <motion.button
      className={clsx(
        "relative inline-flex items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold transition-all duration-200 cursor-pointer",
        variant === "primary" && [
          "bg-gradient-to-r from-cyan-500 via-violet-500 to-pink-500 text-white",
          "shadow-[0_4px_20px_rgba(0,242,254,0.25)]",
          "hover:shadow-[0_6px_30px_rgba(0,242,254,0.4)]",
        ],
        variant === "ghost" && [
          "bg-white/[0.04] text-gray-300 border border-white/[0.08]",
          "hover:bg-white/[0.08] hover:border-white/[0.15]",
        ],
        loading && "opacity-70 pointer-events-none",
        className
      )}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && (
        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin-glow" />
      )}
      {children}
    </motion.button>
  );
}
