import { useState } from "react";
import { write } from "../api";
import { TableViewport } from "../components/TableViewport";
import { Feedback, Field, Modal, RecordsState } from "../components/WorkflowUI";
import { useRecords } from "../hooks/useRecords";
import { translate, type Language } from "../i18n";

type Review = {
  id: number;
  kind: "issue" | "offcut_add" | "offcut_use" | "offcut_correction";
  state: "pending" | "reviewed" | "flagged";
  material: { display_name: string };
  issue: number | null;
  offcut: number | null;
  actor: { name: string };
  quantity: string;
  note: string;
  review_note: string;
  reviewed_at: string | null;
  reviewer: { name: string } | null;
  created_at: string;
  corrected: boolean;
};
const kinds = {
  issue: "tookStock",
  offcut_add: "addOffcut",
  offcut_use: "useOffcut",
  offcut_correction: "offcutCorrection",
} as const;

export function WarehouseReview({
  lang,
  onUpdate,
}: {
  lang: Language;
  onUpdate: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [pendingOnly, setPendingOnly] = useState(false);
  const [selection, setSelection] = useState<{
    row: Review;
    action: "reviewed" | "flagged" | "correct";
  } | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const records = useRecords<Review>(
    "/api/v1/warehouse-reviews/" + (pendingOnly ? "?pending=true" : ""),
    lang,
  );

  return (
    <>
      <div className="workflow-toolbar">
        <label className="check-label">
          <input
            type="checkbox"
            checked={pendingOnly}
            onChange={(e) => setPendingOnly(e.target.checked)}
          />
          {t("pending")}
        </label>
        <button className="secondary" onClick={records.reload}>
          {t("refresh")}
        </button>
      </div>
      <TableViewport lang={lang} className="">
        <table>
          <thead>
            <tr>
              {(
                [
                  "reference",
                  "operationDate",
                  "material",
                  "operationKind",
                  "quantity",
                  "createdBy",
                  "note",
                  "status",
                  "actions",
                ] as const
              ).map((key) => (
                <th key={key}>{t(key)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {records.data.map((row) => (
              <tr key={row.id}>
                <td>
                  #{row.id}
                  {row.issue && (
                    <>
                      {" "}
                      · {t("issue")} #{row.issue}
                    </>
                  )}
                  {row.offcut && (
                    <>
                      {" "}
                      · {t("offcutStock")} #{row.offcut}
                    </>
                  )}
                </td>
                <td>
                  {new Intl.DateTimeFormat(lang === "uz" ? "uz-UZ" : lang, {
                    dateStyle: "short",
                    timeStyle: "short",
                    timeZone: "Asia/Tashkent",
                  }).format(new Date(row.created_at))}
                </td>
                <td>{row.material.display_name}</td>
                <td>{t(kinds[row.kind])}</td>
                <td>{Number(row.quantity)}</td>
                <td>{row.actor.name}</td>
                <td className="wrap-cell">{row.note || "—"}</td>
                <td>
                  {t(row.state)}
                  {row.corrected && <> · {t("correctRecord")}</>}
                  {row.reviewer && (
                    <small className="review-detail">
                      {row.reviewer.name}
                      {row.review_note && " · " + row.review_note}
                    </small>
                  )}
                </td>
                <td>
                  <div className="row-actions">
                    {row.state === "pending" && (
                      <>
                        <button
                          className="text-button"
                          onClick={() => {
                            setError(null);
                            setSelection({ row, action: "reviewed" });
                          }}
                        >
                          {t("markReviewed")}
                        </button>
                        <button
                          className="text-button"
                          onClick={() => {
                            setError(null);
                            setSelection({ row, action: "flagged" });
                          }}
                        >
                          {t("markFlagged")}
                        </button>
                      </>
                    )}
                    {row.state === "flagged" && row.kind === "issue" && (
                      <a
                        className="text-button"
                        href={`#operations?return=${row.issue}`}
                      >
                        {t("return")}
                      </a>
                    )}
                    {row.state === "flagged" &&
                      row.offcut &&
                      !row.corrected && (
                        <button
                          className="text-button"
                          onClick={() => {
                            setError(null);
                            setSelection({ row, action: "correct" });
                          }}
                        >
                          {t("correctRecord")}
                        </button>
                      )}
                  </div>
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
      {selection && (
        <Modal
          lang={lang}
          title={t(
            selection.action === "correct"
              ? "correctRecord"
              : selection.action === "reviewed"
                ? "markReviewed"
                : "markFlagged",
          )}
          close={() => setSelection(null)}
          busy={busy}
        >
          <p>
            {selection.row.material.display_name} · #{selection.row.id}
          </p>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              const note = new FormData(e.currentTarget).get("note");
              setBusy(true);
              setError(null);
              try {
                const { action, row } = selection;
                await write(
                  `/api/v1/warehouse-reviews/${row.id}/${action === "correct" ? "correct" : "decide"}/`,
                  lang,
                  { state: action, note },
                );
                setSelection(null);
                records.reload();
                onUpdate();
              } catch (err) {
                setError(err);
              } finally {
                setBusy(false);
              }
            }}
          >
            <Feedback lang={lang} error={error} />
            <Field label={t("reason")}>
              <input
                name="note"
                required={selection.action !== "reviewed"}
                maxLength={500}
                disabled={busy}
              />
            </Field>
            <div className="dialog-actions">
              <button className="primary" disabled={busy}>
                {t("saveChanges")}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
