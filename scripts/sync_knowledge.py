#!/usr/bin/env python3
"""
sync_knowledge.py — Pipeline de synchronisation du cerveau de données
======================================================================
Unique point de mise à jour autorisé pour data/knowledge_map.json.

Usage:
  python scripts/sync_knowledge.py                    # Sync complète
  python scripts/sync_knowledge.py --validate         # Validation seule (dry-run)
  python scripts/sync_knowledge.py --add-commune      # Assistant ajout commune
  python scripts/sync_knowledge.py --report           # Rapport de l'état actuel

RÈGLE ABSOLUE : Ce script ne lit JAMAIS COMPILATION_AVEC_DATES.txt directement.
Les données entrantes doivent être fournies via --input-file ou stdin en JSON.
"""

import json
import sys
import os
import argparse
import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Chemins ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "knowledge_map.json"
BACKUP_DIR = ROOT / "data" / ".backups"

# ── Schema de validation (Zod-like en Python) ─────────────────────────────────

REQUIRED_COMMUNE_KEYS = {
    "slug", "name", "insee", "cp", "zone", "population",
    "geo", "assainissement", "spanc", "adjacentes", "seo", "artisans"
}

REQUIRED_GEO_KEYS = {"lat", "lng"}
REQUIRED_SEO_KEYS = {"priorite", "volumeEstimeMensuel", "titleDebouchage", "metaDescription"}
VALID_ZONES = {"nord", "sud"}
VALID_ASSAINISSEMENT = {"collectif", "non-collectif", "mixte"}
VALID_PRIORITES = {"haute", "moyenne", "basse"}


# ── Validation ────────────────────────────────────────────────────────────────

def validate_commune(commune: dict, index: int) -> list[str]:
    """Valide une commune et retourne la liste des erreurs."""
    errors = []
    slug = commune.get("slug", f"commune[{index}]")

    # Clés obligatoires
    missing = REQUIRED_COMMUNE_KEYS - set(commune.keys())
    if missing:
        errors.append(f"[{slug}] Clés manquantes : {missing}")

    # Zone valide
    if commune.get("zone") not in VALID_ZONES:
        errors.append(f"[{slug}] zone invalide : '{commune.get('zone')}' (attendu: {VALID_ZONES})")

    # Assainissement valide
    if commune.get("assainissement") not in VALID_ASSAINISSEMENT:
        errors.append(f"[{slug}] assainissement invalide : '{commune.get('assainissement')}'")

    # Geo
    geo = commune.get("geo", {})
    if not isinstance(geo, dict) or not REQUIRED_GEO_KEYS.issubset(geo.keys()):
        errors.append(f"[{slug}] geo invalide (requis: lat, lng)")

    # SEO
    seo = commune.get("seo", {})
    if not isinstance(seo, dict):
        errors.append(f"[{slug}] seo doit être un objet")
    else:
        missing_seo = REQUIRED_SEO_KEYS - set(seo.keys())
        if missing_seo:
            errors.append(f"[{slug}] seo.{missing_seo} manquant(s)")
        if seo.get("priorite") not in VALID_PRIORITES:
            errors.append(f"[{slug}] seo.priorite invalide : '{seo.get('priorite')}'")

    # CP doit être une liste
    if not isinstance(commune.get("cp"), list):
        errors.append(f"[{slug}] cp doit être une liste (ex: [\"91000\"])")

    # Slug cohérent avec le nom (avertissement uniquement)
    # ISBN check : communes Sud sans SPANC assigné
    if commune.get("zone") == "sud" and commune.get("assainissement") != "collectif":
        if commune.get("spanc") is None:
            errors.append(f"[{slug}] AVERTISSEMENT : commune Sud non-collectif sans SPANC assigné")

    return errors


