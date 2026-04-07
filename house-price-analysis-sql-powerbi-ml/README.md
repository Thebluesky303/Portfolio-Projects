# House Price Analysis: SQL, Power BI, and Machine Learning

This project analyzes London house price data to explore pricing patterns, rental trends, and property characteristics using Python, SQL, and Power BI. It is designed as a portfolio project that demonstrates an end-to-end analytics workflow from exploratory data analysis to business-facing visualization and machine learning preparation.

## Project Overview

The workflow in this repository covers:

- Data loading and exploratory data analysis in Jupyter Notebook
- SQL queries for business-oriented property insights
- Power BI dashboards for visual storytelling
- A machine learning-oriented dataset preparation workflow

The dataset contains more than 418,000 records and includes property details such as postcode, bedrooms, bathrooms, floor area, sale estimates, rent estimates, and historical pricing.

## Objectives

- Understand how property features relate to house prices
- Explore price and rent patterns across outcodes
- Analyze historical house price trends over time
- Prepare a clean dataset for visualization and future predictive modeling

## Tech Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook
- SQL
- Power BI
- Scikit-learn

## Repository Structure

```text
house-price-analysis-sql-powerbi-ml/
|-- data/
|   |-- house_price_data.csv
|   `-- dataset link.txt
|-- notebooks/
|   `-- eda.ipynb
|-- powerbi/
|   |-- data-visualization.pbix
|   `-- house_price_visualization.pbix
|-- sql/
|   `-- house_price_sql_query.sql
|-- requirements.txt
`-- README.md
```

## Dataset

Source: [Kaggle House Price Data](https://www.kaggle.com/datasets/jakewright/house-price-data?select=kaggle_london_house_price_data.parquet)

The project uses London housing data containing:

- Geographic information such as postcode and outcode
- Property features such as bedrooms, bathrooms, living rooms, and floor area
- Sales history and estimated sale values
- Rental estimates and confidence indicators

## Analysis Workflow

### 1. Exploratory Data Analysis

The notebook in [notebooks/eda.ipynb](/C:/Users/User/Desktop/Bikash%20Limbu/Portfolio%20Projects/house-price-analysis-sql-powerbi-ml/notebooks/eda.ipynb) performs:

- Dataset loading
- Data type inspection
- Missing value analysis
- Datetime conversion
- Descriptive statistics
- Export preparation for visualization

### 2. SQL Analysis

The SQL script in [sql/house_price_sql_query.sql](/C:/Users/User/Desktop/Bikash%20Limbu/Portfolio%20Projects/house-price-analysis-sql-powerbi-ml/sql/house_price_sql_query.sql) answers portfolio-ready business questions such as:

- What is the average historical price by property type?
- Which outcodes have the highest average rent?
- How have house prices changed over time?
- How do bedroom counts relate to average historical prices?

### 3. Power BI Dashboard

The Power BI files in [powerbi](/C:/Users/User/Desktop/Bikash%20Limbu/Portfolio%20Projects/house-price-analysis-sql-powerbi-ml/powerbi) support visual exploration of:

- Price trends
- Rent comparisons by area
- Property-type comparisons
- Distribution of key housing features

### 4. Machine Learning Readiness

This repository also lays the foundation for predictive modeling by:

- Cleaning columns
- Converting date fields
- Handling missing values
- Preparing structured tabular data for downstream training

## Example Insights

- Flats and maisonettes appear frequently in the dataset and are important to segment separately from other property types.
- Outcodes can show strong differences in rent and historical sale price, making location a critical explanatory factor.
- Bedrooms, floor area, and sale estimate features are likely to be useful predictors for house price modeling.

These insights should be validated and expanded through the notebook, SQL outputs, and Power BI visuals.

## How To Run

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Launch Jupyter Notebook:

```bash
jupyter notebook
```

4. Open [notebooks/eda.ipynb](/C:/Users/User/Desktop/Bikash%20Limbu/Portfolio%20Projects/house-price-analysis-sql-powerbi-ml/notebooks/eda.ipynb) and run the analysis cells.

## Portfolio Value

This project demonstrates:

- Real-world data cleaning and exploration
- SQL-based analytical thinking
- Dashboard development in Power BI
- Preparation for machine learning workflows
- Ability to communicate insights across technical and business audiences

## Next Improvements

- Add model training and evaluation notebook
- Include dashboard screenshots in the README
- Add data dictionary and feature descriptions
- Add explicit business recommendations from the analysis

