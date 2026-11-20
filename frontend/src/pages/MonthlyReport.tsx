import { useEffect, useMemo, useState } from "react";
import { request } from "../api";
import { TableViewport } from "../components/TableViewport";
import { Feedback } from "../components/WorkflowUI";
import { localDate, money } from "../format";
import { translate, unitLabel, type Language } from "../i18n";

const movements = {
  received: "amountReceived",
  issued: "amountIssued",
  returned: "amountReturned",
  written_off: "amountWrittenOff",
} as const;

type Metric = keyof typeof movements;

type MaterialCategory = {
  id: number;
  name: string;
};

type ReportRow = {
  material: {
    id: number;
    name: string;
    unit: string;
    category?: MaterialCategory | null;
  };
  current_stock?: string;
  stock_value_usd?: string;
  net_issued?: string;
  net_issued_usd?: string;
} & Partial<Record<Metric | `${Metric}_usd`, string>>;

type CategorySummary = {
  id: number;
  name: string;
  materials_count: number;
  received_units: string;
  received_usd?: string;
  issued_units: string;
  issued_usd?: string;
  returned_units: string;
  returned_usd?: string;
  written_off_units: string;
  written_off_usd?: string;
  net_issued_units: string;
  net_issued_usd?: string;
};

type ExpenseBreakdown = {
  type_id: number;
  code: string;
  name_uz: string;
  name_ru: string;
  name_en: string;
  amount: string;
  percentage: number;
  count: number;
};

type RecipientBreakdown = {
  recipient: string;
  total_quantity: string;
  issues_count: number;
  total_usd?: string;
};

type ReportTotals = {
  received: string;
  issued: string;
  returned: string;
  written_off: string;
  net_issued: string;
  warehouse_value: string;
};

type Report = {
  month: string;
  rows: ReportRow[];
  categories_breakdown?: CategorySummary[];
  recipients_breakdown?: RecipientBreakdown[];
  expenses_breakdown?: ExpenseBreakdown[];
  top_consumed?: ReportRow[];
  totals?: ReportTotals;
  expenses?: string;
};

function formatMonthLabel(ym: string, lang: Language): string {
  if (!/^\d{4}-\d{2}$/.test(ym)) return ym;
  const [y, m] = ym.split("-").map(Number);
  const date = new Date(y, m - 1, 1);
  const locale = lang === "uz" ? "uz-UZ" : lang === "ru" ? "ru-RU" : "en-US";
  return date.toLocaleDateString(locale, { year: "numeric", month: "long" });
}

function offsetMonth(ym: string, delta: number): string {
  const [y, m] = ym.split("-").map(Number);
  const d = new Date(y, m - 1 + delta, 1);
  const nextY = d.getFullYear();
  const nextM = String(d.getMonth() + 1).padStart(2, "0");
  return `${nextY}-${nextM}`;
}

