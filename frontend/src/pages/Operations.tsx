import { EntryTable } from "../components/EntryTable";
import { TableViewport } from "../components/TableViewport";
import { useEffect, useState, type FormEvent } from "react";
import Decimal from "decimal.js";
import {
  allPages,
  request,
  can,
  write,
  type User,
  type StockRow,
  type StockBatch,
  type Operation,
  type Allocation,
} from "../api";
import { translate, unitLabel, type Language } from "../i18n";
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

import {
  availableOperations,
  workerAccess,
  operationAccess,
  type OperationKind as Kind,
} from "../access";
const labels = {
  issues: "issue",
  returns: "return",
  "write-offs": "write_off",
} as const;
export function Operations({ lang, user }: { lang: Language; user: User }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const allowed = availableOperations(user);
  const names = workerAccess(user)
    ? { ...labels, issues: "tookStock" as const }
    : labels;
  const [selected, setKind] = useState<Kind | null>(() =>
    new URLSearchParams(location.hash.split("?")[1]).has("return")
      ? "returns"
      : null,
  );
  const kind = selected && allowed.includes(selected) ? selected : allowed[0];
  const [status, setStatus] = useState("");
  const [selection, setSelection] = useState<{ kind: Kind; id: string } | null>(
    null,
  );
  const [revision, setRevision] = useState(0);
  const [decision, setDecision] = useState<{
    row: Operation;
    kind: Kind;
    action: "approve" | "reject";
  } | null>(null);
  const records = useRecords<Operation>(
    kind
      ? `/api/v1/${kind}/` +
          (status && kind !== "issues" ? `?status=${status}` : "")
      : null,
    lang,
    revision,
  );
  if (!kind) return null;
  const approvalCode = operationAccess[kind].approve;
  const canApprove = approvalCode !== null && can(user, approvalCode);
  const pendingRows = records.data.filter((row) => row.status === "pending");
  const picked =
    selection?.kind === kind
      ? pendingRows.find((row) => String(row.id) === selection.id)
      : undefined;
  return (
    <>
      <div className="workflow-toolbar">
        <div className="tabs" role="tablist" aria-label={t("operations")}>
          {allowed.map((k) => (
            <button
              key={k}
              role="tab"
              aria-selected={kind === k}
              className={kind === k ? "selected" : ""}
              onClick={() => {
                setDecision(null);
                setSelection(null);
                setKind(k);
                setStatus("");
              }}
            >
              {t(names[k])}
            </button>
          ))}
        </div>
        {kind !== "issues" && (
          <select
            aria-label={t("status")}
            value={status}
            onChange={(e) => {
              setSelection(null);
              setStatus(e.target.value);
            }}
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
      {can(user, operationAccess[kind].create) && (
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
          <h2>{t(names[kind])}</h2>
          <button className="text-button" onClick={records.reload}>
            {t("refresh")}
          </button>
        </div>
        {canApprove && pendingRows.length > 0 && (
          <div
            className="mobile-decision-toolbar"
            role="group"
            aria-label={t("reviewRequests")}
          >
            <Field label={t("pendingReview")}>
              <select
                value={picked?.id ?? ""}
                onChange={(event) =>
                  setSelection({ kind, id: event.target.value })
                }
              >
                <option value="">{t("choose")}</option>
                {pendingRows.map((row) => (
                  <option key={row.id} value={row.id}>
                    #{row.id} · {row.material.display_name} · {row.quantity}{" "}
                    {unitLabel(row.material.unit, lang)}
                  </option>
                ))}
              </select>
            </Field>
            <button
              className="primary"
              disabled={!picked}
              onClick={() => {
                if (picked)
                  setDecision({ row: picked, kind, action: "approve" });
              }}
            >
              {t("approve")}
            </button>
            <button
              className="secondary danger-text"
              disabled={!picked}
              onClick={() => {
                if (picked)
                  setDecision({ row: picked, kind, action: "reject" });
              }}
            >
              {t("reject")}
            </button>
          </div>
        )}
        <TableViewport lang={lang} className="">
          <table>
            <thead>
              <tr>
                <th>{t("reference")}</th>
                <th>{t("material")}</th>
                <th>{t("quantity")}</th>
                <th>{t("operationDate")}</th>
                <th>{t("recipient")}</th>
                {kind === "issues" && <th>{t("projectId")}</th>}
                <th>{t("status")}</th>
                <th>{t("createdBy")}</th>
                {canApprove && (
                  <th className="decision-column">{t("actions")}</th>
                )}
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
                  {kind === "issues" && <td>{row.project_id ?? "—"}</td>}
                  <td>
                    <Status value={row.status} lang={lang} />
                    {!row.status && "—"}
                  </td>
                  <td>{row.created_by.name}</td>
                  {canApprove && (
                    <td className="decision-column">
                      {row.status === "pending" && (
                        <div className="row-actions">
                          <button
                            className="text-button"
                            onClick={() =>
                              setDecision({ row, kind, action: "approve" })
                            }
                          >
                            {t("approve")}
                          </button>
                          <button
                            className="text-button danger-text"
                            onClick={() =>
                              setDecision({ row, kind, action: "reject" })
                            }
                          >
                            {t("reject")}
                          </button>
                        </div>
                      )}
                    </td>
                  )}
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
      {decision?.kind === kind && canApprove && (
        <Decision
          {...decision}
          lang={lang}
          close={() => setDecision(null)}
          saved={() => {
            setSelection(null);
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
  const workerIssue = kind === "issues" && workerAccess(user);
  const stocks = useRecords<StockRow>(
    kind === "returns" ? null : "/api/v1/stock/",
    lang,
    0,
    true,
  );
  const issues = useRecords<Operation>(
    kind === "returns" ? "/api/v1/issues/" : null,
    lang,
    0,
    true,
  );
  const [workerQuantity, setWorkerQuantity] = useState("");
  const [material, setMaterial] = useState("");
  const [issueId, setIssueId] = useState(() =>
    kind === "returns"
      ? new URLSearchParams(location.hash.split("?")[1]).get("return") || ""
      : "",
  );
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
    if (workerIssue || (kind === "returns" ? !selectedIssue : !material)) {
      setPartLoading(false);
      return;
    }
    const controller = new AbortController();
    setPartLoading(true);
    const loaded =
      kind === "returns"
        ? request<{ allocations: Allocation[] }>(
            `/api/v1/issues/${selectedIssue!.id}/returnable/`,
            lang,
            { signal: controller.signal },
          ).then((response) => {
            if (!controller.signal.aborted) setIssueParts(response.allocations);
          })
        : allPages<StockBatch>(
            `/api/v1/stock/${material}/batches/`,
            lang,
            controller.signal,
          ).then((rows) => {
            if (!controller.signal.aborted) setParts(rows);
          });
    loaded
      .catch((err) => {
        if (!controller.signal.aborted) setPartError(err);
      })
      .finally(() => {
        if (!controller.signal.aborted) setPartLoading(false);
      });
    return () => controller.abort();
  }, [material, selectedIssue, kind, lang, reset, workerIssue]);
  const allocations =
    kind === "returns"
      ? issueParts.map((p) => ({
          id: p.batch_id,
          available: p.returnable_quantity ?? "0",
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
    const result = await operation.submit(
      workerIssue
        ? {
            material_id: Number(material),
            quantity: workerQuantity,
            project_id: Number(form.get("project")),
            note: form.get("reason"),
          }
        : {
            ...body,
            allocations: chosen.map(([batch_id, quantity]) => ({
              batch_id: Number(batch_id),
              quantity,
            })),
          },
    );
    if (result) {
      setNotice(true);
      setWorkerQuantity("");
      setQuantities({});
      setReset((n) => n + 1);
      stocks.reload();
      issues.reload();
      saved();
    }
  }
  return (
    <section className="workflow-panel">
      <h2>{t(workerIssue ? "tookStock" : labels[kind])}</h2>
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
          <EntryTable lang={lang} className="operation-entry-table">
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
                  {stocks.data
                    .filter((s) => Number(s.quantity_on_hand) > 0)
                    .map((s) => (
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
            {kind !== "write-offs" && !workerIssue && (
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
                {workerIssue ? (
                  <Field label={t("quantity")}>
                    <input
                      type="number"
                      required
                      min="0.01"
                      step="0.01"
                      value={workerQuantity}
                      onChange={(event) =>
                        setWorkerQuantity(event.target.value)
                      }
                    />
                  </Field>
                ) : (
                  <Field label={t("recipient")}>
                    <input name="recipient" required maxLength={200} />
                  </Field>
                )}
                <Field label={t("projectId")}>
                  <input
                    name="project"
                    type="number"
                    min="1"
                    step="1"
                    required={workerIssue}
                  />
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
          </EntryTable>
          {!workerIssue && (
            <div className="allocation-section">
              <h3>{t("batchSelection")}</h3>
              <p className="form-hint">
                {t(kind === "returns" ? "returnBatches" : "manualBatches")}
              </p>
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
          )}
        </fieldset>
        <div className="dialog-actions">
          {!workerIssue && (
            <span>
              {t("selectedTotal")}: <strong>{total.toFixed(2)}</strong>
            </span>
          )}
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
              disabled={
                operation.busy ||
                partLoading ||
                (workerIssue
                  ? !material || !Number(workerQuantity)
                  : !chosen.length)
              }
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
