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
    add_text("Matricule : ANOA171019790001")

    elements.append(Spacer(1, 10))
    add_heading("Encadré par :")
    add_title("Dr BAKAYOKO")

    elements.append(Spacer(1, 15))
    add_text("Année académique : 2025 - 2026")
    add_text(f"Date de génération : {datetime.now().strftime('%d/%m/%Y %H:%M')}")


    add_title("TABLE DES MATIÈRES")

    add_text("1. Introduction générale")
    add_text("2. Données utilisées")
    add_text("3. Résumé exécutif")
    add_text("4. Activité horaire")
    add_text("5. Analyse des moyens de paiement")
    add_text("6. Heures de pointe vs heures creuses")
    add_text("7. Évolution hebdomadaire des recettes")
    add_text("8. Zones de départ prioritaires")
    add_text("9. Créneaux les plus rentables")
    add_text("10. Détection des anomalies")
    add_text("11. Impact Business de la solution")
    add_text("12. Architecture technique du pipeline")
    add_text("13. Compétences acquises")
    add_text("14. Recommandations finales")
    add_text("15. Limites du projet")
    add_text("16. Conclusion générale")

    elements.append(PageBreak())

    add_title("1. Introduction générale")

    add_text("Le Big Data occupe aujourd'hui une place importante dans l'analyse et l'exploitation des grands volumes de données produits par les entreprises et les services numériques. Dans le domaine du transport urbain, les données générées par les trajets permettent de mieux comprendre la demande, les périodes de forte activité, les comportements de paiement, les zones stratégiques et les anomalies opérationnelles.")

    add_text("Ce projet porte sur l'analyse décisionnelle du dataset public NYC Taxi Trip Records, relatif aux trajets de taxis de la ville de New York sur la période allant de janvier à mars 2023. Ce jeu de données contient plusieurs millions d'enregistrements décrivant les courses réalisées, les distances parcourues, les montants facturés, les moyens de paiement et les informations temporelles associées aux trajets.")

    add_text("L'objectif principal est de mettre en place une chaîne complète de traitement Big Data permettant de transformer des données brutes en indicateurs exploitables pour la prise de décision. Le projet vise notamment à analyser l'activité horaire, les zones de départ prioritaires, les créneaux les plus rentables, les moyens de paiement utilisés, les vitesses moyennes et les courses suspectes.")

    add_text("La méthodologie adoptée repose sur plusieurs outils complémentaires : Hadoop HDFS pour le stockage distribué, MapReduce pour les traitements massifs, Apache Hive pour les requêtes analytiques, Python et Pandas pour la préparation des résultats, Flask et Plotly pour le dashboard web, puis ReportLab pour la génération automatique du rapport PDF.")

    add_text("Ce rapport présente les principaux résultats obtenus, leur interprétation métier, ainsi que les recommandations permettant d'exploiter ces informations dans une logique de Business Intelligence et d'aide à la décision.")

    elements.append(PageBreak())

    add_title("2. Données utilisées")

    add_heading("Origine du dataset")
    add_text("Les données analysées proviennent du dataset public NYC Taxi Trip Records, relatif aux trajets de taxis de la ville de New York.")

    add_heading("Période analysée")
    add_text("La période retenue pour cette étude couvre les mois de janvier, février et mars 2023.")

    add_heading("Volume de données")
    add_text("Le traitement porte sur plus de 9 millions de trajets, précisément 9 177 627 lignes issues de Hive et 9 177 544 courses consolidées dans le pipeline d'analyse.")

    add_heading("Nature des informations exploitées")
    add_text("Les données contiennent notamment les dates et heures de prise en charge, les distances parcourues, les montants facturés, les pourboires, les moyens de paiement, les zones de départ et d'arrivée ainsi que les informations permettant d'étudier la durée et la vitesse moyenne des trajets.")

    add_heading("Formats et technologies")
    add_text("Les fichiers sources ont été exploités au format Parquet, puis transformés et analysés à travers Hadoop HDFS, MapReduce, Apache Hive, Python, Flask, Plotly, Matplotlib et ReportLab.")

    add_heading("Intérêt analytique")
    add_text("Ce dataset permet de produire des indicateurs décisionnels utiles pour comprendre la demande, optimiser le positionnement des chauffeurs, suivre les recettes, analyser les modes de paiement et détecter certaines anomalies opérationnelles.")

    elements.append(PageBreak())

    add_title("3. Résumé exécutif")
    add_heading("Indicateurs clés")

    if not kpi.empty:
        kpi_extra = pd.DataFrame([
            {"indicateur": "Moyen de paiement dominant", "valeur": "Carte bancaire"},
            {"indicateur": "Zone de départ principale", "valeur": "132"},
            {"indicateur": "Vitesse moyenne observée", "valeur": "22,3 km/h (13,85 mph)"}
        ])
        kpi_exec = pd.concat([kpi, kpi_extra], ignore_index=True)
    else:
        kpi_exec = pd.DataFrame([
            {"indicateur": "Moyen de paiement dominant", "valeur": "Carte bancaire"},
            {"indicateur": "Zone de départ principale", "valeur": "132"},
            {"indicateur": "Vitesse moyenne observée", "valeur": "22,3 km/h (13,85 mph)"}
        ])

    add_table(kpi_exec, 10)

    add_heading("Lecture générale")
    add_text("Le projet analyse plus de 9 millions de trajets de taxis. Les résultats montrent une forte activité en fin de journée, une domination du paiement par carte bancaire, une concentration des départs dans quelques zones prioritaires et 4 156 courses potentiellement suspectes détectées par Hive.")

    add_heading("Messages clés pour la direction")
    add_text("• Le créneau le plus rentable est JEUDI-18.")
    add_text("• Le paiement par carte bancaire représente environ 80 % des courses.")
    add_text("• Les zones 132, 237, 161 et 236 sont prioritaires pour le positionnement des chauffeurs.")
    add_text("• La vitesse moyenne observée sur l'ensemble des trajets est de 22,3 km/h (13,85 mph).")
    add_text("• Le trafic le plus fluide est observé le dimanche à 06h avec une vitesse moyenne de 37,7 km/h (23,4 mph).")
    add_text("• Le trafic le plus congestionné est observé le jeudi à 15h avec une vitesse moyenne de 14,8 km/h (9,2 mph).")
    add_text("• Les heures creuses génèrent une forte recette totale car elles couvrent une plage horaire plus large.")
    add_text("• Les courses suspectes doivent faire l'objet d'un contrôle qualité automatisé.")
    elements.append(PageBreak())

    add_title("4. Activité horaire")
    add_image(chart_activity)
    add_text("Analyse : l'activité augmente progressivement à partir de 7h et atteint un pic autour de 18h avec plus de 650 000 courses. Cette plage horaire doit être considérée comme prioritaire pour le déploiement des chauffeurs.")
    add_text("Décision : renforcer la disponibilité des véhicules entre 16h et 19h afin de réduire l'attente des clients et améliorer le chiffre d'affaires.")
    elements.append(PageBreak())
    add_heading("Tableau synthétique - Activité horaire")
    add_text("Le tableau ci-dessous présente un extrait synthétique. Les résultats complets restent disponibles dans le dashboard Flask.")
    add_table(trips, 8)
    elements.append(PageBreak())

    add_title("5. Analyse des moyens de paiement")
    add_image(chart_payment, width=500, height=330)
    add_text("Analyse : le paiement par carte bancaire représente environ 80 % des courses, tandis que le cash représente environ 17 %. Cela montre une forte adoption du paiement électronique.")
    add_text("Décision : renforcer les infrastructures de paiement numérique, suivre les commissions et réduire les risques associés à la manipulation d'espèces.")
    elements.append(PageBreak())
    add_heading("Tableau synthétique - Moyens de paiement")
    add_text("Le tableau ci-dessous présente les principaux modes de paiement issus de Hive.")
    add_table(payment, 5)
    elements.append(PageBreak())

    add_title("6. Heures de pointe vs heures creuses")
    add_image(chart_peakoff)
    add_text("Analyse : les heures creuses génèrent la recette totale la plus élevée, principalement parce qu'elles couvrent une plage horaire plus longue. Les périodes de pointe restent cependant stratégiques pour l'allocation des chauffeurs.")
    add_text("Décision : équilibrer la flotte entre périodes de pointe et heures creuses afin de maximiser les recettes globales.")
    add_table(peakoff, 3)
    elements.append(PageBreak())

    add_title("7. Évolution hebdomadaire des recettes")
    add_image(chart_weekly)
    add_text("Analyse : les premières semaines présentent une activité importante et relativement stable. Les semaines très faibles doivent être interprétées avec prudence, car elles correspondent probablement à des données partielles ou incomplètes.")
    add_text("Remarque : cette étude porte uniquement sur les données NYC Taxi de janvier à mars 2023. Les semaines absentes ou incomplètes en dehors de cette période ne doivent pas être interprétées comme une baisse réelle d'activité.")
    add_text("Décision : utiliser le suivi hebdomadaire comme outil de pilotage pour détecter les baisses inhabituelles de recettes.")
    elements.append(PageBreak())
    add_heading("Tableau synthétique - Recettes hebdomadaires")
    add_text("Le tableau ci-dessous présente un extrait des semaines analysées. Les valeurs faibles correspondent probablement à des données partielles.")
    add_table(weekly, 8)
    elements.append(PageBreak())

    add_title("8. Zones de départ prioritaires")
    add_image(chart_zones)
    add_text("Analyse : les zones 132, 237, 161 et 236 concentrent une part importante de l'activité. Ces zones sont stratégiques pour le positionnement des véhicules.")
    add_text("Décision : pré-positionner les chauffeurs dans ces zones pour améliorer le temps de réponse et augmenter le nombre de courses.")
    elements.append(PageBreak())
    add_heading("Tableau synthétique - Zones prioritaires")
    add_text("Le tableau ci-dessous présente les principales zones de départ. Le détail complet est consultable dans le dashboard.")
    add_table(zones, 8)
    elements.append(PageBreak())

    add_title("9. Créneaux les plus rentables")
    add_image(chart_peak)
    add_text("Analyse : les créneaux du jeudi et du vendredi en fin d'après-midi dominent le classement des recettes. Le créneau JEUDI-18 ressort comme le plus rentable.")
    add_text("Décision : concentrer davantage de véhicules sur les créneaux du jeudi et du vendredi entre 16h et 19h.")
    elements.append(PageBreak())
    add_heading("Tableau synthétique - Créneaux rentables")
    add_text("Le tableau ci-dessous présente les créneaux les plus rentables pour l’activité taxi.")
    add_table(peak, 8)
    elements.append(PageBreak())

    add_title("10. Détection des anomalies")
    add_table(suspicious, 1)
    add_text("Analyse : Hive a détecté 4 156 courses suspectes. Ces courses présentent une distance significative mais une durée anormalement faible.")
    add_text("Interprétation : ces trajets peuvent correspondre à des erreurs de saisie, des anomalies GPS, des données corrompues ou des cas nécessitant une vérification.")
    add_heading("Recommandations de contrôle")
    add_text("• Mettre en place un contrôle automatique des trajets très courts en durée mais longs en distance.")
    add_text("• Comparer les trajets suspects avec les données GPS et les montants facturés.")
    add_text("• Produire un rapport d'anomalies hebdomadaire pour les responsables opérationnels.")
    elements.append(PageBreak())

    add_title("11. Impact Business de la Solution")
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

    add_title("12. Architecture technique du pipeline")
    add_image("pipeline_schema.png", width=300, height=380)
    add_text("Les données sont d'abord stockées dans HDFS. MapReduce permet de produire les premières agrégations massives. Hive enrichit l'analyse avec des requêtes SQL décisionnelles. Les résultats sont ensuite exportés en CSV pour alimenter le dashboard Flask et le rapport PDF.")
    add_heading("Technologies utilisées")
    add_text("• Hadoop HDFS : stockage distribué des données.")
    add_text("• MapReduce : traitements distribués et agrégations.")
    add_text("• Hive : requêtes SQL analytiques.")
    add_text("• Python Flask : application web de visualisation.")
    add_text("• Plotly/Matplotlib : graphiques interactifs et graphiques PDF.")
    add_text("• ReportLab : génération automatique du rapport PDF.")
    elements.append(PageBreak())

    add_title("13. Compétences acquises")
    add_text("Ce projet a permis de consolider plusieurs compétences techniques et analytiques liées au traitement Big Data et à la Business Intelligence.")

    add_heading("Compétences techniques")
    add_text("• Hadoop HDFS : stockage distribué des données massives.")
    add_text("• MapReduce : traitement parallèle et agrégation de grands volumes de données.")
    add_text("• Apache Hive : analyse SQL sur des données stockées dans Hadoop.")
    add_text("• Python Pandas : nettoyage, préparation et transformation des données.")
    add_text("• Flask : développement d'un dashboard web décisionnel.")
    add_text("• Plotly et Matplotlib : visualisation des résultats sous forme de graphiques.")
    add_text("• ReportLab : génération automatique d'un rapport PDF professionnel.")

    add_heading("Compétences analytiques")
    add_text("• Construction d'indicateurs clés de performance.")
    add_text("• Analyse des périodes de forte activité.")
    add_text("• Identification des zones de départ prioritaires.")
    add_text("• Détection d'anomalies dans les trajets.")
    add_text("• Transformation de données brutes en informations décisionnelles.")

    elements.append(PageBreak())

    add_title("14. Recommandations finales")
    add_text("1. Renforcer la disponibilité des chauffeurs entre 16h et 19h.")
    add_text("2. Prioriser les zones 132, 237, 161 et 236 pour le positionnement des véhicules.")
    add_text("3. Encourager davantage les paiements électroniques, car la carte bancaire est le moyen dominant.")
    add_text("4. Exploiter les analyses Hive pour suivre les recettes hebdomadaires et prévoir la demande.")
    add_text("5. Surveiller automatiquement les courses suspectes afin d'améliorer la qualité des données.")
    add_text("6. Utiliser le dashboard comme outil de pilotage pour les décisions de flotte, de zones et de créneaux horaires.")
    add_text("7. Mettre à jour régulièrement les données afin de transformer ce projet en outil de Business Intelligence évolutif.")

    elements.append(PageBreak())

    add_title("15. Limites du projet")

    add_text("• L'analyse porte uniquement sur les données NYC Taxi de janvier à mars 2023.")
    add_text("• Certaines semaines apparaissent incomplètes car elles sont en dehors du périmètre temporel étudié.")
    add_text("• Les zones sont représentées par des identifiants numériques sans cartographie détaillée.")
    add_text("• Les conditions météorologiques et les événements exceptionnels n'ont pas été intégrés à l'analyse.")
    add_text("• Les courses suspectes détectées nécessitent une validation métier complémentaire avant toute décision opérationnelle.")
    add_text("• Le dashboard repose sur les données actuellement disponibles et devra être mis à jour pour conserver sa pertinence dans le temps.")

    elements.append(PageBreak())

    add_title("16. Conclusion générale")

    add_text("Ce rapport présente les résultats d’une étude décisionnelle réalisée sur le dataset public NYC Taxi Trip Records à l’aide des technologies Big Data étudiées dans le cadre du Master 1 Bases de Données et Génie Logiciel.")
    add_text("Ce travail a été réalisé par ANON Amoncou Diom Sébastien (Matricule : ANOA171019790001).")

    add_text("Ce projet a permis de mettre en œuvre une chaîne complète de traitement Big Data reposant sur Hadoop HDFS, MapReduce, Apache Hive, Python, Flask et ReportLab.")

    add_text("L'étude s'appuie sur le dataset public NYC Taxi Trip Records correspondant aux trajets de taxis de la ville de New York sur la période allant de janvier à mars 2023. Ce jeu de données contient plusieurs millions d'enregistrements décrivant les courses effectuées, les distances parcourues, les montants facturés, les moyens de paiement ainsi que les informations temporelles associées aux trajets.")

    add_text("À partir de plus de 9 millions de courses analysées, plusieurs indicateurs décisionnels ont été produits afin d'identifier les périodes de forte activité, les zones géographiques stratégiques, les comportements de paiement dominants, les créneaux les plus rentables ainsi que les anomalies potentielles présentes dans les données.")

    add_text("Les résultats obtenus mettent notamment en évidence la prédominance du paiement par carte bancaire, la concentration de l'activité dans certaines zones prioritaires, l'existence de créneaux particulièrement rentables et la présence de plusieurs milliers de courses suspectes nécessitant un contrôle supplémentaire. L'analyse des vitesses moyennes a également permis de caractériser les périodes les plus fluides et les plus congestionnées du trafic.")

    add_text("Ce projet démontre l'apport des technologies Big Data dans le traitement et la valorisation de grands volumes de données. Il illustre la manière dont des données brutes peuvent être transformées en informations exploitables pour la prise de décision grâce à l'utilisation conjointe du stockage distribué, des traitements analytiques et des outils de visualisation.")

    add_text("Enfin, le dashboard décisionnel développé ainsi que le rapport PDF généré automatiquement constituent une base solide pour la mise en place d'une solution de Business Intelligence capable d'accompagner l'optimisation des performances opérationnelles, la planification des ressources et l'amélioration continue de la qualité des services.")

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
