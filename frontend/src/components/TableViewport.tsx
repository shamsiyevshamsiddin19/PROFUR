import {
  Children,
  Fragment,
  cloneElement,
  isValidElement,
  useCallback,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type HTMLAttributes,
  type ReactElement,
  type ReactNode,
} from "react";
import { MoveHorizontal } from "lucide-react";
import { translate, type Language } from "../i18n";

type TableElement = ReactElement<HTMLAttributes<HTMLElement>, string>;

// Conditional columns can be grouped in fragments, for example prices.
function tableChildren(children: ReactNode): ReactNode[] {
  return Children.toArray(children).flatMap((child) =>
    isValidElement<{ children?: ReactNode }>(child) && child.type === Fragment
      ? tableChildren(child.props.children)
      : [child],
  );
}

function isTag(node: ReactNode, tag: string): node is TableElement {
  return isValidElement(node) && node.type === tag;
}

function mapCells(
  children: ReactNode,
  render: (cell: ReactNode) => ReactNode,
): ReactNode {
  return Children.map(children, (cell) =>
    isValidElement<{ children?: ReactNode }>(cell) && cell.type === Fragment
      ? cloneElement(cell, {}, mapCells(cell.props.children, render))
      : render(cell),
  );
}

function labelTable(table: ReactNode, entry: boolean): ReactNode {
  if (!isTag(table, "table")) return table;
  const groups = tableChildren(table.props.children);
  const header = groups.find((group) => isTag(group, "thead"));
  const headings = header
    ? tableChildren(header.props.children).flatMap((row) =>
        isTag(row, "tr")
          ? tableChildren(row.props.children).filter((cell) =>
              isTag(cell, "th"),
            )
          : [],
      )
    : [];

  // Explicit roles preserve table semantics when CSS reflows the rows.
  return cloneElement(
    table,
    { role: "table" },
    groups.map((group) => {
      if (!isTag(group, "thead") && !isTag(group, "tbody")) return group;
      return cloneElement(
        group,
        { role: "rowgroup" },
        tableChildren(group.props.children).map((row) => {
          if (!isTag(row, "tr")) return row;
          let column = 0;
          return cloneElement(
            row,
            { role: "row" },
            mapCells(row.props.children, (cell) => {
              if (isTag(cell, "th")) {
                return cloneElement(cell, { role: "columnheader" });
              }
              if (!isTag(cell, "td")) return cell;
              const label = headings[column++]?.props.children;
              return cloneElement(
                cell,
                { role: "cell" },
                !entry && label && (
                  <span className="mobile-cell-label" aria-hidden="true">
                    {label}
                  </span>
                ),
                cell.props.children,
              );
            }),
          );
        }),
      );
    }),
  );
}

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
  const table = useMemo(
    () =>
      Children.map(children, (child) =>
        labelTable(child, className === "entry-viewport"),
      ),
    [children, className],
  );
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
        {table}
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
