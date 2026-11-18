import { useState, type FormEvent } from "react";
import { can, write, type StockRow, type StockBatch, type User } from "../api";
import { translate, type Language } from "../i18n";
import { money } from "../format";
import { useRecords } from "../hooks/useRecords";
import { Modal, Field, Feedback, RecordsState } from "../components/WorkflowUI";
export function StockDetail({
  row,
  user,
  lang,
  close,
  saved,
}: {
  row: StockRow;
  user: User;
  lang: Language;
  close: () => void;
  saved: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const records = useRecords<StockBatch>(
    `/api/v1/stock/${row.material.id}/batches/`,
    lang,
  );
  const [minimum, setMinimum] = useState(row.min_quantity ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await write(
        `/api/v1/stock/${row.material.id}/`,
        lang,
        { min_quantity: minimum || null },
        undefined,
        "PATCH",
      );
      saved();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal
      title={row.material.display_name}
      lang={lang}
      close={close}
      busy={busy}
    >
      <div className="inline-summary">
        <span>{t("stock")}</span>
        <strong>{row.quantity_on_hand}</strong>
      </div>
      {can(user, "inventory.change_min_quantity") && (
        <form onSubmit={submit} className="minimum-form">
          <Field label={t("minLimit")}>
            <input
              type="number"
              min="0"
              step="0.01"
              value={minimum}
              onChange={(e) => setMinimum(e.target.value)}
            />
          </Field>
          <button className="primary" disabled={busy}>
            {t("apply")}
          </button>
          <p>{t("minHint")}</p>
        </form>
      )}
      <Feedback error={error} lang={lang} />
      <h3>{t("batches")}</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{t("batch")}</th>
              <th>{t("operationDate")}</th>
              <th>{t("remainingBatch")}</th>
              {can(user, "inventory.view_purchase_price") && (
                <th>{t("unitPrice")}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {records.data.map((b) => (
              <tr key={b.id}>
                <td>#{b.id}</td>
                <td>{b.received_on}</td>
                <td>{b.quantity_remaining}</td>
                {can(user, "inventory.view_purchase_price") && (
                  <td>{b.unit_price ? money(b.unit_price, lang) : "—"}</td>
                )}
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
    </Modal>
  );
}
