"""Tests unitaires de base pour le moteur de scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compliance_tool.models import Control
from compliance_tool.scoring import (
    calculer_syntheses_par_domaine,
    calculer_taux_global,
    construire_findings,
    construire_plan_action,
)


def _controle(id_, domaine="Domaine A", criticite="Moyenne"):
    return Control(
        id=id_,
        domaine=domaine,
        controle=f"Contrôle {id_}",
        description="desc",
        preuve_attendue="preuve",
        criticite=criticite,
        reference="REF",
        action_recommandee="action",
    )


def test_taux_global_tous_conformes():
    controles = [_controle("C1"), _controle("C2")]
    reponses = {
        "C1": {"statut": "conforme", "preuve_fournie": "oui", "commentaire": ""},
        "C2": {"statut": "conforme", "preuve_fournie": "oui", "commentaire": ""},
    }
    findings = construire_findings(controles, reponses)
    assert calculer_taux_global(findings) == 100.0


def test_taux_global_avec_partiel_et_na():
    controles = [_controle("C1"), _controle("C2"), _controle("C3")]
    reponses = {
        "C1": {"statut": "conforme", "preuve_fournie": "oui", "commentaire": ""},
        "C2": {"statut": "partiel", "preuve_fournie": "oui", "commentaire": ""},
        "C3": {"statut": "non_applicable", "preuve_fournie": "non", "commentaire": ""},
    }
    findings = construire_findings(controles, reponses)
    # 2 applicables : 1 conforme (1.0) + 1 partiel (0.5) = 1.5 / 2 = 75%
    assert calculer_taux_global(findings) == 75.0


def test_reponse_manquante_devient_non_conforme():
    controles = [_controle("C1")]
    findings = construire_findings(controles, reponses={})
    assert findings[0].statut == "non_conforme"
    assert "Aucune réponse" in findings[0].commentaire


def test_plan_action_trie_par_criticite():
    controles = [
        _controle("C1", criticite="Faible"),
        _controle("C2", criticite="Élevée"),
        _controle("C3", criticite="Moyenne"),
    ]
    reponses = {
        "C1": {"statut": "non_conforme", "preuve_fournie": "non", "commentaire": ""},
        "C2": {"statut": "non_conforme", "preuve_fournie": "non", "commentaire": ""},
        "C3": {"statut": "partiel", "preuve_fournie": "non", "commentaire": ""},
    }
    findings = construire_findings(controles, reponses)
    plan = construire_plan_action(findings)
    assert [f.control.id for f in plan] == ["C2", "C3", "C1"]


def test_syntheses_par_domaine():
    controles = [
        _controle("C1", domaine="D1"),
        _controle("C2", domaine="D1"),
        _controle("C3", domaine="D2"),
    ]
    reponses = {
        "C1": {"statut": "conforme", "preuve_fournie": "oui", "commentaire": ""},
        "C2": {"statut": "non_conforme", "preuve_fournie": "non", "commentaire": ""},
        "C3": {"statut": "conforme", "preuve_fournie": "oui", "commentaire": ""},
    }
    findings = construire_findings(controles, reponses)
    syntheses = calculer_syntheses_par_domaine(findings)
    d1 = next(s for s in syntheses if s.domaine == "D1")
    d2 = next(s for s in syntheses if s.domaine == "D2")
    assert d1.taux_conformite == 50.0
    assert d2.taux_conformite == 100.0


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    echecs = 0
    for t in tests:
        try:
            t()
            print(f"OK   {t.__name__}")
        except Exception:
            echecs += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - echecs}/{len(tests)} tests réussis")
    raise SystemExit(1 if echecs else 0)
