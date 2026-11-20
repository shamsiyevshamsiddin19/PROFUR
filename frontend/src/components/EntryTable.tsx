import { Children, Fragment, isValidElement, type ReactNode } from "react";
import { Field } from "./WorkflowUI";
import { TableViewport } from "./TableViewport";
import { translate, type Language } from "../i18n";

// Fragments preserve conditional columns without duplicating form state or controls.
function fields(children: ReactNode): ReactNode[] {
  return Children.toArray(children).flatMap((child) =>
    isValidElement<{ children?: ReactNode }>(child) && child.type === Fragment
      ? fields(child.props.children)
      : [child],
  );
}

/** One new record per row; saving still uses the original validated form. */
export function EntryTable({
  children,
  lang,
  className = "",
}: {
  children: ReactNode;
  lang: Language;
  className?: string;
}) {
  const columns = fields(children).filter(
    (child) => isValidElement<{ label: string }>(child) && child.type === Field,
  );
  return (
    <TableViewport lang={lang} className="entry-viewport">
      <table
        className={`entry-table ${className}`.trim()}
        data-columns={columns.length}
      >
        <caption className="visually-hidden">
          {translate(lang, "entryTable")}
        </caption>
        <thead>
          <tr>
            {columns.map((column, index) => (
              <th scope="col" key={index} className={`entry-col-${index}`}>
                {isValidElement<{ label: string }>(column)
                  ? column.props.label
                  : ""}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            {columns.map((column, index) => (
              <td key={index} className={`entry-col-${index}`}>
                {column}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </TableViewport>
  );
}
