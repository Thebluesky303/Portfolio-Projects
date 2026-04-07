-- House Price Analysis Project
-- This script contains exploratory SQL queries for analyzing London house prices.

CREATE DATABASE IF NOT EXISTS house_price_prediction;

-- Show available tables in the active database.
SHOW TABLES;

-- Review the schema before analysis.
DESCRIBE house_price_data_db;

-- Preview the raw data.
SELECT *
FROM house_price_prediction.house_price_data_db;

-- Average historical sale price by property type.
SELECT propertyType,
       AVG(history_price) AS avg_history_price,
       COUNT(*) AS total_records
FROM house_price_data_db
WHERE propertyType IS NOT NULL
GROUP BY propertyType
ORDER BY avg_history_price DESC;

-- Average rent by outcode.
SELECT outcode,
       AVG(rentEstimate_currentPrice) AS avg_rent,
       COUNT(*) AS total_records
FROM house_price_data_db
WHERE outcode IS NOT NULL
  AND rentEstimate_currentPrice IS NOT NULL
GROUP BY outcode
ORDER BY avg_rent DESC;

-- Historical price trend by year.
SELECT YEAR(history_date) AS sale_year,
       AVG(history_price) AS avg_history_price,
       COUNT(*) AS total_sales
FROM house_price_data_db
WHERE history_date IS NOT NULL
GROUP BY YEAR(history_date)
ORDER BY sale_year;

-- Relationship between bedroom count and average historical price.
SELECT bedrooms,
       AVG(history_price) AS avg_history_price,
       COUNT(*) AS total_records
FROM house_price_data_db
WHERE bedrooms IS NOT NULL
GROUP BY bedrooms
ORDER BY bedrooms;

-- High-value outcodes with at least 10 records.
SELECT outcode,
       AVG(history_price) AS avg_history_price,
       AVG(rentEstimate_currentPrice) AS avg_rent_estimate,
       COUNT(*) AS total_records
FROM house_price_data_db
WHERE outcode IS NOT NULL
GROUP BY outcode
HAVING COUNT(*) >= 10
ORDER BY avg_history_price DESC;
