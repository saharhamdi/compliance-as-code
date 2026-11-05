"""Chargement du référentiel (YAML) et des réponses d'audit (CSV)."""

import csv
from pathlib import Path
from typing import Dict, List

import yaml

from .models import Control


def charger_referentiel(chemin_yaml: str) -> List[Control]:
    """Lit un fichier YAML de référentiel et retourne une liste de Control."""
    chemin = Path(chemin_yaml)
    if not chemin.exists():
        raise FileNotFoundError(f"Référentiel introuvable : {chemin_yaml}")

    with chemin.open(encoding="utf-8") as f:
        donnees = yaml.safe_load(f)

    if not isinstance(donnees, list):
        raise ValueError(
            f"Le référentiel {chemin_yaml} doit être une liste de contrôles YAML."
        )

    controles = []
    champs_requis = {"id", "domaine", "controle", "description", "preuve_attendue", "criticite", "reference"}
    for entree in donnees:
        manquants = champs_requis - entree.keys()
        if manquants:
            raise ValueError(
                f"Contrôle {entree.get('id', '?')} : champs manquants {manquants}"
            )
        controles.append(
            Control(
                id=entree["id"],
                domaine=entree["domaine"],
                controle=entree["controle"],
                description=entree["description"].strip(),
                preuve_attendue=entree["preuve_attendue"],
                criticite=entree["criticite"],
                reference=entree["reference"],
                action_recommandee=entree.get("action_recommandee", ""),
            )
        )

    _verifier_ids_uniques(controles, chemin_yaml)
    return controles


def _verifier_ids_uniques(controles: List[Control], source: str) -> None:
    vus = set()
    for c in controles:
        if c.id in vus:
            raise ValueError(f"Identifiant de contrôle dupliqué '{c.id}' dans {source}")
        vus.add(c.id)


def charger_reponses(chemin_csv: str) -> Dict[str, dict]:
    """Lit le CSV des réponses d'audit, indexé par control_id."""
    chemin = Path(chemin_csv)
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier de réponses introuvable : {chemin_csv}")

    reponses: Dict[str, dict] = {}
    with chemin.open(encoding="utf-8", newline="") as f:
        lecteur = csv.DictReader(f)
        colonnes_requises = {"control_id", "statut"}
        if not colonnes_requises.issubset(lecteur.fieldnames or []):
            raise ValueError(
                f"Le fichier {chemin_csv} doit contenir au moins les colonnes {colonnes_requises}"
            )
        for ligne in lecteur:
            reponses[ligne["control_id"]] = {
                "statut": ligne["statut"].strip(),
                "preuve_fournie": ligne.get("preuve_fournie", "non").strip(),
                "commentaire": ligne.get("commentaire", "").strip(),
            }
    return reponses
