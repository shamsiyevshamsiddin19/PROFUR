import { receiptKeyboard } from "../keyboard";
import { TableViewport } from "../components/TableViewport";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import {
  AlertTriangle,
  ArrowDownLeft,
  Check,
  ChevronRight,
  ClipboardList,
  Package,
  Search,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import Decimal from "decimal.js";
import {
  ApiError,
  fieldErrors,
  request,
  write,
  type Material,
  type Page,
  type Receipt,
  type ReceiptInput,
  type StockRow,
  type User,
  type Category,
  can,
} from "../api";
import { errorKey, localDate, money } from "../format";
import { translate, unitLabel, type Language, type MessageKey } from "../i18n";

import { useRecords } from "../hooks/useRecords";
import { StockDetail } from "./StockDetail";

function newDraft() {
  return {
    material_id: "",
    received_on: localDate(),
    quantity: "",
    total_amount: "",
    supplier: "",
    document_number: "",
    note: "",
  };
}

export function WarehouseContent({
  screen,
  lang,
  userId,
  user,
}: {
  screen: "receiving" | "materials" | "stock";
  lang: Language;
  userId: number;
  user: User;
}) {
  const t = useCallback((key: MessageKey) => translate(lang, key), [lang]);
  const [detail, setDetail] = useState<StockRow | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [stockRows, setStockRows] = useState<StockRow[]>([]);
  const [categoryFilter, setCategoryFilter] = useState("");
  const categories = useRecords<Category>(
    screen === "stock" && can(user, "catalog.view_material")
      ? "/api/v1/categories/"
      : null,
    lang,
  );
  const [belowMinOnly, setBelowMinOnly] = useState(false);
  const [next, setNext] = useState<string | null>(null);
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<MessageKey | null>(null);
  const [search, setSearch] = useState("");
  const [revision, setRevision] = useState(0);
  const storageKey = "profur.receipt.pending." + userId;
  const [restored] = useState<{ key: string; body: ReceiptInput } | null>(
    () => {
      try {
        const stored = JSON.parse(sessionStorage.getItem(storageKey) || "null");
        return stored &&
          typeof stored.key === "string" &&
          stored.body?.currency === "USD" &&
          typeof stored.body.material_id === "number"
          ? stored
          : null;
      } catch {
        return null;
      }
    },
  );
  const [draft, setDraft] = useState(() =>
    restored
      ? { ...restored.body, material_id: String(restored.body.material_id) }
      : newDraft(),
  );
  const [saving, setSaving] = useState(false);
  const [uncertain, setUncertain] = useState(Boolean(restored));
  const [saveError, setSaveError] = useState<MessageKey | null>(
    restored ? "locked" : null,
  );
  const [fields, setFields] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState<Receipt | null>(null);
  const pending = useRef<{ key: string; body: ReceiptInput } | null>(restored);
  const selected = materials.find((m) => String(m.id) === draft.material_id);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setLoadError(null);
    const timer = window.setTimeout(async () => {
      try {
        if (screen === "stock") {
          const params = new URLSearchParams();
          if (search) params.set("search", search);
          if (belowMinOnly) params.set("below_min", "true");
          if (categoryFilter) params.set("category", categoryFilter);
          const query = params.toString() ? "?" + params.toString() : "";
          const page = await request<Page<StockRow>>(
            "/api/v1/stock/" + query,
            lang,
            { signal: controller.signal },
          );
          setStockRows(page.results);
          setNext(page.next);
        } else {
          const page = await request<Page<Material>>(
            "/api/v1/materials/?is_active=true&search=" +
              encodeURIComponent(search),
            lang,
            { signal: controller.signal },
          );
          setMaterials(page.results);
          setNext(page.next);
          if (screen === "receiving") {
            const receipts = await request<Page<Receipt>>(
              "/api/v1/receipts/",
              lang,
              { signal: controller.signal },
            );
            setReceipts(receipts.results);
          }
        }
      } catch (e) {
        if (!controller.signal.aborted) setLoadError(errorKey(e));
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }, 180);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [lang, screen, search, belowMinOnly, categoryFilter, revision]);

  async function more() {
    if (!next || loading) return;
    // Sahifalash manzili API hostidan qat’i nazar o‘z originimizga o‘tkaziladi.
    const url = new URL(next, location.origin);
    if (
      !url.pathname.startsWith("/api/v1/materials/") &&
      !url.pathname.startsWith("/api/v1/stock/")
    )
      return;
    setLoading(true);
    try {
      if (screen === "stock") {
        const page = await request<Page<StockRow>>(
          url.pathname + url.search,
          lang,
        );
        setStockRows((items) => [...items, ...page.results]);
        setNext(page.next);
      } else {
        const page = await request<Page<Material>>(
          url.pathname + url.search,
          lang,
        );
        setMaterials((items) => [...items, ...page.results]);
        setNext(page.next);
      }
    } catch (e) {
      setLoadError(errorKey(e));
    } finally {
      setLoading(false);
    }
  }
  function change(field: keyof typeof draft, value: string) {
    setDraft((current) => ({ ...current, [field]: value }));
    setSaved(null);
    setFields({});
    setSaveError(null);
  }
  let preview = "—";
  try {
    if (
      new Decimal(draft.quantity || 0).gt(0) &&
      new Decimal(draft.total_amount || 0).gt(0)
    ) {
      preview = money(
        new Decimal(draft.total_amount).div(draft.quantity).toFixed(2),
        lang,
      );
    }
  } catch {
    /* Kiritilayotgan to‘liq bo‘lmagan son hisoblanmaydi. */
  }

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (saving || !can(user, "inventory.add_receipt")) return;
    if (!pending.current) {
      if (!selected || draft.received_on > localDate()) {
        setSaveError("invalid");
        return;
      }
      pending.current = {
        key: crypto.randomUUID(),
        body: {
          ...draft,
          material_id: selected.id,
          currency: "USD",
        },
      };
    }
    setSaving(true);
    setSaveError(null);
    setFields({});
    setSaved(null);
    try {
      sessionStorage.setItem(storageKey, JSON.stringify(pending.current));
      const receipt = await write<Receipt>(
        "/api/v1/receipts/",
        lang,
        pending.current.body,
        pending.current.key,
      );
      setSaved(receipt);
      sessionStorage.removeItem(storageKey);
      pending.current = null;
      setUncertain(false);
      setDraft(newDraft());
      setRevision((n) => n + 1);
    } catch (error) {
      const unknownResult = !(error instanceof ApiError) || error.status >= 500;
      setUncertain(unknownResult);
      if (!unknownResult) {
        pending.current = null;
        sessionStorage.removeItem(storageKey);
      }
      setSaveError(unknownResult ? "locked" : errorKey(error));
      setFields(fieldErrors(error));
    } finally {
      setSaving(false);
    }
  }
  const locked = saving || uncertain || !can(user, "inventory.add_receipt");
  const loadingNotice = loading && (
    <div className="load-line" role="status">
      <RefreshCw size={15} className="spin" />
      {t("loading")}
    </div>
  );
  const unavailable = loadError && (
    <div className="notice" role="status">
      <Package size={18} />
      <span>{t(loadError)}</span>
      <button className="text-button" onClick={() => setRevision((n) => n + 1)}>
        <RefreshCw size={14} />
        {t("retry")}
      </button>
    </div>
  );

  if (screen !== "receiving")
    return (
      <>
        {detail && (
          <StockDetail
            row={detail}
            user={user}
            lang={lang}
            close={() => setDetail(null)}
            saved={() => {
              setDetail(null);
              setRevision((n) => n + 1);
            }}
          />
        )}
        <div className="toolbar-wrap">
          <div className="toolbar">
            <Search size={17} />
            <input
              data-search-field
              aria-keyshortcuts="/ Control+k Meta+k"
              aria-label={t("search")}
              placeholder={t("search")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          {screen === "stock" && categories.data.length > 0 && (
            <select
              className="stock-category"
              aria-label={t("category")}
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="">
                {t("category")}: {t("all")}
              </option>
              {categories.data.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          )}
          {screen === "stock" && (
            <label className="filter-chip">
              <input
                type="checkbox"
                checked={belowMinOnly}
                onChange={(e) => setBelowMinOnly(e.target.checked)}
              />
              {t("belowMinFilter")}
            </label>
          )}
        </div>
        {loadingNotice}
        {unavailable}
        <TableViewport
          lang={lang}
          className={screen === "stock" ? "stock-ledger" : ""}
        >
          {screen === "stock" ? (
            <table>
              <thead>
                <tr>
                  <th>{t("material")}</th>
                  <th>{t("category")}</th>
                  <th>{t("unit")}</th>
                  <th>{t("stock")}</th>
                  <th>{t("batches")}</th>
                  <th>{t("minLimit")}</th>
                  <th>{t("stockValue")}</th>
                </tr>
              </thead>
              <tbody>
                {stockRows.map((row) => (
                  <tr key={row.material.id}>
                    <td>
                      <span className="material-symbol">
                        <Package size={16} />
                      </span>
                      <button
                        className="text-button material-link"
                        onClick={() => setDetail(row)}
                      >
                        {row.material.display_name}
                      </button>
                    </td>
                    <td data-label={t("category")}>
                      {row.material.category.name}
                    </td>
                    <td data-label={t("unit")}>
                      {unitLabel(row.material.unit, lang)}
                    </td>
                    <td data-label={t("stock")}>
                      <strong>{row.quantity_on_hand}</strong>
                      {row.is_below_min && (
                        <span className="badge-warning" title={t("lowStock")}>
                          <AlertTriangle size={12} />
                          {t("lowStock")}
                        </span>
                      )}
                    </td>
                    <td data-label={t("batches")}>{row.open_batches}</td>
                    <td data-label={t("minLimit")}>
                      {row.min_quantity ?? "—"}
                    </td>
                    <td data-label={t("stockValue")}>
                      {row.value_by_currency?.[0]?.amount
                        ? money(row.value_by_currency[0].amount, lang)
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>{t("material")}</th>
                  <th>{t("category")}</th>
                  <th>{t("unit")}</th>
                </tr>
              </thead>
              <tbody>
                {materials.map((m) => (
                  <tr key={m.id}>
                    <td>
                      <span className="material-symbol">
                        <Package size={16} />
                      </span>
                      {m.display_name || m.name}
                    </td>
                    <td>{m.category.name}</td>
                    <td>{unitLabel(m.unit, lang)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {!loading &&
            !loadError &&
            (screen === "stock"
              ? stockRows.length === 0
              : materials.length === 0) && (
              <Empty
                text={t("empty")}
                action={
                  <>
                    {(search || categoryFilter || belowMinOnly) && (
                      <button
                        className="secondary"
                        onClick={() => {
                          setSearch("");
                          setCategoryFilter("");
                          setBelowMinOnly(false);
                        }}
                      >
                        {t("resetFilters")}
                      </button>
                    )}
                    {can(user, "catalog.view_material") && (
                      <a className="secondary" href="#materials">
                        {t("openMaterials")}
                      </a>
                    )}
                  </>
                }
              />
            )}
        </TableViewport>
        {next && (
          <button className="secondary" onClick={more} disabled={loading}>
            {t(screen === "stock" ? "stock" : "materials")}
            <ChevronRight size={15} />
          </button>
        )}
      </>
    );

  function input(
    field: keyof typeof draft,
    key: MessageKey,
    optional = false,
    type = "text",
  ) {
    return (
      <label className={field === "note" ? "wide" : ""}>
        <span
          className={optional ? "field-label optional-label" : "field-label"}
        >
          {t(key)}
          {optional && <small>{t("optional")}</small>}
        </span>
        <input
          type={type}
          value={draft[field]}
          disabled={locked}
          required={!optional}
          onChange={(e) => change(field, e.target.value)}
          step={type === "number" ? "0.01" : undefined}
          min={type === "number" ? "0.01" : undefined}
          max={type === "date" ? localDate() : undefined}
          maxLength={
            field === "supplier"
              ? 200
              : field === "document_number"
                ? 100
                : field === "note"
                  ? 500
                  : undefined
          }
          aria-invalid={Boolean(fields[field])}
          aria-describedby={fields[field] ? "error-" + field : undefined}
        />
        {fields[field] && (
          <span className="field-error" id={"error-" + field}>
            {fields[field]}
          </span>
        )}
      </label>
    );
  }
  return (
    <>
      {unavailable}
      {saved && (
        <div className="notice success" role="status">
          <Check size={19} />
          <span>
            {t("success")} {t("batch")} #{saved.id} · {t("remaining")}:{" "}
            {saved.quantity_on_hand_after ?? "—"}
          </span>
        </div>
      )}
      <div className="receipt-layout">
        <form
          className="receipt-form panel"
          onSubmit={submit}
          onKeyDown={(event) => receiptKeyboard(event, locked)}
        >
          <div className="panel-heading">
            <span className="section-icon">
              <ArrowDownLeft size={22} />
            </span>
            <div>
              <h2>{t("details")}</h2>
              <p>{t("detailsHint")}</p>
            </div>
          </div>
          <div className="form-grid">
            <label className="wide">
              {t("material")}
              <select
                required
                aria-invalid={Boolean(fields.material_id)}
                aria-describedby={
                  fields.material_id ? "error-material" : undefined
                }
                value={draft.material_id}
                disabled={locked || loading || materials.length === 0}
                onChange={(e) => change("material_id", e.target.value)}
              >
                <option value="">{t("select")}</option>
                {materials.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.display_name || m.name} · {unitLabel(m.unit, lang)}
                  </option>
                ))}
              </select>
              {fields.material_id && (
                <span className="field-error" id="error-material">
                  {fields.material_id}
                </span>
              )}
            </label>
            {next && (
              <button
                type="button"
                className="text-button wide"
                onClick={more}
                disabled={locked}
              >
                {t("materials")}
                <ChevronRight size={14} />
              </button>
            )}
            {input("received_on", "date", false, "date")}
            <label>
              {t("unit")}
              <div className="readonly">
                {selected ? unitLabel(selected.unit, lang) : "—"}
              </div>
            </label>
            {input("quantity", "quantity", false, "number")}
            {input("total_amount", "total", false, "number")}
          </div>
          <div className="form-divider" />
          <div className="form-grid">
            {input("supplier", "supplier", true)}
            {input("document_number", "document", true)}
            {input("note", "note", true)}
          </div>
          {saveError && (
            <div className="notice error" role="alert">
              {t(saveError)}
              {fields.non_field_errors}
            </div>
          )}
          {!loading && !loadError && materials.length === 0 && (
            <div className="form-hint">
              {t("noMaterials")}
              {can(user, "catalog.view_material") && (
                <a className="text-button" href="#materials">
                  {t("openMaterials")}
                </a>
              )}
            </div>
          )}
          <p className="form-hint keyboard-hint">{t("receiptKeyboard")}</p>
          <div className="form-actions">
            <span>
              <ShieldCheck size={15} />
              USD · $
            </span>
            <button
              type="submit"
              className="primary"
              disabled={
                !can(user, "inventory.add_receipt") ||
                saving ||
                (!uncertain && (Boolean(loadError) || loading || !selected))
              }
            >
              {saving ? (
                <RefreshCw size={16} className="spin" />
              ) : (
                <Check size={17} />
              )}
              {t(saving ? "saving" : uncertain ? "again" : "save")}
            </button>
          </div>
        </form>
        <aside className="summary panel">
          <span className="eyebrow">{t("newReceipt")}</span>
          <h2>{t("summary")}</h2>
          <p className="selected-material">
            {selected?.display_name || selected?.name || t("select")}
          </p>
          <dl>
            <div>
              <dt>{t("quantity")}</dt>
              <dd>
                {draft.quantity || "—"}{" "}
                {selected && unitLabel(selected.unit, lang)}
              </dd>
            </div>
            <div>
              <dt>{t("unitPrice")}</dt>
              <dd>{preview}</dd>
            </div>
            <div>
              <dt>{t("currency")}</dt>
              <dd>USD ($)</dd>
            </div>
          </dl>
          <div className="total">
            <span>{t("total")}</span>
            <strong>
              {draft.total_amount ? money(draft.total_amount, lang) : "$0.00"}
            </strong>
          </div>
          <p className="summary-hint">{t("estimate")}</p>
        </aside>
      </div>
      <section className="recent">
        <div className="section-heading">
          <h2>
            <ClipboardList size={19} />
            {t("recent")}
          </h2>
          <button
            className="icon-button"
            aria-label={t("retry")}
            onClick={() => setRevision((n) => n + 1)}
          >
            <RefreshCw size={17} />
          </button>
        </div>
        {loadingNotice}
        {receipts.length ? (
          <TableViewport lang={lang} className="">
            <table>
              <thead>
                <tr>
                  <th>{t("material")}</th>
                  <th>{t("date")}</th>
                  <th>{t("quantity")}</th>
                  <th>{t("total")}</th>
                </tr>
              </thead>
              <tbody>
                {receipts.map((r) => (
                  <tr key={r.id}>
                    <td>{r.material.display_name}</td>
                    <td>{r.received_on}</td>
                    <td>
                      {r.quantity} {unitLabel(r.material.unit, lang)}
                    </td>
                    <td>
                      {r.total_amount ? money(r.total_amount, lang) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableViewport>
        ) : (
          !loading && <Empty text={loadError ? t(loadError) : t("empty")} />
        )}
      </section>
    </>
  );
}

function Empty({
  text,
  action,
}: {
  text: string;
  action?: import("react").ReactNode;
}) {
  return (
    <div className="empty">
      <Package size={26} strokeWidth={1.2} />
      <p>{text}</p>
      {action && <div className="empty-actions">{action}</div>}
    </div>
  );
}
