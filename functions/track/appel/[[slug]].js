/**
 * Cloudflare Pages Function — Tracking des clics "Appeler"
 * Route  : /track/appel/*
 * Exemples :
 *   /track/appel/debouchage-urgence/nord-essonne/evry-courcouronnes/
 *   /track/appel/vidange-fosse-septique/sud-essonne/etampes/
 *   /track/appel/homepage/hero/
 *   /track/appel/header/
 *
 * Principe : redirect 302 → tel:
 *   - Zéro JS côté client, zéro cookie, conforme RGPD.
 *   - Chaque clic = 1 requête HTTP loggée nativement dans Cloudflare Analytics.
 *   - L'URL /track/appel/{service}/{zone}/{commune} permet un filtre par commune
 *     directement dans le dashboard Cloudflare (Top Paths) ou via Workers Analytics Engine.
 *
 * Variables d'environnement (Cloudflare Pages → Settings → Environment variables) :
 *   PHONE_NUMBER  — ex: "+33612345678"  (fallback : valeur ci-dessous)
 */

const PHONE_FALLBACK = '+33XXXXXXXXX';

export async function onRequest(context) {
  const phone = context.env?.PHONE_NUMBER ?? PHONE_FALLBACK;

  // Optionnel : log structuré vers Workers Analytics Engine si activé
  // context.env?.ANALYTICS?.writeDataPoint({ indexes: [context.params.slug] });

  return new Response(null, {
    status: 302,
    headers: {
      'Location': `tel:${phone}`,
      // Empêcher la mise en cache du redirect (chaque appel doit être loggé)
      'Cache-Control': 'no-store, no-cache, must-revalidate',
      // Éviter l'indexation de ces URLs par Google
      'X-Robots-Tag': 'noindex',
    },
  });
}
