import {
  ArrowDownLeft,
  ArrowUpRight,
  ArrowRight,
  Box,
  Layers3,
  ReceiptText,
  History,
} from "lucide-react";
import { can, type User } from "../api";
import { translate, type Language, type MessageKey } from "../i18n";
import { screenAllowed, type Screen } from "../navigation";

const actions = [
  { screen: "stock", hint: "homeStockHint", icon: Layers3 },
  { screen: "receiving", hint: "homeReceiptHint", icon: ArrowDownLeft },
  { screen: "operations", hint: "homeOperationsHint", icon: ArrowUpRight },
  { screen: "materials", hint: "homeMaterialsHint", icon: Box },
  { screen: "expenses", hint: "homeExpensesHint", icon: ReceiptText },
  { screen: "history", hint: "homeHistoryHint", icon: History },
] as const;
export function Home({ user, lang }: { user: User; lang: Language }) {
  const t = (key: MessageKey) => translate(lang, key);
  const visible = actions.filter((action) =>
    screenAllowed(user, action.screen),
  );
  const steps = (["materials", "receiving", "stock"] as Screen[]).filter(
    (screen) => screenAllowed(user, screen),
  );
  return (
    <>
      <section className="home-actions" aria-label={t("homeTasks")}>
        {visible.map(({ screen, hint, icon: Icon }) => (
          <a className="home-action" href={"#" + screen} key={screen}>
            <span className="home-action-icon">
              <Icon size={22} aria-hidden="true" />
            </span>
            <span>
              <strong>{t(screen)}</strong>
              <small>{t(hint)}</small>
            </span>
            <ArrowRight size={18} aria-hidden="true" />
          </a>
        ))}
      </section>
      {can(user, "inventory.add_receipt") && steps.length === 3 && (
        <section className="workflow-guide" aria-label={t("homeGuide")}>
          <h2>{t("homeGuide")}</h2>
          <p>{t("homeGuideHint")}</p>
          <ol>
            {steps.map((screen) => (
              <li key={screen}>
                <a href={"#" + screen}>{t(screen)}</a>
              </li>
            ))}
          </ol>
        </section>
      )}
      {!visible.length && <div className="notice">{t("homeNoTasks")}</div>}
    </>
  );
}
