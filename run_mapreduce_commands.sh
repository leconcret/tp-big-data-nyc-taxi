#!/usr/bin/env bash

export HDFS_USER=$(whoami)
export HADOOP_STREAMING_JAR=$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.4.0.jar

echo "HDFS_USER=$HDFS_USER"
echo "HADOOP_STREAMING_JAR=$HADOOP_STREAMING_JAR"

hdfs dfs -rm -r -f /user/$HDFS_USER/taxi/processed/trips_per_hour
hadoop jar $HADOOP_STREAMING_JAR -D mapreduce.job.reduces=1 -input /user/$HDFS_USER/taxi/raw/ -output /user/$HDFS_USER/taxi/processed/trips_per_hour -mapper "python3 trips_hour_mapper.py" -reducer "python3 trips_hour_reducer.py" -file scripts/ex1/trips_hour_mapper.py -file scripts/ex1/trips_hour_reducer.py

hdfs dfs -rm -r -f /user/$HDFS_USER/taxi/processed/revenue_per_zone
hadoop jar $HADOOP_STREAMING_JAR -D mapreduce.job.reduces=1 -input /user/$HDFS_USER/taxi/raw/ -output /user/$HDFS_USER/taxi/processed/revenue_per_zone -mapper "python3 revenue_zone_mapper.py" -reducer "python3 revenue_zone_reducer.py" -file scripts/ex2/revenue_zone_mapper.py -file scripts/ex2/revenue_zone_reducer.py

hdfs dfs -rm -r -f /user/$HDFS_USER/taxi/processed/speed_analysis
hadoop jar $HADOOP_STREAMING_JAR -D mapreduce.job.reduces=1 -input /user/$HDFS_USER/taxi/raw/ -output /user/$HDFS_USER/taxi/processed/speed_analysis -mapper "python3 speed_analysis_mapper.py" -reducer "python3 speed_analysis_reducer.py" -file scripts/ex3/speed_analysis_mapper.py -file scripts/ex3/speed_analysis_reducer.py

hdfs dfs -rm -r -f /user/$HDFS_USER/taxi/processed/peak_revenue
hadoop jar $HADOOP_STREAMING_JAR -D mapreduce.job.reduces=1 -D mapreduce.job.name="NYC_Taxi_Peak_Revenue" -input /user/$HDFS_USER/taxi/raw/ -output /user/$HDFS_USER/taxi/processed/peak_revenue -mapper "python3 peak_revenue_mapper.py" -reducer "python3 peak_revenue_reducer.py" -file scripts/ex5/peak_revenue_mapper.py -file scripts/ex5/peak_revenue_reducer.py
