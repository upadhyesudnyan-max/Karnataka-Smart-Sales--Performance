"""
Karnataka Smart Sales — Performance Analysis Dashboard
Run locally with:  streamlit run app.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from sklearn.linear_model import LinearRegression

sns.set_style("whitegrid")


# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Karnataka Smart Sales Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Karnataka Smart Sales — Performance Analysis")
st.caption(
    "Upload your sales CSV to clean the data, engineer features, explore trends, "
    "and forecast future revenue."
)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
REQUIRED_COLS = ["Date", "Region", "Product", "Quantity", "Unit_Price"]


@st.cache_data(show_spinner=False)
def load_data(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.columns = [c.strip() for c in df.columns]
    return df


def clean_and_engineer(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Mirrors the cleaning + feature engineering steps from the original script."""
    stats = {}
    stats["raw_rows"] = df.shape[0]
    stats["raw_cols"] = df.shape[1]
    stats["missing_before"] = int(df.isnull().sum().sum())
    stats["duplicates_before"] = int(df.duplicated().sum())

    df = df.drop_duplicates().copy()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Revenue / Net Revenue
    if {"Quantity", "Unit_Price"}.issubset(df.columns):
        df["Net Revenue"] = df["Quantity"] * df["Unit_Price"]
    if "Revenue" not in df.columns and "Net Revenue" in df.columns:
        df["Revenue"] = df["Net Revenue"]

    # Profit fallback if not present (assume 20% margin) so the dashboard still works
    if "Profit" not in df.columns and "Revenue" in df.columns:
        df["Profit"] = df["Revenue"] * 0.20

    if "Date" in df.columns:
        df["Month"] = df["Date"].dt.month_name()
        df["Month_Num"] = df["Date"].dt.month
        df["Year"] = df["Date"].dt.year
        df["Quarter"] = df["Date"].dt.quarter
        df["Year_Month"] = df["Date"].dt.to_period("M").astype(str)
        df["Year_Quarter"] = df["Date"].dt.to_period("Q").astype(str)

    stats["clean_rows"] = df.shape[0]
    stats["clean_cols"] = df.shape[1]
    stats["missing_after"] = int(df.isnull().sum().sum())
    stats["duplicates_after"] = int(df.duplicated().sum())

    return df, stats


def kpi_card(col, label, value, help_text=None):
    col.metric(label, value, help=help_text)


def show_fig(fig):
    """Render a matplotlib figure in Streamlit and close it to free memory."""
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ----------------------------------------------------------------------------
# Sidebar — upload + filters
# ----------------------------------------------------------------------------
st.sidebar.header("1. Data")
uploaded = st.sidebar.file_uploader("Upload Sales CSV", type=["csv"])

use_sample = st.sidebar.checkbox("Use generated sample data instead", value=not uploaded)

if uploaded is not None:
    raw_df = load_data(uploaded)
elif use_sample:
    rng = np.random.default_rng(42)
    n = 2000
    regions = ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi"]
    products = ["Electronics", "Groceries", "Apparel", "Furniture", "Beauty", "Sports"]
    channels = ["Online", "Retail Store", "Distributor"]
    dates = pd.date_range("2023-01-01", "2025-12-31", periods=n)
    raw_df = pd.DataFrame(
        {
            "Transaction_ID": np.arange(1, n + 1),
            "Date": rng.permutation(dates),
            "Region": rng.choice(regions, n),
            "City": rng.choice(regions, n),
            "Product": rng.choice(products, n),
            "Sales_Channel": rng.choice(channels, n),
            "Quantity": rng.integers(1, 20, n),
            "Unit_Price": rng.integers(100, 5000, n),
        }
    )
    raw_df["Revenue"] = raw_df["Quantity"] * raw_df["Unit_Price"]
    raw_df["Profit"] = raw_df["Revenue"] * rng.uniform(0.1, 0.35, n)
else:
    st.info("⬅️ Upload a CSV in the sidebar, or check 'Use generated sample data' to explore the dashboard.")
    st.stop()

df, stats = clean_and_engineer(raw_df)

missing_required = [c for c in REQUIRED_COLS if c not in raw_df.columns]
if missing_required:
    st.warning(
        f"Your file is missing expected columns: {missing_required}. "
        "Some charts may not render until these are present."
    )

