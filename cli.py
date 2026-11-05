#!/usr/bin/env python3
"""
Compliance-as-Code — CLI

Génère un rapport de conformité (Excel) à partir d'un référentiel de
contrôles (YAML) et des réponses d'audit (CSV).

Exemple :
    python cli.py --referentiel referentiels/nis2.yaml \\
                   --reponses exemples/reponses_exemple_nis2.csv \\
                   --organisation "PME Exemple SARL" \\
                   --out rapports/rapport_nis2.xlsx
"""

import argparse
import sys
from pathlib import Path

from compliance_tool.loader import charger_referentiel, charger_reponses
from compliance_tool.report_excel import generer_rapport_excel
from compliance_tool.scoring import generer_rapport


def parser_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Génère un rapport de conformité Excel à partir d'un référentiel YAML et de réponses d'audit CSV."
    )
    parser.add_argument(
        "--referentiel", required=True,
        help="Chemin du fichier YAML du référentiel (ex: referentiels/nis2.yaml)",
    )
    parser.add_argument(
        "--reponses", required=True,
        help="Chemin du fichier CSV des réponses d'audit",
    )
    parser.add_argument(
        "--out", default="rapports/rapport_conformite.xlsx",
        help="Chemin du fichier Excel à générer (défaut: rapports/rapport_conformite.xlsx)",
    )
    parser.add_argument(
        "--nom-referentiel", default=None,
        help="Nom du référentiel affiché dans le rapport (défaut : nom du fichier)",
    )
    parser.add_argument(
        "--organisation", default="Organisation auditée",
        help="Nom de l'organisation auditée, affiché dans le rapport",
    )
    return parser.parse_args()


def main() -> int:
    args = parser_arguments()

    try:
        controles = charger_referentiel(args.referentiel)
        reponses = charger_reponses(args.reponses)
    except (FileNotFoundError, ValueError) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

    rapport = generer_rapport(controles, reponses)

    nom_referentiel = args.nom_referentiel or Path(args.referentiel).stem
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    chemin = generer_rapport_excel(
        rapport,
        chemin_sortie=args.out,
        nom_referentiel=nom_referentiel,
        nom_organisation=args.organisation,
    )

    print(f"Rapport généré : {chemin}")
    print(f"Taux de conformité global : {rapport.taux_global} %")
    print(f"Contrôles en écart (plan d'action) : {len(rapport.plan_action)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
