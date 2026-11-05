"""Génération du rapport Excel (Synthèse, Détail des contrôles, Plan d'action)."""

from datetime import date

from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from .models import RapportConformite

POLICE = "Arial"
BLEU_FONCE = "1F3864"
VERT = "C6EFCE"
VERT_TEXTE = "006100"
ORANGE = "FFEB9C"
ORANGE_TEXTE = "9C6500"
ROUGE = "FFC7CE"
ROUGE_TEXTE = "9C0006"
GRIS = "F2F2F2"

BORDURE = Border(
    left=Side(style="thin", color="BFBFBF"),
    right=Side(style="thin", color="BFBFBF"),
    top=Side(style="thin", color="BFBFBF"),
    bottom=Side(style="thin", color="BFBFBF"),
)

COULEURS_STATUT = {
    "conforme": (VERT, VERT_TEXTE),
    "partiel": (ORANGE, ORANGE_TEXTE),
    "non_conforme": (ROUGE, ROUGE_TEXTE),
    "non_applicable": (GRIS, "595959"),
}

LIBELLES_STATUT = {
    "conforme": "Conforme",
    "partiel": "Partiel",
    "non_conforme": "Non conforme",
    "non_applicable": "Non applicable",
}


def _entete(ws, colonnes, ligne=1):
    for i, texte in enumerate(colonnes, start=1):
        cell = ws.cell(row=ligne, column=i, value=texte)
        cell.font = Font(name=POLICE, bold=True, color="FFFFFF", size=10)
        cell.fill = PatternFill("solid", fgColor=BLEU_FONCE)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDURE


def _feuille_synthese(wb: Workbook, rapport: RapportConformite, nom_referentiel: str, nom_organisation: str):
    ws = wb.active
    ws.title = "Synthèse"

    ws.merge_cells("A1:F1")
    ws["A1"] = f"Rapport de conformité — {nom_referentiel}"
    ws["A1"].font = Font(name=POLICE, bold=True, size=16, color=BLEU_FONCE)

    ws["A2"] = f"Organisation : {nom_organisation}"
    ws["A3"] = f"Date du rapport : {date.today().strftime('%d/%m/%Y')}"
    for c in ("A2", "A3"):
        ws[c].font = Font(name=POLICE, size=11, color="595959")

    ws["A5"] = "Taux de conformité global"
    ws["A5"].font = Font(name=POLICE, bold=True, size=13)
    ws["B5"] = (rapport.taux_global or 0) / 100
    ws["B5"].number_format = "0.0%"
    ws["B5"].font = Font(name=POLICE, bold=True, size=20, color=BLEU_FONCE)

    # Répartition globale des statuts, pour le graphique en secteurs
    total_par_statut = {"conforme": 0, "partiel": 0, "non_conforme": 0, "non_applicable": 0}
    for f in rapport.findings:
        total_par_statut[f.statut] += 1

    ws["A7"] = "Statut"
    ws["B7"] = "Nombre de contrôles"
    ws["A7"].font = ws["B7"].font = Font(name=POLICE, bold=True)
    ligne = 8
    for statut, libelle in LIBELLES_STATUT.items():
        ws.cell(row=ligne, column=1, value=libelle)
        ws.cell(row=ligne, column=2, value=total_par_statut[statut])
        ligne += 1

    pie = PieChart()
    pie.title = "Répartition des contrôles par statut"
    data = Reference(ws, min_col=2, min_row=7, max_row=ligne - 1)
    cats = Reference(ws, min_col=1, min_row=8, max_row=ligne - 1)
    pie.add_data(data, titles_from_data=True)
    pie.set_categories(cats)
    pie.height = 8
    pie.width = 12
    ws.add_chart(pie, "D7")

    # Taux de conformité par domaine
    debut_domaine = ligne + 2
    ws.cell(row=debut_domaine, column=1, value="Domaine").font = Font(name=POLICE, bold=True)
    ws.cell(row=debut_domaine, column=2, value="Taux de conformité").font = Font(name=POLICE, bold=True)
    l = debut_domaine + 1
    for s in rapport.syntheses_par_domaine:
        ws.cell(row=l, column=1, value=s.domaine)
        taux = (s.taux_conformite or 0) / 100
        cell = ws.cell(row=l, column=2, value=taux)
        cell.number_format = "0.0%"
        l += 1

    bar = BarChart()
    bar.type = "bar"
    bar.title = "Taux de conformité par domaine"
    data = Reference(ws, min_col=2, min_row=debut_domaine, max_row=l - 1)
    cats = Reference(ws, min_col=1, min_row=debut_domaine + 1, max_row=l - 1)
    bar.add_data(data, titles_from_data=True)
    bar.set_categories(cats)
    bar.height = 10
    bar.width = 18
    bar.y_axis.numFmt = "0%"
    ws.add_chart(bar, f"D{debut_domaine}")

    for col, largeur in zip("ABCDEF", (32, 18, 14, 14, 14, 14)):
        ws.column_dimensions[col].width = largeur


