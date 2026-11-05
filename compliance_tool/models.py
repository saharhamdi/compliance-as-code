"""Structures de données du projet Compliance-as-Code."""

from dataclasses import dataclass, field
from typing import Optional

STATUTS_VALIDES = {"conforme", "non_conforme", "partiel", "non_applicable"}
CRITICITES_ORDRE = {"Élevée": 0, "Moyenne": 1, "Faible": 2}


@dataclass
class Control:
    """Un contrôle issu du référentiel (YAML)."""

    id: str
    domaine: str
    controle: str
    description: str
    preuve_attendue: str
    criticite: str
    reference: str
    action_recommandee: str = ""


@dataclass
class Finding:
    """Le résultat d'audit d'un contrôle : le contrôle + la réponse fournie."""

    control: Control
    statut: str
    preuve_fournie: str = "non"
    commentaire: str = ""

    def __post_init__(self) -> None:
        if self.statut not in STATUTS_VALIDES:
            raise ValueError(
                f"Statut invalide '{self.statut}' pour {self.control.id}. "
                f"Valeurs acceptées : {sorted(STATUTS_VALIDES)}"
            )

    @property
    def est_applicable(self) -> bool:
        return self.statut != "non_applicable"

    @property
    def est_un_ecart(self) -> bool:
        return self.statut in {"non_conforme", "partiel"}


@dataclass
class DomaineSynthese:
    """Synthèse agrégée pour un domaine du référentiel."""

    domaine: str
    total: int = 0
    conformes: int = 0
    partiels: int = 0
    non_conformes: int = 0
    non_applicables: int = 0

    @property
    def applicables(self) -> int:
        return self.total - self.non_applicables

    @property
    def taux_conformite(self) -> Optional[float]:
        if self.applicables == 0:
            return None
        # un contrôle "partiel" compte pour une demi-conformité
        score = self.conformes + 0.5 * self.partiels
        return round(100 * score / self.applicables, 1)


@dataclass
class RapportConformite:
    """Résultat complet d'un audit : findings + synthèses."""

    findings: list = field(default_factory=list)
    syntheses_par_domaine: list = field(default_factory=list)
    taux_global: Optional[float] = None
    plan_action: list = field(default_factory=list)
