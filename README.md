
# 📊 Karnataka Smart Sales — Performance Analysis

An end-to-end sales analytics project for a simulated Karnataka retail dataset, covering data cleaning, feature engineering, exploratory data analysis, SQL-based reporting, an interactive Streamlit dashboard, and a Power BI dashboard with a revenue forecasting model.

---

## 🗂️ Project Overview

| Layer | Tool | Purpose |
|---|---|---|
| Data Cleaning & EDA | Python (Pandas, Matplotlib, Seaborn) | Clean raw data, engineer features, explore trends |
| Forecasting | Scikit-learn (Linear Regression) | Forecast future monthly revenue |
| Reporting | SQL | Aggregate summary tables (region, product, city, channel) |
| Interactive Dashboard | Streamlit | Web app for upload, cleaning, EDA, SQL-style summaries, and forecasting |
| BI Dashboard | Power BI | Executive dashboard with KPIs, trends, and regional breakdowns |

---

## 📁 Repository Structure

```
karnataka-smart-sales/
├── data/
│   └── Karnataka_Smart_Sales_Dataset_Sales_Data.csv
├── analysis.py              # Core pandas/matplotlib analysis script
├── app.py                   # Streamlit dashboard
├── queries.sql               # SQL summary queries
├── powerbi/
│   └── karnataka_sales_dashboard.pbix
└── README.md
```

---

## 📈 Dataset

The dataset contains transaction-level sales records across Karnataka with fields including:

- `Transaction_ID`, `Date`, `Region`, `City`, `Product`, `Sales_Channel`
- `Quantity`, `Unit_Price`, `Revenue`, `Profit`

**Coverage:** Jan 2025 – Jun 2026 · 6 regions · 20 cities · 10 products

---

## 🧹 Data Cleaning & Preprocessing

The pipeline (`analysis.py`):

1. Loads the raw CSV and inspects shape, dtypes, nulls, and duplicates.
2. Drops duplicate rows.
3. Converts `Date` to `datetime`.
4. Re-validates cleanliness (no missing values, no duplicates).
5. Saves the cleaned dataset back to disk.

---

## 🛠️ Feature Engineering

- **Net Revenue** = `Quantity × Unit_Price`
- **Month**, **Month_Num**, **Year**, **Quarter** — derived from `Date`
- **Year_Month**, **Year_Quarter** — period-based grouping keys for trend analysis
- **Profit by Region** — aggregated summary

---

## 🔍 Exploratory Data Analysis

Visualizations generated with Matplotlib/Seaborn:

- Revenue by Karnataka Region (bar)
- Monthly Sales Trend (line)
- Revenue by Product Category × Region (heatmap)
- Revenue Distribution by Product Category (pie)
- Top 10 Products by Revenue (bar)
- Region-wise Sales (bar)
- Top 5 Products: Revenue vs Profit (grouped bar)
- Yearly Growth Trend (line)

---

## 🔮 Sales Forecasting

A simple **Linear Regression** model is fit on a monthly time index of `Net Revenue` to:

- Predict historical monthly sales (trend line)
- Forecast the next 12 months of revenue
- Plot actual vs predicted vs forecasted sales

---

## 🗄️ SQL Reporting

`queries.sql` reproduces the core aggregations for a relational database (see file), including:

- Total transactions, revenue, quantity, and profit margin
- Revenue/profit/quantity by **Region**, **Product**, **City**, and **Sales_Channel**
- Top 10 transactions by revenue

---

## 💻 Streamlit Dashboard

`app.py` is a self-contained interactive dashboard that mirrors and extends the Python analysis:

**Features:**
- CSV upload or generated sample data
- Sidebar filters (Region, Product, Date range)
- **Overview** tab — KPI cards (Transactions, Revenue, Profit, Margin) + data preview
- **Cleaning Report** tab — before/after stats, dtypes, statistical summary, cleaned CSV download
- **EDA** tab — all core charts, filtered live
- **SQL-style Summary** tab — grouped tables matching the SQL queries
- **Forecast** tab — adjustable forecast horizon (3–24 months), trend chart, forecast table + CSV export

**Run locally:**
```bash
pip install streamlit pandas numpy matplotlib seaborn scikit-learn
streamlit run app.py
```

---

## 📊 Power BI Dashboard

The `.pbix` file includes:

- **KPI cards:** Total Revenue (₹252.95M), Total Profit (₹69.96M), Transactions (1K), Profit Margin
- **Revenue trend** by Year and Month (line chart)
- **Revenue by Sales Channel** (donut chart — Retail Store, Distributor, Corporate, Online)
- **Revenue by Region** (horizontal bar — South, Kalyana, North, Coastal, Malnad, Central Karnataka)
- **Top 10 City Revenue** table with region, revenue, and profit breakdown

---

## 🚀 Getting Started

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/karnataka-smart-sales.git
   cd karnataka-smart-sales
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the analysis script:
   ```bash
   python analysis.py
   ```
4. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```
5. Open `powerbi/karnataka_sales_dashboard.pbix` in Power BI Desktop for the executive view.

---

## 🧰 Tech Stack

`Python` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `Scikit-learn` · `Streamlit` · `SQL` · `Power BI`

---

## 📌 Notes

- Update the file path in `analysis.py` to point to your local dataset location.
- The Streamlit app auto-derives `Profit` (20% margin assumption) if it's missing from the uploaded CSV, and falls back to generated sample data if no file is uploaded.

---

## 📄 License

This project is available for personal and educational use. Add a license of your choice (e.g., MIT) if publishing publicly.
