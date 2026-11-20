import { useEffect, useState } from "react";
import { request, write } from "../api";
import { translate, type Language } from "../i18n";
import { Feedback } from "./WorkflowUI";

export type SignupRole = { code: string; name: string };

export function WorkerRegistration({
  lang,
  close,
}: {
  lang: Language;
  close: () => void;
}) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [roles, setRoles] = useState<SignupRole[] | null>(null);
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  useEffect(() => {
    const controller = new AbortController();
    void request<SignupRole[]>("/api/auth/signup-roles/", lang, {
      signal: controller.signal,
    })
      .then((rows) => {
        if (!controller.signal.aborted) setRoles(rows);
      })
      .catch((err) => {
        if (!controller.signal.aborted) setError(err);
      });
    return () => controller.abort();
  }, [lang]);
  return (
    <div className="login-form worker-registration">
      <h1>{t("registerWorker")}</h1>
      <Feedback lang={lang} error={error} />
      {sent ? (
        <p role="status">{t("registrationSent")}</p>
      ) : (
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            const data = new FormData(e.currentTarget);
            setBusy(true);
            setError(null);
            try {
              await write("/api/auth/register/", lang, {
                username: data.get("username"),
                password: data.get("password"),
                first_name: data.get("first_name"),
                last_name: data.get("last_name"),
                phone: data.get("phone"),
                requested_roles: data.getAll("requested_roles"),
              });
              setSent(true);
            } catch (err) {
              setError(err);
            } finally {
              setBusy(false);
            }
          }}
        >
          <fieldset className="registration-fields" disabled={busy || !roles}>
            <label>
              {t("username")}
              <input
                name="username"
                autoComplete="username"
                required
                maxLength={150}
              />
            </label>
            <label>
              {t("password")}
              <input
                name="password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
              />
            </label>
            <label>
              {t("firstName")}
              <input
                name="first_name"
                autoComplete="given-name"
                required
                maxLength={150}
              />
            </label>
            <label>
              {t("lastName")}
              <input
                name="last_name"
                autoComplete="family-name"
                maxLength={150}
              />
            </label>
            <label>
              {t("phone")}
              <input
                name="phone"
                type="tel"
                autoComplete="tel"
                maxLength={20}
              />
            </label>
            {Boolean(roles?.length) && (
              <fieldset className="permission-list">
                <legend>{t("roles")}</legend>
                {roles!.map((role) => (
                  <label className="check-label" key={role.code}>
                    <input
                      type="checkbox"
                      name="requested_roles"
                      value={role.code}
                    />
                    {role.name}
                  </label>
                ))}
              </fieldset>
            )}
            <button className="primary" disabled={busy || !roles}>
              {t("registerWorker")}
            </button>
          </fieldset>
        </form>
      )}
      <button
        className="secondary"
        type="button"
        disabled={busy}
        onClick={close}
      >
        {t("login")}
      </button>
    </div>
  );
}