def validate_knowledge_map(data: dict) -> tuple[bool, list[str]]:
    """Valide la structure complète du knowledge_map. Retourne (is_valid, errors)."""
    errors = []

    # Clés racine obligatoires
    for key in ["_meta", "zones", "communes", "services", "spanc", "eeat", "artisans"]:
        if key not in data:
            errors.append(f"Clé racine manquante : '{key}'")

    # Communes
    communes = data.get("communes", [])
    if not isinstance(communes, list):
        errors.append("'communes' doit être une liste")
    else:
        slugs = [c.get("slug") for c in communes]
        # Doublons
        seen = set()
        for slug in slugs:
            if slug in seen:
                errors.append(f"Slug en doublon : '{slug}'")
            seen.add(slug)
        # Validation individuelle
        for i, commune in enumerate(communes):
            errors.extend(validate_commune(commune, i))

    # Cohérence zones/communes
    zones_data = data.get("zones", {})
    for zone_key, zone in zones_data.items():
        for commune_slug in zone.get("communes", []):
            slugs_existing = [c.get("slug") for c in data.get("communes", [])]
            if commune_slug not in slugs_existing:
                errors.append(
                    f"Zone '{zone_key}' référence une commune inexistante : '{commune_slug}'"
                )

    is_valid = len([e for e in errors if "AVERTISSEMENT" not in e]) == 0
    return is_valid, errors


# ── Backup ────────────────────────────────────────────────────────────────────

def backup_current(data: dict) -> Path:
    """Sauvegarde l'état courant avant toute modification."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup_path = BACKUP_DIR / f"knowledge_map_{ts}.json"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return backup_path


# ── Chargement ────────────────────────────────────────────────────────────────

def load_knowledge_map() -> dict:
    if not DATA_FILE.exists():
        print(f"[ERREUR] Fichier introuvable : {DATA_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_knowledge_map(data: dict) -> None:
    # Mettre à jour le timestamp de sync
    data["_meta"]["lastSync"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["_meta"]["communeCount"] = len(data.get("communes", []))
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Merge ─────────────────────────────────────────────────────────────────────

def merge_communes(existing: dict, incoming: list[dict]) -> tuple[int, int, int]:
    """
    Fusionne les nouvelles communes dans le knowledge_map.
    Stratégie : upsert par slug (ajout si nouveau, mise à jour si existant).
    Retourne (ajoutées, mises_à_jour, ignorées).
    """
    existing_by_slug = {c["slug"]: i for i, c in enumerate(existing["communes"])}
    added = updated = skipped = 0

    for commune in incoming:
        slug = commune.get("slug")
        if not slug:
            print(f"  [IGNORÉ] Commune sans slug : {commune.get('name', '?')}")
            skipped += 1
            continue

        if slug in existing_by_slug:
            # Mise à jour : on ne touche pas aux artisans mockés
            idx = existing_by_slug[slug]
            old = existing["communes"][idx]
            merged = {**old, **commune}
            # Préserver les artisans existants si la commune entrante n'en a pas
            if not commune.get("artisans") and old.get("artisans"):
                merged["artisans"] = old["artisans"]
            existing["communes"][idx] = merged
            updated += 1
            print(f"  [MIS À JOUR] {slug}")
        else:
            existing["communes"].append(commune)
            added += 1
            print(f"  [AJOUTÉ] {slug}")

    return added, updated, skipped


# ── Commandes ─────────────────────────────────────────────────────────────────

def cmd_validate(data: dict) -> None:
    """Valide le fichier courant et affiche le rapport."""
    print(f"\n{'='*60}")
    print("VALIDATION DU KNOWLEDGE_MAP")
    print(f"{'='*60}")
    is_valid, errors = validate_knowledge_map(data)

    warnings = [e for e in errors if "AVERTISSEMENT" in e]
    hard_errors = [e for e in errors if "AVERTISSEMENT" not in e]

    if hard_errors:
        print(f"\n[ERREURS] {len(hard_errors)} problème(s) bloquant(s) :")
        for err in hard_errors:
            print(f"  ✗ {err}")
    if warnings:
        print(f"\n[AVERTISSEMENTS] {len(warnings)} point(s) d'attention :")
        for warn in warnings:
            print(f"  ⚠ {warn}")

    print(f"\n{'─'*60}")
    if is_valid:
        print(f"  ✓ JSON valide — {len(data['communes'])} communes, {len(data['services'])} services")
    else:
        print(f"  ✗ {len(hard_errors)} erreur(s) bloquante(s) à corriger")
    print(f"{'='*60}\n")

    sys.exit(0 if is_valid else 1)


def cmd_report(data: dict) -> None:
    """Affiche un rapport synthétique de l'état du knowledge_map."""
    meta = data.get("_meta", {})
    communes = data.get("communes", [])
    artisans_total = sum(len(c.get("artisans", [])) for c in communes)
    premium_count = sum(
        1 for a in data.get("artisans", {}).get("items", []) if a.get("premium")
    )

    print(f"""
╔══════════════════════════════════════════════════════╗
║        KNOWLEDGE MAP — ÉTAT ACTUEL                   ║
╠══════════════════════════════════════════════════════╣
║  Version    : {meta.get('version', '?'):<38} ║
║  Dernière sync : {meta.get('lastSync', '?'):<35} ║
║  Seed only  : {str(meta.get('seedOnly', '?')):<38} ║
╠══════════════════════════════════════════════════════╣
║  Communes   : {len(communes):<38} ║
║    → Nord   : {sum(1 for c in communes if c.get('zone')=='nord'):<38} ║
║    → Sud    : {sum(1 for c in communes if c.get('zone')=='sud'):<38} ║
║  Services   : {len(data.get('services', {})):<38} ║
║  SPANC      : {len(data.get('spanc', {})):<38} ║
║  Artisans   : {artisans_total} dans communes + {len(data.get('artisans',{}).get('items',[]))} mockés   ║
║  Premium    : {premium_count:<38} ║
╚══════════════════════════════════════════════════════╝
""")


