import type { KeyboardEvent } from "react";

export function focusCurrentSearch(): boolean {
  if (document.querySelector("dialog[open]")) return false;
  const input = document.querySelector<HTMLInputElement>(
    "main [data-search-field]",
  );
  if (!input || input.disabled) return false;
  input.focus();
  input.select();
  return true;
}

/** Never replaces select/textarea behaviour or bypasses native form validation. */
export function receiptKeyboard(
  event: KeyboardEvent<HTMLFormElement>,
  locked: boolean,
) {
  if (event.key !== "Enter" || event.nativeEvent.isComposing || event.altKey)
    return;
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  const advances =
    target instanceof HTMLInputElement &&
    ["text", "number", "email", "tel", "url", "search"].includes(target.type);
  if (event.repeat && (advances || event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    return;
  }
  if (event.ctrlKey || event.metaKey) {
    event.preventDefault();
    if (!locked) {
      const submit = event.currentTarget.querySelector<HTMLButtonElement>(
        'button[type="submit"]',
      );
      if (submit && !submit.disabled) event.currentTarget.requestSubmit(submit);
    }
    return;
  }
  if (!advances || !(target instanceof HTMLInputElement)) return;
  event.preventDefault();
  if (locked) return;
  // An invalid field remains focused so a mistake cannot be silently skipped.
  if (!target.reportValidity()) return;
  const controls = Array.from(
    event.currentTarget.querySelectorAll<HTMLElement>(
      'input:not([type="hidden"]):not(:disabled),select:not(:disabled),textarea:not(:disabled),button[type="submit"]:not(:disabled)',
    ),
  );
  controls[controls.indexOf(target) + 1]?.focus();
}
