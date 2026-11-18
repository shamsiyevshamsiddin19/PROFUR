import { useState } from "react";
import { write } from "../api";
import { translate, type Language } from "../i18n";
import { useRecords } from "../hooks/useRecords";
import { Feedback, RecordsState } from "../components/WorkflowUI";
type Notification = {
  id: number;
  material: number;
  material_name: string;
  quantity: string;
  minimum: string;
  created_at: string;
  read_at: string | null;
};
export function Notifications({
  lang,
  onRead,
}: {
  lang: Language;
  onRead: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [unread, setUnread] = useState(false);
  const [revision, setRevision] = useState(0);
  const [busy, setBusy] = useState<number | null>(null);
  const [error, setError] = useState<unknown>(null);
  const records = useRecords<Notification>(
    "/api/v1/notifications/?unread=" + unread,
    lang,
    revision,
  );
  async function markRead(id: number) {
    setBusy(id);
    setError(null);
    try {
      await write(`/api/v1/notifications/${id}/read/`, lang, {});
      setRevision((n) => n + 1);
      onRead();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(null);
    }
  }
  return (
    <section className="workflow-panel">
      <div className="workflow-toolbar">
        <label className="filter-chip">
          <input
            type="checkbox"
            checked={unread}
            onChange={(e) => setUnread(e.target.checked)}
          />
          {t("unread")}
        </label>
        <button className="secondary" onClick={records.reload}>
          {t("refresh")}
        </button>
      </div>
      <Feedback error={error} lang={lang} />
      <div className="admin-records">
        {records.data.map((item) => (
          <article key={item.id} className="admin-record">
            <div>
              <strong>{item.material_name}</strong>
              <p>
                {t("lowStockMessage")}: {item.quantity} / {item.minimum}
              </p>
              <small>
                {new Date(item.created_at).toLocaleString(
                  lang === "uz" ? "uz-UZ" : lang === "ru" ? "ru-RU" : "en-US",
                  { timeZone: "Asia/Tashkent" },
                )}
              </small>
            </div>
            {!item.read_at && (
              <button
                className="secondary"
                disabled={busy !== null}
                onClick={() => markRead(item.id)}
              >
                {t("markRead")}
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
    </section>
  );
}
