#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import json

from flask import Flask, render_template, send_file, jsonify
import pandas as pd
import plotly.express as px
import plotly

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
app = Flask(__name__, template_folder=".")


def read_csv(name):
    path = DATA / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def fig_json(fig):
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@app.route("/")
def index():
    kpi = read_csv("kpi_summary.csv")
    trips = read_csv("trips_per_hour.csv")
    zones = read_csv("revenue_per_zone.csv")
    speed = read_csv("speed_analysis.csv")
    peak = read_csv("peak_revenue.csv")

    payment = read_csv("payment_methods.csv")
    peakoff = read_csv("peak_vs_offpeak.csv")
    weekly = read_csv("weekly_revenue.csv")
    suspicious = read_csv("suspicious_trips.csv")

    kpis = dict(zip(kpi["indicateur"], kpi["valeur"])) if not kpi.empty else {}

    if not suspicious.empty:
        kpis["Courses suspectes Hive"] = int(suspicious.iloc[0]["courses_suspectes"])

    if not payment.empty:
        dominant_payment = payment.sort_values("nb_courses", ascending=False).iloc[0]["mode_paiement"]
        kpis["Moyen de paiement dominant"] = dominant_payment

    charts = {}

    if not trips.empty:
        charts["trips"] = fig_json(
            px.bar(trips, x="heure", y="nb_courses", title="Nombre de courses par heure")
        )

    if not zones.empty:
        charts["zones"] = fig_json(
            px.bar(
                zones.head(15),
                x="zone_depart",
                y="nb_courses",
                title="Top 15 zones de départ"
            )
        )

    if not speed.empty:
        charts["speed"] = fig_json(
            px.bar(
                speed.sort_values("vitesse_moyenne_mph", ascending=False).head(15),
                x="creneau",
                y="vitesse_moyenne_mph",
                title="Top 15 vitesses moyennes"
            )
        )

    if not peak.empty:
        charts["peak"] = fig_json(
            px.bar(
                peak.sort_values("recette_totale", ascending=False).head(10),
                x="creneau",
                y="recette_totale",
                title="Top 10 créneaux rentables"
            )
        )

    if not payment.empty:
        charts["payment"] = fig_json(
            px.pie(
                payment,
                names="mode_paiement",
                values="nb_courses",
                title="Répartition des moyens de paiement"
            )
        )

    if not peakoff.empty:
        charts["peakoff"] = fig_json(
            px.bar(
                peakoff,
                x="periode",
                y="recette_totale",
                title="Heures de pointe vs heures creuses"
            )
        )

    if not weekly.empty:
        charts["weekly"] = fig_json(
            px.line(
                weekly.sort_values("semaine"),
                x="semaine",
                y="recette_totale",
                title="Évolution hebdomadaire des recettes"
            )
        )

    tables = {
        "trips": trips.head(24).to_html(classes="table", index=False) if not trips.empty else "",
        "zones": zones.head(20).to_html(classes="table", index=False) if not zones.empty else "",
        "speed": speed.head(20).to_html(classes="table", index=False) if not speed.empty else "",
        "peak": peak.head(20).to_html(classes="table", index=False) if not peak.empty else "",
        "payment": payment.to_html(classes="table", index=False) if not payment.empty else "",
        "peakoff": peakoff.to_html(classes="table", index=False) if not peakoff.empty else "",
        "weekly": weekly.head(20).to_html(classes="table", index=False) if not weekly.empty else "",
        "suspicious": suspicious.to_html(classes="table", index=False) if not suspicious.empty else "",
    }

    return render_template("index.html", kpis=kpis, charts=charts, tables=tables)




