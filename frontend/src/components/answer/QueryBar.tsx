import { useState, useRef, useEffect, type KeyboardEvent } from "react";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { StatusLine } from "./StatusLine";

interface QueryBarProps {
  onSubmit: (query: string) => void;
  loading: boolean;
  centered?: boolean; // true in empty state, anchored bottom otherwise
}

const EXAMPLE_QUESTIONS = [
  "How does GraphRAG improve retrieval over flat vector search?",
  "What is Self-RAG and how does it reduce hallucination?",
  "How does Corrective RAG detect and fix retrieval errors?",
  "What role do knowledge graphs play in RAG systems?",
  "How does agentic RAG differ from standard RAG architectures?",
  "Explain multi-hop reasoning in retrieval-augmented systems.",
  "What are the key differences between sparse and dense retrieval?",
  "How do re-rankers improve RAG precision?",
  "What is FLARE and when should it be used?",
];

const TYPEWRITER_CHAR_MS = 42;
const TYPEWRITER_HOLD_MS = 1600;
const TYPEWRITER_ERASE_MS = 18;

/**
 * QueryBar — sharp-edged input with:
 * - Orange focus underline (not a rounded glow ring)
 * - Typewriter placeholder cycling example questions
 * - StatusLine progress during retrieval
 * - Submit button: sharp, typographic, no fill-color change on hover
 */
export function QueryBar({ onSubmit, loading, centered = false }: QueryBarProps) {
  const [input, setInput] = useState("");
  const [placeholder, setPlaceholder] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const phaseRef = useRef<"typing" | "holding" | "erasing">("typing");
  const qIndexRef = useRef(0);
  const charIndexRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Typewriter effect — stops the instant user focuses
  useEffect(() => {
    if (isFocused || input) return;

    const tick = () => {
      const q = EXAMPLE_QUESTIONS[qIndexRef.current];

      if (phaseRef.current === "typing") {
        charIndexRef.current++;
        setPlaceholder(q.slice(0, charIndexRef.current));
        if (charIndexRef.current >= q.length) {
          phaseRef.current = "holding";
          timerRef.current = setTimeout(tick, TYPEWRITER_HOLD_MS);
        } else {
          timerRef.current = setTimeout(tick, TYPEWRITER_CHAR_MS);
        }
      } else if (phaseRef.current === "holding") {
        phaseRef.current = "erasing";
        timerRef.current = setTimeout(tick, TYPEWRITER_ERASE_MS);
      } else {
        charIndexRef.current--;
        setPlaceholder(q.slice(0, charIndexRef.current));
        if (charIndexRef.current <= 0) {
          qIndexRef.current = (qIndexRef.current + 1) % EXAMPLE_QUESTIONS.length;
          phaseRef.current = "typing";
          timerRef.current = setTimeout(tick, 200);
        } else {
          timerRef.current = setTimeout(tick, TYPEWRITER_ERASE_MS);
        }
      }
    };

    timerRef.current = setTimeout(tick, 600);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isFocused, input]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 140) + "px";
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <motion.div
      layout
      className="query-bar"
      style={{
        position: "relative",
        maxWidth: "640px",
        width: "100%",
        ...(centered ? {} : { marginTop: "auto" }),
      }}
    >
      <div style={{
        display: "flex",
        alignItems: "flex-end",
        gap: "8px",
        padding: loading ? "10px 10px 22px 14px" : "10px 10px 10px 14px",
        transition: "padding 150ms ease",
      }}>
        <textarea
          ref={textareaRef}
          id="marginalia-query-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={!input ? (isFocused ? "" : placeholder) : ""}
          rows={1}
          disabled={loading}
          style={{
            flex: 1,
            background: "transparent",
            border: "none",
            outline: "none",
            resize: "none",
            fontFamily: "'Inter', sans-serif",
            fontSize: "0.9rem",
            fontWeight: 400,
            color: "var(--ink)",
            lineHeight: 1.55,
            maxHeight: "140px",
            padding: 0,
            caretColor: "var(--orange)",
          }}
          aria-label="Research query"
        />

        {/* Submit button */}
        <motion.button
          id="marginalia-submit-btn"
          className="btn-submit"
          onClick={handleSubmit}
          disabled={!input.trim() || loading}
          whileTap={{ scale: 0.95 }}
          style={{
            width: "36px",
            height: "36px",
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          aria-label="Submit query"
        >
          {loading ? (
            <span style={{
              width: "12px",
              height: "12px",
              border: "1.5px solid rgba(255,255,255,0.3)",
              borderTopColor: "#fff",
              borderRadius: "50%",
              display: "block",
              animation: "spin 0.9s linear infinite",
            }} />
          ) : (
            <ArrowRight size={15} strokeWidth={2.5} />
          )}
        </motion.button>
      </div>

      {/* StatusLine — progress indicator in the bottom hairline */}
      <StatusLine active={loading} />
    </motion.div>
  );
}
