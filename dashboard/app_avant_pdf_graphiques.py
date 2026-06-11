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
    pdf_path = BASE / "rapport_executif_nyc_taxi.pdf"

    kpi = read_csv("kpi_summary.csv")
    trips = read_csv("trips_per_hour.csv")
    zones = read_csv("revenue_per_zone.csv")
    speed = read_csv("speed_analysis.csv")
    peak = read_csv("peak_revenue.csv")
    payment = read_csv("payment_methods.csv")
    peakoff = read_csv("peak_vs_offpeak.csv")
    weekly = read_csv("weekly_revenue.csv")
    suspicious = read_csv("suspicious_trips.csv")

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

    elements.append(Paragraph("Rapport Exécutif NYC Taxi", styles["Title"]))
    elements.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("1. Indicateurs clés", styles["Heading1"]))

    if not kpi.empty:
        data = [["Indicateur", "Valeur"]] + kpi.astype(str).values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(table)

    elements.append(Spacer(1, 18))
    elements.append(Paragraph("Synthèse managériale", styles["Heading1"]))
    elements.append(Paragraph(
        "Le dashboard permet d'identifier les heures les plus actives, les zones de départ dominantes, "
        "les périodes de congestion, les créneaux les plus rentables et les moyens de paiement les plus utilisés. "
        "Les résultats montrent notamment une forte domination du paiement par carte et une rentabilité élevée "
        "sur les créneaux de fin d'après-midi.",
        styles["Normal"]
    ))

    elements.append(PageBreak())

    def add_table(title, df, limit=15):
        elements.append(Paragraph(title, styles["Heading1"]))

        if df.empty:
            elements.append(Paragraph("Aucune donnée disponible.", styles["Normal"]))
            elements.append(Spacer(1, 12))
            return

        temp = df.head(limit).copy()
        data = [list(temp.columns)] + temp.astype(str).values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 16))

    add_table("2. Activité par heure", trips, 24)
    add_table("3. Moyens de paiement", payment, 10)

    elements.append(PageBreak())

    add_table("4. Heures de pointe vs heures creuses", peakoff, 10)
    add_table("5. Recettes hebdomadaires", weekly, 20)

    elements.append(PageBreak())

    add_table("6. Zones de départ", zones, 15)
    add_table("7. Analyse vitesse / congestion", speed, 15)

    elements.append(PageBreak())

    add_table("8. Créneaux les plus rentables", peak, 15)
    add_table("9. Courses suspectes", suspicious, 5)

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
