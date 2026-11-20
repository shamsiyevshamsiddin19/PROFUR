import { useEffect, useState } from "react";
import { request, write } from "../api";
import { TableViewport } from "../components/TableViewport";
import { Feedback, Modal } from "../components/WorkflowUI";
import { translate, type Language } from "../i18n";

type AccountRequest = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  phone: string;
  requested_roles: string[];
};
type RoleOption = {
  id: number;
  code: string;
  name: string;
  permissions: string[];
};

export function PendingAccounts({
  roles,
  lang,
  onUpdate,
}: {
  roles: RoleOption[];
  lang: Language;
  onUpdate: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [rows, setRows] = useState<AccountRequest[]>([]);
  const [revision, setRevision] = useState(0);
  const [selected, setSelected] = useState<{
    row: AccountRequest;
    approve: boolean;
  } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [picked, setPicked] = useState<number[]>([]);
  const workerRoles = roles.filter(
    (role) =>
      role.code !== "ADMIN" &&
      !role.permissions.includes("*") &&
      (role.code === "WORKER" || role.permissions.includes("inventory.worker")),
  );
  useEffect(() => {
    const controller = new AbortController();
    void request<AccountRequest[]>("/api/auth/pending/", lang, {
      signal: controller.signal,
    })
      .then((value) => {
        if (!controller.signal.aborted) setRows(value);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setError(err);
      });
    return () => controller.abort();
  }, [lang, revision]);
  if (!rows.length && !error) return null;
  return (
    <section className="admin-section">
      <h2>{t("pendingAccounts")}</h2>
      {!selected && <Feedback lang={lang} error={error} />}
      <TableViewport lang={lang} className="">
        <table>
          <thead>
            <tr>
              <th>{t("username")}</th>
              <th>{t("name")}</th>
              <th>{t("phone")}</th>
              <th>{t("roles")}</th>
              <th>{t("actions")}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.username}</td>
                <td>
                  {row.first_name} {row.last_name}
                </td>
                <td>{row.phone || "—"}</td>
                <td>
                  {row.requested_roles
                    .map(
                      (code) =>
                        roles.find((role) => role.code === code)?.name ?? code,
                    )
                    .join(", ") || "—"}
                </td>
                <td>
                  <div className="row-actions">
                    <button
                      className="text-button"
                      onClick={() => {
                        setPicked(
                          workerRoles
                            .filter((role) =>
                              row.requested_roles.includes(role.code),
                            )
                            .map((role) => role.id),
                        );
                        setError(null);
                        setSelected({ row, approve: true });
                      }}
                    >
                      {t("approve")}
                    </button>
                    <button
                      className="text-button"
                      onClick={() => {
                        setError(null);
                        setSelected({ row, approve: false });
                      }}
                    >
                      {t("reject")}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableViewport>
      {selected && (
        <Modal
          lang={lang}
          title={t(selected.approve ? "approve" : "reject")}
          busy={busy}
          close={() => setSelected(null)}
        >
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              setError(null);
              setBusy(true);
              try {
                await write(
                  `/api/auth/users/${selected.row.id}/${selected.approve ? "approve" : "reject"}/`,
                  lang,
                  { role_ids: picked },
                );
                setSelected(null);
                setRevision((value) => value + 1);
                onUpdate();
              } catch (err) {
                setError(err);
              } finally {
                setBusy(false);
              }
            }}
          >
            <p>{selected.row.username}</p>
            <Feedback lang={lang} error={error} />
            {selected.approve && (
              <fieldset className="permission-list" disabled={busy}>
                <legend>{t("roles")}</legend>
                {workerRoles.map((role) => (
                  <label className="check-label" key={role.id}>
                    <input
                      type="checkbox"
                      checked={picked.includes(role.id)}
                      onChange={(e) =>
                        setPicked((previous) =>
                          e.target.checked
                            ? [...previous, role.id]
                            : previous.filter((id) => id !== role.id),
                        )
                      }
                    />
                    {role.name}
                  </label>
                ))}
              </fieldset>
            )}
            <div className="dialog-actions">
              <button
                className="secondary"
                type="button"
                onClick={() => setSelected(null)}
                disabled={busy}
              >
                {t("cancel")}
              </button>
              <button
                className="primary"
                disabled={busy || (selected.approve && !picked.length)}
              >
                {t(selected.approve ? "approve" : "reject")}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </section>
  );
}
