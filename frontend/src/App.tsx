import { useCallback, useEffect, useState } from "react";
import {
  ArrowDownLeft,
  Box,
  ChevronRight,
  CircleDollarSign,
  Layers3,
  LogOut,
  Menu,
  ShieldCheck,
  Warehouse,
  X,
} from "lucide-react";
import { ApiError, request, write, type User } from "./api";
import { errorKey } from "./format";
import {
  initialLanguage,
  languages,
  translate,
  type Language,
  type MessageKey,
} from "./i18n";
import { Login } from "./components/Login";
import { WarehouseContent } from "./pages/WarehouseContent";

type Screen = "receiving" | "materials" | "stock";
const screens = { receiving: ArrowDownLeft, materials: Box, stock: Layers3 };
function currentScreen(): Screen {
  const hash = location.hash.slice(1);
  return hash === "materials" || hash === "stock" ? hash : "receiving";
}
export function App() {
  const [lang, setLang] = useState<Language>(initialLanguage);
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(true);
  const [authError, setAuthError] = useState<MessageKey | null>(null);
  const [screen, setScreen] = useState<Screen>(currentScreen);
  const [drawer, setDrawer] = useState(false);
  const t = useCallback((key: MessageKey) => translate(lang, key), [lang]);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.title = "PROFUR · " + t("warehouse");
    try {
      localStorage.setItem("profur.language", lang);
    } catch {
      /* Til sessiyada saqlanadi. */
    }
  }, [lang, t]);
  useEffect(() => {
    const controller = new AbortController();
    request<User>("/api/auth/me/", initialLanguage(), {
      signal: controller.signal,
    })
      .then(setUser)
      .catch((error) => {
        if (error instanceof DOMException && error.name === "AbortError")
          return;
        if (!(
          error instanceof ApiError &&
          (error.status === 401 || error.status === 403)
        ))
          setAuthError(errorKey(error));
      })
      .finally(() => {
        if (!controller.signal.aborted) setChecking(false);
      });
    return () => controller.abort();
  }, []);
  useEffect(() => {
    const onHash = () => {
      setScreen(currentScreen());
      setDrawer(false);
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  useEffect(() => {
    if (!drawer) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawer(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [drawer]);

  const languagePicker = (
    <select
      className="language"
      aria-label="Language"
      value={lang}
      onChange={(e) => setLang(e.target.value as Language)}
    >
      {Object.entries(languages).map(([code, name]) => (
        <option key={code} value={code}>
          {name}
        </option>
      ))}
    </select>
  );
  if (checking)
    return (
      <div className="connecting" role="status">
        <Warehouse size={30} />
        <span>{t("loading")}</span>
        <div className="indeterminate" />
      </div>
    );
  if (!user)
    return (
      <Login
        lang={lang}
        languagePicker={languagePicker}
        initialError={authError}
        onLogin={(user) => {
          setDrawer(false);
          setUser(user);
        }}
      />
    );

  const name =
    [user.first_name, user.last_name].filter(Boolean).join(" ") ||
    user.username;
  async function logout() {
    setDrawer(false);
    try {
      await write("/api/auth/logout/", lang, {});
      setUser(null);
      setAuthError(null);
    } catch (e) {
      if (e instanceof ApiError && e.status === 403) {
        setUser(null);
        setAuthError("session");
      } else setAuthError(errorKey(e));
    }
  }
  return (
    <div className="app">
      {drawer && (
        <button
          className="scrim"
          onClick={() => setDrawer(false)}
          aria-label={t("close")}
        />
      )}
      <aside className={drawer ? "sidebar open" : "sidebar"}>
        <a className="brand" href="#receiving" onClick={() => setDrawer(false)}>
          <span className="brand-icon">
            <Warehouse size={22} />
          </span>
          PROFUR
          <span className="brand-dot" />
        </a>
        <button
          className="icon-button drawer-close"
          onClick={() => setDrawer(false)}
          aria-label={t("close")}
        >
          <X size={20} />
        </button>
        <div className="sidebar-label">{t("workspace")}</div>
        <nav>
          {(Object.entries(screens) as [Screen, typeof Box][]).map(
            ([key, Icon]) => (
              <a
                href={"#" + key}
                className={key === screen ? "nav-item active" : "nav-item"}
                key={key}
                onClick={() => setDrawer(false)}
                aria-current={key === screen ? "page" : undefined}
              >
                <Icon size={19} />
                {t(key)}
                {key === screen && <span className="nav-dot" />}
              </a>
            ),
          )}
        </nav>
        <div className="sidebar-bottom">
          <div className="warehouse-label">
            <Warehouse size={18} />
            <div>
              <strong>PROFUR</strong>
              <span>{t("warehouse")}</span>
            </div>
            <ShieldCheck size={17} />
          </div>
          <div className="profile">
            <span className="avatar">{name.slice(0, 1).toUpperCase()}</span>
            <span className="profile-name">{name}</span>
            <button
              className="icon-button"
              onClick={logout}
              aria-label={t("logout")}
            >
              <LogOut size={17} />
            </button>
          </div>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div className="breadcrumbs">
            <button
              className="icon-button mobile-menu"
              onClick={() => setDrawer(true)}
              aria-label={t("menu")}
              aria-expanded={drawer}
            >
              <Menu size={21} />
            </button>
            <Warehouse size={15} />
            <span>{t("warehouse")}</span>
            <ChevronRight size={14} />
            <strong>{t(screen)}</strong>
          </div>
          {languagePicker}
        </header>
        <main>
          <div className="page-heading">
            <div>
              <h1>{t(screen)}</h1>
              <p>{screen === "receiving" ? t("intro") : t("search")}</p>
            </div>
            <span className="currency-badge">
              <CircleDollarSign size={16} />
              USD
            </span>
          </div>
          {authError && (
            <div className="notice error" role="alert">
              {t(authError)}
              <button
                onClick={() => setAuthError(null)}
                aria-label={t("close")}
              >
                <X size={16} />
              </button>
            </div>
          )}
          <WarehouseContent
            key={screen}
            screen={screen}
            lang={lang}
            userId={user.id}
          />
          <footer>
            <span>PROFUR</span>
            <span>{t("allMoney")} · USD</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
