"""Croisement référentiel / réponses, calcul des taux et du plan d'action."""

from typing import Dict, List

from .models import (
    CRITICITES_ORDRE,
    Control,
    DomaineSynthese,
    Finding,
    RapportConformite,
)


def construire_findings(controles: List[Control], reponses: Dict[str, dict]) -> List[Finding]:
    """Associe chaque contrôle du référentiel à sa réponse d'audit.

    Un contrôle du référentiel qui n'a pas de réponse dans le CSV est
    considéré comme 'non_conforme' par défaut (absence de preuve = écart),
    avec un commentaire explicite pour que l'auditeur le complète.
    """
    findings = []
    for controle in controles:
        reponse = reponses.get(controle.id)
        if reponse is None:
            findings.append(
                Finding(
                    control=controle,
                    statut="non_conforme",
                    preuve_fournie="non",
                    commentaire="Aucune réponse d'audit fournie pour ce contrôle (à compléter)",
                )
            )
        else:
            findings.append(
                Finding(
                    control=controle,
                    statut=reponse["statut"],
                    preuve_fournie=reponse.get("preuve_fournie", "non"),
                    commentaire=reponse.get("commentaire", ""),
                )
            )
    return findings


def calculer_syntheses_par_domaine(findings: List[Finding]) -> List[DomaineSynthese]:
    """Agrège les findings par domaine, dans l'ordre d'apparition du référentiel."""
    ordre_domaines: List[str] = []
    syntheses: Dict[str, DomaineSynthese] = {}

    for f in findings:
        d = f.control.domaine
        if d not in syntheses:
            syntheses[d] = DomaineSynthese(domaine=d)
            ordre_domaines.append(d)
        s = syntheses[d]
        s.total += 1
        if f.statut == "conforme":
            s.conformes += 1
        elif f.statut == "partiel":
            s.partiels += 1
        elif f.statut == "non_conforme":
            s.non_conformes += 1
        elif f.statut == "non_applicable":
            s.non_applicables += 1

    return [syntheses[d] for d in ordre_domaines]


def calculer_taux_global(findings: List[Finding]) -> float:
    applicables = [f for f in findings if f.est_applicable]
    if not applicables:
        return 0.0
    score = sum(1.0 if f.statut == "conforme" else 0.5 if f.statut == "partiel" else 0.0 for f in applicables)
    return round(100 * score / len(applicables), 1)


def construire_plan_action(findings: List[Finding]) -> List[Finding]:
    """Retourne les écarts (non_conforme / partiel), triés par criticité puis domaine."""
    ecarts = [f for f in findings if f.est_un_ecart]
    ecarts.sort(
        key=lambda f: (
            CRITICITES_ORDRE.get(f.control.criticite, 99),
            f.control.domaine,
            f.control.id,
        )
    )
    return ecarts


def generer_rapport(controles: List[Control], reponses: Dict[str, dict]) -> RapportConformite:
    """Point d'entrée unique : construit le RapportConformite complet."""
    findings = construire_findings(controles, reponses)
    return RapportConformite(
        findings=findings,
        syntheses_par_domaine=calculer_syntheses_par_domaine(findings),
        taux_global=calculer_taux_global(findings),
        plan_action=construire_plan_action(findings),
    )
