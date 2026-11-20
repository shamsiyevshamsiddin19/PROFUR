import { useState, type FormEvent } from "react";
import {
  Pencil,
  KeyRound,
  Plus,
  UserPlus,
  Search,
  Shield,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { type User, write } from "../api";
import { translate, type Language, type MessageKey } from "../i18n";
import { useRecords } from "../hooks/useRecords";
import { Field, Feedback, Modal, RecordsState } from "../components/WorkflowUI";
import { TableViewport } from "../components/TableViewport";

import { PendingAccounts } from "./PendingAccounts";

type Role = {
  id: number;
  code: string;
  name: string;
  description: string;
  permissions: string[];
  is_system: boolean;
};
type Account = Omit<User, "roles"> & {
  email: string;
  phone: string;
  is_active: boolean;
  roles: Role[];
};
const permissions: [string, MessageKey][] = [
  ["*", "fullAccess"],
  ["catalog.view_material", "materials"],
  ["catalog.add_material", "newMaterial"],
  ["catalog.change_material", "edit"],
  ["catalog.add_category", "newCategory"],
  ["catalog.change_category", "categories"],
  ["inventory.view_stock", "stock"],
  ["inventory.view_purchase_price", "unitPrice"],
  ["inventory.add_receipt", "newReceipt"],
  ["inventory.add_issue", "issue"],
  ["inventory.worker", "workerMode"],
  ["inventory.view_offcut", "offcutStock"],
  ["inventory.add_offcut", "addOffcut"],
  ["inventory.use_offcut", "useOffcut"],
  ["inventory.view_report", "monthlyReport"],
  ["inventory.add_return", "return"],
  ["inventory.approve_return", "approve"],
  ["inventory.add_write_off", "write_off"],
  ["inventory.approve_write_off", "confirmDecision"],
  ["inventory.change_min_quantity", "minLimit"],
  ["expenses.view_expense", "expenses"],
  ["expenses.add_expense", "saveChanges"],
  ["expenses.reverse_expense", "reverse"],
  ["expenses.view_expensetype", "expenseType"],
  ["expenses.add_expensetype", "newCategory"],
  ["expenses.change_expensetype", "edit"],
];
export function Administration({
  lang,
  user,
  onSelfChange,
  onOwnPasswordReset,
}: {
  lang: Language;
  user: User;
  onSelfChange: () => Promise<void>;
  onOwnPasswordReset: () => void;
}) {
  const t = (key: MessageKey) => translate(lang, key);
  const [revision, setRevision] = useState(0);
  const [search, setSearch] = useState("");
  const [active, setActive] = useState("");
  const accounts = useRecords<Account>(
    "/api/auth/users/?" + new URLSearchParams({ search, is_active: active }),
    lang,
    revision,
  );
  const roles = useRecords<Role>("/api/auth/roles/", lang, revision, true);
  const [editor, setEditor] = useState<
    | { kind: "user"; value?: Account }
    | { kind: "role"; value?: Role }
    | { kind: "password"; value: Account }
    | null
  >(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [saved, setSaved] = useState(false);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!editor) return;
    const data = new FormData(e.currentTarget);
    const value = editor.value;
    let path = editor.kind === "role" ? "/api/auth/roles/" : "/api/auth/users/";
    let body: Record<string, unknown>;
    if (editor.kind === "password") {
      path += value!.id + "/reset-password/";
      body = { new_password: data.get("new_password") };
    } else if (editor.kind === "role") {
      body = {
        name: data.get("name"),
        code: data.get("code"),
        description: data.get("description"),
        permissions: data.getAll("permissions"),
      };
      if (value) path += value.id + "/";
    } else {
      body = {
        username: data.get("username"),
        first_name: data.get("first_name"),
        last_name: data.get("last_name"),
        email: data.get("email"),
        phone: data.get("phone"),
        is_active: data.has("is_active"),
        role_ids: [
          ...data.getAll("role_ids").map(Number),
          ...(editor.value?.roles
            .filter((r) => !roles.data.some((loaded) => loaded.id === r.id))
            .map((r) => r.id) || []),
        ],
      };
      if (value) path += value.id + "/";
      else body.password = data.get("password");
    }
    setBusy(true);
    setError(null);
    setSaved(false);
    try {
      await write(
        path,
        lang,
        body,
        undefined,
        value && editor.kind !== "password" ? "PATCH" : "POST",
      );
      if (editor.kind === "password" && value?.id === user.id) {
        onOwnPasswordReset();
        return;
      }
      if (
        editor.kind === "role" ||
        (editor.kind === "user" && value?.id === user.id)
      )
        await onSelfChange();
      setEditor(null);
      setRevision((n) => n + 1);
      setSaved(true);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="admin-page-container">
      <PendingAccounts
        roles={roles.data}
        lang={lang}
        onUpdate={() => setRevision((n) => n + 1)}
      />
      {saved && (
        <div className="notice success" role="status">
          {t("savedChanges")}
        </div>
      )}
      <section className="admin-section">
        <div className="admin-toolbar">
          <div className="admin-toolbar-start">
            <h2>{t("users")}</h2>
            <span className="count-pill">{accounts.data.length}</span>
          </div>
          <div className="admin-toolbar-end">
            <div className="admin-search-box">
              <Search
                size={15}
                className="admin-search-icon"
                aria-hidden="true"
              />
              <input
                data-search-field
                aria-keyshortcuts="/ Control+k Meta+k"
                aria-label={t("searchUsers")}
                placeholder={t("searchUsers")}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <select
              aria-label={t("status")}
              value={active}
              onChange={(e) => setActive(e.target.value)}
              className="admin-filter-select"
            >
              <option value="">{t("all")}</option>
              <option value="true">{t("active")}</option>
              <option value="false">{t("inactive")}</option>
            </select>
            <button
              type="button"
              className="primary admin-create-btn"
              onClick={() => {
                setError(null);
                setEditor({ kind: "user" });
              }}
            >
              <UserPlus size={15} aria-hidden="true" />
              <span>{t("newUser")}</span>
            </button>
          </div>
        </div>
        {accounts.data.length > 0 && (
          <TableViewport lang={lang} className="admin-table-viewport">
            <table className="admin-table">
              <thead>
                <tr>
                  <th style={{ width: "26%" }}>{t("fullName")}</th>
                  <th style={{ width: "16%" }}>{t("userLogin")}</th>
                  <th style={{ width: "22%" }}>{t("role")}</th>
                  <th style={{ width: "12%" }}>{t("status")}</th>
                  <th className="cell-actions" style={{ width: "24%" }}>
                    {t("actions")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {accounts.data.map((account) => (
                  <tr key={account.id}>
                    <td>
                      <div className="user-name-cell">
                        <strong>
                          {[account.first_name, account.last_name]
                            .filter(Boolean)
                            .join(" ") || account.username}
                        </strong>
                        {(account.email || account.phone) && (
                          <span className="cell-subtext">
                            {[account.email, account.phone]
                              .filter(Boolean)
                              .join(" · ")}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <code>{account.username}</code>
                    </td>
                    <td>
                      {account.roles.length > 0 ? (
                        <span className="role-tags">
                          {account.roles.map((role) => (
                            <span key={role.id} className="role-tag">
                              <Shield size={12} aria-hidden="true" />
                              {role.name}
                            </span>
                          ))}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td>
                      <span
                        className={`status-pill ${account.is_active ? "active" : "inactive"}`}
                      >
                        {account.is_active ? (
                          <CheckCircle2 size={12} aria-hidden="true" />
                        ) : (
                          <XCircle size={12} aria-hidden="true" />
                        )}
                        <span>
                          {t(account.is_active ? "active" : "inactive")}
                        </span>
                      </span>
                    </td>
                    <td className="cell-actions">
                      <div className="admin-actions">
                        <button
                          type="button"
                          className="admin-action-btn edit-btn"
                          onClick={() => {
                            setError(null);
                            setEditor({ kind: "user", value: account });
                          }}
                          title={t("edit")}
                        >
                          <Pencil size={13} aria-hidden="true" />
                          <span>{t("edit")}</span>
                        </button>
                        <button
                          type="button"
                          className="admin-action-btn password-btn"
                          onClick={() => {
                            setError(null);
                            setEditor({ kind: "password", value: account });
                          }}
                          title={t("resetPassword")}
                        >
                          <KeyRound size={13} aria-hidden="true" />
                          <span>{t("resetPassword")}</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableViewport>
        )}
        <RecordsState
          {...accounts}
          empty={!accounts.data.length}
          more={accounts.next ? accounts.more : undefined}
          lang={lang}
        />
      </section>

      <section className="admin-section roles-section">
        <div className="admin-toolbar">
          <div className="admin-toolbar-start">
            <h2>{t("roles")}</h2>
            <span className="count-pill">{roles.data.length}</span>
          </div>
          <div className="admin-toolbar-end">
            <button
              type="button"
              className="primary admin-create-btn"
              onClick={() => {
                setError(null);
                setEditor({ kind: "role" });
              }}
            >
              <Plus size={15} aria-hidden="true" />
              <span>{t("newRole")}</span>
            </button>
          </div>
        </div>
        {roles.data.length > 0 && (
          <TableViewport lang={lang} className="admin-table-viewport">
            <table className="admin-table">
              <thead>
                <tr>
                  <th style={{ width: "28%" }}>{t("roleName")}</th>
                  <th style={{ width: "18%" }}>{t("roleCode")}</th>
                  <th style={{ width: "38%" }}>{t("permissions")}</th>
                  <th className="cell-actions" style={{ width: "16%" }}>
                    {t("actions")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {roles.data.map((role) => (
                  <tr key={role.id}>
                    <td>
                      <div className="role-name-cell">
                        <strong>{role.name}</strong>
                        {role.description && (
                          <span className="cell-subtext">
                            {role.description}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <code>{role.code}</code>
                    </td>
                    <td>
                      <span className="permissions-badge">
                        {role.permissions?.includes("*")
                          ? t("fullAccess")
                          : `${role.permissions?.length || 0} ${t("permissions").toLowerCase()}`}
                      </span>
                    </td>
                    <td className="cell-actions">
                      <div className="admin-actions">
                        <button
                          type="button"
                          className="admin-action-btn edit-btn"
                          onClick={() => {
                            setError(null);
                            setEditor({ kind: "role", value: role });
                          }}
                          title={t("edit")}
                        >
                          <Pencil size={13} aria-hidden="true" />
                          <span>{t("edit")}</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </TableViewport>
        )}
        <RecordsState
          {...roles}
          empty={!roles.data.length}
          more={roles.next ? roles.more : undefined}
          lang={lang}
        />
      </section>
      {editor && (
        <Modal
          title={t(
            editor.kind === "password"
              ? "resetPassword"
              : editor.kind === "role"
                ? editor.value
                  ? "edit"
                  : "newRole"
                : editor.value
                  ? "edit"
                  : "newUser",
          )}
          close={() => setEditor(null)}
          busy={busy}
          lang={lang}
        >
          <form onSubmit={submit}>
            <Feedback error={error} lang={lang} />
            <fieldset disabled={busy}>
              <div className="form-grid">
                {editor.kind === "password" ? (
                  <Field label={t("newPassword")} wide>
                    <input
                      name="new_password"
                      type="password"
                      autoComplete="new-password"
                      minLength={8}
                      required
                    />
                  </Field>
                ) : editor.kind === "role" ? (
                  <>
                    <Field label={t("roleCode")}>
                      <input
                        name="code"
                        required
                        maxLength={50}
                        defaultValue={editor.value?.code}
                        readOnly={
                          !!editor.value?.is_system ||
                          editor.value?.code === "ADMIN"
                        }
                      />
                    </Field>
                    <Field label={t("name")}>
                      <input
                        name="name"
                        required
                        maxLength={100}
                        defaultValue={editor.value?.name}
                      />
                    </Field>
                    <Field label={t("note")} wide>
                      <textarea
                        name="description"
                        defaultValue={editor.value?.description}
                      />
                    </Field>
                    <div className="wide">
                      <p>{t("adminWarning")}</p>
                      <fieldset className="permission-list">
                        <legend>{t("permissions")}</legend>
                        {[
                          ...permissions,
                          ...(editor.value?.permissions
                            .filter(
                              (code) =>
                                !permissions.some(([known]) => known === code),
                            )
                            .map(
                              (code) =>
                                [code, "customPermission"] as [
                                  string,
                                  MessageKey,
                                ],
                            ) || []),
                        ].map(([code, label]) => (
                          <label key={code}>
                            <input
                              type="checkbox"
                              name="permissions"
                              value={code}
                              defaultChecked={editor.value?.permissions.includes(
                                code,
                              )}
                            />
                            <span>
                              {t(label)}
                              <small>{code}</small>
                            </span>
                          </label>
                        ))}
                      </fieldset>
                    </div>
                  </>
                ) : (
                  <>
                    <Field label={t("username")}>
                      <input
                        name="username"
                        required
                        maxLength={150}
                        readOnly={!!editor.value}
                        defaultValue={editor.value?.username}
                        autoComplete="off"
                      />
                    </Field>
                    {!editor.value && (
                      <Field label={t("password")}>
                        <input
                          name="password"
                          type="password"
                          required
                          minLength={8}
                          autoComplete="new-password"
                        />
                      </Field>
                    )}
                    <Field label={t("firstName")}>
                      <input
                        name="first_name"
                        maxLength={150}
                        defaultValue={editor.value?.first_name}
                      />
                    </Field>
                    <Field label={t("lastName")}>
                      <input
                        name="last_name"
                        maxLength={150}
                        defaultValue={editor.value?.last_name}
                      />
                    </Field>
                    <Field label={t("email")}>
                      <input
                        name="email"
                        type="email"
                        defaultValue={editor.value?.email}
                      />
                    </Field>
                    <Field label={t("phone")}>
                      <input
                        name="phone"
                        maxLength={20}
                        defaultValue={editor.value?.phone}
                      />
                    </Field>
                    <label className="filter-chip">
                      <input
                        type="checkbox"
                        name="is_active"
                        defaultChecked={editor.value?.is_active ?? true}
                      />
                      {t("active")}
                    </label>
                    <fieldset className="permission-list wide">
                      <legend>{t("roles")}</legend>
                      {roles.data.map((role) => (
                        <label key={role.id}>
                          <input
                            type="checkbox"
                            name="role_ids"
                            value={role.id}
                            defaultChecked={editor.value?.roles.some(
                              (r) => r.id === role.id,
                            )}
                          />
                          <span>
                            {role.name}
                            <small>{role.code}</small>
                          </span>
                        </label>
                      ))}
                    </fieldset>
                    {roles.next && (
                      <button
                        type="button"
                        className="secondary"
                        onClick={roles.more}
                      >
                        {t("more")}
                      </button>
                    )}
                  </>
                )}
              </div>
            </fieldset>
            <div className="dialog-actions">
              <button
                type="button"
                disabled={busy}
                className="secondary"
                onClick={() => setEditor(null)}
              >
                {t("cancel")}
              </button>
              <button
                className="primary"
                disabled={
                  busy ||
                  (editor.kind === "user" && (!!roles.error || roles.loading))
                }
              >
                {t(busy ? "saving" : "saveChanges")}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
