/**
 * BlueprintGrid — animated fine-line grid background.
 * Barely perceptible (2-4% opacity). "Corpus breathing" pulse points idle ambiently.
 * On query submit, pulse point fires a visible wave.
 */
export function BlueprintGrid({ active }: { active?: boolean }) {
  return (
    <>
      {/* CSS grid via index.css .blueprint-grid */}
      <div className="blueprint-grid" aria-hidden />

      {/* Corpus breathing pulse points — idle state */}
      {[
        { top: "18%", left: "22%", delay: "0s" },
        { top: "55%", left: "67%", delay: "1.4s" },
        { top: "32%", left: "78%", delay: "2.8s" },
        { top: "72%", left: "35%", delay: "0.7s" },
      ].map((p, i) => (
        <div
          key={i}
          className={`corpus-pulse ${active ? "corpus-pulse--active" : ""}`}
          style={{ top: p.top, left: p.left, animationDelay: p.delay }}
          aria-hidden
        />
      ))}
    </>
  );
}
