#!/usr/bin/env python3
from pathlib import Path
from flask import Flask, render_template, send_file, jsonify
import pandas as pd
import plotly.express as px
import plotly
import json

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
app = Flask(__name__, template_folder=".")

def read_csv(name):
    p = DATA / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

def fig_json(fig):
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route("/")
def index():
    kpi = read_csv("kpi_summary.csv")
    trips = read_csv("trips_per_hour.csv")
    zones = read_csv("revenue_per_zone.csv")
    speed = read_csv("speed_analysis.csv")
    peak = read_csv("peak_revenue.csv")

    kpis = dict(zip(kpi["indicateur"], kpi["valeur"])) if not kpi.empty else {}
    charts = {}

    if not trips.empty:
        charts["trips"] = fig_json(px.bar(trips, x="heure", y="nb_courses", title="Nombre de courses par heure"))
    if not zones.empty:
        charts["zones"] = fig_json(px.bar(zones.head(15), x="zone_depart", y="nb_courses", title="Top 15 zones de départ"))
    if not speed.empty:
        charts["speed"] = fig_json(px.bar(speed.sort_values("vitesse_moyenne_mph", ascending=False).head(15), x="creneau", y="vitesse_moyenne_mph", title="Top 15 vitesses moyennes"))
    if not peak.empty:
        charts["peak"] = fig_json(px.bar(peak.sort_values("recette_totale", ascending=False).head(10), x="creneau", y="recette_totale", title="Top 10 créneaux rentables"))

    tables = {
        "trips": trips.head(24).to_html(classes="table", index=False) if not trips.empty else "",
        "zones": zones.head(20).to_html(classes="table", index=False) if not zones.empty else "",
        "speed": speed.head(20).to_html(classes="table", index=False) if not speed.empty else "",
        "peak": peak.head(20).to_html(classes="table", index=False) if not peak.empty else "",
    }

    return render_template("index.html", kpis=kpis, charts=charts, tables=tables)

@app.route("/download/<dataset>")
def download(dataset):
    files = {
        "trips_per_hour": "trips_per_hour.csv",
        "revenue_per_zone": "revenue_per_zone.csv",
        "speed_analysis": "speed_analysis.csv",
        "peak_revenue": "peak_revenue.csv",
        "kpi_summary": "kpi_summary.csv",
    }
    if dataset not in files:
        return "Dataset inconnu", 404
    p = DATA / files[dataset]
    return send_file(p, as_attachment=True) if p.exists() else ("Fichier introuvable", 404)

@app.route("/api/<dataset>")
def api(dataset):
    files = {
        "trips_per_hour": "trips_per_hour.csv",
        "revenue_per_zone": "revenue_per_zone.csv",
        "speed_analysis": "speed_analysis.csv",
        "peak_revenue": "peak_revenue.csv",
        "kpi_summary": "kpi_summary.csv",
    }
    if dataset not in files:
        return jsonify({"error": "Dataset inconnu"}), 404
    df = read_csv(files[dataset])
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