@app.route("/export_pdf")
def export_pdf():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from reportlab.platypus import Image as RLImage

    pdf_path = BASE / "rapport_executif_nyc_taxi.pdf"
    chart_dir = BASE / "pdf_charts"
    chart_dir.mkdir(exist_ok=True)

    kpi = read_csv("kpi_summary.csv")
    trips = read_csv("trips_per_hour.csv")
    zones = read_csv("revenue_per_zone.csv")
    speed = read_csv("speed_analysis.csv")
    peak = read_csv("peak_revenue.csv")
    payment = read_csv("payment_methods.csv")
    peakoff = read_csv("peak_vs_offpeak.csv")
    weekly = read_csv("weekly_revenue.csv")
    suspicious = read_csv("suspicious_trips.csv")

    def to_num(df, cols):
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        return df

    trips = to_num(trips, ["heure", "nb_courses"])
    zones = to_num(zones, ["zone_depart", "nb_courses", "montant_moyen"])
    speed = to_num(speed, ["vitesse_moyenne_mph", "nb_courses"])
    peak = to_num(peak, ["recette_totale", "nb_courses"])
    payment = to_num(payment, ["nb_courses", "recette_totale"])
    peakoff = to_num(peakoff, ["nb_courses", "recette_totale"])
    weekly = to_num(weekly, ["semaine", "recette_totale", "nb_courses"])

    def save_bar(df, x, y, title, filename, limit=None, sort=False):
        if df.empty:
            return None
        temp = df.copy()
        if sort:
            temp = temp.sort_values(y, ascending=False)
        if limit:
            temp = temp.head(limit)
        path = chart_dir / filename
        plt.figure(figsize=(10, 4))
        plt.bar(temp[x].astype(str), temp[y])
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def save_line(df, x, y, title, filename):
        if df.empty:
            return None
        temp = df.sort_values(x).copy()
        path = chart_dir / filename
        plt.figure(figsize=(10, 4))
        plt.plot(temp[x], temp[y], marker="o")
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def save_pie(df, names, values, title, filename):
        if df.empty:
            return None
        path = chart_dir / filename
        plt.figure(figsize=(7, 5))
        plt.pie(df[values], labels=df[names], autopct="%1.1f%%", startangle=90)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    chart_activity = save_bar(trips, "heure", "nb_courses", "Activité par heure", "activite_heure.png")
    chart_payment = save_pie(payment, "mode_paiement", "nb_courses", "Répartition des moyens de paiement", "paiements.png")
    chart_peakoff = save_bar(peakoff, "periode", "recette_totale", "Heures de pointe vs heures creuses", "peakoff.png")
    chart_weekly = save_line(weekly, "semaine", "recette_totale", "Évolution hebdomadaire des recettes", "weekly.png")
    chart_zones = save_bar(zones, "zone_depart", "nb_courses", "Top zones de départ", "zones.png", limit=10, sort=True)
    chart_peak = save_bar(peak, "creneau", "recette_totale", "Créneaux les plus rentables", "peak.png", limit=10, sort=True)

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()
    elements = []

    def add_title(text):
        elements.append(Paragraph(text, styles["Title"]))
        elements.append(Spacer(1, 12))

    def add_heading(text):
        elements.append(Paragraph(text, styles["Heading1"]))
        elements.append(Spacer(1, 8))

    def add_text(text):
        elements.append(Paragraph(text, styles["BodyText"]))
        elements.append(Spacer(1, 10))

    def add_image(path, width=620, height=260):
        if path and Path(path).exists():
            elements.append(RLImage(str(path), width=width, height=height))
            elements.append(Spacer(1, 12))

    def add_table(df, limit=10):
        if df.empty:
            add_text("Aucune donnée disponible.")
            return
        temp = df.head(limit).copy()
        data = [list(temp.columns)] + temp.astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    elements.append(Spacer(1, 35))

    add_title("UNIVERSITÉ FÉLIX HOUPHOUËT-BOIGNY")
    add_heading("UFR MATHÉMATIQUES ET INFORMATIQUE")
    add_heading("MASTER 1 BASES DE DONNÉES ET GÉNIE LOGICIEL")

    elements.append(Spacer(1, 20))
    add_title("RAPPORT DÉCISIONNEL BIG DATA")
    add_heading("Analyse des NYC Taxi Trip Records")
    add_text("Conception d’un pipeline Big Data avec Hadoop HDFS, MapReduce, Hive, Flask et Python.")

    elements.append(Spacer(1, 20))
    add_heading("Réalisé par :")
    add_title("ANON Amoncou Diom Sébastien")

    elements.append(Spacer(1, 10))
    add_heading("Encadré par :")
    add_title("Dr BAKAYOKO")

    elements.append(Spacer(1, 15))
    add_text("Année académique : 2025 - 2026")
    add_text(f"Date de génération : {datetime.now().strftime('%d/%m/%Y %H:%M')}")


    elements.append(PageBreak())

    add_title("TABLE DES MATIÈRES")

    add_text("1. Résumé exécutif")
    add_text("2. Activité horaire")
    add_text("3. Analyse des moyens de paiement")
    add_text("4. Heures de pointe vs heures creuses")
    add_text("5. Évolution hebdomadaire des recettes")
    add_text("6. Zones de départ prioritaires")
    add_text("7. Créneaux les plus rentables")
    add_text("8. Détection des anomalies")
    add_text("9. Impact Business de la solution")
    add_text("10. Architecture technique du pipeline")
    add_text("11. Recommandations finales")

    elements.append(PageBreak())

    add_title("1. Résumé exécutif")
    add_heading("Indicateurs clés")
    add_table(kpi, 10)

    add_heading("Lecture générale")
    add_text("Le projet analyse plus de 9 millions de trajets de taxis. Les résultats montrent une forte activité en fin de journée, une domination du paiement par carte bancaire, une concentration des départs dans quelques zones prioritaires et 4 156 courses potentiellement suspectes détectées par Hive.")

    add_heading("Messages clés pour la direction")
    add_text("• Le créneau le plus rentable est JEUDI-18.")
    add_text("• Le paiement par carte bancaire représente environ 80 % des courses.")
    add_text("• Les zones 132, 237, 161 et 236 sont prioritaires pour le positionnement des chauffeurs.")
    add_text("• Les heures creuses génèrent une forte recette totale car elles couvrent une plage horaire plus large.")
    add_text("• Les courses suspectes doivent faire l'objet d'un contrôle qualité automatisé.")
    elements.append(PageBreak())

    add_title("2. Activité horaire")
    add_image(chart_activity)
    add_text("Analyse : l'activité augmente progressivement à partir de 7h et atteint un pic autour de 18h avec plus de 650 000 courses. Cette plage horaire doit être considérée comme prioritaire pour le déploiement des chauffeurs.")
    add_text("Décision : renforcer la disponibilité des véhicules entre 16h et 19h afin de réduire l'attente des clients et améliorer le chiffre d'affaires.")
    add_table(trips, 8)
    elements.append(PageBreak())

    add_title("3. Analyse des moyens de paiement")
    add_image(chart_payment, width=500, height=330)
    add_text("Analyse : le paiement par carte bancaire représente environ 80 % des courses, tandis que le cash représente environ 17 %. Cela montre une forte adoption du paiement électronique.")
    add_text("Décision : renforcer les infrastructures de paiement numérique, suivre les commissions et réduire les risques associés à la manipulation d'espèces.")
    add_table(payment, 5)
    elements.append(PageBreak())

    add_title("4. Heures de pointe vs heures creuses")
    add_image(chart_peakoff)
    add_text("Analyse : les heures creuses génèrent la recette totale la plus élevée, principalement parce qu'elles couvrent une plage horaire plus longue. Les périodes de pointe restent cependant stratégiques pour l'allocation des chauffeurs.")
    add_text("Décision : équilibrer la flotte entre périodes de pointe et heures creuses afin de maximiser les recettes globales.")
    add_table(peakoff, 3)
    elements.append(PageBreak())

    add_title("5. Évolution hebdomadaire des recettes")
    add_image(chart_weekly)
    add_text("Analyse : les premières semaines présentent une activité importante et relativement stable. Les semaines très faibles doivent être interprétées avec prudence, car elles correspondent probablement à des données partielles ou incomplètes.")
    add_text("Décision : utiliser le suivi hebdomadaire comme outil de pilotage pour détecter les baisses inhabituelles de recettes.")
    add_table(weekly, 8)
    elements.append(PageBreak())

    add_title("6. Zones de départ prioritaires")
    add_image(chart_zones)
    add_text("Analyse : les zones 132, 237, 161 et 236 concentrent une part importante de l'activité. Ces zones sont stratégiques pour le positionnement des véhicules.")
    add_text("Décision : pré-positionner les chauffeurs dans ces zones pour améliorer le temps de réponse et augmenter le nombre de courses.")
    add_table(zones, 8)
    elements.append(PageBreak())

    add_title("7. Créneaux les plus rentables")
    add_image(chart_peak)
    add_text("Analyse : les créneaux du jeudi et du vendredi en fin d'après-midi dominent le classement des recettes. Le créneau JEUDI-18 ressort comme le plus rentable.")
    add_text("Décision : concentrer davantage de véhicules sur les créneaux du jeudi et du vendredi entre 16h et 19h.")
    add_table(peak, 8)
    elements.append(PageBreak())

    add_title("8. Détection des anomalies")
    add_table(suspicious, 1)
    add_text("Analyse : Hive a détecté 4 156 courses suspectes. Ces courses présentent une distance significative mais une durée anormalement faible.")
    add_text("Interprétation : ces trajets peuvent correspondre à des erreurs de saisie, des anomalies GPS, des données corrompues ou des cas nécessitant une vérification.")
    add_heading("Recommandations de contrôle")
    add_text("• Mettre en place un contrôle automatique des trajets très courts en durée mais longs en distance.")
    add_text("• Comparer les trajets suspects avec les données GPS et les montants facturés.")
    add_text("• Produire un rapport d'anomalies hebdomadaire pour les responsables opérationnels.")
    elements.append(PageBreak())

    add_title("9. Impact Business de la Solution")
    add_text("Cette solution transforme des fichiers volumineux en indicateurs directement exploitables par un décideur.")
    add_text("Elle permet de réduire le temps d'analyse, d'identifier les zones prioritaires, d'optimiser l'affectation des chauffeurs, de surveiller les anomalies et de suivre les performances financières.")
    add_text("Le passage de HDFS à MapReduce, puis Hive, puis Flask, montre une chaîne complète de traitement Big Data allant du stockage distribué jusqu'à la restitution décisionnelle.")

    add_heading("Bénéfices principaux")
    add_text("• Meilleure visibilité sur les pics d'activité.")
    add_text("• Optimisation du positionnement des véhicules.")
    add_text("• Meilleur suivi des recettes.")
    add_text("• Détection automatique des anomalies.")
    add_text("• Amélioration de la qualité de décision.")
    elements.append(PageBreak())

    add_title("10. Architecture technique du pipeline")
    add_text("Dataset NYC Taxi → HDFS → MapReduce → Hive → CSV d'analyse → Dashboard Flask/Plotly → Rapport PDF décisionnel.")
    add_text("Les données sont d'abord stockées dans HDFS. MapReduce permet de produire les premières agrégations massives. Hive enrichit l'analyse avec des requêtes SQL décisionnelles. Les résultats sont ensuite exportés en CSV pour alimenter le dashboard Flask et le rapport PDF.")
    add_heading("Technologies utilisées")
    add_text("• Hadoop HDFS : stockage distribué des données.")
    add_text("• MapReduce : traitements distribués et agrégations.")
    add_text("• Hive : requêtes SQL analytiques.")
    add_text("• Python Flask : application web de visualisation.")
    add_text("• Plotly/Matplotlib : graphiques interactifs et graphiques PDF.")
    add_text("• ReportLab : génération automatique du rapport PDF.")
    elements.append(PageBreak())

    add_title("11. Recommandations finales")
    add_text("1. Renforcer la disponibilité des chauffeurs entre 16h et 19h.")
    add_text("2. Prioriser les zones 132, 237, 161 et 236 pour le positionnement des véhicules.")
    add_text("3. Encourager davantage les paiements électroniques, car la carte bancaire est le moyen dominant.")
    add_text("4. Exploiter les analyses Hive pour suivre les recettes hebdomadaires et prévoir la demande.")
    add_text("5. Surveiller automatiquement les courses suspectes afin d'améliorer la qualité des données.")
    add_text("6. Utiliser le dashboard comme outil de pilotage pour les décisions de flotte, de zones et de créneaux horaires.")
    add_text("7. Mettre à jour régulièrement les données afin de transformer ce projet en outil de Business Intelligence évolutif.")

    doc.build(elements)

    return send_file(pdf_path, as_attachment=True)


