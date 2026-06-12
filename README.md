# NYC Taxi Big Data Analytics Platform

## Présentation du projet

Ce projet présente la conception et la mise en œuvre d'une plateforme Big Data décisionnelle basée sur le dataset public NYC Taxi Trip Records 2023.

L'objectif est de construire une chaîne complète de traitement de données massives permettant de collecter, stocker, traiter, analyser et visualiser plusieurs millions de trajets de taxis new-yorkais.

Le projet a été réalisé dans le cadre du Master 1 Bases de Données et Génie Logiciel à l'Université Félix Houphouët-Boigny.

---

## Objectifs du projet

- Stocker des données massives dans Hadoop HDFS
- Réaliser des traitements distribués avec MapReduce
- Effectuer des analyses décisionnelles avec Apache Hive
- Produire des indicateurs métier exploitables
- Développer un dashboard interactif avec Flask et Plotly
- Générer automatiquement un rapport PDF décisionnel

---

## Technologies utilisées

- Apache Hadoop HDFS
- MapReduce
- Apache Hive
- Python
- Pandas
- Flask
- Plotly
- ReportLab
- Linux (WSL Ubuntu)
- Git & GitHub

---

## Données utilisées

Dataset : NYC Taxi Trip Records 2023

Période analysée :

- Janvier 2023
- Février 2023
- Mars 2023

Volume traité :

- Plus de 9 millions de trajets
- Plus de 170 millions USD de recettes analysées
- Traitement distribué avec Hadoop

---

## Architecture du pipeline

NYC Taxi Trip Records

↓
Hadoop HDFS

↓
MapReduce

↓
Apache Hive

↓
Exports CSV

↓
Dashboard Flask / Plotly

↓
Rapport PDF décisionnel

Le schéma détaillé du pipeline est disponible dans :

dashboard/pipeline_schema.png

---

## Principaux résultats obtenus

- Nombre total de trajets analysés : 9 177 544
- Recette totale observée : 171 948 024,90 $
- Créneau le plus rentable : JEUDI-18
- Courses suspectes détectées : 4 156
- Paiement dominant : Carte bancaire
- Vitesse moyenne observée : 22,3 km/h

---

## Analyses réalisées

- Activité horaire des taxis
- Analyse des moyens de paiement
- Analyse des heures de pointe
- Analyse des heures creuses
- Évolution hebdomadaire des recettes
- Analyse des vitesses moyennes
- Identification des zones prioritaires
- Détection des anomalies et trajets suspects

---

## Dashboard décisionnel

Le dashboard interactif permet :

- l'exploration des indicateurs clés ;
- l'analyse des recettes ;
- l'analyse du trafic ;
- la détection des anomalies ;
- l'export des données ;
- la génération automatique d'un rapport PDF.

Les captures d'écran sont disponibles dans :

docs/screenshots/

---

## Rapport PDF

Le rapport décisionnel généré automatiquement est disponible dans :

dashboard/rapport_executif_nyc_taxi.pdf

---

## Compétences démontrées

### Data Engineering

- Hadoop HDFS
- MapReduce
- Hive
- Traitement distribué

### Data Analysis

- Analyse exploratoire
- KPI
- Agrégations
- Détection d'anomalies

### Business Intelligence

- Dashboarding
- Reporting décisionnel
- Data Visualization
- Aide à la décision

---

## Auteur

ANON Amoncou Diom Sébastien

Matricule : ANOA171019790001

Master 1 Bases de Données et Génie Logiciel

Université Félix Houphouët-Boigny

Abidjan - Côte d'Ivoire

---

## Démonstration vidéo

https://www.youtube.com/watch?v=GsyqUfSC0bQ&t=68s