export function MonthlyReport({ lang }: { lang: Language }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const currentMonthStr = useMemo(() => localDate().slice(0, 7), []);
  const [month, setMonth] = useState(() => currentMonthStr);
  const [error, setError] = useState<unknown>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [activeTab, setActiveTab] = useState<"turnover" | "categories" | "expenses" | "recipients">("turnover");

  // Filters for turnover table
  const [search, setSearch] = useState("");
  const [selectedCat, setSelectedCat] = useState<string>("all");
  const [onlyActive, setOnlyActive] = useState(false);

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

  // Extract available categories from rows
  const categories = useMemo(() => {
    if (!report?.rows) return [];
    const map = new Map<number, string>();
    for (const r of report.rows) {
      if (r.material.category) {
        map.set(r.material.category.id, r.material.category.name);
      }
    }
    return Array.from(map.entries()).map(([id, name]) => ({ id, name }));
  }, [report?.rows]);

  // Filtered rows for turnover table
  const filteredRows = useMemo(() => {
    if (!report?.rows) return [];
    return report.rows.filter((r) => {
      if (search) {
        const q = search.toLowerCase();
        if (!r.material.name.toLowerCase().includes(q)) return false;
      }
      if (selectedCat !== "all") {
        if (String(r.material.category?.id) !== selectedCat) return false;
      }
      if (onlyActive) {
        const hasRec = r.received && parseFloat(r.received) > 0;
        const hasIss = r.issued && parseFloat(r.issued) > 0;
        const hasRet = r.returned && parseFloat(r.returned) > 0;
        const hasWro = r.written_off && parseFloat(r.written_off) > 0;
        if (!hasRec && !hasIss && !hasRet && !hasWro) return false;
      }
      return true;
    });
  }, [report?.rows, search, selectedCat, onlyActive]);

  // Filtered table totals
  const filteredTotals = useMemo(() => {
    let recUnits = 0;
    let recUsd = 0;
    let issUnits = 0;
    let issUsd = 0;
    let retUnits = 0;
    let retUsd = 0;
    let wroUnits = 0;
    let wroUsd = 0;
    let netUnits = 0;
    let netUsd = 0;
    let stockUsd = 0;

    for (const r of filteredRows) {
      recUnits += parseFloat(r.received || "0");
      recUsd += parseFloat(r.received_usd || "0");
      issUnits += parseFloat(r.issued || "0");
      issUsd += parseFloat(r.issued_usd || "0");
      retUnits += parseFloat(r.returned || "0");
      retUsd += parseFloat(r.returned_usd || "0");
      wroUnits += parseFloat(r.written_off || "0");
      wroUsd += parseFloat(r.written_off_usd || "0");
      netUnits += parseFloat(r.net_issued || "0");
      netUsd += parseFloat(r.net_issued_usd || "0");
      stockUsd += parseFloat(r.stock_value_usd || "0");
    }

    return {
      recUnits: recUnits.toFixed(2),
      recUsd: recUsd.toFixed(2),
      issUnits: issUnits.toFixed(2),
      issUsd: issUsd.toFixed(2),
      retUnits: retUnits.toFixed(2),
      retUsd: retUsd.toFixed(2),
      wroUnits: wroUnits.toFixed(2),
      wroUsd: wroUsd.toFixed(2),
      netUnits: netUnits.toFixed(2),
      netUsd: netUsd.toFixed(2),
      stockUsd: stockUsd.toFixed(2),
    };
  }, [filteredRows]);

  const handleExportCsv = () => {
    if (!report?.rows?.length) return;
    const headers = [
      "ID",
      t("material"),
      t("materials"),
      t("unit"),
      `${t("amountReceived")} (${t("quantity")})`,
      `${t("amountReceived")} (USD)`,
      `${t("amountIssued")} (${t("quantity")})`,
      `${t("amountIssued")} (USD)`,
      `${t("amountReturned")} (${t("quantity")})`,
      `${t("amountReturned")} (USD)`,
      `${t("amountWrittenOff")} (${t("quantity")})`,
      `${t("amountWrittenOff")} (USD)`,
      `${t("amountNet")} (${t("quantity")})`,
      `${t("amountNet")} (USD)`,
      `${t("currentStock")} (${t("quantity")})`,
      `${t("stockValue")} (USD)`,
    ];

    const lines = [
      headers.join(","),
      ...report.rows.map((r) =>
        [
          r.material.id,
          `"${r.material.name.replace(/"/g, '""')}"`,
          `"${(r.material.category?.name || "").replace(/"/g, '""')}"`,
          r.material.unit,
          r.received || "0",
          r.received_usd || "0",
          r.issued || "0",
          r.issued_usd || "0",
          r.returned || "0",
          r.returned_usd || "0",
          r.written_off || "0",
          r.written_off_usd || "0",
          r.net_issued || "0",
          r.net_issued_usd || "0",
          r.current_stock || "0",
          r.stock_value_usd || "0",
        ].join(","),
      ),
    ];

    // UTF-8 BOM
    const blob = new Blob(["\ufeff" + lines.join("\r\n")], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `profur-hisobot-${month}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="monthly-report-page">
      {/* Top Header Controls */}
      <div className="report-header-controls">
        <div className="report-period-group">
          <button
            type="button"
            className="btn-report-action"
            title={t("prevMonth")}
            onClick={() => setMonth((m) => offsetMonth(m, -1))}
          >
            ◀
          </button>
          <input
            type="month"
            min="1900-01"
            max="9998-12"
            value={month}
            className="report-filter-select"
            style={{ fontWeight: 600 }}
            onChange={(e) => {
              if (/^\d{4}-\d{2}$/.test(e.target.value)) setMonth(e.target.value);
            }}
          />
          <button
            type="button"
            className="btn-report-action"
            title={t("nextMonth")}
            onClick={() => setMonth((m) => offsetMonth(m, 1))}
          >
            ▶
          </button>
          {month !== currentMonthStr && (
            <button
              type="button"
              className="btn-report-action"
              onClick={() => setMonth(currentMonthStr)}
            >
              {t("currentMonth")}
            </button>
          )}
          <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--accent)", marginLeft: 6 }}>
            {formatMonthLabel(month, lang)}
          </span>
        </div>

        <div className="report-actions-group">
          <button
            type="button"
            className="btn-report-action primary"
            onClick={handleExportCsv}
            disabled={!report?.rows?.length}
          >
            📥 {t("exportCsv")}
          </button>
          <button
            type="button"
            className="btn-report-action"
            onClick={() => window.print()}
          >
            🖨️ {t("printReport")}
          </button>
        </div>
      </div>

      <Feedback error={error} lang={lang} />
      {!report && !error && <p role="status">{t("loading")}</p>}

      {report && (
        <>
          {/* Executive KPI Summary Cards */}
          {(report.totals || report.expenses !== undefined) && (
            <div className="report-kpi-grid">
              {report.totals && (
                <>
                  <div className="report-kpi-card highlight">
                    <div className="kpi-label">{t("warehouseValueNow")}</div>
                    <div className="kpi-value">{money(report.totals.warehouse_value, lang)}</div>
                    <div className="kpi-badge">📦 {t("currentStock")}</div>
                  </div>
                  <div className="report-kpi-card">
                    <div className="kpi-label">{t("amountReceived")}</div>
                    <div className="kpi-value">{money(report.totals.received, lang)}</div>
                    <div className="kpi-badge">📥 {report.rows.reduce((acc, r) => acc + (parseFloat(r.received || "0") > 0 ? 1 : 0), 0)} ta partiya</div>
                  </div>
                  <div className="report-kpi-card">
                    <div className="kpi-label">{t("amountNet")}</div>
                    <div className="kpi-value">{money(report.totals.net_issued, lang)}</div>
                    <div className="kpi-badge">📤 Ishlab chiqarish</div>
                  </div>
                  <div className="report-kpi-card">
                    <div className="kpi-label">{t("amountReturned")}</div>
                    <div className="kpi-value">{money(report.totals.returned, lang)}</div>
                    <div className="kpi-badge">↩️ Qaytarilgan</div>
                  </div>
                  <div className="report-kpi-card">
                    <div className="kpi-label">{t("amountWrittenOff")}</div>
                    <div className="kpi-value">{money(report.totals.written_off, lang)}</div>
                    <div className="kpi-badge">⚠️ Spisaniye/Brak</div>
                  </div>
                </>
              )}
              {report.expenses !== undefined && (
                <div className="report-kpi-card">
                  <div className="kpi-label">{t("expenses")}</div>
                  <div className="kpi-value">{money(report.expenses, lang)}</div>
                  <div className="kpi-badge">💸 Operatsion</div>
                </div>
              )}
            </div>
          )}

          {/* Top Consumed Materials Highlight */}
          {report.top_consumed && report.top_consumed.length > 0 && (
            <div style={{ marginBottom: 18 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", marginBottom: 8, letterSpacing: 0.5 }}>
                ⭐ {t("topConsumed")}
              </div>
              <div className="report-top-consumed">
                {report.top_consumed.map((item) => (
                  <div key={item.material.id} className="report-top-item">
                    <div className="report-top-title">{item.material.name}</div>
                    <div className="report-top-meta">
                      <span>{item.net_issued} {unitLabel(item.material.unit, lang)}</span>
                      {item.net_issued_usd !== undefined && (
                        <strong style={{ color: "var(--accent)" }}>{money(item.net_issued_usd, lang)}</strong>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tabs Navigation */}
          <div className="report-tabs">
            <button
              type="button"
              className={`report-tab-btn ${activeTab === "turnover" ? "active" : ""}`}
              onClick={() => setActiveTab("turnover")}
            >
              📋 {t("turnoverTable")} ({filteredRows.length})
            </button>
            {report.categories_breakdown && report.categories_breakdown.length > 0 && (
              <button
                type="button"
                className={`report-tab-btn ${activeTab === "categories" ? "active" : ""}`}
                onClick={() => setActiveTab("categories")}
              >
                🗂️ {t("categoriesSummary")} ({report.categories_breakdown.length})
              </button>
            )}
            {report.expenses_breakdown && report.expenses_breakdown.length > 0 && (
              <button
                type="button"
                className={`report-tab-btn ${activeTab === "expenses" ? "active" : ""}`}
                onClick={() => setActiveTab("expenses")}
              >
                💰 {t("expensesSummary")} ({report.expenses_breakdown.length})
              </button>
            )}
            {report.recipients_breakdown && report.recipients_breakdown.length > 0 && (
              <button
                type="button"
                className={`report-tab-btn ${activeTab === "recipients" ? "active" : ""}`}
                onClick={() => setActiveTab("recipients")}
              >
                👷 {t("recipientsSummary")} ({report.recipients_breakdown.length})
              </button>
            )}
          </div>

          {/* TAB 1: Turnover Table */}
          {activeTab === "turnover" && (
            <>
              <div className="report-filters-bar">
                <input
                  type="search"
                  className="report-search-input"
                  placeholder={t("searchMaterial")}
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                {categories.length > 0 && (
                  <select
                    className="report-filter-select"
                    value={selectedCat}
                    onChange={(e) => setSelectedCat(e.target.value)}
                  >
                    <option value="all">{t("allCategories")}</option>
                    {categories.map((c) => (
                      <option key={c.id} value={String(c.id)}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                )}
                <label className="report-filter-checkbox">
                  <input
                    type="checkbox"
                    checked={onlyActive}
                    onChange={(e) => setOnlyActive(e.target.checked)}
                  />
                  {t("onlyWithActivity")}
                </label>
              </div>

              <TableViewport lang={lang} className="">
                <table>
                  <thead>
                    <tr>
                      <th>{t("material")}</th>
                      <th>{t("materials")}</th>
                      <th>{t("unit")}</th>
                      {(Object.keys(movements) as Metric[]).map((key) => (
                        <th key={key}>{t(movements[key])}</th>
                      ))}
                      <th>{t("amountNet")}</th>
                      <th>{t("currentStock")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRows.map((row) => (
                      <tr key={row.material.id}>
                        <td>
                          <strong>{row.material.name}</strong>
                        </td>
                        <td>
                          {row.material.category ? (
                            <span className="kpi-badge">{row.material.category.name}</span>
                          ) : (
                            "—"
                          )}
                        </td>
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
                        <td>
                          <strong>{row.net_issued ?? "0"}</strong>
                          {row.net_issued_usd !== undefined && (
                            <small className="review-detail" style={{ color: "var(--accent)" }}>
                              {money(row.net_issued_usd, lang)}
                            </small>
                          )}
                        </td>
                        <td>
                          {row.current_stock ?? "—"}
                          {row.stock_value_usd !== undefined && (
                            <small className="review-detail">
                              {money(row.stock_value_usd, lang)}
                            </small>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  {filteredRows.length > 0 && (
                    <tfoot>
                      <tr style={{ background: "rgba(255, 255, 255, 0.04)", fontWeight: 700 }}>
                        <td colSpan={3}>{t("grandTotal")} ({filteredRows.length})</td>
                        <td>
                          {filteredTotals.recUnits}
                          <small className="review-detail">{money(filteredTotals.recUsd, lang)}</small>
                        </td>
                        <td>
                          {filteredTotals.issUnits}
                          <small className="review-detail">{money(filteredTotals.issUsd, lang)}</small>
                        </td>
                        <td>
                          {filteredTotals.retUnits}
                          <small className="review-detail">{money(filteredTotals.retUsd, lang)}</small>
                        </td>
                        <td>
                          {filteredTotals.wroUnits}
                          <small className="review-detail">{money(filteredTotals.wroUsd, lang)}</small>
                        </td>
                        <td>
                          <span style={{ color: "var(--accent)" }}>{filteredTotals.netUnits}</span>
                          <small className="review-detail" style={{ color: "var(--accent)" }}>
                            {money(filteredTotals.netUsd, lang)}
                          </small>
                        </td>
                        <td>
                          <small className="review-detail">{money(filteredTotals.stockUsd, lang)}</small>
                        </td>
                      </tr>
                    </tfoot>
                  )}
                </table>
              </TableViewport>
              {!filteredRows.length && <p className="empty">{t("empty")}</p>}
            </>
          )}

          {/* TAB 2: Categories Analytics */}
          {activeTab === "categories" && report.categories_breakdown && (
            <div className="category-analytics-grid">
              {report.categories_breakdown.map((cat) => (
                <div key={cat.id} className="category-card">
                  <div className="category-card-header">
                    <span className="category-card-title">{cat.name}</span>
                    <span className="kpi-badge">{cat.materials_count} ta material</span>
                  </div>
                  <div className="category-metrics">
                    <div>
                      <div className="kpi-label">{t("amountReceived")}</div>
                      <div className="category-metric-val">{cat.received_units}</div>
                      {cat.received_usd && (
                        <small className="review-detail">{money(cat.received_usd, lang)}</small>
                      )}
                    </div>
                    <div>
                      <div className="kpi-label">{t("amountNet")}</div>
                      <div className="category-metric-val" style={{ color: "var(--accent)" }}>
                        {cat.net_issued_units}
                      </div>
                      {cat.net_issued_usd && (
                        <small className="review-detail" style={{ color: "var(--accent)" }}>
                          {money(cat.net_issued_usd, lang)}
                        </small>
                      )}
                    </div>
                    <div>
                      <div className="kpi-label">{t("amountReturned")}</div>
                      <div className="category-metric-val">{cat.returned_units}</div>
                      {cat.returned_usd && (
                        <small className="review-detail">{money(cat.returned_usd, lang)}</small>
                      )}
                    </div>
                    <div>
                      <div className="kpi-label">{t("amountWrittenOff")}</div>
                      <div className="category-metric-val">{cat.written_off_units}</div>
                      {cat.written_off_usd && (
                        <small className="review-detail">{money(cat.written_off_usd, lang)}</small>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 3: Expenses Breakdown */}
          {activeTab === "expenses" && report.expenses_breakdown && (
            <TableViewport lang={lang} className="">
              <table>
                <thead>
                  <tr>
                    <th>Xarajat turi</th>
                    <th>{t("percentage")}</th>
                    <th>Yozuvlar soni</th>
                    <th>{t("total")}</th>
                  </tr>
                </thead>
                <tbody>
                  {report.expenses_breakdown.map((exp) => (
                    <tr key={exp.type_id}>
                      <td>
                        <strong>
                          {lang === "ru" ? exp.name_ru : lang === "en" ? exp.name_en : exp.name_uz}
                        </strong>
                      </td>
                      <td style={{ minWidth: 160 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <span style={{ minWidth: 42, fontSize: 13, fontWeight: 600 }}>
                            {exp.percentage}%
                          </span>
                          <div className="report-progress-track">
                            <div
                              className="report-progress-fill"
                              style={{ width: `${Math.min(100, exp.percentage)}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td>{exp.count} ta</td>
                      <td>
                        <strong style={{ fontSize: 15, color: "var(--accent)" }}>
                          {money(exp.amount, lang)}
                        </strong>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </TableViewport>
          )}

          {/* TAB 4: Recipients Breakdown */}
          {activeTab === "recipients" && report.recipients_breakdown && (
            <TableViewport lang={lang} className="">
              <table>
                <thead>
                  <tr>
                    <th>{t("recipient")}</th>
                    <th>{t("issuesCount")}</th>
                    <th>Jami olingan miqdor</th>
                    {report.recipients_breakdown.some((r) => r.total_usd) && (
                      <th>Qiymati (USD)</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {report.recipients_breakdown.map((rec, i) => (
                    <tr key={i}>
                      <td>
                        <strong>👷 {rec.recipient}</strong>
                      </td>
                      <td>{rec.issues_count} marta</td>
                      <td>
                        <strong>{rec.total_quantity}</strong>
                      </td>
                      {rec.total_usd !== undefined && (
                        <td>
                          <span style={{ color: "var(--accent)", fontWeight: 700 }}>
                            {money(rec.total_usd, lang)}
                          </span>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </TableViewport>
          )}
        </>
      )}
    </div>
  );
}
