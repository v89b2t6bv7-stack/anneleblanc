# Traductions

- `fr.json` — contenu français, source de vérité.
- `en.json` — copie temporaire du français. La traduction anglaise est une étape séparée, à faire une fois le contenu FR validé (voir brief). Le site FR/EN fonctionne déjà techniquement : basculer `en.json` vers de vraies traductions suffira, sans toucher au code des pages.

Chaque page lit ses textes via `src/i18n/index.ts` (`useTranslations(lang)`), jamais en dur dans les composants.
