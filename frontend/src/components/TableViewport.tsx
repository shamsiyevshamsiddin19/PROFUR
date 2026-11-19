import {
  useCallback,
  useLayoutEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { MoveHorizontal } from "lucide-react";
import { translate, type Language } from "../i18n";

/** Shadows describe actual overflow; native keyboard and touch scrolling are preserved. */
export function TableViewport({
  children,
  lang,
  className = "",
}: {
  children: ReactNode;
  lang: Language;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [edges, setEdges] = useState({
    left: false,
    right: false,
    vertical: false,
  });
  const update = useCallback(() => {
    const node = ref.current;
    if (!node) return;
    const next = {
      left: node.scrollLeft > 1,
      right: node.scrollWidth - node.clientWidth - node.scrollLeft > 1,
      vertical: node.scrollHeight - node.clientHeight > 1,
    };
    setEdges((old) =>
      old.left === next.left &&
      old.right === next.right &&
      old.vertical === next.vertical
        ? old
        : next,
    );
  }, []);
  useLayoutEffect(() => {
    const node = ref.current;
    if (!node) return;
    update();
    const observer =
      typeof ResizeObserver === "undefined" ? null : new ResizeObserver(update);
    observer?.observe(node);
    const table = node.querySelector("table");
    if (table) observer?.observe(table);
    window.addEventListener("resize", update);
    return () => {
      observer?.disconnect();
      window.removeEventListener("resize", update);
    };
  }, [update]);
  const scrollable = edges.left || edges.right || edges.vertical;
  return (
    <div
      className={
        "table-region" +
        (edges.left ? " scroll-left" : "") +
        (edges.right ? " scroll-right" : "")
      }
    >
      <div
        ref={ref}
        className={"table-wrap " + className}
        onScroll={update}
        tabIndex={scrollable ? 0 : undefined}
        role={scrollable ? "region" : undefined}
        aria-label={scrollable ? translate(lang, "tableData") : undefined}
      >
        {children}
      </div>
      {(edges.left || edges.right) && (
        <div className="table-scroll-hint">
          <MoveHorizontal size={15} aria-hidden="true" />
          {translate(lang, "scrollColumns")}
        </div>
      )}
    </div>
  );
}
