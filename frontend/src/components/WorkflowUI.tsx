import {
  Children,
  cloneElement,
  isValidElement,
  useEffect,
  useId,
  useRef,
  type ReactElement,
  type ReactNode,
} from "react";
import { RefreshCw, X } from "lucide-react";
import { ApiError, fieldErrors } from "../api";
import { errorKey } from "../format";
import { translate, type Language, type MessageKey } from "../i18n";

export function Feedback({ error, lang }: { error: unknown; lang: Language }) {
  if (!error) return null;
  const fields = fieldErrors(error);
  const detail =
    error instanceof ApiError && error.data && typeof error.data === "object"
      ? (error.data as { detail?: unknown; error?: { message?: string } })
          .detail
      : null;
  return (
    <div className="notice error" role="alert">
      <div>
        <strong>
          {typeof detail === "string"
            ? detail
            : translate(lang, errorKey(error))}
        </strong>
        {Object.entries(fields)
          .filter(([key, value]) => value && !["detail", "code"].includes(key))
          .map(([key, value]) => (
            <div key={key}>{value}</div>
          ))}
      </div>
    </div>
  );
}
export function RecordsState({
  error,
  loading,
  empty,
  more,
  reload,
  lang,
}: {
  error: unknown;
  loading: boolean;
  empty: boolean;
  more?: () => void;
  reload: () => void;
  lang: Language;
}) {
  return (
    <>
      <Feedback error={error} lang={lang} />
      {loading && (
        <div className="load-line" role="status">
          <RefreshCw size={16} className="spin" />
          {translate(lang, "loading")}
        </div>
      )}
      {!loading && empty && !error && (
        <div className="empty">{translate(lang, "empty")}</div>
      )}
      {error ? (
        <button className="secondary" onClick={reload}>
          {translate(lang, "retry")}
        </button>
      ) : (
        more && (
          <button className="secondary" disabled={loading} onClick={more}>
            {translate(lang, "more")}
          </button>
        )
      )}
    </>
  );
}
export function Field({
  label,
  children,
  wide = false,
}: {
  label: string;
  children: ReactNode;
  wide?: boolean;
}) {
  const id = useId();
  const controls = Children.map(children, (child) => {
    if (
      isValidElement(child) &&
      typeof child.type === "string" &&
      ["input", "select", "textarea"].includes(child.type)
    ) {
      return cloneElement(child as ReactElement<{ id?: string }>, { id });
    }
    return child;
  });
  return (
    <div className={wide ? "field wide" : "field"}>
      <label htmlFor={id}>{label}</label>
      {controls}
    </div>
  );
}
export function Modal({
  title,
  close,
  children,
  lang,
  busy = false,
}: {
  title: string;
  close: () => void;
  children: ReactNode;
  lang: Language;
  busy?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const id = useId();
  useEffect(() => {
    const dialog = ref.current;
    dialog?.showModal();
    return () => dialog?.close();
  }, []);
  return (
    <dialog
      ref={ref}
      className="workflow-dialog"
      aria-labelledby={id}
      onCancel={(event) => {
        event.preventDefault();
        if (!busy) close();
      }}
    >
      <div className="dialog-heading">
        <h2 id={id}>{title}</h2>
        <button
          disabled={busy}
          className="icon-button"
          onClick={close}
          aria-label={translate(lang, "close")}
        >
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
export function Status({
  value,
  lang,
}: {
  value?: "pending" | "approved" | "rejected";
  lang: Language;
}) {
  return value ? (
    <span className={"status-tag " + value}>
      {translate(lang, value as MessageKey)}
    </span>
  ) : null;
}