def cmd_sync(data: dict, input_file: str | None) -> None:
    """Synchronise avec des données entrantes (JSON)."""
    if not input_file:
        print("[INFO] Aucun --input-file fourni. Validation et mise à jour du timestamp uniquement.")
        is_valid, errors = validate_knowledge_map(data)
        if not is_valid:
            hard = [e for e in errors if "AVERTISSEMENT" not in e]
            print(f"[ERREUR] {len(hard)} erreur(s) bloquante(s). Sync annulée.")
            for e in hard:
                print(f"  ✗ {e}")
            sys.exit(1)
        backup_path = backup_current(data)
        print(f"[BACKUP] {backup_path.name}")
        save_knowledge_map(data)
        print(f"[OK] Timestamp mis à jour — {len(data['communes'])} communes.")
        return

    with open(input_file, encoding="utf-8") as f:
        incoming = json.load(f)

    communes_in = incoming if isinstance(incoming, list) else incoming.get("communes", [])
    print(f"\n[SYNC] {len(communes_in)} commune(s) entrante(s)")

    backup_path = backup_current(data)
    print(f"[BACKUP] {backup_path.name}")

    added, updated, skipped = merge_communes(data, communes_in)

    # Validation post-merge
    is_valid, errors = validate_knowledge_map(data)
    hard_errors = [e for e in errors if "AVERTISSEMENT" not in e]
    if hard_errors:
        print(f"\n[ERREUR] Validation échouée après merge — rollback")
        for e in hard_errors:
            print(f"  ✗ {e}")
        sys.exit(1)

    save_knowledge_map(data)
    print(f"\n[RÉSULTAT] Ajoutées: {added} | Mises à jour: {updated} | Ignorées: {skipped}")
    print(f"[OK] knowledge_map.json synchronisé — {len(data['communes'])} communes total.")


# ── Entrypoint ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de synchronisation du knowledge_map.json"
    )
    parser.add_argument("--validate", action="store_true", help="Validation seule (dry-run)")
    parser.add_argument("--report", action="store_true", help="Rapport de l'état actuel")
    parser.add_argument("--input-file", type=str, help="Fichier JSON de communes à merger")
    args = parser.parse_args()

    data = load_knowledge_map()

    if args.validate:
        cmd_validate(data)
    elif args.report:
        cmd_report(data)
    else:
        cmd_sync(data, args.input_file)


if __name__ == "__main__":
    main()
