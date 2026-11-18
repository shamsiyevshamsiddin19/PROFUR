import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import {
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
} from "../api";
import { errorKey, localDate, money } from "../format";
import { translate, unitLabel, type Language, type MessageKey } from "../i18n";

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
}: {
  screen: "receiving" | "materials" | "stock";
  lang: Language;
  userId: number;
}) {
  const t = useCallback((key: MessageKey) => translate(lang, key), [lang]);
  const [materials, setMaterials] = useState<Material[]>([]);
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
  }, [lang, screen, search, revision]);

  async function more() {
    if (!next || loading) return;
    // Sahifalash manzili API hostidan qat’i nazar o‘z originimizga o‘tkaziladi.
    const url = new URL(next, location.origin);
    if (!url.pathname.startsWith("/api/v1/materials/")) return;
    setLoading(true);
    try {
      const page = await request<Page<Material>>(
        url.pathname + url.search,
        lang,
      );
      setMaterials((items) => [...items, ...page.results]);
      setNext(page.next);
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
    if (saving) return;
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
  const locked = saving || uncertain;
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
        <div className="toolbar">
          <Search size={17} />
          <input
            aria-label={t("search")}
            placeholder={t("search")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        {loadingNotice}
        {unavailable}
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("material")}</th>
                <th>{t("category")}</th>
                <th>{t("unit")}</th>
                {screen === "stock" && <th>{t("stock")}</th>}
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
                  {screen === "stock" && <td>{m.quantity_on_hand ?? "—"}</td>}
                </tr>
              ))}
            </tbody>
          </table>
          {!loading && !loadError && materials.length === 0 && (
            <Empty text={t("empty")} />
          )}
        </div>
        {next && (
          <button className="secondary" onClick={more} disabled={loading}>
            {t("materials")}
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
        {t(key)}
        {optional && <small>{t("optional")}</small>}
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
        <form className="receipt-form panel" onSubmit={submit}>
          <div className="panel-heading">
            <span className="section-icon">
              <ArrowDownLeft size={22} />
            </span>
            <div>
              <h2>{t("details")}</h2>
              <p>{t("detailsHint")}</p>
            </div>
            <span className="subtle-label">USD</span>
          </div>
          <div className="form-grid">
            <label className="wide">
              {t("material")}
              <select
                required
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
                <span className="field-error">{fields.material_id}</span>
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
            <p className="form-hint">{t("noMaterials")}</p>
          )}
          <div className="form-actions">
            <span>
              <ShieldCheck size={15} />
              USD · $
            </span>
            <button
              className="primary"
              disabled={
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
          <div className="summary-graphic" aria-hidden="true">
            <Package size={48} strokeWidth={1} />
            <span className="orb" />
          </div>
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
          <div className="table-wrap">
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
                    <td>{money(r.total_amount, lang)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          !loading && <Empty text={loadError ? t(loadError) : t("empty")} />
        )}
      </section>
    </>
  );
}

function Empty({ text }: { text: string }) {
  return (
    <div className="empty">
      <Package size={26} strokeWidth={1.2} />
      <p>{text}</p>
    </div>
  );
}
