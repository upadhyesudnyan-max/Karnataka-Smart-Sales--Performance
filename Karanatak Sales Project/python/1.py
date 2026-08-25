#####################################################################################
## Mini Project: Smart Sales Performance Analysis
#####################################################################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

# 1. Data Set Loading
df = pd.read_csv(
    r"E:\Karanatak Sales Project\data\Karnataka_Smart_Sales_Dataset_-Sales_Data.csv"
)

print("First 10 Rows:")
print(df.head(10))


# 2. Data Cleaning & Preprocessing
print("\nCleaning Data & Preprocessing...")

# First 5 rows
print("\nFirst 5 Rows:")
print(df.head())

# Last 5 rows
print("\nLast 5 Rows:")
print(df.tail())

# Dataset information
print("\nDataset Information:")
print(df.info())

# Statistical summary
print("\nStatistical Summary:")
print(df.describe())

# Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Duplicate values
print("\nDuplicate Rows:")
print(df.duplicated().sum())

# Remove duplicates
df.drop_duplicates(inplace=True)

print("\nDuplicate rows removed.")

# Column names
print("\nColumn Names:")
print(df.columns)

# Rows and columns
print("\nDataset Shape:")
print(df.shape)

# Unique values
print("\nNumber of Unique Values:")
print(df.nunique())

# Data types
print("\nData Types:")
print(df.dtypes)

#Add Date conversion
df["Date"] = pd.to_datetime(df["Date"])
print(df["Date"].dtype)

# Check missing values
print(df.isnull().sum())

# Remove duplicates
df.drop_duplicates(inplace=True)

# Convert Date
df["Date"] = pd.to_datetime(df["Date"])

# Check again
print("\nAfter Cleaning:")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print("Duplicates:", df.duplicated().sum())
print("Missing Values:", df.isnull().sum().sum())

# Save cleaned dataset
output_file = r"E:\Karanatak Sales Project\data\Karnataka_Smart_Sales_Dataset_-Sales_Data.csv"

df.to_csv(output_file, index=False)

print("Clean dataset saved successfully!")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])



#3.	Feature engineering (Revenue, Month, Quarter)

# Revenue Calculation
print("\nCalculating Revenue...")

df['Net Revenue'] = df['Quantity'] * df['Unit_Price']
print("\nData after Revenue Calculation:")
print(df.head())

#Exploring the data Analysis
print("\nExploring the data Analysis:")
print("Sum:", df['Net Revenue'].sum())
print("Mean:", df['Net Revenue'].mean())
print("Max:", df['Net Revenue'].max())
print("Min:", df['Net Revenue'].min())
print("Median:", df['Net Revenue'].median())
print("Standard Deviation:", df['Net Revenue'].std())
print("\nData after Revenue Calculation:")
print(df.head())


# Convert Month to Quarter
print("\nConverting Month to Quarter...")
#Convert Date
df['Date'] = pd.to_datetime(df['Date'])

#Create Month Column
df['Month'] = df['Date'].dt.month_name()

#Create Month Column number
df['Month_Num'] = df['Date'].dt.month

#Create Year Column
df['Year'] = df['Date'].dt.year

#Create Quarter Column
df['Quarter'] = df['Date'].dt.quarter

# Create Year-Month column
df["Year_Month"] = df["Date"].dt.to_period("M").astype(str)

# Create Year-Quarter column
df["Year_Quarter"] = df["Date"].dt.to_period("Q").astype(str)

print("\nData after Feature Engineering:")
print(df.head())

# PROFIT BY REGION

print("\n--- PROFIT BY REGION ---")
region_profit = (
    df.groupby("Region")["Profit"].sum().sort_values(ascending=False))

print(region_profit)



#4. Exploratory Data Analysis (EDA)
print("\nExploratory Data Analysis (EDA)...")

#Revenue by Karnataka Region:
region_rev = df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
plt.figure(figsize=(8,5))
sns.barplot(x=region_rev.values, y=region_rev.index)
plt.title("Revenue by Karnataka Region")
plt.xlabel("Revenue (₹)")
plt.ylabel("Region")
plt.show()

#Monthly Sales Trend
monthly_sales = df.groupby("Month")['Net Revenue'].sum()
monthly_sales.plot(kind='line', marker='o', color='green')
plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Total Revenue (USD)")
plt.show()

#Heatmap: Revenue by Product Category and Region
pivot_table = df.pivot_table(values='Net Revenue', index='Product', columns='Region', aggfunc='sum')
sns.heatmap(pivot_table, annot=True, fmt=".0f")
plt.title("Revenue by Product Category and Region")
plt.xlabel("Region")
plt.ylabel("Product Category")
plt.show()

#pie Chart: Revenue Distribution by Product Category
category_revenue = df.groupby("Product")['Net Revenue'].sum()
category_revenue.plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='Set3')
plt.title("Revenue Distribution by Product Category")
plt.ylabel("")
plt.show()

# Top Products:
top=df.groupby("Product")["Net Revenue"].sum().sort_values(ascending=False).head(10)
top.plot(kind="bar")
plt.title("Top Products by Revenue")
plt.xlabel("Product Category")
plt.ylabel("Total Revenue")
plt.show()

# Region Wise Sales:
region_sales=df.groupby("Region")["Net Revenue"].sum()
region_sales.plot(kind="bar")
plt.title("Region Wise Sales")
plt.xlabel("Region")
plt.ylabel("Total_Revenue")
plt.show()

#Profit by Product
top5_combined = df.groupby("Product")[["Revenue","Profit"]].sum().sort_values("Profit", ascending=False).head(5)
top5_combined.plot(kind="bar", figsize=(10,6))
plt.title("Top 5 Products: Revenue vs Profit")
plt.xlabel("Product")
plt.ylabel("Value (INR)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#5.	Pattern detection (seasonality, growth trends)

yearly_sales = df.groupby('Year')['Net Revenue'].sum().reset_index()
sns.lineplot(x='Year', y='Net Revenue', data=yearly_sales, marker='o')
plt.title("Yearly Growth Trend")
plt.show()

#6.	Sales forecasting using ML

# Aggregate monthly revenue
monthly_sales = df.groupby('Year_Month')['Net Revenue'].sum().reset_index()

# Create time index
monthly_sales['Time_Index'] = np.arange(len(monthly_sales))

# Features and target
X = monthly_sales[['Time_Index']]
y = monthly_sales['Net Revenue']

# Train model
model = LinearRegression()
model.fit(X, y)

# Predict historical sales
monthly_sales['Predicted_Sales'] = model.predict(X)

# Forecast next 12 months
future_index = np.arange(len(monthly_sales), len(monthly_sales) + 12).reshape(-1, 1)
future_sales = model.predict(future_index)

# Create future dates
last_date = pd.to_datetime(monthly_sales['Year_Month'].iloc[-1])
future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=12, freq='MS')

forecast_df = pd.DataFrame({'Date': future_dates, 'Forecasted_Sales': future_sales})

# Plot
plt.figure(figsize=(12,6))
plt.plot(monthly_sales['Time_Index'], monthly_sales['Net Revenue'], label='Actual Sales', marker='o')
plt.plot(monthly_sales['Time_Index'], monthly_sales['Predicted_Sales'], label='Predicted Sales', linestyle='--')
plt.plot(np.arange(len(monthly_sales), len(monthly_sales) + 12), future_sales, label='Forecasted Sales', marker='o')
plt.title("Actual vs Predicted and Forecasted Sales")
plt.xlabel("Time Index")
plt.ylabel("Revenue (USD)")
plt.legend()
plt.grid(True)
plt.show()