# Sidebar filters
st.sidebar.header("2. Filters")
if "Region" in df.columns:
    regions_sel = st.sidebar.multiselect("Region", sorted(df["Region"].dropna().unique()), default=None)
    if regions_sel:
        df = df[df["Region"].isin(regions_sel)]
if "Product" in df.columns:
    products_sel = st.sidebar.multiselect("Product", sorted(df["Product"].dropna().unique()), default=None)
    if products_sel:
        df = df[df["Product"].isin(products_sel)]
if "Date" in df.columns and df["Date"].notna().any():
    min_d, max_d = df["Date"].min(), df["Date"].max()
    date_range = st.sidebar.date_input("Date range", (min_d.date(), max_d.date()))
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df = df[(df["Date"] >= start) & (df["Date"] <= end)]

rev_col = "Net Revenue" if "Net Revenue" in df.columns else ("Revenue" if "Revenue" in df.columns else None)

# ----------------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------------
tab_overview, tab_clean, tab_eda, tab_sql, tab_forecast = st.tabs(
    ["🏠 Overview", "🧹 Cleaning Report", "📈 EDA", "🗄️ SQL-style Summary", "🔮 Forecast"]
)

# ----------------------------------------------------------------------------
# Overview
# ----------------------------------------------------------------------------
with tab_overview:
    st.subheader("Key Metrics")
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "Transactions", f"{df.shape[0]:,}")
    if rev_col:
        kpi_card(c2, "Total Revenue", f"₹{df[rev_col].sum():,.0f}")
        kpi_card(c3, "Avg Order Value", f"₹{df[rev_col].mean():,.0f}")
    if "Profit" in df.columns:
        kpi_card(c4, "Total Profit", f"₹{df['Profit'].sum():,.0f}")
        if rev_col:
            margin = (df["Profit"].sum() / df[rev_col].sum()) * 100 if df[rev_col].sum() else 0
            kpi_card(c5, "Profit Margin", f"{margin:.2f}%")

    st.divider()
    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

# ----------------------------------------------------------------------------
# Cleaning Report
# ----------------------------------------------------------------------------
with tab_clean:
    st.subheader("Cleaning & Preprocessing Summary")
    left, right = st.columns(2)
    with left:
        st.markdown("**Before cleaning**")
        st.write(f"- Rows: {stats['raw_rows']:,}")
        st.write(f"- Columns: {stats['raw_cols']}")
        st.write(f"- Missing values: {stats['missing_before']:,}")
        st.write(f"- Duplicate rows: {stats['duplicates_before']:,}")
    with right:
        st.markdown("**After cleaning**")
        st.write(f"- Rows: {stats['clean_rows']:,}")
        st.write(f"- Columns: {stats['clean_cols']}")
        st.write(f"- Missing values: {stats['missing_after']:,}")
        st.write(f"- Duplicate rows: {stats['duplicates_after']:,}")

    st.divider()
    st.markdown("**Data types**")
    st.dataframe(df.dtypes.astype(str).rename("dtype"), use_container_width=True)

    st.markdown("**Statistical summary (numeric columns)**")
    st.dataframe(df.describe(), use_container_width=True)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download cleaned dataset (CSV)",
        data=csv_bytes,
        file_name="Karnataka_Smart_Sales_Dataset_Cleaned.csv",
        mime="text/csv",
    )

