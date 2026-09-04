import fr from './fr.json';
import en from './en.json';

export const languages = {
  fr: 'Français',
  en: 'English',
};

export const defaultLang = 'fr';

const dictionaries = { fr, en };

export type Lang = keyof typeof dictionaries;

export function useTranslations(lang: string) {
  return dictionaries[lang as Lang] ?? dictionaries[defaultLang];
}

/** Given the current URL and a target lang, returns the equivalent path in that lang. */
export function getLocalizedPath(pathname: string, targetLang: Lang): string {
  const stripped = pathname.replace(/^\/en/, '') || '/';
  if (targetLang === defaultLang) return stripped;
  return `/en${stripped === '/' ? '' : stripped}`;
}

export function getCurrentLang(pathname: string): Lang {
  return pathname.startsWith('/en') ? 'en' : 'fr';
}
