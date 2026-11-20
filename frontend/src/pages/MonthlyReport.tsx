import { useEffect, useState } from "react";
import { request } from "../api";
import { TableViewport } from "../components/TableViewport";
import { Feedback, Field } from "../components/WorkflowUI";
import { localDate, money } from "../format";
import { translate, unitLabel, type Language } from "../i18n";

const movements = {
  received: "amountReceived",
  issued: "amountIssued",
  returned: "amountReturned",
  written_off: "amountWrittenOff",
} as const;
const moneyRows = {
  ...movements,
  net_issued: "amountNet",
  warehouse_value: "warehouseValueNow",
} as const;
type Metric = keyof typeof movements;
type Report = {
  month: string;
  rows: ({ material: { id: number; name: string; unit: string } } & Partial<
    Record<Metric | `${Metric}_usd`, string>
  >)[];
  totals?: Record<keyof typeof moneyRows, string>;
  expenses?: string;
};

export function MonthlyReport({ lang }: { lang: Language }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [month, setMonth] = useState(() => localDate().slice(0, 7));
  const [error, setError] = useState<unknown>(null);
  const [report, setReport] = useState<Report | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    setError(null);
    setReport(null);
    void request<Report>(
      "/api/v1/dashboard/?" + new URLSearchParams({ month }),
      lang,
      { signal: controller.signal },
    )
      .then((value) => {
        if (!controller.signal.aborted) setReport(value);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setError(err);
      });
    return () => controller.abort();
  }, [month, lang]);

  return (
    <>
      <div className="workflow-toolbar">
        <Field label={t("reportMonth")}>
          <input
            type="month"
            min="1900-01"
            max="9998-12"
            value={month}
            onChange={(e) => {
              if (/^\d{4}-\d{2}$/.test(e.target.value))
                setMonth(e.target.value);
            }}
          />
        </Field>
      </div>
      <Feedback error={error} lang={lang} />
      {!report && !error && <p role="status">{t("loading")}</p>}
      {report && (
        <>
          {(report.totals || report.expenses !== undefined) && (
            <dl className="report-summary">
              {report.totals &&
                (Object.keys(moneyRows) as (keyof typeof moneyRows)[]).map(
                  (key) => (
                    <div key={key}>
                      <dt>{t(moneyRows[key])}</dt>
                      <dd>{money(report.totals![key], lang)}</dd>
                    </div>
                  ),
                )}
              {report.expenses !== undefined && (
                <div>
                  <dt>{t("expenses")}</dt>
                  <dd>{money(report.expenses, lang)}</dd>
                </div>
              )}
            </dl>
          )}
          <TableViewport lang={lang} className="">
            <table>
              <thead>
                <tr>
                  <th>{t("material")}</th>
                  <th>{t("unit")}</th>
                  {(Object.keys(movements) as Metric[]).map((key) => (
                    <th key={key}>{t(movements[key])}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {report.rows.map((row) => (
                  <tr key={row.material.id}>
                    <td>{row.material.name}</td>
                    <td>{unitLabel(row.material.unit, lang)}</td>
                    {(Object.keys(movements) as Metric[]).map((key) => (
                      <td key={key}>
                        {row[key] ?? "0"}
                        {row[`${key}_usd`] !== undefined && (
                          <small className="review-detail">
                            {money(row[`${key}_usd`]!, lang)}
                          </small>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </TableViewport>
          {!report.rows.length && <p className="empty">{t("empty")}</p>}
        </>
      )}
    </>
  );
}