def _feuille_detail(wb: Workbook, rapport: RapportConformite):
    ws = wb.create_sheet("Détail des contrôles")
    colonnes = [
        "ID", "Domaine", "Contrôle", "Criticité", "Statut",
        "Preuve fournie", "Commentaire", "Référence",
    ]
    _entete(ws, colonnes)

    for i, f in enumerate(rapport.findings, start=2):
        valeurs = [
            f.control.id,
            f.control.domaine,
            f.control.controle,
            f.control.criticite,
            LIBELLES_STATUT[f.statut],
            f.preuve_fournie,
            f.commentaire,
            f.control.reference,
        ]
        for col, val in enumerate(valeurs, start=1):
            cell = ws.cell(row=i, column=col, value=val)
            cell.font = Font(name=POLICE, size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDURE
        fond, texte = COULEURS_STATUT[f.statut]
        statut_cell = ws.cell(row=i, column=5)
        statut_cell.fill = PatternFill("solid", fgColor=fond)
        statut_cell.font = Font(name=POLICE, size=10, bold=True, color=texte)

    largeurs = [12, 26, 34, 11, 14, 13, 40, 26]
    for col, largeur in zip("ABCDEFGH", largeurs):
        ws.column_dimensions[col].width = largeur
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:H{len(rapport.findings) + 1}"


def _feuille_plan_action(wb: Workbook, rapport: RapportConformite):
    ws = wb.create_sheet("Plan d'action")
    colonnes = [
        "Priorité", "ID", "Domaine", "Contrôle", "Criticité", "Statut",
        "Preuve attendue", "Action recommandée", "Responsable", "Échéance",
    ]
    _entete(ws, colonnes)

    for i, f in enumerate(rapport.plan_action, start=2):
        valeurs = [
            i - 1,
            f.control.id,
            f.control.domaine,
            f.control.controle,
            f.control.criticite,
            LIBELLES_STATUT[f.statut],
            f.control.preuve_attendue,
            f.control.action_recommandee,
            "",  # à remplir par le client
            "",  # à remplir par le client
        ]
        for col, val in enumerate(valeurs, start=1):
            cell = ws.cell(row=i, column=col, value=val)
            cell.font = Font(name=POLICE, size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDURE
        fond, texte = COULEURS_STATUT[f.statut]
        crit_cell = ws.cell(row=i, column=5)
        crit_cell.fill = PatternFill("solid", fgColor=fond if f.control.criticite == "Élevée" else fond)

    largeurs = [10, 12, 26, 32, 11, 14, 34, 40, 18, 14]
    for col, largeur in zip("ABCDEFGHIJ", largeurs):
        ws.column_dimensions[col].width = largeur
    ws.freeze_panes = "A2"
    if rapport.plan_action:
        ws.auto_filter.ref = f"A1:J{len(rapport.plan_action) + 1}"


def generer_rapport_excel(
    rapport: RapportConformite,
    chemin_sortie: str,
    nom_referentiel: str = "Référentiel",
    nom_organisation: str = "Organisation auditée",
) -> str:
    """Construit le classeur Excel à 3 onglets et l'enregistre sur disque."""
    wb = Workbook()
    _feuille_synthese(wb, rapport, nom_referentiel, nom_organisation)
    _feuille_detail(wb, rapport)
    _feuille_plan_action(wb, rapport)
    wb.save(chemin_sortie)
    return chemin_sortie