@app.route("/download/<dataset>")
def download(dataset):
    files = {
        "trips_per_hour": "trips_per_hour.csv",
        "revenue_per_zone": "revenue_per_zone.csv",
        "speed_analysis": "speed_analysis.csv",
        "peak_revenue": "peak_revenue.csv",
        "kpi_summary": "kpi_summary.csv",
        "payment_methods": "payment_methods.csv",
        "peak_vs_offpeak": "peak_vs_offpeak.csv",
        "weekly_revenue": "weekly_revenue.csv",
        "suspicious_trips": "suspicious_trips.csv",
    }

    if dataset not in files:
        return "Dataset inconnu", 404

    path = DATA / files[dataset]
    return send_file(path, as_attachment=True) if path.exists() else ("Fichier introuvable", 404)


@app.route("/api/<dataset>")
def api(dataset):
    files = {
        "trips_per_hour": "trips_per_hour.csv",
        "revenue_per_zone": "revenue_per_zone.csv",
        "speed_analysis": "speed_analysis.csv",
        "peak_revenue": "peak_revenue.csv",
        "kpi_summary": "kpi_summary.csv",
        "payment_methods": "payment_methods.csv",
        "peak_vs_offpeak": "peak_vs_offpeak.csv",
        "weekly_revenue": "weekly_revenue.csv",
        "suspicious_trips": "suspicious_trips.csv",
    }

    if dataset not in files:
        return jsonify({"error": "Dataset inconnu"}), 404

    df = read_csv(files[dataset])
    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
