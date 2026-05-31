CREATE DATABASE IF NOT EXISTS nyc_taxi_tp;
USE nyc_taxi_tp;

CREATE EXTERNAL TABLE IF NOT EXISTS yellow_taxi (
VendorID INT,
tpep_pickup_datetime STRING,
tpep_dropoff_datetime STRING,
passenger_count INT,
trip_distance FLOAT,
RatecodeID INT,
store_and_fwd_flag STRING,
PULocationID INT,
DOLocationID INT,
payment_type INT,
fare_amount FLOAT,
extra FLOAT,
mta_tax FLOAT,
tip_amount FLOAT,
tolls_amount FLOAT,
improvement_surcharge FLOAT,
total_amount FLOAT,
congestion_surcharge FLOAT,
airport_fee FLOAT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/leconcret/taxi/raw/'
TBLPROPERTIES ("skip.header.line.count"="1");

SELECT COUNT(*) FROM yellow_taxi;

SELECT
CASE payment_type
WHEN 1 THEN 'Carte_credit'
WHEN 2 THEN 'Cash'
WHEN 3 THEN 'Pas_charge'
WHEN 4 THEN 'Litige'
WHEN 5 THEN 'Inconnu'
WHEN 6 THEN 'Annule'
ELSE CONCAT('Autre(',CAST(payment_type AS STRING),')')
END AS mode_paiement,
COUNT(*) AS nb_courses,
ROUND(AVG(fare_amount),2) AS tarif_moyen,
ROUND(AVG(tip_amount),2) AS pourboire_moyen,
ROUND(AVG(tip_amount / NULLIF(fare_amount,0))*100,1) AS taux_pourboire_pct,
ROUND(SUM(total_amount),0) AS recette_totale
FROM yellow_taxi
WHERE fare_amount>0 AND fare_amount<500 AND tip_amount>=0
GROUP BY payment_type
ORDER BY nb_courses DESC;

SELECT
PULocationID AS zone_depart,
DOLocationID AS zone_arrivee,
COUNT(*) AS nb_courses,
ROUND(AVG(trip_distance),2) AS dist_moy_miles,
ROUND(AVG(fare_amount),2) AS tarif_moy,
ROUND(AVG(tip_amount),2) AS pourboire_moy
FROM yellow_taxi
WHERE trip_distance>0 AND fare_amount>0 AND PULocationID != DOLocationID
GROUP BY PULocationID, DOLocationID
ORDER BY nb_courses DESC
LIMIT 20;

SELECT
WEEKOFYEAR(TO_DATE(tpep_pickup_datetime)) AS semaine,
YEAR(TO_DATE(tpep_pickup_datetime)) AS annee,
COUNT(*) AS nb_courses,
ROUND(SUM(total_amount),0) AS recette_totale,
ROUND(AVG(total_amount),2) AS recette_moyenne,
ROUND(AVG(trip_distance),2) AS distance_moyenne,
ROUND(AVG(passenger_count),2) AS passagers_moyens
FROM yellow_taxi
WHERE tpep_pickup_datetime IS NOT NULL
AND total_amount>0 AND total_amount<500
AND YEAR(TO_DATE(tpep_pickup_datetime))=2023
GROUP BY YEAR(TO_DATE(tpep_pickup_datetime)), WEEKOFYEAR(TO_DATE(tpep_pickup_datetime))
ORDER BY annee, semaine;

SELECT COUNT(*) AS courses_suspectes
FROM yellow_taxi
WHERE trip_distance > 1
AND (unix_timestamp(tpep_dropoff_datetime)-unix_timestamp(tpep_pickup_datetime)) < 60;

CREATE VIEW IF NOT EXISTS peak_vs_offpeak AS
SELECT *,
CASE
WHEN HOUR(CAST(tpep_pickup_datetime AS TIMESTAMP)) BETWEEN 7 AND 9 THEN 'POINTE_MATIN'
WHEN HOUR(CAST(tpep_pickup_datetime AS TIMESTAMP)) BETWEEN 16 AND 19 THEN 'POINTE_SOIR'
ELSE 'HEURE_CREUSE'
END AS periode
FROM yellow_taxi;

SELECT
periode,
COUNT(*) AS nb_courses,
ROUND(AVG(fare_amount),2) AS recette_moy,
ROUND(AVG(tip_amount),2) AS pourboire_moy,
ROUND(SUM(total_amount),0) AS recette_totale
FROM peak_vs_offpeak
WHERE fare_amount>0 AND total_amount<500
GROUP BY periode
ORDER BY recette_totale DESC;
