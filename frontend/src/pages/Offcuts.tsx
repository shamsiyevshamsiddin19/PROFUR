import { useState, type FormEvent } from "react";
import { can, type Operation, type User } from "../api";
import { EntryTable } from "../components/EntryTable";
import { TableViewport } from "../components/TableViewport";
import { Feedback, Field, Modal, RecordsState } from "../components/WorkflowUI";
import { useIdempotentWrite } from "../hooks/useIdempotentWrite";
import { useRecords } from "../hooks/useRecords";
import { translate, type Language } from "../i18n";

type CutPiece = {
  id: number;
  material_name: string;
  length_mm: string;
  width_mm: string | null;
  quantity: string;
  source_issue: number | null;
  registered_by_name: string;
  note: string;
};

export function Offcuts({ user, lang }: { user: User; lang: Language }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const canAdd =
    can(user, "inventory.add_offcut") && can(user, "inventory.view_stock");
  const [search, setSearch] = useState("");
  const [revision, setRevision] = useState(0);
  const [source, setSource] = useState("");
  const [taking, setTaking] = useState<CutPiece | null>(null);
  const [saved, setSaved] = useState(false);
  const records = useRecords<CutPiece>(
    "/api/v1/offcuts/?" + new URLSearchParams({ search }),
    lang,
    revision,
  );
  const issues = useRecords<Operation>(
    canAdd ? "/api/v1/issues/" : null,
    lang,
    0,
    true,
  );
  const options = issues.data.filter((row) =>
    ["sheet", "meter"].includes(row.material.unit),
  );
  const picked = options.find((row) => String(row.id) === source);
  const create = useIdempotentWrite<CutPiece>("offcuts", user.id, lang);
  function refresh() {
    setRevision((value) => value + 1);
    setSaved(true);
  }
  async function save(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    if (
      await create.submit({
        issue_id: Number(source),
        length_mm: data.get("length_mm"),
        width_mm: data.get("width_mm") || null,
        quantity: Number(data.get("quantity")),
        note: data.get("note"),
      })
    ) {
      setSource("");
      refresh();
    }
  }
  return (
    <>
      {saved && (
        <p className="notice success" role="status">
          {t("savedChanges")}
        </p>
      )}
      {canAdd && (
        <form onSubmit={save} key={revision}>
          <h2>{t("addOffcut")}</h2>
          <Feedback lang={lang} error={create.error || issues.error} />
          {!issues.loading && !issues.error && !options.length && (
            <p>{t("noEligibleIssue")}</p>
          )}
          <fieldset
            disabled={create.busy || Boolean(create.pending) || !options.length}
          >
            <EntryTable lang={lang}>
              <Field label={t("originalIssue")}>
                <select
                  required
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                >
                  <option value="">{t("choose")}</option>
                  {options.map((issue) => (
                    <option key={issue.id} value={issue.id}>
                      #{issue.id} · {issue.material.display_name} ·{" "}
                      {issue.issued_on}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label={t("offcutLengthMm")}>
                <input
                  name="length_mm"
                  type="number"
                  min="0.01"
                  step="0.01"
                  required
                />
              </Field>
              {picked?.material.unit !== "meter" && (
                <Field label={t("offcutWidthMm")}>
                  <input
                    name="width_mm"
                    type="number"
                    min="0.01"
                    step="0.01"
                    required
                  />
                </Field>
              )}
              <Field label={t("quantity")}>
                <input
                  name="quantity"
                  type="number"
                  min="1"
                  step="1"
                  defaultValue="1"
                  required
                />
              </Field>
              <Field label={t("note")}>
                <input name="note" maxLength={500} />
              </Field>
            </EntryTable>
          </fieldset>
          <div className="dialog-actions">
            {create.pending ? (
              <button
                className="primary"
                type="button"
                disabled={create.busy}
                onClick={async () => {
                  if (await create.submit(null)) {
                    setSource("");
                    refresh();
                  }
                }}
              >
                {t("again")}
              </button>
            ) : (
              <button className="primary" disabled={create.busy || !picked}>
                {t("saveChanges")}
              </button>
            )}
          </div>
        </form>
      )}
      <section className="recent">
        <div className="workflow-toolbar">
          <input
            data-search-field
            aria-label={t("search")}
            placeholder={t("search")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
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
                    "material",
                    "dimensions",
                    "quantity",
                    "originalIssue",
                    "createdBy",
                    "note",
                  ] as const
                ).map((key) => (
                  <th key={key}>{t(key)}</th>
                ))}
                {can(user, "inventory.use_offcut") && <th>{t("actions")}</th>}
              </tr>
            </thead>
            <tbody>
              {records.data.map((row) => (
                <tr key={row.id}>
                  <td>{row.material_name}</td>
                  <td>
                    {row.length_mm}
                    {row.width_mm && " × " + row.width_mm} mm
                  </td>
                  <td>{Number(row.quantity)}</td>
                  <td>{row.source_issue ? "#" + row.source_issue : "—"}</td>
                  <td>{row.registered_by_name}</td>
                  <td className="wrap-cell">{row.note || "—"}</td>
                  {can(user, "inventory.use_offcut") && (
                    <td>
                      <button
                        className="text-button"
                        onClick={() => setTaking(row)}
                      >
                        {t("useOffcut")}
                      </button>
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
      {taking && can(user, "inventory.use_offcut") && (
        <TakePiece
          row={taking}
          user={user}
          lang={lang}
          close={() => setTaking(null)}
          done={() => {
            setTaking(null);
            refresh();
          }}
        />
      )}
    </>
  );
}

function TakePiece({
  row,
  user,
  lang,
  close,
  done,
}: {
  row: CutPiece;
  user: User;
  lang: Language;
  close: () => void;
  done: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const action = useIdempotentWrite<CutPiece>(
    `offcuts/${row.id}/withdraw`,
    user.id,
    lang,
  );
  return (
    <Modal lang={lang} title={t("useOffcut")} close={close} busy={action.busy}>
      <p>
        {row.material_name} · #{row.id}
      </p>
      <Feedback lang={lang} error={action.error} />
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          const data = new FormData(e.currentTarget);
          if (
            await action.submit({
              quantity: Number(data.get("quantity")),
              reason: data.get("note"),
            })
          )
            done();
        }}
      >
        <fieldset disabled={action.busy || Boolean(action.pending)}>
          <Field label={t("quantity")}>
            <input
              name="quantity"
              type="number"
              min="1"
              max={Number(row.quantity)}
              step="1"
              defaultValue="1"
              required
            />
          </Field>
          <Field label={t("note")}>
            <input name="note" maxLength={500} />
          </Field>
        </fieldset>
        <div className="dialog-actions">
          <button
            className="secondary"
            type="button"
            disabled={action.busy}
            onClick={close}
          >
            {t("cancel")}
          </button>
          {action.pending ? (
            <button
              type="button"
              className="primary"
              disabled={action.busy}
              onClick={async () => {
                if (await action.submit(null)) done();
              }}
            >
              {t("again")}
            </button>
          ) : (
            <button className="primary" disabled={action.busy}>
              {t("useOffcut")}
            </button>
          )}
        </div>
      </form>
    </Modal>
  );
}
