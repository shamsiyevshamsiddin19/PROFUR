import { focusCurrentSearch } from "./keyboard";
import { initialAppearance } from "./appearance";
import { Settings } from "./pages/Settings";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  Search,
  Settings2,
  Tags,
  Users,
  Bell,
  ArrowDownLeft,
  Box,
  ChevronRight,
  CircleDollarSign,
  Layers3,
  LogOut,
  Menu,
  Warehouse,
  ArrowUpRight,
  History as HistoryIcon,
  ReceiptText,
  X,
} from "lucide-react";
import { ApiError, request, write, type User, can } from "./api";
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

import { ExpenseTypes } from "./pages/ExpenseTypes";
import { Administration } from "./pages/Administration";
import { Notifications } from "./pages/Notifications";
import { Catalog } from "./pages/Catalog";
import { Operations } from "./pages/Operations";
import { Expenses } from "./pages/Expenses";
import { History } from "./pages/History";
type Screen =
  | "settings"
  | "receiving"
  | "materials"
  | "stock"
  | "operations"
  | "expenses"
  | "history"
  | "expenseTypes"
  | "administration"
  | "notifications";
const screens = {
  settings: Settings2,
  expenseTypes: Tags,
  administration: Users,
  notifications: Bell,
  receiving: ArrowDownLeft,
  materials: Box,
  stock: Layers3,
  operations: ArrowUpRight,
  expenses: ReceiptText,
  history: HistoryIcon,
};
function currentScreen(): Screen {
  const hash = location.hash.slice(1);
  return Object.hasOwn(screens, hash) ? (hash as Screen) : "receiving";
}
export function App() {
  const [appearance, setAppearance] = useState(initialAppearance);
  const [storageAvailable, setStorageAvailable] = useState(true);
  useEffect(() => {
    document.documentElement.dataset.accent = appearance.accent;
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute(
        "content",
        { teal: "#087d68", indigo: "#4855bd", violet: "#7851a9" }[
          appearance.accent
        ],
      );
    document.documentElement.dataset.density = appearance.density;
    document.documentElement.dataset.motion = appearance.reducedMotion
      ? "reduced"
      : "full";
    try {
      localStorage.setItem("profur.appearance", JSON.stringify(appearance));
      setStorageAvailable(true);
    } catch {
      setStorageAvailable(false);
    }
  }, [appearance]);
  const [lang, setLang] = useState<Language>(initialLanguage);
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(true);
  const [authError, setAuthError] = useState<MessageKey | null>(null);
  const [screen, setScreen] = useState<Screen>(currentScreen);
  const [unreadCount, setUnreadCount] = useState(0);
  const navRef = useRef<HTMLElement>(null);
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

  useEffect(() => {
    if (!user || !can(user, "inventory.view_stock")) return;
    const controller = new AbortController();
    const check = () =>
      request<{ count: number }>("/api/v1/notifications/?unread=true", lang, {
        signal: controller.signal,
      })
        .then((page) => {
          if (!controller.signal.aborted) setUnreadCount(page.count);
        })
        .catch(() => {
          /* Inbox itself shows read errors and retry. */
        });
    void check();
    const interval = setInterval(check, 30000);
    return () => {
      controller.abort();
      clearInterval(interval);
    };
  }, [user, lang, screen]);

  useEffect(() => {
    const nav = navRef.current;
    const active = nav?.querySelector<HTMLElement>('[aria-current="page"]');
    if (!nav || !active) return;
    if (active.offsetTop < nav.scrollTop) nav.scrollTop = active.offsetTop;
    else if (
      active.offsetTop + active.offsetHeight >
      nav.scrollTop + nav.clientHeight
    )
      nav.scrollTop =
        active.offsetTop + active.offsetHeight - nav.clientHeight + 8;
  }, [screen, lang, user, drawer]);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (
        event.defaultPrevented ||
        event.isComposing ||
        event.altKey ||
        event.repeat
      )
        return;
      if (document.querySelector("dialog[open]")) return;
      const target = event.target;
      if (
        target instanceof Element &&
        target.closest(
          'input,select,textarea,[contenteditable]:not([contenteditable="false"])',
        )
      )
        return;
      const slash = event.key === "/" && !event.ctrlKey && !event.metaKey;
      const command =
        event.key.toLowerCase() === "k" && (event.ctrlKey || event.metaKey);
      if ((slash || command) && focusCurrentSearch()) event.preventDefault();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

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

  const allowed = (key: Screen) =>
    key === "settings"
      ? true
      : key === "administration"
        ? user.is_superuser || user.role_codes.includes("ADMIN")
        : can(
            user,
            key === "expenseTypes"
              ? "expenses.view_expensetype"
              : key === "materials"
                ? "catalog.view_material"
                : key === "expenses"
                  ? "expenses.view_expense"
                  : "inventory.view_stock",
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
        <nav ref={navRef} aria-label={t("workspace")}>
          {(
            [
              [
                "warehouseNav",
                ["receiving", "materials", "stock", "operations"],
              ],
              ["activityNav", ["expenses", "history", "notifications"]],
              ["managementNav", ["expenseTypes", "administration", "settings"]],
            ] as [MessageKey, Screen[]][]
          ).map(
            ([label, keys]) =>
              keys.some(allowed) && (
                <div className="nav-group" key={label}>
                  <div className="sidebar-label">{t(label)}</div>
                  {keys.filter(allowed).map((key) => {
                    const Icon = screens[key];
                    return (
                      <a
                        href={"#" + key}
                        className={
                          key === screen ? "nav-item active" : "nav-item"
                        }
                        key={key}
                        onClick={() => {
                          setScreen(key);
                          setDrawer(false);
                        }}
                        aria-current={key === screen ? "page" : undefined}
                      >
                        <span className="nav-icon">
                          <Icon size={18} />
                        </span>
                        <span className="nav-text">{t(key)}</span>
                        {key === "notifications" && unreadCount > 0 && (
                          <span className="notification-count">
                            {unreadCount}
                          </span>
                        )}
                        {key === screen && (
                          <ChevronRight size={14} className="nav-arrow" />
                        )}
                      </a>
                    );
                  })}
                </div>
              ),
          )}
        </nav>
        <div className="sidebar-bottom">
          <div className="profile">
            <span className="avatar">{name.slice(0, 1).toUpperCase()}</span>
            <span className="profile-name">
              {name}
              <small>{user.roles[0]?.name || user.username}</small>
            </span>
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
          <div className="topbar-actions">
            {["materials", "stock", "administration"].includes(screen) &&
              allowed(screen) && (
                <button
                  className="search-shortcut"
                  onClick={focusCurrentSearch}
                  aria-label={t("quickSearch")}
                >
                  <Search size={15} />
                  <span>{t("quickSearch")}</span>
                  <kbd>/</kbd>
                </button>
              )}
            {languagePicker}
          </div>
        </header>
        <main>
          <div className="page-heading">
            <div>
              <h1>{t(screen)}</h1>
              <p>
                {screen === "receiving"
                  ? t("intro")
                  : t(
                      screen === "settings"
                        ? "settingsHint"
                        : screen === "expenseTypes"
                          ? "expenseTypesHint"
                          : screen === "administration"
                            ? "administrationHint"
                            : screen === "notifications"
                              ? "notificationsHint"
                              : screen === "materials"
                                ? "catalogueHint"
                                : screen === "operations"
                                  ? "operationsHint"
                                  : screen === "expenses"
                                    ? "expenseHint"
                                    : screen === "history"
                                      ? "historyHint"
                                      : "stockHint",
                    )}
              </p>
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
          {!allowed(screen) ? (
            <div className="notice">{t("noPermission")}</div>
          ) : screen === "settings" ? (
            <Settings
              lang={lang}
              setLanguage={setLang}
              value={appearance}
              onChange={setAppearance}
              user={user}
              storageAvailable={storageAvailable}
            />
          ) : screen === "administration" ? (
            <Administration
              lang={lang}
              user={user}
              onOwnPasswordReset={() => setUser(null)}
              onSelfChange={async () =>
                setUser(await request<User>("/api/auth/me/", lang))
              }
            />
          ) : screen === "notifications" ? (
            <Notifications
              lang={lang}
              onRead={() => setUnreadCount((n) => Math.max(0, n - 1))}
            />
          ) : screen === "materials" ? (
            <Catalog lang={lang} user={user} />
          ) : screen === "operations" ? (
            <Operations lang={lang} user={user} />
          ) : screen === "expenseTypes" ? (
            <ExpenseTypes lang={lang} user={user} />
          ) : screen === "expenses" ? (
            <Expenses lang={lang} user={user} />
          ) : screen === "history" ? (
            <History lang={lang} />
          ) : (
            <WarehouseContent
              key={screen}
              screen={screen}
              lang={lang}
              userId={user.id}
              user={user}
            />
          )}

          <footer>
            <span>PROFUR</span>
            <span>{t("allMoney")} · USD</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
