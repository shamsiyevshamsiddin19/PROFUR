import { focusCurrentSearch } from "./keyboard";
import { initialAppearance } from "./appearance";
import { Settings } from "./pages/Settings";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  Settings2,
  Tags,
  Users,
  Bell,
  ArrowDownLeft,
  Box,
  ChevronRight,
  Layers3,
  LogOut,
  Menu,
  Warehouse,
  ArrowUpRight,
  History as HistoryIcon,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  ReceiptText,
  X,
} from "lucide-react";
import { ApiError, request, write, type User, can } from "./api";
import { screenAllowed } from "./access";
import { errorKey } from "./format";
import {
  initialLanguage,
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
function currentScreen(): Screen | null {
  const hash = location.hash.slice(1);
  return Object.hasOwn(screens, hash) ? (hash as Screen) : null;
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
  const [requestedScreen, setScreen] = useState(currentScreen);
  const allowed = (key: Screen) => user !== null && screenAllowed(user, key);
  const defaultScreen: Screen =
    (
      [
        "receiving",
        "operations",
        "stock",
        "materials",
        "expenses",
        "expenseTypes",
        "administration",
        "settings",
      ] as const
    ).find(allowed) ?? "settings";
  const screen =
    requestedScreen && allowed(requestedScreen)
      ? requestedScreen
      : defaultScreen;
  const canSeeNotifications = allowed("notifications");
  useEffect(() => {
    if (
      user &&
      screen !== requestedScreen &&
      location.hash &&
      currentScreen() === requestedScreen
    ) {
      history.replaceState(history.state, "", "#" + screen);
      setScreen(screen);
    }
  }, [user, requestedScreen, screen]);
  const [unreadCount, setUnreadCount] = useState(0);
  const navRef = useRef<HTMLElement>(null);
  const [drawer, setDrawer] = useState(false);
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem("profur.sidebar.collapsed") === "true";
    } catch {
      return false;
    }
  });
  const t = useCallback((key: MessageKey) => translate(lang, key), [lang]);

  useEffect(() => {
    try {
      localStorage.setItem("profur.sidebar.collapsed", String(collapsed));
    } catch {
      /* Saqlash yopiq bo'lsa sessiyada saqlanadi. */
    }
  }, [collapsed]);

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
  const userId = user?.id;
  useEffect(() => setUnreadCount(0), [userId]);
  useEffect(() => {
    if (!userId) return;
    let controller: AbortController | undefined;
    const refresh = () => {
      if (document.hidden) return;
      controller?.abort();
      const current = new AbortController();
      controller = current;
      void request<User>("/api/auth/me/", lang, { signal: current.signal })
        .then((updated) => {
          if (!current.signal.aborted)
            setUser((previous) =>
              previous?.id === userId ? updated : previous,
            );
        })
        .catch((error) => {
          if (
            !current.signal.aborted &&
            error instanceof ApiError &&
            (error.status === 401 || error.status === 403)
          )
            setUser((previous) => (previous?.id === userId ? null : previous));
        });
    };
    window.addEventListener("focus", refresh);
    window.addEventListener("hashchange", refresh);
    const interval = window.setInterval(refresh, 60_000);
    return () => {
      controller?.abort();
      window.clearInterval(interval);
      window.removeEventListener("focus", refresh);
      window.removeEventListener("hashchange", refresh);
    };
  }, [userId, lang]);
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
    if (!canSeeNotifications) return;
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
  }, [canSeeNotifications, userId, lang, screen]);

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
      {Object.entries({ uz: "uz", ru: "ru", en: "eng" }).map(
        ([code, label]) => (
          <option key={code} value={code}>
            {label}
          </option>
        ),
      )}
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
    <div className={collapsed ? "app sidebar-collapsed" : "app"}>
      {drawer && (
        <button
          className="scrim"
          onClick={() => setDrawer(false)}
          aria-label={t("close")}
        />
      )}
      <aside className={drawer ? "sidebar open" : "sidebar"}>
        <div className="brand-row">
          <button
            className="collapse-toggle"
            onClick={() => setCollapsed((c) => !c)}
            aria-label={t(collapsed ? "expandSidebar" : "collapseSidebar")}
            title={t(collapsed ? "expandSidebar" : "collapseSidebar")}
          >
            {collapsed ? (
              <PanelLeftOpen size={18} />
            ) : (
              <PanelLeftClose size={18} />
            )}
          </button>
          <a
            className="brand"
            href={"#" + defaultScreen}
            onClick={() => {
              setScreen(defaultScreen);
              setDrawer(false);
            }}
          >
            <span className="brand-text">PROFUR</span>
          </a>
        </div>
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
                "warehouseOps",
                [
                  "receiving",
                  "operations",
                  "stock",
                  ...(!allowed("receiving") && allowed("materials")
                    ? ["materials"]
                    : []),
                ],
              ],
              ["recordsNav", ["expenses", "history"]],
              [
                "managementNav",
                [
                  ...(!allowed("expenses") && allowed("expenseTypes")
                    ? ["expenseTypes"]
                    : []),
                  "administration",
                  "settings",
                ],
              ],
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
                        title={collapsed ? t(key) : undefined}
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
            {languagePicker}
            {allowed("notifications") && (
              <a
                href="#notifications"
                className="icon-button topbar-notifications"
                aria-label={t("notifications")}
                onClick={() => {
                  setScreen("notifications");
                  setDrawer(false);
                }}
              >
                <Bell size={18} />
                {unreadCount > 0 && (
                  <span className="notification-badge">{unreadCount}</span>
                )}
              </a>
            )}
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
            {screen === "receiving" && allowed("materials") && (
              <a
                href="#materials"
                className="page-action-button"
                onClick={() => {
                  setScreen("materials");
                  setDrawer(false);
                }}
              >
                {can(user, "catalog.add_material") && <Plus size={16} />}
                <span>
                  {t(
                    can(user, "catalog.add_material")
                      ? "newMaterial"
                      : "materials",
                  )}
                </span>
              </a>
            )}
            {screen === "expenses" && allowed("expenseTypes") && (
              <a
                href="#expenseTypes"
                className="page-action-button"
                onClick={() => {
                  setScreen("expenseTypes");
                  setDrawer(false);
                }}
              >
                {can(user, "expenses.add_expensetype") && <Plus size={16} />}
                <span>
                  {t(
                    can(user, "expenses.add_expensetype")
                      ? "addExpenseType"
                      : "expenseTypes",
                  )}
                </span>
              </a>
            )}
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
          {defaultScreen === "settings" && (
            <p className="notice">{t("noWorkAssigned")}</p>
          )}
          {screen === "settings" ? (
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
          </footer>
        </main>
      </div>
    </div>
  );
}
