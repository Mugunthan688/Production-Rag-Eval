export function Shimmer({ className = "" }: { className?: string }) {
  return (
    <div className={`relative overflow-hidden rounded-xl bg-white/[0.03] ${className}`}>
      <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/[0.04] to-transparent" />
    </div>
  );
}

export function ShimmerBlock() {
  return (
    <div className="space-y-3 p-6">
      <Shimmer className="h-4 w-3/4" />
      <Shimmer className="h-4 w-full" />
      <Shimmer className="h-4 w-5/6" />
      <Shimmer className="h-4 w-2/3" />
    </div>
  );
}
