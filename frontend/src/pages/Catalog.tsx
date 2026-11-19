import { EntryTable } from "../components/EntryTable";
import { TableViewport } from "../components/TableViewport";
import { useState, type FormEvent } from "react";
import { Plus, Pencil } from "lucide-react";
import { can, write, type User, type Material, type Category } from "../api";
import { translate, unitLabel, type Language } from "../i18n";
import { useRecords } from "../hooks/useRecords";
import { Field, Feedback, Modal, RecordsState } from "../components/WorkflowUI";

export function Catalog({ lang, user }: { lang: Language; user: User }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [search, setSearch] = useState("");
  const [active, setActive] = useState("true");
  const [category, setCategory] = useState("");
  const [editing, setEditing] = useState<Material | "new" | null>(null);
  const [revision, setRevision] = useState(0);
  const [categoryEdit, setCategoryEdit] = useState<Category | "new" | null>(
    null,
  );
  const [showCategories, setShowCategories] = useState(false);
  const records = useRecords<Material>(
    "/api/v1/materials/?" +
      new URLSearchParams({
        search,
        ...(active ? { is_active: active } : {}),
        ...(category ? { category } : {}),
      }),
    lang,
    revision,
  );
  const categories = useRecords<Category>(
    "/api/v1/categories/",
    lang,
    revision,
  );
  return (
    <>
      <div className="workflow-toolbar">
        <input
          data-search-field
          aria-keyshortcuts="/ Control+k Meta+k"
          aria-label={t("search")}
          placeholder={t("search")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          aria-label={t("category")}
          value={category}
          onChange={(e) => setCategory(e.target.value)}
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
        <select
          aria-label={t("status")}
          value={active}
          onChange={(e) => setActive(e.target.value)}
        >
          <option value="true">{t("active")}</option>
          <option value="false">{t("inactive")}</option>
          <option value="">{t("all")}</option>
        </select>
        {can(user, "catalog.add_material") && (
          <button className="primary" onClick={() => setEditing("new")}>
            <Plus size={17} />
            {t("newMaterial")}
          </button>
        )}
        <button
          className="secondary"
          onClick={() => setShowCategories((value) => !value)}
        >
          {t("categories")}
        </button>
      </div>
      {showCategories && (
        <section className="workflow-panel category-panel">
          <div className="section-heading">
            <h2>{t("categories")}</h2>
            {can(user, "catalog.add_category") && (
              <button
                className="text-button"
                onClick={() => setCategoryEdit("new")}
              >
                {t("newCategory")}
              </button>
            )}
          </div>
          <div className="category-list">
            {categories.data.map((c) => (
              <div key={c.id}>
                <span>
                  {c.name} · {t(c.is_active ? "active" : "inactive")}
                </span>
                {can(user, "catalog.change_category") && (
                  <button
                    className="text-button"
                    onClick={() => setCategoryEdit(c)}
                  >
                    {t("edit")}
                  </button>
                )}
              </div>
            ))}
          </div>
          <RecordsState
            {...categories}
            empty={!categories.data.length}
            emptyAction={
              can(user, "catalog.add_category") ? (
                <button
                  className="secondary"
                  onClick={() => setCategoryEdit("new")}
                >
                  {t("newCategory")}
                </button>
              ) : undefined
            }
            more={categories.next ? categories.more : undefined}
            lang={lang}
          />
        </section>
      )}
      <TableViewport lang={lang} className="">
        <table>
          <thead>
            <tr>
              <th>{t("material")}</th>
              <th>{t("category")}</th>
              <th>{t("unit")}</th>
              <th>{t("dimensions")}</th>
              <th>{t("status")}</th>
              <th>{t("actions")}</th>
            </tr>
          </thead>
          <tbody>
            {records.data.map((m) => (
              <tr key={m.id}>
                <td>{m.display_name}</td>
                <td>{m.category.name}</td>
                <td>{unitLabel(m.unit, lang)}</td>
                <td>
                  {m.length_cm || m.width_cm || m.thickness_cm
                    ? [m.length_cm, m.width_cm, m.thickness_cm]
                        .filter(Boolean)
                        .join(" × ") + " sm"
                    : "—"}
                </td>
                <td>{t(m.is_active ? "active" : "inactive")}</td>
                <td>
                  {can(user, "catalog.change_material") && (
                    <button
                      className="text-button"
                      onClick={() => setEditing(m)}
                    >
                      <Pencil size={15} />
                      {t("edit")}
                    </button>
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
        emptyAction={
          <>
            {(search || category || active) && (
              <button
                className="secondary"
                onClick={() => {
                  setSearch("");
                  setCategory("");
                  setActive("");
                }}
              >
                {t("resetFilters")}
              </button>
            )}
            {can(user, "catalog.add_material") && (
              <button className="primary" onClick={() => setEditing("new")}>
                {t("newMaterial")}
              </button>
            )}
          </>
        }
        more={records.next ? records.more : undefined}
        lang={lang}
      />
      {categoryEdit && (
        <CategoryForm
          category={categoryEdit === "new" ? undefined : categoryEdit}
          lang={lang}
          close={() => setCategoryEdit(null)}
          saved={() => {
            setCategoryEdit(null);
            setRevision((n) => n + 1);
          }}
        />
      )}
      {editing && (
        <MaterialForm
          key={typeof editing === "string" ? "new" : editing.id}
          material={editing === "new" ? undefined : editing}
          lang={lang}
          categories={categories.data}
          close={() => setEditing(null)}
          saved={() => {
            setEditing(null);
            setRevision((n) => n + 1);
          }}
        />
      )}
    </>
  );
}
function MaterialForm({
  material,
  lang,
  categories,
  close,
  saved,
}: {
  material?: Material;
  lang: Language;
  categories: Category[];
  close: () => void;
  saved: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    setBusy(true);
    setError(null);
    const dimensions = Object.fromEntries(
      ["length_cm", "width_cm", "thickness_cm"].map((key) => [
        key,
        data.get(key) || null,
      ]),
    );
    try {
      await write(
        `/api/v1/materials/${material ? material.id + "/" : ""}`,
        lang,
        {
          name: data.get("name"),
          category_id: Number(data.get("category_id")),
          color: data.get("color"),
          unit: data.get("unit"),
          is_active: data.get("is_active") === "on",
          ...dimensions,
        },
        undefined,
        material ? "PATCH" : "POST",
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
      title={t(material ? "edit" : "newMaterial")}
      lang={lang}
      close={close}
      busy={busy}
    >
      <form onSubmit={submit}>
        <Feedback error={error} lang={lang} />
        <fieldset disabled={busy}>
          <EntryTable lang={lang} className="catalog-entry-table">
            <Field label={t("name")} wide>
              <input
                name="name"
                required
                maxLength={200}
                defaultValue={material?.name}
              />
            </Field>
            <Field label={t("category")}>
              <select
                name="category_id"
                required
                defaultValue={material?.category.id || ""}
              >
                <option value="">{t("choose")}</option>
                {categories
                  .filter((c) => c.is_active || c.id === material?.category.id)
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
              </select>
            </Field>
            <Field label={t("unit")}>
              <select
                name="unit"
                defaultValue={material?.unit || "sheet"}
              >
                {["sheet", "piece", "kg", "liter", "meter", "m2"].map((u) => (
                  <option key={u} value={u}>
                    {unitLabel(u, lang)}
                  </option>
                ))}
              </select>
            </Field>
            <Field label={t("color")}>
              <input
                name="color"
                maxLength={50}
                defaultValue={material?.color}
              />
            </Field>
            {(["length", "width", "thickness"] as const).map((key) => (
              <Field key={key} label={t(key)}>
                <input
                  name={key + "_cm"}
                  type="number"
                  min="0.01"
                  step="0.01"
                  defaultValue={material?.[`${key}_cm`] || ""}
                />
              </Field>
            ))}
          </EntryTable>
          <label className="check-label">
            <input
              type="checkbox"
              name="is_active"
              defaultChecked={material?.is_active ?? true}
            />
            {t("active")}
          </label>
        </fieldset>
        <div className="dialog-actions">
          <button
            type="button"
            disabled={busy}
            className="secondary"
            onClick={close}
          >
            {t("cancel")}
          </button>
          <button className="primary" disabled={busy}>
            {t(busy ? "saving" : "saveChanges")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function CategoryForm({
  category,
  lang,
  close,
  saved,
}: {
  category?: Category;
  lang: Language;
  close: () => void;
  saved: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      await write(
        `/api/v1/categories/${category ? category.id + "/" : ""}`,
        lang,
        { name: data.get("name"), is_active: data.get("active") === "on" },
        undefined,
        category ? "PATCH" : "POST",
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
      title={t(category ? "edit" : "newCategory")}
      close={close}
      lang={lang}
      busy={busy}
    >
      <form onSubmit={submit}>
        <Feedback error={error} lang={lang} />
        <Field label={t("name")}>
          <input
            name="name"
            required
            maxLength={100}
            defaultValue={category?.name}
            disabled={busy}
          />
        </Field>
        <label className="check-label">
          <input
            type="checkbox"
            name="active"
            defaultChecked={category?.is_active ?? true}
            disabled={busy}
          />
          {t("active")}
        </label>
        <div className="dialog-actions">
          <button className="primary" disabled={busy}>
            {t(busy ? "saving" : "saveChanges")}
          </button>
        </div>
      </form>
    </Modal>
  );
}