# ----------------------------------------------------------------------------
# EDA (matplotlib / seaborn, same style as the original script)
# ----------------------------------------------------------------------------
with tab_eda:
    if rev_col is None:
        st.warning("Need a Revenue / Quantity+Unit_Price column to build EDA charts.")
    else:
        st.subheader("Revenue by Region")
        if "Region" in df.columns:
            region_rev = df.groupby("Region")[rev_col].sum().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(x=region_rev.values, y=region_rev.index, ax=ax)
            ax.set_title("Revenue by Karnataka Region")
            ax.set_xlabel("Revenue (₹)")
            ax.set_ylabel("Region")
            show_fig(fig)

        st.subheader("Monthly Sales Trend")
        if "Year_Month" in df.columns:
            monthly = df.groupby("Year_Month")[rev_col].sum().sort_index()
            fig, ax = plt.subplots(figsize=(10, 5))
            monthly.plot(kind="line", marker="o", color="green", ax=ax)
            ax.set_title("Monthly Sales Trend")
            ax.set_xlabel("Month")
            ax.set_ylabel("Total Revenue (₹)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            show_fig(fig)

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Revenue by Product & Region")
            if {"Product", "Region"}.issubset(df.columns):
                pivot = df.pivot_table(values=rev_col, index="Product", columns="Region", aggfunc="sum")
                fig, ax = plt.subplots(figsize=(7, 6))
                sns.heatmap(pivot, annot=True, fmt=".0f", ax=ax, cmap="Blues")
                ax.set_title("Revenue by Product Category and Region")
                ax.set_xlabel("Region")
                ax.set_ylabel("Product Category")
                plt.tight_layout()
                show_fig(fig)

        with col_b:
            st.subheader("Revenue Distribution by Product")
            if "Product" in df.columns:
                cat_rev = df.groupby("Product")[rev_col].sum()
                fig, ax = plt.subplots(figsize=(7, 6))
                cat_rev.plot(kind="pie", autopct="%1.1f%%", startangle=90, cmap="Set3", ax=ax)
                ax.set_title("Revenue Distribution by Product Category")
                ax.set_ylabel("")
                plt.tight_layout()
                show_fig(fig)

        st.subheader("Top 10 Products by Revenue")
        if "Product" in df.columns:
            top = df.groupby("Product")[rev_col].sum().sort_values(ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(9, 5))
            top.plot(kind="bar", ax=ax)
            ax.set_title("Top Products by Revenue")
            ax.set_xlabel("Product Category")
            ax.set_ylabel("Total Revenue")
            plt.xticks(rotation=45)
            plt.tight_layout()
            show_fig(fig)

        st.subheader("Region-wise Sales")
        if "Region" in df.columns:
            region_sales = df.groupby("Region")[rev_col].sum()
            fig, ax = plt.subplots(figsize=(9, 5))
            region_sales.plot(kind="bar", ax=ax)
            ax.set_title("Region Wise Sales")
            ax.set_xlabel("Region")
            ax.set_ylabel("Total Revenue")
            plt.xticks(rotation=45)
            plt.tight_layout()
            show_fig(fig)

        if "Profit" in df.columns and "Product" in df.columns:
            st.subheader("Top 5 Products: Revenue vs Profit")
            top5 = df.groupby("Product")[[rev_col, "Profit"]].sum().sort_values("Profit", ascending=False).head(5)
            fig, ax = plt.subplots(figsize=(10, 6))
            top5.plot(kind="bar", ax=ax)
            ax.set_title("Top 5 Products: Revenue vs Profit")
            ax.set_xlabel("Product")
            ax.set_ylabel("Value (₹)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            show_fig(fig)

        if "Year" in df.columns:
            st.subheader("Yearly Growth Trend")
            yearly = df.groupby("Year")[rev_col].sum().reset_index()
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.lineplot(x="Year", y=rev_col, data=yearly, marker="o", ax=ax)
            ax.set_title("Yearly Growth Trend")
            plt.tight_layout()
            show_fig(fig)

# ----------------------------------------------------------------------------
# SQL-style Summary tables (mirrors the SQL script)
# ----------------------------------------------------------------------------
with tab_sql:
    st.subheader("Summary tables (equivalent to the SQL queries)")

    if rev_col:
        st.markdown("**Overall totals**")
        totals = {
            "Total Transactions": [df.shape[0]],
            "Total Revenue": [df[rev_col].sum()],
            "Total Quantity": [df["Quantity"].sum() if "Quantity" in df.columns else None],
        }
        if "Profit" in df.columns:
            totals["Total Profit"] = [df["Profit"].sum()]
            totals["Profit Margin %"] = [
                round((df["Profit"].sum() / df[rev_col].sum()) * 100, 2) if df[rev_col].sum() else 0
            ]
        st.dataframe(pd.DataFrame(totals), use_container_width=True)

    if "Region" in df.columns and rev_col:
        st.markdown("**By Region**")
        agg = {"Transactions": (rev_col, "count"), "Total_Revenue": (rev_col, "sum")}
        if "Profit" in df.columns:
            agg["Total_Profit"] = ("Profit", "sum")
        if "Quantity" in df.columns:
            agg["Total_Quantity"] = ("Quantity", "sum")
        by_region = df.groupby("Region").agg(**agg).sort_values("Total_Revenue", ascending=False).reset_index()
        st.dataframe(by_region, use_container_width=True)

    if "Product" in df.columns and rev_col:
        st.markdown("**By Product**")
        agg = {"Transactions": (rev_col, "count"), "Total_Revenue": (rev_col, "sum")}
        if "Profit" in df.columns:
            agg["Total_Profit"] = ("Profit", "sum")
        if "Quantity" in df.columns:
            agg["Total_Quantity"] = ("Quantity", "sum")
        by_product = df.groupby("Product").agg(**agg).sort_values("Total_Revenue", ascending=False).reset_index()
        st.dataframe(by_product, use_container_width=True)

    if "City" in df.columns and rev_col:
        st.markdown("**By City**")
        agg = {"Total_Revenue": (rev_col, "sum")}
        if "Profit" in df.columns:
            agg["Total_Profit"] = ("Profit", "sum")
        by_city = df.groupby("City").agg(**agg).sort_values("Total_Revenue", ascending=False).reset_index()
        st.dataframe(by_city, use_container_width=True)

    if "Sales_Channel" in df.columns and rev_col:
        st.markdown("**By Sales Channel**")
        agg = {"Transactions": (rev_col, "count"), "Revenue": (rev_col, "sum")}
        if "Quantity" in df.columns:
            agg["Quantity"] = ("Quantity", "sum")
        if "Profit" in df.columns:
            agg["Profit"] = ("Profit", "sum")
        by_channel = df.groupby("Sales_Channel").agg(**agg).sort_values("Revenue", ascending=False).reset_index()
        st.dataframe(by_channel, use_container_width=True)

    if rev_col:
        st.markdown("**Top 10 transactions by Revenue**")
        cols_show = [c for c in ["Transaction_ID", "Date", "City", "Region", "Product", rev_col, "Profit"] if c in df.columns]
        st.dataframe(df.sort_values(rev_col, ascending=False)[cols_show].head(10), use_container_width=True)

# ----------------------------------------------------------------------------
# Forecast
# ----------------------------------------------------------------------------
with tab_forecast:
    st.subheader("Sales Forecasting (Linear Regression)")

    if rev_col is None or "Year_Month" not in df.columns:
        st.warning("Need Date + Revenue columns to build a forecast.")
    else:
        horizon = st.slider("Months to forecast", min_value=3, max_value=24, value=12)

        monthly_sales = df.groupby("Year_Month")[rev_col].sum().reset_index().sort_values("Year_Month")
        monthly_sales["Time_Index"] = np.arange(len(monthly_sales))

        if len(monthly_sales) < 3:
            st.warning("Not enough monthly data points to fit a reliable trend line.")
        else:
            X = monthly_sales[["Time_Index"]]
            y = monthly_sales[rev_col]

            model = LinearRegression()
            model.fit(X, y)
            monthly_sales["Predicted_Sales"] = model.predict(X)

            future_index = np.arange(len(monthly_sales), len(monthly_sales) + horizon).reshape(-1, 1)
            future_sales = model.predict(future_index)

            last_period = pd.Period(monthly_sales["Year_Month"].iloc[-1], freq="M")
            future_periods = pd.period_range(last_period + 1, periods=horizon, freq="M")
            forecast_df = pd.DataFrame({"Year_Month": future_periods.astype(str), "Forecasted_Sales": future_sales})

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(monthly_sales["Time_Index"], monthly_sales[rev_col], label="Actual Sales", marker="o")
            ax.plot(
                monthly_sales["Time_Index"],
                monthly_sales["Predicted_Sales"],
                label="Predicted Sales",
                linestyle="--",
            )
            ax.plot(
                np.arange(len(monthly_sales), len(monthly_sales) + horizon),
                future_sales,
                label="Forecasted Sales",
                marker="o",
            )
            ax.set_title("Actual vs Predicted and Forecasted Sales")
            ax.set_xlabel("Time Index")
            ax.set_ylabel("Revenue (₹)")
            ax.legend()
            ax.grid(True)
            plt.tight_layout()
            show_fig(fig)

            c1, c2 = st.columns(2)
            c1.metric("Avg monthly growth (slope)", f"₹{model.coef_[0]:,.0f}/month")
            c2.metric(f"Forecasted revenue (next {horizon} mo)", f"₹{future_sales.sum():,.0f}")

            st.markdown("**Forecast table**")
            st.dataframe(forecast_df, use_container_width=True)

            fc_csv = forecast_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download forecast (CSV)", data=fc_csv, file_name="sales_forecast.csv", mime="text/csv")

st.divider()
st.caption("Built with Streamlit • Replicates and extends the original pandas/matplotlib analysis script.")