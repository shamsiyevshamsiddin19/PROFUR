import { TableViewport } from "../components/TableViewport";
import { useState } from "react";
import { allPages, type StockMovement, type StockRow } from "../api";
import { translate, type Language, type MessageKey } from "../i18n";
import { useRecords } from "../hooks/useRecords";
import { Feedback, Field, RecordsState } from "../components/WorkflowUI";

export function csvCell(value: string) {
  // Excel/Sheets qiymatni formula sifatida bajarmasin.
  const safe = /^[\s]*[=+\-@\t\r]/.test(value) ? "'" + value : value;
  return '"' + safe.replaceAll('"', '""') + '"';
}
export function History({ lang }: { lang: Language }) {
  const t = (key: MessageKey) => translate(lang, key);
  const [filters, setFilters] = useState({
    type: "",
    material: "",
    date_from: "",
    date_to: "",
  });
  const query = new URLSearchParams(
    Object.entries(filters).filter(([, v]) => v),
  );
  const path = "/api/v1/movements/?" + query;
  const records = useRecords<StockMovement>(path, lang);
  const materials = useRecords<StockRow>("/api/v1/stock/", lang);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  async function download() {
    setBusy(true);
    setError(null);
    try {
      const rows = await allPages<StockMovement>(path, lang);
      const header = [
        t("operationDate"),
        t("reference"),
        t("material"),
        t("quantity"),
        t("remaining"),
        t("createdBy"),
        t("reason"),
      ];
      const values = rows.map((row) => [
        row.created_at,
        `${t(row.reference.kind === "opening" ? "openingBalance" : (row.type as MessageKey))} #${row.reference.id}`,
        row.material.display_name,
        row.quantity,
        row.quantity_on_hand_after,
        row.created_by.name,
        row.reason,
      ]);
      const csv =
        "\ufeff" +
        [header, ...values]
          .map((row) => row.map(csvCell).join(","))
          .join("\r\n");
      const url = URL.createObjectURL(
        new Blob([csv], { type: "text/csv;charset=utf-8;" }),
      );
      const link = document.createElement("a");
      link.href = url;
      link.download = "PROFUR-movements.csv";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="workflow-toolbar">
        <select
          aria-label={t("filter")}
          value={filters.type}
          onChange={(e) => setFilters((f) => ({ ...f, type: e.target.value }))}
        >
          <option value="">{t("all")}</option>
          {["receipt", "issue", "return", "write_off"].map((type) => (
            <option key={type} value={type}>
              {t(type as MessageKey)}
            </option>
          ))}
        </select>
        <select
          aria-label={t("material")}
          value={filters.material}
          onChange={(e) =>
            setFilters((f) => ({ ...f, material: e.target.value }))
          }
        >
          <option value="">
            {t("material")}: {t("all")}
          </option>
          {materials.data.map((row) => (
            <option key={row.material.id} value={row.material.id}>
              {row.material.display_name}
            </option>
          ))}
        </select>
        <Field label={t("dateFrom")}>
          <input
            type="date"
            value={filters.date_from}
            onChange={(e) =>
              setFilters((f) => ({ ...f, date_from: e.target.value }))
            }
          />
        </Field>
        <Field label={t("dateTo")}>
          <input
            type="date"
            value={filters.date_to}
            onChange={(e) =>
              setFilters((f) => ({ ...f, date_to: e.target.value }))
            }
          />
        </Field>
        <button
          className="secondary"
          onClick={() =>
            setFilters({ type: "", material: "", date_from: "", date_to: "" })
          }
        >
          {t("resetFilters")}
        </button>
        <button
          className="primary"
          disabled={busy || records.loading}
          onClick={download}
        >
          {t("exportCsv")}
        </button>
      </div>
      {materials.next && (
        <button className="text-button" onClick={materials.more}>
          {t("more")} · {t("materials")}
        </button>
      )}
      <p className="form-hint">{t("reportHint")}</p>
      <Feedback error={error || materials.error} lang={lang} />
      <TableViewport lang={lang} className="recent">
        <table>
          <thead>
            <tr>
              <th>{t("operationDate")}</th>
              <th>{t("reference")}</th>
              <th>{t("material")}</th>
              <th>{t("batch")}</th>
              <th>{t("quantity")}</th>
              <th>{t("remaining")}</th>
              <th>{t("createdBy")}</th>
              <th>{t("reason")}</th>
            </tr>
          </thead>
          <tbody>
            {records.data.map((row) => (
              <tr key={row.id}>
                <td>
                  {new Intl.DateTimeFormat(lang === "uz" ? "uz-UZ" : lang, {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    timeZone: "Asia/Tashkent",
                  }).format(new Date(row.created_at))}
                </td>
                <td>
                  {t(
                    row.reference.kind === "opening"
                      ? "openingBalance"
                      : (row.type as MessageKey),
                  )}{" "}
                  #{row.reference.id}
                </td>
                <td>{row.material.display_name}</td>
                <td>{row.batch_id ? "#" + row.batch_id : "—"}</td>
                <td
                  className={row.quantity.startsWith("-") ? "danger-text" : ""}
                >
                  {row.quantity}
                </td>
                <td>{row.quantity_on_hand_after}</td>
                <td>{row.created_by.name}</td>
                <td className="wrap-cell">{row.reason || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableViewport>
      <RecordsState
        {...records}
        empty={!records.data.length}
        emptyAction={
          <button
            className="secondary"
            onClick={() => {
              setFilters({
                type: "",
                material: "",
                date_from: "",
                date_to: "",
              });
              records.reload();
            }}
          >
            {t(
              Object.values(filters).some(Boolean) ? "resetFilters" : "refresh",
            )}
          </button>
        }
        more={records.next ? records.more : undefined}
        lang={lang}
      />
    </>
  );
}
