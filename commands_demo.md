# Commandes utilisées pour la vidéo

## Vérification Hadoop

```bash
jps
```

## Variables

```bash
export HDFS_USER=$(whoami)
export HADOOP_STREAMING_JAR=$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar
echo $HDFS_USER
echo $HADOOP_STREAMING_JAR
```

## Vérification HDFS

```bash
hdfs dfs -ls -h /user/$HDFS_USER/taxi/raw/
hdfs dfs -du -s -h /user/$HDFS_USER/taxi/raw/
```

## Résultat exercice 1

```bash
hdfs dfs -cat /user/$HDFS_USER/taxi/processed/trips_per_hour/part-00000
```

## Résultat exercice 2

```bash
hdfs dfs -cat /user/$HDFS_USER/taxi/processed/revenue_per_zone/part-* | sort -t$'\t' -k2 -nr | head -20
```

## Résultat exercice 3

```bash
hdfs dfs -cat /user/$HDFS_USER/taxi/processed/speed_analysis/part-00000 | sort -t$'\t' -k5 -nr | head -10
```

## Hive

```bash
cd ~
hive
```

Dans Beeline :

```sql
!connect jdbc:hive2://
USE nyc_taxi_tp;
SHOW TABLES;
SHOW VIEWS;
SELECT COUNT(*) FROM yellow_taxi;
```

## Pipeline final

```bash
head ~/tp_hadoop_taxi/results/rapport_final.tsv
python3 ~/tp_hadoop_taxi/scripts/ex5/analyse_rapport.py
```
