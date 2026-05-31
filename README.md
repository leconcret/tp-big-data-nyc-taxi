# TP BIG DATA — Apache Hadoop / NYC Taxi Trip Records

## Présentation
Ce dépôt accompagne la vidéo de démonstration du TP Big Data réalisé avec Hadoop, HDFS, MapReduce, Hive et Python sur le dataset NYC Taxi Trip Records.

## Objectif
Construire un pipeline Big Data complet :
1. préparation du dataset ;
2. chargement dans HDFS ;
3. traitements MapReduce ;
4. analyses Hive ;
5. pipeline final End-to-End ;
6. export et analyse Python.

## Environnement utilisé
- Windows + WSL Ubuntu
- Hadoop 3.4.0
- Hive 4.0.1
- Python 3
- Hadoop Streaming
- HDFS

## Structure du dépôt

```text
tp-big-data-nyc-taxi/
├── README.md
├── .gitignore
├── commands_demo.md
├── run_mapreduce_commands.sh
├── hive/
│   └── queries_hive.sql
├── scripts/
│   ├── ex1/
│   ├── ex2/
│   ├── ex3/
│   └── ex5/
└── results/
    └── README_results.md
```

## Variables importantes

```bash
export HDFS_USER=$(whoami)
export HADOOP_STREAMING_JAR=$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar
```

## Chemins utilisés

Données locales :

```bash
~/tp_hadoop_taxi/csv_data
```

Données HDFS :

```bash
/user/leconcret/taxi/raw/
```

Résultats HDFS :

```bash
/user/leconcret/taxi/processed/
```

Résultat final local :

```bash
~/tp_hadoop_taxi/results/rapport_final.tsv
```

## Résultats principaux obtenus

```text
Nombre total de lignes Hive : 9 177 627
Pipeline final : 9 177 544 courses
Recette totale : 171 948 024.9 $
Créneau le plus rentable : JEUDI-18
Courses suspectes détectées : 4 156
```

## Lien vidéo
À compléter :

```text
Lien YouTube : ___________________https://www.youtube.com/watch?v=GsyqUfSC0bQ&t=68s___________
```
