#!/usr/bin/env python3
"""
Valide tous les référentiels YAML du dossier referentiels/.

Vérifie :
- que le fichier se charge correctement (YAML valide, champs requis présents)
- que les identifiants de contrôle sont uniques
- que la criticité est l'une des valeurs attendues

Utilisé en local avant un commit, et par le workflow GitHub Actions (CI).
Code de sortie 0 si tout est valide, 1 sinon.
"""

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from compliance_tool.loader import charger_referentiel  # noqa: E402
from compliance_tool.models import CRITICITES_ORDRE  # noqa: E402

DOSSIER_REFERENTIELS = RACINE / "referentiels"


def valider_un_fichier(chemin: Path) -> list:
    erreurs = []
    try:
        controles = charger_referentiel(str(chemin))
    except (FileNotFoundError, ValueError) as e:
        return [f"{chemin.name} : {e}"]

    for c in controles:
        if c.criticite not in CRITICITES_ORDRE:
            erreurs.append(
                f"{chemin.name} [{c.id}] : criticité invalide '{c.criticite}' "
                f"(attendu : {sorted(CRITICITES_ORDRE)})"
            )
        if not c.description.strip():
            erreurs.append(f"{chemin.name} [{c.id}] : description vide")
        if not c.preuve_attendue.strip():
            erreurs.append(f"{chemin.name} [{c.id}] : preuve_attendue vide")

    print(f"  {chemin.name} : {len(controles)} contrôle(s) chargé(s)")
    return erreurs


def main() -> int:
    if not DOSSIER_REFERENTIELS.exists():
        print(f"Dossier introuvable : {DOSSIER_REFERENTIELS}", file=sys.stderr)
        return 1

    fichiers = sorted(DOSSIER_REFERENTIELS.glob("*.yaml"))
    if not fichiers:
        print("Aucun référentiel YAML trouvé.", file=sys.stderr)
        return 1

    print(f"Validation de {len(fichiers)} référentiel(s)...")
    toutes_erreurs = []
    for f in fichiers:
        toutes_erreurs.extend(valider_un_fichier(f))

    if toutes_erreurs:
        print("\nErreurs de validation :", file=sys.stderr)
        for e in toutes_erreurs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("\nTous les référentiels sont valides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
