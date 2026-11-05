# Compliance-as-Code — Audit de conformité ISO 27001 / NIS2 automatisé

Un outil en Python qui transforme un référentiel de conformité (ISO 27001,
NIS2...) en **audit exploitable** : il croise les contrôles du référentiel
avec les réponses d'un audit, calcule les taux de conformité, et génère un
**rapport Excel professionnel** (synthèse graphique, détail des contrôles,
plan d'action priorisé par criticité).

> Projet compagnon du **Guide pratique NIS2 pour PME** : là où le guide
> explique *quoi* faire, cet outil aide à *mesurer où on en est* et à
> prioriser les actions restantes.

![Aperçu de la synthèse du rapport](docs/images/synthese_apercu.png)

## Pourquoi ce projet

Les PME et institutions qui doivent se conformer à NIS2 ou ISO 27001 n'ont
souvent ni RSSI interne, ni budget pour un audit coûteux. La plupart des
checklists de conformité existent en PDF ou en tableur statique : utiles
pour lire, inutiles pour **suivre dans le temps** ou produire un rapport
présentable à une direction.

Ce projet répond à un besoin concret : un référentiel **réutilisable et
versionnable** (YAML), un audit **reproductible** (le même script donne
toujours le même rapport pour les mêmes réponses), et une sortie **prête à
être partagée** (Excel avec graphiques, pas un export brut).

## Fonctionnalités

- Référentiels de contrôles en YAML, faciles à étendre ou à adapter à un
  autre cadre normatif (ANCS, PCI DSS, etc.)
- Calcul du taux de conformité global et par domaine (un contrôle `partiel`
  compte pour une demi-conformité)
- Plan d'action automatiquement **priorisé par criticité**, avec la preuve
  attendue et une action recommandée pour chaque écart
- Rapport Excel à 3 onglets : **Synthèse** (graphiques), **Détail des
  contrôles** (code couleur par statut), **Plan d'action**
- Gestion explicite du `non_applicable` (exclu du calcul du taux)
- Un contrôle du référentiel sans réponse d'audit n'est jamais ignoré : il
  apparaît en `non_conforme` avec un commentaire à compléter — aucun écart
  ne peut passer sous le radar

## Installation

```bash
git clone https://github.com/<votre-compte>/compliance-as-code.git
cd compliance-as-code
pip install -r requirements.txt
```

Nécessite Python 3.9+.

## Utilisation

```bash
python cli.py \
  --referentiel referentiels/nis2.yaml \
  --reponses exemples/reponses_exemple_nis2.csv \
  --organisation "PME Exemple SARL" \
  --nom-referentiel "NIS2 (sous-ensemble)" \
  --out rapports/rapport_nis2.xlsx
```

```
Rapport généré : rapports/rapport_nis2.xlsx
Taux de conformité global : 50.0 %
Contrôles en écart (plan d'action) : 11
```

Même logique avec le référentiel ISO 27001 fourni :

```bash
python cli.py \
  --referentiel referentiels/iso27001_annexe_a.yaml \
  --reponses exemples/reponses_exemple_iso27001.csv \
  --organisation "PME Exemple SARL" \
  --out rapports/rapport_iso27001.xlsx
```

### Options

| Option | Description |
|---|---|
| `--referentiel` | Fichier YAML du référentiel (obligatoire) |
| `--reponses` | Fichier CSV des réponses d'audit (obligatoire) |
| `--out` | Chemin du rapport Excel à générer |
| `--organisation` | Nom affiché dans l'en-tête du rapport |
| `--nom-referentiel` | Nom du référentiel affiché (défaut : nom du fichier) |

## Format du référentiel (YAML)

```yaml
- id: "NIS2-1.1"
  domaine: "1. Analyse des risques et politique de sécurité"
  controle: "Politique de sécurité des systèmes d'information"
  description: "..."
  preuve_attendue: "Document de politique SSI signé et daté"
  criticite: "Élevée"           # Élevée | Moyenne | Faible
  action_recommandee: "..."
  reference: "Directive (UE) 2022/2555, art. 21(2)(a)"
```

## Format des réponses d'audit (CSV)

```csv
control_id,statut,preuve_fournie,commentaire
NIS2-1.1,conforme,oui,Politique SSI v2 approuvée par la direction en mars 2026
NIS2-2.2,non_conforme,non,Aucun processus de notification réglementaire formalisé
```

Statuts acceptés : `conforme`, `non_conforme`, `partiel`, `non_applicable`.

## Architecture du projet

```
compliance-as-code/
├── referentiels/              # Référentiels de contrôles (YAML)
│   ├── nis2.yaml
│   └── iso27001_annexe_a.yaml
├── compliance_tool/            # Package Python
│   ├── models.py               # Structures de données (Control, Finding...)
│   ├── loader.py                # Chargement YAML/CSV
│   ├── scoring.py               # Calcul des taux et du plan d'action
│   └── report_excel.py          # Génération du rapport Excel
├── exemples/                   # Réponses d'audit factices, pour la démo
├── rapports/                   # Rapports générés (ignorés par git)
├── tests/                      # Tests unitaires du moteur de scoring
└── cli.py                      # Point d'entrée en ligne de commande
```

## Étendre à un autre référentiel

Ajouter un nouveau cadre normatif (PCI DSS, ANCS...) se résume à créer un
nouveau fichier YAML suivant le même schéma — aucune modification du code
n'est nécessaire.

## Tests

```bash
python tests/test_scoring.py
```

## Limites et avertissement

- Les référentiels fournis (`referentiels/`) sont des **sous-ensembles
  pédagogiques**, reformulés librement à partir des textes publics de la
  directive NIS2 et de la structure de l'Annexe A d'ISO/IEC 27001:2022.
  Ils ne remplacent pas le texte officiel de la norme (ISO 27001 est
  protégée par le droit d'auteur ISO) ni un audit mené par un professionnel
  qualifié.
- Les fichiers d'exemple dans `exemples/` contiennent des données
  **entièrement fictives**, pour la démonstration.
- Cet outil mesure un état déclaratif (ce que l'auditeur a constaté et
  consigné) — il ne remplace pas la collecte de preuves elle-même.

## À propos

Projet réalisé par **Sahar Hamdi**, Ingénieure Cybersécurité / RSSI,
spécialisée en GRC, audit de conformité (ISO 27001, NIS2) et IAM/PAM.

- LinkedIn : *(lien à compléter)*
- Autres projets portfolio : [Risk Management Lab](#), [Secure IaC Lab](#)

## Licence

MIT — voir [LICENSE](LICENSE).
