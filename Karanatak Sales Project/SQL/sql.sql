create database karnataka_sales;
use karnataka_sales;

SELECT *
FROM sales;

SELECT COUNT(*) AS Total_Transactions
FROM sales;


SELECT SUM(Revenue) AS Total_Revenue
FROM sales;

SELECT SUM(Quantity) AS Total_Quantity
FROM sales;
SELECT COUNT(*) AS Total_Transactions
FROM sales;
SELECT 
    ROUND((SUM(Profit) / SUM(Revenue)) * 100, 2) AS Profit_Margin
FROM sales;

SELECT 
    Region,
    SUM(Revenue) AS Total_Revenue,
    SUM(Profit) AS Total_Profit,
    SUM(Quantity) AS Total_Quantity
FROM sales
GROUP BY Region
ORDER BY Total_Revenue DESC;

SELECT 
    Product,
    SUM(Revenue) AS Total_Revenue,
    SUM(Profit) AS Total_Profit,
    SUM(Quantity) AS Total_Quantity
FROM sales
GROUP BY Product
ORDER BY Total_Revenue DESC;

SELECT 
    City,
    SUM(Revenue) AS Total_Revenue,
    SUM(Profit) AS Total_Profit
FROM sales
GROUP BY City
ORDER BY Total_Revenue DESC;


SELECT
    Sales_Channel,
    COUNT(*) AS Transactions,
    SUM(Quantity) AS Quantity,
    SUM(Revenue) AS Revenue,
    SUM(Profit) AS Profit
FROM sales
GROUP BY Sales_Channel
ORDER BY Revenue DESC;

SELECT
    Transaction_ID,
    Date,
    City,
    Region,
    Product,
    Revenue,
    Profit
FROM sales
ORDER BY Revenue DESC
LIMIT 10;

