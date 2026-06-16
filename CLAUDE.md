# CLAUDE.md — Le Guide de l'Assainissement 91

## Stack & Architecture

- **Framework** : Astro 4 (SSG pur — zéro JS par défaut)
- **Styling** : Tailwind CSS
- **Hébergement** : Cloudflare Pages (free tier)
- **Modèle économique** : Annuaire thématique (listings gratuits + Premium par flag JSON)

## Règles absolues

1. **INTERDIT** de lire `COMPILATION_AVEC_DATES.txt` directement.
2. **Toute donnée métier** (villes, tarifs, services, EEAT) transite exclusivement par `data/knowledge_map.json`.
3. **`scripts/sync_knowledge.py`** est le seul script autorisé à modifier `knowledge_map.json`.
4. Les données artisans sont **mockées** jusqu'à synchronisation explicite.

## Flux de données

```
Source locale → scripts/sync_knowledge.py → data/knowledge_map.json → Astro build → dist/ (HTML statique)
```

## Géographie cible

| Zone | Profil | Services prioritaires |
|------|--------|----------------------|
| Nord Essonne | Urbain / Réseau collectif | Débouchage urgence, Curage, Inspection caméra |
| Sud Essonne | Rural / Non-collectif | Vidange fosse septique, Contrôle SPANC |

## Seed de développement (6 communes)

- **Nord** : Évry-Courcouronnes, Massy, Palaiseau
- **Sud** : Étampes, Dourdan, Milly-la-Forêt

## Conventions d'édition (token reduction)

- Toujours `Grep` avant `Read` pour localiser une cible
- Toujours `Edit` (diff) plutôt que `Write` pour les fichiers existants
- Toujours `jq` ciblé plutôt que lecture complète de `knowledge_map.json`
- Ne jamais réécrire un fichier entier pour changer < 20 lignes

## Structure des URLs

```
/[service]-essonne/              ← Hub service (ex: /debouchage-urgence-essonne/)
/[zone]-essonne/                 ← Hub géographique (ex: /nord-essonne/)
/[service]/[ville]/              ← Page locale (ex: /debouchage/evry-courcouronnes/)
/annuaire/[ville]/               ← Listing artisans par commune
/spanc-essonne/                  ← Page EEAT différenciateur
```
