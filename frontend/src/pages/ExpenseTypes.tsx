import { useState, type FormEvent } from "react";
import { can, write, type User, type ExpenseType } from "../api";
import { translate, type Language } from "../i18n";
import { useRecords } from "../hooks/useRecords";
import { Field, Feedback, Modal, RecordsState } from "../components/WorkflowUI";
type Type = ExpenseType & { name_uz: string; name_ru: string; name_en: string };
export function ExpenseTypes({
  lang,
  user,
  changed,
}: {
  lang: Language;
  user: User;
  changed: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const records = useRecords<Type>("/api/v1/expense-types/", lang);
  const [editor, setEditor] = useState<Type | "new" | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    const body = {
      code: data.get("code"),
      name_uz: data.get("name_uz"),
      name_ru: data.get("name_ru"),
      name_en: data.get("name_en"),
      is_active: data.has("is_active"),
    };
    setBusy(true);
    setError(null);
    try {
      await write(
        "/api/v1/expense-types/" +
          (editor && editor !== "new" ? editor.id + "/" : ""),
        lang,
        body,
        undefined,
        editor === "new" ? "POST" : "PATCH",
      );
      setEditor(null);
      records.reload();
      changed();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="workflow-panel">
      <div className="workflow-toolbar">
        <h2>{t("expenseTypes")}</h2>
        {can(user, "expenses.add_expensetype") && (
          <button
            className="secondary"
            onClick={() => {
              setError(null);
              setEditor("new");
            }}
          >
            {t("addExpenseType")}
          </button>
        )}
      </div>
      <div className="admin-records">
        {records.data.map((item) => (
          <article className="admin-record" key={item.id}>
            <div>
              <strong>{item.name}</strong>
              <p>{t(item.is_active ? "active" : "inactive")}</p>
            </div>
            {can(user, "expenses.change_expensetype") && (
              <button
                className="secondary"
                onClick={() => {
                  setError(null);
                  setEditor(item);
                }}
              >
                {t("edit")}
              </button>
            )}
          </article>
        ))}
      </div>
      <RecordsState
        {...records}
        empty={!records.data.length}
        more={records.next ? records.more : undefined}
        lang={lang}
      />
      {editor && (
        <Modal
          title={t(editor === "new" ? "addExpenseType" : "edit")}
          lang={lang}
          close={() => setEditor(null)}
          busy={busy}
        >
          <form onSubmit={submit}>
            <Feedback error={error} lang={lang} />
            <fieldset disabled={busy}>
              <div className="form-grid">
                <Field label={t("expenseCode")}>
                  <input
                    name="code"
                    required
                    pattern="[-a-zA-Z0-9_]+"
                    maxLength={50}
                    readOnly={editor !== "new"}
                    defaultValue={editor === "new" ? "" : editor.code}
                  />
                </Field>
                {(["uz", "ru", "en"] as const).map((code) => (
                  <Field
                    key={code}
                    label={t("name") + " · " + code.toUpperCase()}
                  >
                    <input
                      name={"name_" + code}
                      required={code === "uz"}
                      maxLength={100}
                      defaultValue={
                        editor === "new" ? "" : editor[`name_${code}`]
                      }
                    />
                  </Field>
                ))}
                <label className="filter-chip">
                  <input
                    name="is_active"
                    type="checkbox"
                    defaultChecked={editor === "new" || editor.is_active}
                  />
                  {t("active")}
                </label>
              </div>
            </fieldset>
            <div className="dialog-actions">
              <button className="primary" disabled={busy}>
                {t(busy ? "saving" : "saveChanges")}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </section>
  );
}
