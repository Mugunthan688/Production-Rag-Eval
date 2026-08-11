import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { HistoryEntry } from "../../api/client";

interface HistoryRailProps {
  history: HistoryEntry[];
  activeId: string | null;
  onSelect: (entry: HistoryEntry) => void;
}

/**
 * HistoryRail — left column (200px, collapsible).
 * Past queries rendered as annotated notebook tabs with tick-mark icons.
 * Monospace timestamps, truncated query previews.
 */
export function HistoryRail({ history, activeId, onSelect }: HistoryRailProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <motion.aside
      id="history-rail"
      animate={{ width: collapsed ? 40 : 200 }}
      transition={{ type: "spring", stiffness: 320, damping: 30 }}
      style={{
        height: "100vh",
        borderRight: "1px solid var(--border)",
        backgroundColor: "var(--canvas)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        flexShrink: 0,
        position: "relative",
        zIndex: 20,
      }}
    >
      {/* Rail header + collapse toggle */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: collapsed ? "center" : "space-between",
        padding: "14px 10px",
        borderBottom: "1px solid var(--border)",
        minHeight: "48px",
        flexShrink: 0,
      }}>
        {!collapsed && (
          <span className="mono-label" style={{ fontSize: "0.58rem", letterSpacing: "0.14em", whiteSpace: "nowrap" }}>
            History
          </span>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? "Expand history" : "Collapse history"}
          style={{
            background: "none",
            border: "1px solid var(--border)",
            borderRadius: "2px",
            color: "var(--ink-muted)",
            cursor: "pointer",
            padding: "3px",
            display: "flex",
            alignItems: "center",
            transition: "border-color 120ms ease, color 120ms ease",
          }}
        >
          {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
        </button>
      </div>

      {/* History tabs — only shown when expanded */}
      <AnimatePresence>
        {!collapsed && (
          <motion.nav
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            style={{
              flex: 1,
              overflowY: "auto",
              overflowX: "hidden",
              padding: "8px 6px",
            }}
          >
            {history.length === 0 ? (
              <p className="mono-label" style={{ padding: "10px 6px", fontSize: "0.58rem", lineHeight: 1.5, opacity: 0.6 }}>
                Past queries will appear here.
              </p>
            ) : (
              [...history].reverse().map((entry) => {
                const isActive = entry.id === activeId;
                const timeStr = new Date(entry.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                });

                return (
                  <button
                    key={entry.id}
                    className={`history-tab ${isActive ? "history-tab--active" : ""}`}
                    onClick={() => onSelect(entry)}
                    style={{ width: "100%", textAlign: "left", background: "none", border: "1px solid transparent", cursor: "pointer" }}
                    aria-label={`View query: ${entry.query}`}
                    aria-pressed={isActive}
                  >
                    {/* Tick mark — notebook annotation aesthetic */}
                    <span className="history-tab__tick" aria-hidden>✓</span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p className="history-tab__text">{entry.query}</p>
                      <p className="mono-label" style={{ fontSize: "0.55rem", marginTop: "3px" }}>{timeStr}</p>
                    </div>
                  </button>
                );
              })
            )}
          </motion.nav>
        )}
      </AnimatePresence>

      {/* Footer: Marginalia wordmark — only when expanded */}
      {!collapsed && (
        <div style={{
          padding: "10px 12px",
          borderTop: "1px solid var(--border)",
          flexShrink: 0,
        }}>
          <p className="mono-label" style={{ fontSize: "0.55rem", letterSpacing: "0.1em" }}>
            MARGINALIA v1.0
          </p>
        </div>
      )}
    </motion.aside>
  );
}
