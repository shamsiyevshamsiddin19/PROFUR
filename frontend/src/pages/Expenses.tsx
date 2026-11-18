import { useState, type FormEvent } from "react";
import { can, type Expense, type ExpenseType, type User } from "../api";
import { translate, type Language } from "../i18n";
import { localDate, money } from "../format";
import { useIdempotentWrite } from "../hooks/useIdempotentWrite";
import { useRecords } from "../hooks/useRecords";
import { Field, Feedback, Modal, RecordsState } from "../components/WorkflowUI";
export function Expenses({ lang, user }: { lang: Language; user: User }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [filters, setFilters] = useState({
    project_id: "",
    expense_type: "",
    date_from: "",
    date_to: "",
  });
  const [revision, setRevision] = useState(0);
  const query = new URLSearchParams(
    Object.entries(filters).filter(([, v]) => v),
  );
  const records = useRecords<Expense>(
    "/api/v1/expenses/?" + query,
    lang,
    revision,
  );
  const types = useRecords<ExpenseType>("/api/v1/expense-types/", lang);
  const operation = useIdempotentWrite<Expense>("expenses", user.id, lang);
  const { busy, error, pending } = operation;
  const [success, setSuccess] = useState(false);
  const [reverse, setReverse] = useState<Expense | null>(null);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    setSuccess(false);
    const result = await operation.submit(expenseBody(new FormData(form)));
    if (result) {
      form.reset();
      setSuccess(true);
      setRevision((n) => n + 1);
    }
  }
  return (
    <>
      <Feedback error={error || types.error} lang={lang} />
      {success && (
        <div className="notice success" role="status">
          {t("savedChanges")}
        </div>
      )}
      {pending && !busy && (
        <div className="notice" role="alert">
          {t("locked")}
        </div>
      )}
      {can(user, "expenses.add_expense") && (
        <section className="workflow-panel">
          <h2>{t("expenses")}</h2>
          <form onSubmit={submit}>
            <fieldset disabled={busy || Boolean(pending)}>
              <ExpenseFields types={types.data} lang={lang} />
            </fieldset>
            <div className="dialog-actions">
              <span>USD</span>
              {pending ? (
                <button
                  type="button"
                  disabled={busy}
                  className="primary"
                  onClick={async () => {
                    if (await operation.submit(null)) {
                      setSuccess(true);
                      setRevision((n) => n + 1);
                    }
                  }}
                >
                  {t(busy ? "saving" : "again")}
                </button>
              ) : (
                <button
                  disabled={busy || !types.data.length}
                  className="primary"
                >
                  {t(busy ? "saving" : "saveChanges")}
                </button>
              )}
            </div>
          </form>
        </section>
      )}
      <div className="workflow-toolbar recent">
        <select
          aria-label={t("expenseType")}
          value={filters.expense_type}
          onChange={(e) =>
            setFilters((f) => ({ ...f, expense_type: e.target.value }))
          }
        >
          <option value="">
            {t("expenseType")}: {t("all")}
          </option>
          {types.data.map((type) => (
            <option key={type.code} value={type.code}>
              {type.name}
            </option>
          ))}
        </select>
        <input
          aria-label={t("projectId")}
          placeholder={t("projectId")}
          type="number"
          min="1"
          value={filters.project_id}
          onChange={(e) =>
            setFilters((f) => ({ ...f, project_id: e.target.value }))
          }
        />
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
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{t("reference")}</th>
              <th>{t("expenseType")}</th>
              <th>{t("spentOn")}</th>
              <th>{t("projectId")}</th>
              <th>{t("amount")}</th>
              <th>{t("note")}</th>
              <th>{t("status")}</th>
              <th>{t("actions")}</th>
            </tr>
          </thead>
          <tbody>
            {records.data.map((row) => (
              <tr key={row.id}>
                <td>#{row.id}</td>
                <td>{row.expense_type_name}</td>
                <td>{row.spent_on}</td>
                <td>{row.project_id ?? "—"}</td>
                <td>{money(row.amount, lang)}</td>
                <td className="wrap-cell">{row.note || "—"}</td>
                <td>
                  {row.reverses
                    ? t("reversal")
                    : row.reversal
                      ? t("reversed")
                      : "—"}
                </td>
                <td>
                  {!row.reversal &&
                    !row.reverses &&
                    can(user, "expenses.reverse_expense") && (
                      <button
                        className="text-button danger-text"
                        onClick={() => setReverse(row)}
                      >
                        {t("reverse")}
                      </button>
                    )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <RecordsState
        {...records}
        empty={!records.data.length}
        more={records.next ? records.more : undefined}
        lang={lang}
      />
      {types.next && (
        <button className="text-button" onClick={types.more}>
          {t("more")} · {t("expenseType")}
        </button>
      )}
      {reverse && (
        <ReverseExpense
          row={reverse}
          userId={user.id}
          lang={lang}
          types={types.data}
          close={() => setReverse(null)}
          saved={() => {
            setReverse(null);
            setRevision((n) => n + 1);
          }}
        />
      )}
    </>
  );
}
function expenseBody(data: FormData) {
  return {
    expense_type: data.get("expense_type"),
    amount: data.get("amount"),
    spent_on: data.get("spent_on"),
    project_id: Number(data.get("project_id")),
    note: data.get("note"),
    currency: "USD",
  };
}
function ExpenseFields({
  types,
  lang,
  row,
}: {
  types: ExpenseType[];
  lang: Language;
  row?: Expense;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  return (
    <div className="form-grid">
      <Field label={t("expenseType")}>
        <select
          name="expense_type"
          required
          defaultValue={row?.expense_type || ""}
        >
          <option value="">{t("choose")}</option>
          {types
            .filter((type) => type.is_active)
            .map((type) => (
              <option key={type.code} value={type.code}>
                {type.name}
              </option>
            ))}
        </select>
      </Field>
      <Field label={t("amount") + " · USD"}>
        <input
          name="amount"
          type="number"
          required
          min="0.01"
          step="0.01"
          defaultValue={row?.amount}
        />
      </Field>
      <Field label={t("spentOn")}>
        <input
          name="spent_on"
          type="date"
          required
          defaultValue={row?.spent_on || localDate()}
        />
      </Field>
      <Field label={t("projectId")}>
        <input
          name="project_id"
          type="number"
          required
          min="1"
          step="1"
          defaultValue={row?.project_id || ""}
        />
      </Field>
      <Field label={t("note")} wide>
        <input name="note" defaultValue={row?.note} />
      </Field>
    </div>
  );
}
function ReverseExpense({
  row,
  userId,
  lang,
  types,
  close,
  saved,
}: {
  row: Expense;
  userId: number;
  lang: Language;
  types: ExpenseType[];
  close: () => void;
  saved: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [correction, setCorrection] = useState(false);
  const operation = useIdempotentWrite<{ reversal: Expense }>(
    `expenses/${row.id}/reverse`,
    userId,
    lang,
  );
  const { busy, error, pending } = operation;
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    if (
      await operation.submit({
        reason: data.get("reason"),
        ...(correction ? { replacement: expenseBody(data) } : {}),
      })
    )
      saved();
  }
  return (
    <Modal title={t("reverse")} lang={lang} close={close} busy={busy}>
      <p className="form-hint">{t("reverseHint")}</p>
      <div className="inline-summary">
        <strong>
          #{row.id} · {row.expense_type_name}
        </strong>
        <span>{money(row.amount, lang)}</span>
      </div>
      <form onSubmit={submit}>
        <Feedback error={error} lang={lang} />
        {pending && !busy && (
          <div className="notice" role="alert">
            {t("locked")}
          </div>
        )}
        <fieldset disabled={busy || Boolean(pending)}>
          <Field label={t("reason")}>
            <input name="reason" required maxLength={1000} />
          </Field>
          <label className="check-label">
            <input
              type="checkbox"
              checked={correction}
              onChange={(e) => setCorrection(e.target.checked)}
            />
            {t("correction")}
          </label>
          {correction && <ExpenseFields lang={lang} types={types} row={row} />}
        </fieldset>
        <div className="dialog-actions">
          <button
            type="button"
            disabled={busy}
            onClick={close}
            className="secondary"
          >
            {t("cancel")}
          </button>
          {pending ? (
            <button
              type="button"
              disabled={busy}
              className="primary"
              onClick={async () => {
                if (await operation.submit(null)) saved();
              }}
            >
              {t(busy ? "saving" : "again")}
            </button>
          ) : (
            <button disabled={busy} className="primary">
              {t(busy ? "saving" : "reverse")}
            </button>
          )}
        </div>
      </form>
    </Modal>
  );
}
