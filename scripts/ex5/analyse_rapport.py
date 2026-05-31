#!/usr/bin/env python3
import pandas as pd

fichier = "/home/leconcret/tp_hadoop_taxi/results/rapport_final.tsv"
colonnes = ["creneau", "nb_courses", "fare_moy", "tip_moy", "tip_rate", "recette_totale"]

df = pd.read_csv(fichier, sep="\t", header=None, names=colonnes)

print("\n===== RAPPORT FINAL =====")
print("\nNombre de créneaux :", len(df))
print("\nNombre total de courses :", format(int(df["nb_courses"].sum()), ","))
print("\nRecette totale :", round(df["recette_totale"].sum(), 2), "$")

print("\n===== TOP 5 CRENEAUX =====")
top = df.sort_values("recette_totale", ascending=False).head(5)
print(top)

print("\n===== CRENEAU LE PLUS RENTABLE =====")
print(top.iloc[0])
