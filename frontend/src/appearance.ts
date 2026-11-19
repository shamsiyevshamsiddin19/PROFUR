export type Appearance = {
  accent: "teal" | "indigo" | "violet";
  density: "comfortable" | "compact";
  reducedMotion: boolean;
};
export const defaultAppearance: Appearance = {
  accent: "teal",
  density: "comfortable",
  reducedMotion: false,
};
export function initialAppearance(): Appearance {
  try {
    const value = JSON.parse(localStorage.getItem("profur.appearance") || "{}");
    return {
      accent: ["teal", "indigo", "violet"].includes(value?.accent)
        ? value.accent
        : "teal",
      density: value?.density === "compact" ? "compact" : "comfortable",
      reducedMotion: value?.reducedMotion === true,
    };
  } catch {
    return { ...defaultAppearance };
  }
}
