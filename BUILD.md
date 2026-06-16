# Build

## Local (sandbox — timeout 45s)

```bash
# Générer/mettre à jour uniquement les hubs (rapide, ~40s)
ASTRO_FILTER=hubs_only npm run build

# Preview local
npm run preview
```

## Production (Cloudflare Pages / CI — pas de timeout)

```bash
npm run build   # ~55-60s, génère ~532 pages
```

## Après modification de knowledge_map.json

```bash
# 1. Valider les données
python scripts/sync_knowledge.py --validate

# 2. Rebuilder les hubs
ASTRO_FILTER=hubs_only npm run build
```

## Pages générées (build complet)

| Route | Count |
|-------|-------|
| `/[service]/[zone]/[ville]/` | ~444 pages (73 nord×3 + 75 sud×2) |
| `/[service]/[zone]/` | 5 zone hubs |
| `/[service]/` | 5 service hubs |
| `/` | 1 homepage |
| **Total** | **~455 pages** |
