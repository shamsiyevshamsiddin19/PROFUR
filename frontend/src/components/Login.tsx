import { useState, type FormEvent, type ReactNode } from "react";
import { ArrowRight, Warehouse } from "lucide-react";
import { ApiError, write, type User } from "../api";
import { errorKey } from "../format";
import { translate, type Language, type MessageKey } from "../i18n";

export function Login({
  lang,
  languagePicker,
  initialError,
  onLogin,
}: {
  lang: Language;
  languagePicker: ReactNode;
  initialError: MessageKey | null;
  onLogin: (user: User) => void;
}) {
  const t = (key: MessageKey) => translate(lang, key);
  const [error, setError] = useState<MessageKey | null>(initialError);
  const [busy, setBusy] = useState(false);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const data = new FormData(e.currentTarget);
    try {
      const response = await write<{ user: User }>("/api/auth/login/", lang, {
        username: data.get("username"),
        password: data.get("password"),
      });
      onLogin(response.user);
    } catch (e) {
      setError(
        e instanceof ApiError && e.status === 400 ? "credentials" : errorKey(e),
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="login-page">
      <header>
        <span className="brand">
          <span className="brand-icon">
            <Warehouse size={22} />
          </span>
          PROFUR
          <span className="brand-dot" />
        </span>
        {languagePicker}
      </header>
      <div className="login-content">
        <form className="login-form" onSubmit={submit}>
          <span className="eyebrow">{t("warehouse")}</span>
          <h1>{t("loginTitle")}</h1>
          <p>{t("loginHint")}</p>
          <label>
            {t("username")}
            <input
              name="username"
              autoComplete="username"
              required
              disabled={busy}
            />
          </label>
          <label>
            {t("password")}
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              required
              disabled={busy}
            />
          </label>
          {error && (
            <div className="notice error" role="alert">
              {t(error)}
            </div>
          )}
          <button className="primary" disabled={busy}>
            {t(busy ? "loading" : "login")}
            <ArrowRight size={18} />
          </button>
        </form>
      </div>
      <footer>
        <span>PROFUR</span>
      </footer>
    </div>
  );
}
