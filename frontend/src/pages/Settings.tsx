import {
  Check,
  Palette,
  SlidersHorizontal,
  Globe2,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";
import type { User } from "../api";
import { languages, translate, type Language, type MessageKey } from "../i18n";
import { defaultAppearance, type Appearance } from "../appearance";
export function Settings({
  lang,
  setLanguage,
  value,
  onChange,
  user,
  storageAvailable,
}: {
  lang: Language;
  setLanguage: (lang: Language) => void;
  value: Appearance;
  onChange: (value: Appearance) => void;
  user: User;
  storageAvailable: boolean;
}) {
  const t = (key: MessageKey) => translate(lang, key);
  return (
    <div className="settings-layout">
      <section className="settings-card appearance-card">
        <div className="settings-section-heading">
          <span className="settings-icon">
            <Palette size={21} />
          </span>
          <div>
            <h2>{t("appearance")}</h2>
            <p>{t("appearanceHint")}</p>
          </div>
        </div>
        <fieldset className="accent-field">
          <legend>{t("accentColor")}</legend>
          <div className="accent-options">
            {(["teal", "indigo", "violet"] as const).map((accent) => (
              <label
                key={accent}
                className={
                  "accent-option " +
                  accent +
                  (value.accent === accent ? " selected" : "")
                }
              >
                <input
                  type="radio"
                  name="accent"
                  value={accent}
                  checked={value.accent === accent}
                  onChange={() => onChange({ ...value, accent })}
                />
                <span className="accent-preview" aria-hidden="true">
                  <span />
                  <i />
                  <i />
                  <i />
                </span>
                <span className="accent-option-caption">
                  {t(accent)}
                  {value.accent === accent && <Check size={17} />}
                </span>
              </label>
            ))}
          </div>
        </fieldset>
        <div className="settings-row">
          <div>
            <strong>{t("density")}</strong>
            <p>{t("densityHint")}</p>
          </div>
          <div
            className="density-control"
            role="group"
            aria-label={t("density")}
          >
            {(["comfortable", "compact"] as const).map((density) => (
              <button
                key={density}
                aria-pressed={value.density === density}
                onClick={() => onChange({ ...value, density })}
              >
                {t(density)}
              </button>
            ))}
          </div>
        </div>
        <label className="settings-row motion-control">
          <span>
            <strong>{t("motion")}</strong>
            <span className="settings-description">{t("motionHint")}</span>
          </span>
          <input
            type="checkbox"
            checked={value.reducedMotion}
            onChange={(e) =>
              onChange({ ...value, reducedMotion: e.target.checked })
            }
          />
        </label>
        <div className="settings-card-footer">
          <span role="status">
            {t(storageAvailable ? "preferenceScope" : "preferenceUnavailable")}
          </span>
          <button
            className="text-button"
            onClick={() => onChange({ ...defaultAppearance })}
          >
            <RotateCcw size={15} />
            {t("resetAppearance")}
          </button>
        </div>
      </section>
      <section className="settings-card">
        <div className="settings-section-heading">
          <span className="settings-icon">
            <Globe2 size={21} />
          </span>
          <div>
            <h2>{t("interfaceLanguage")}</h2>
          </div>
        </div>
        <select
          className="settings-language"
          aria-label={t("interfaceLanguage")}
          value={lang}
          onChange={(e) => setLanguage(e.target.value as Language)}
        >
          {Object.entries(languages).map(([code, name]) => (
            <option value={code} key={code}>
              {name}
            </option>
          ))}
        </select>
      </section>
      <section className="settings-card">
        <div className="settings-section-heading">
          <span className="settings-icon">
            <SlidersHorizontal size={21} />
          </span>
          <div>
            <h2>{t("workspaceRules")}</h2>
          </div>
        </div>
        <dl className="settings-facts">
          <div>
            <dt>{t("warehouse")}</dt>
            <dd>{t("mainWarehouse")}</dd>
          </div>
          <div>
            <dt>{t("currency")}</dt>
            <dd>
              USD <span className="settings-value-tag">$</span>
            </dd>
          </div>
        </dl>
      </section>
      <section className="settings-card">
        <div className="settings-section-heading">
          <span className="settings-icon">
            <ShieldCheck size={21} />
          </span>
          <div>
            <h2>{t("profileSettings")}</h2>
          </div>
        </div>
        <strong className="account-name">
          {[user.first_name, user.last_name].filter(Boolean).join(" ") ||
            user.username}
        </strong>
        <p className="account-login">{user.username}</p>
        <div className="role-tags">
          {user.roles.map((role) => (
            <span key={role.code}>{role.name}</span>
          ))}
        </div>
      </section>
    </div>
  );
}
