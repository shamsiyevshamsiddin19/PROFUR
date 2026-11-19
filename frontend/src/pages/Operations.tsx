import { TableViewport } from "../components/TableViewport";
import { useEffect, useState, type FormEvent } from "react";
import Decimal from "decimal.js";
import {
  allPages,
  can,
  write,
  type User,
  type StockRow,
  type StockBatch,
  type Operation,
  type Allocation,
} from "../api";
import { translate, type Language } from "../i18n";
import { localDate, money } from "../format";
import { useRecords } from "../hooks/useRecords";
import { useIdempotentWrite } from "../hooks/useIdempotentWrite";
import {
  Field,
  Feedback,
  Modal,
  RecordsState,
  Status,
} from "../components/WorkflowUI";

type Kind = "issues" | "returns" | "write-offs";
const labels = {
  issues: "issue",
  returns: "return",
  "write-offs": "write_off",
} as const;
const permissions = {
  issues: "inventory.add_issue",
  returns: "inventory.add_return",
  "write-offs": "inventory.add_write_off",
};
export function Operations({ lang, user }: { lang: Language; user: User }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [kind, setKind] = useState<Kind>("issues");
  const [status, setStatus] = useState("");
  const [revision, setRevision] = useState(0);
  const [decision, setDecision] = useState<{
    row: Operation;
    action: "approve" | "reject";
  } | null>(null);
  const records = useRecords<Operation>(
    `/api/v1/${kind}/` +
      (status && kind !== "issues" ? `?status=${status}` : ""),
    lang,
    revision,
  );
  const approvalCode =
    kind === "returns"
      ? "inventory.approve_return"
      : "inventory.approve_write_off";
  return (
    <>
      <div className="workflow-toolbar">
        <div className="tabs" role="tablist" aria-label={t("operations")}>
          {(Object.keys(labels) as Kind[]).map((k) => (
            <button
              key={k}
              role="tab"
              aria-selected={kind === k}
              className={kind === k ? "selected" : ""}
              onClick={() => {
                setKind(k);
                setStatus("");
              }}
            >
              {t(labels[k])}
            </button>
          ))}
        </div>
        {kind !== "issues" && (
          <select
            aria-label={t("status")}
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">{t("all")}</option>
            {(["pending", "approved", "rejected"] as const).map((s) => (
              <option key={s} value={s}>
                {t(s)}
              </option>
            ))}
          </select>
        )}
      </div>
      {can(user, permissions[kind]) && (
        <OperationForm
          key={kind}
          kind={kind}
          lang={lang}
          user={user}
          saved={() => setRevision((n) => n + 1)}
        />
      )}
      <section className="recent">
        <div className="section-heading">
          <h2>{t(labels[kind])}</h2>
          <button className="text-button" onClick={records.reload}>
            {t("refresh")}
          </button>
        </div>
        <TableViewport lang={lang} className="">
          <table>
            <thead>
              <tr>
                <th>{t("reference")}</th>
                <th>{t("material")}</th>
                <th>{t("quantity")}</th>
                <th>{t("operationDate")}</th>
                <th>{t("recipient")}</th>
                <th>{t("status")}</th>
                <th>{t("createdBy")}</th>
                <th>{t("actions")}</th>
              </tr>
            </thead>
            <tbody>
              {records.data.map((row) => (
                <tr key={row.id}>
                  <td>#{row.id}</td>
                  <td>{row.material.display_name}</td>
                  <td>{row.quantity}</td>
                  <td>
                    {row.issued_on ||
                      row.returned_on ||
                      row.created_at.slice(0, 10)}
                  </td>
                  <td>
                    {row.recipient_name || row.issue?.recipient_name || "—"}
                  </td>
                  <td>
                    <Status value={row.status} lang={lang} />
                    {!row.status && "—"}
                  </td>
                  <td>{row.created_by.name}</td>
                  <td>
                    {row.status === "pending" && can(user, approvalCode) && (
                      <div className="row-actions">
                        <button
                          className="text-button"
                          onClick={() =>
                            setDecision({ row, action: "approve" })
                          }
                        >
                          {t("approve")}
                        </button>
                        <button
                          className="text-button danger-text"
                          onClick={() => setDecision({ row, action: "reject" })}
                        >
                          {t("reject")}
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableViewport>
        <RecordsState
          {...records}
          empty={!records.data.length}
          more={records.next ? records.more : undefined}
          lang={lang}
        />
      </section>
      {decision && (
        <Decision
          kind={kind}
          {...decision}
          lang={lang}
          close={() => setDecision(null)}
          saved={() => {
            setDecision(null);
            setRevision((n) => n + 1);
          }}
        />
      )}
    </>
  );
}
function OperationForm({
  kind,
  lang,
  user,
  saved,
}: {
  kind: Kind;
  lang: Language;
  user: User;
  saved: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const stocks = useRecords<StockRow>("/api/v1/stock/", lang);
  const issues = useRecords<Operation>(
    kind === "returns" ? "/api/v1/issues/" : null,
    lang,
  );
  const [material, setMaterial] = useState("");
  const [issueId, setIssueId] = useState("");
  const [parts, setParts] = useState<StockBatch[]>([]);
  const [issueParts, setIssueParts] = useState<Allocation[]>([]);
  const [quantities, setQuantities] = useState<Record<number, string>>({});
  const [partError, setPartError] = useState<unknown>(null);
  const [partLoading, setPartLoading] = useState(false);
  const [notice, setNotice] = useState(false);
  const [reset, setReset] = useState(0);
  const operation = useIdempotentWrite<Operation>(kind, user.id, lang);
  const selectedIssue = issues.data.find((i) => String(i.id) === issueId);
  useEffect(() => {
    setQuantities({});
    setPartError(null);
    setParts([]);
    setIssueParts([]);
    if (kind === "returns") {
      setIssueParts(selectedIssue?.allocations || []);
      return;
    }
    if (!material) return;
    const controller = new AbortController();
    setPartLoading(true);
    allPages<StockBatch>(
      `/api/v1/stock/${material}/batches/`,
      lang,
      controller.signal,
    )
      .then((rows) => {
        if (!controller.signal.aborted) setParts(rows);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setPartError(err);
      })
      .finally(() => {
        if (!controller.signal.aborted) setPartLoading(false);
      });
    return () => controller.abort();
  }, [material, selectedIssue, kind, lang, reset]);
  const allocations =
    kind === "returns"
      ? issueParts.map((p) => ({
          id: p.batch_id,
          available: p.quantity,
          date: p.received_on,
          price: p.unit_price,
        }))
      : parts.map((p) => ({
          id: p.id,
          available: p.quantity_remaining,
          date: p.received_on,
          price: p.unit_price,
        }));
  const chosen = Object.entries(quantities).filter(([, qty]) =>
    new Decimal(qty || 0).gt(0),
  );
  const total = chosen.reduce((sum, [, qty]) => sum.plus(qty), new Decimal(0));
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    setNotice(false);
    const body =
      kind === "returns"
        ? {
            issue_id: Number(issueId),
            returned_on: form.get("date"),
            reason: form.get("reason"),
          }
        : {
            material_id: Number(material),
            ...(kind === "issues"
              ? {
                  issued_on: form.get("date"),
                  recipient_name: form.get("recipient"),
                  project_id: form.get("project")
                    ? Number(form.get("project"))
                    : null,
                  note: form.get("reason"),
                }
              : { reason: form.get("reason") }),
          };
    const result = await operation.submit({
      ...body,
      allocations: chosen.map(([batch_id, quantity]) => ({
        batch_id: Number(batch_id),
        quantity,
      })),
    });
    if (result) {
      setNotice(true);
      setQuantities({});
      setReset((n) => n + 1);
      stocks.reload();
      issues.reload();
      saved();
    }
  }
  return (
    <section className="workflow-panel">
      <h2>{t(labels[kind])}</h2>
      {notice && (
        <div className="notice success" role="status">
          {t(kind === "issues" ? "issued" : "requestSaved")}
        </div>
      )}
      <Feedback
        error={operation.error || partError || stocks.error || issues.error}
        lang={lang}
      />
      {operation.pending && !operation.busy && (
        <div className="notice" role="alert">
          {t("locked")}
        </div>
      )}
      <form onSubmit={submit} key={reset}>
        <fieldset disabled={operation.busy || Boolean(operation.pending)}>
          <div className="form-grid">
            {kind === "returns" ? (
              <Field label={t("originalIssue")} wide>
                <select
                  required
                  value={issueId}
                  onChange={(e) => setIssueId(e.target.value)}
                >
                  <option value="">{t("choose")}</option>
                  {issues.data.map((i) => (
                    <option key={i.id} value={i.id}>
                      #{i.id} · {i.material.display_name} · {i.recipient_name} ·{" "}
                      {i.quantity}
                    </option>
                  ))}
                </select>
                {issues.next && (
                  <button
                    type="button"
                    className="text-button"
                    onClick={issues.more}
                  >
                    {t("more")}
                  </button>
                )}
              </Field>
            ) : (
              <Field label={t("material")} wide>
                <select
                  required
                  value={material}
                  onChange={(e) => setMaterial(e.target.value)}
                >
                  <option value="">{t("choose")}</option>
                  {stocks.data.map((s) => (
                    <option key={s.material.id} value={s.material.id}>
                      {s.material.display_name} · {s.quantity_on_hand}
                    </option>
                  ))}
                </select>
                {stocks.next && (
                  <button
                    type="button"
                    className="text-button"
                    onClick={stocks.more}
                  >
                    {t("more")}
                  </button>
                )}
              </Field>
            )}
            {kind !== "write-offs" && (
              <Field label={t("operationDate")}>
                <input
                  type="date"
                  name="date"
                  required
                  max={localDate()}
                  defaultValue={localDate()}
                />
              </Field>
            )}
            {kind === "issues" && (
              <>
                <Field label={t("recipient")}>
                  <input name="recipient" required maxLength={200} />
                </Field>
                <Field label={t("projectId")}>
                  <input name="project" type="number" min="1" step="1" />
                </Field>
              </>
            )}
            <Field label={t("reason")} wide>
              <input
                name="reason"
                required={kind === "write-offs"}
                maxLength={500}
              />
            </Field>
          </div>
          <div className="allocation-section">
            <h3>{t("batchSelection")}</h3>
            <p className="form-hint">{t("manualBatches")}</p>
            {partLoading && <div role="status">{t("loading")}</div>}
            {!allocations.length && !partLoading && (material || issueId) && (
              <p className="empty">{t("noBatches")}</p>
            )}
            {allocations.length > 0 && (
              <TableViewport lang={lang} className="">
                <table>
                  <thead>
                    <tr>
                      <th>{t("batch")}</th>
                      <th>{t("operationDate")}</th>
                      <th>{t("quantity")}</th>
                      {can(user, "inventory.view_purchase_price") && (
                        <th>{t("unitPrice")}</th>
                      )}
                      <th>{t("selectedTotal")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allocations.map((p) => (
                      <tr key={p.id}>
                        <td>#{p.id}</td>
                        <td>{p.date}</td>
                        <td>{p.available}</td>
                        {can(user, "inventory.view_purchase_price") && (
                          <td>{p.price ? money(p.price, lang) : "—"}</td>
                        )}
                        <td>
                          <input
                            className="quantity-input"
                            aria-label={`${t("batch")} #${p.id}`}
                            type="number"
                            min="0"
                            max={p.available}
                            step="0.01"
                            value={quantities[p.id] || ""}
                            onChange={(e) =>
                              setQuantities((q) => ({
                                ...q,
                                [p.id]: e.target.value,
                              }))
                            }
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </TableViewport>
            )}
          </div>
        </fieldset>
        <div className="dialog-actions">
          <span>
            {t("selectedTotal")}: <strong>{total.toFixed(2)}</strong>
          </span>
          {operation.pending ? (
            <button
              type="button"
              className="primary"
              disabled={operation.busy}
              onClick={async () => {
                const result = await operation.submit(null);
                if (result) {
                  setNotice(true);
                  setReset((n) => n + 1);
                  saved();
                }
              }}
            >
              {t(operation.busy ? "saving" : "again")}
            </button>
          ) : (
            <button
              className="primary"
              disabled={operation.busy || !chosen.length || partLoading}
            >
              {t(operation.busy ? "saving" : "saveChanges")}
            </button>
          )}
        </div>
      </form>
    </section>
  );
}
function Decision({
  kind,
  row,
  action,
  lang,
  close,
  saved,
}: {
  kind: Kind;
  row: Operation;
  action: "approve" | "reject";
  lang: Language;
  close: () => void;
  saved: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await write(`/api/v1/${kind}/${row.id}/${action}/`, lang, {
        note: new FormData(e.currentTarget).get("note"),
      });
      saved();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal title={t("confirmDecision")} lang={lang} close={close} busy={busy}>
      <form onSubmit={submit}>
        <p className="form-hint">{t("confirmHint")}</p>
        <div className="inline-summary">
          <strong>{row.material.display_name}</strong>
          <span>{row.quantity}</span>
        </div>
        <p className="form-hint">{row.reason}</p>
        <Feedback error={error} lang={lang} />
        <Field label={t("decisionNote")}>
          <input name="note" maxLength={500} disabled={busy} />
        </Field>
        <div className="dialog-actions">
          <button
            type="button"
            className="secondary"
            disabled={busy}
            onClick={close}
          >
            {t("cancel")}
          </button>
          <button className="primary" disabled={busy}>
            {t(busy ? "saving" : action)}
          </button>
        </div>
      </form>
    </Modal>
  );
}
