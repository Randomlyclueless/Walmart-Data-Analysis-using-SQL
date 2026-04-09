import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="🛒 Walmart SQL Dashboard", layout="wide")

# ========================= LOAD & CLEAN DATA =========================
@st.cache_data
def load_data():
    df = pd.read_csv("Walmart.csv")

    df.columns = (df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
                  .str.replace(".", "", regex=False))

    # Clean unit_price
    if "unit_price" in df.columns:
        df["unit_price"] = df["unit_price"].astype(str).str.replace("$", "", regex=False).str.strip()
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # Numeric columns
    for col in ["quantity", "rating", "profit_margin"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Date & Time
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S", errors="coerce").dt.strftime("%H:%M:%S")

    return df

df = load_data()

# ========================= SQL SETUP =========================
conn = sqlite3.connect(":memory:", check_same_thread=False)
df.to_sql("walmart", conn, index=False, if_exists="replace")

def run_sql(query):
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"SQL Error: {e}")
        return pd.DataFrame()

# ========================= SIDEBAR =========================
st.sidebar.title("🔎 Filters")
branch_filter = st.sidebar.selectbox(
    "Select Branch", ["All"] + sorted(df["branch"].dropna().unique().tolist())
)

filtered_df = df.copy()
if branch_filter != "All":
    filtered_df = filtered_df[filtered_df["branch"] == branch_filter]

filtered_conn = sqlite3.connect(":memory:", check_same_thread=False)
filtered_df.to_sql("walmart", filtered_conn, index=False, if_exists="replace")

def run_filtered_sql(query):
    try:
        return pd.read_sql_query(query, filtered_conn)
    except Exception as e:
        st.error(f"SQL Error: {e}")
        return pd.DataFrame()

# ========================= MAIN UI =========================
st.title("🛒 Walmart Sales Dashboard")
st.markdown("### All SQL Queries with Charts & Tables")

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
total_rev = (filtered_df["unit_price"] * filtered_df["quantity"]).sum()
col1.metric("Total Revenue", f"${total_rev:,.0f}")
col2.metric("Transactions", len(filtered_df))
col3.metric("Avg Rating", f"{filtered_df['rating'].mean():.2f}" if len(filtered_df) > 0 else "N/A")
col4.metric("Total Profit", f"${(filtered_df['unit_price'] * filtered_df['quantity'] * filtered_df.get('profit_margin', 0.05)).sum():,.0f}")

tabs = st.tabs(["📊 Dashboard Visuals", "📋 All SQL Queries", "🔍 Custom SQL Explorer"])

# ====================== TAB 1: DASHBOARD VISUALS ======================
with tabs[0]:
    st.header("Key Visual Insights")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("💳 Payment Distribution")
        r1 = run_filtered_sql("SELECT payment_method, COUNT(*) as count FROM walmart GROUP BY payment_method")
        if not r1.empty:
            fig1 = px.pie(r1, names="payment_method", values="count", hole=0.4, title="Payment Methods")
            st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("⏰ Sales by Shift")
        r4 = run_filtered_sql("""
            SELECT 
                CASE 
                    WHEN CAST(strftime('%H', time) AS INTEGER) < 12 THEN 'MORNING'
                    WHEN CAST(strftime('%H', time) AS INTEGER) BETWEEN 12 AND 17 THEN 'AFTERNOON'
                    ELSE 'EVENING'
                END AS shift,
                COUNT(*) AS total_invoices
            FROM walmart GROUP BY shift
        """)
        if not r4.empty:
            fig4 = px.bar(r4, x="shift", y="total_invoices", color="shift", title="Sales by Shift")
            st.plotly_chart(fig4, use_container_width=True)

    st.subheader("💰 Profit by Category")
    r_profit = run_filtered_sql("""
        SELECT category, 
               ROUND(SUM(unit_price * quantity * COALESCE(profit_margin, 0.05)), 2) as total_profit
        FROM walmart 
        GROUP BY category 
        ORDER BY total_profit DESC
    """)
    if not r_profit.empty:
        fig_profit = px.bar(r_profit, x="category", y="total_profit", 
                            text="total_profit", color="category", title="Total Profit by Category")
        fig_profit.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        st.plotly_chart(fig_profit, use_container_width=True)

# ====================== TAB 2: ALL SQL QUERIES ======================
with tabs[1]:
    st.header("📋 All Business Questions with Results")

    all_queries = [
        ("Q1: Payment methods - Transactions & Quantity", """
            SELECT payment_method, 
                   COUNT(*) as transactions, 
                   SUM(quantity) as total_quantity 
            FROM walmart GROUP BY payment_method;
        """, "bar"),

        ("Q2: Highest rated category per branch", """
            SELECT Branch, category, ROUND(avg_rating, 2) as avg_rating
            FROM (
                SELECT Branch, category, AVG(rating) as avg_rating,
                       ROW_NUMBER() OVER (PARTITION BY Branch ORDER BY AVG(rating) DESC) as rnk
                FROM walmart GROUP BY Branch, category
            ) t WHERE rnk = 1;
        """, None),

        ("Q3: Busiest day for each branch", """
            SELECT Branch, day_name, total_transactions
            FROM (
                SELECT Branch,
                       CASE strftime('%w', date)
                           WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday' WHEN '2' THEN 'Tuesday'
                           WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday'
                           WHEN '6' THEN 'Saturday'
                       END as day_name,
                       COUNT(*) as total_transactions,
                       ROW_NUMBER() OVER (PARTITION BY Branch ORDER BY COUNT(*) DESC) as rn
                FROM walmart GROUP BY Branch, day_name
            ) t WHERE rn = 1;
        """, None),

        ("Q4: Total quantity sold per payment method", """
            SELECT payment_method, SUM(quantity) as total_quantity_sold 
            FROM walmart GROUP BY payment_method ORDER BY total_quantity_sold DESC;
        """, "bar"),

        ("Q5: Rating stats per city", """
            SELECT City as city, 
                   ROUND(AVG(rating), 2) as avg_rating,
                   MIN(rating) as min_rating,
                   MAX(rating) as max_rating
            FROM walmart GROUP BY City;
        """, None),

        ("Q6: Total Profit per Category", """
            SELECT category, 
                   ROUND(SUM(unit_price * quantity * COALESCE(profit_margin, 0.05)), 2) as total_profit
            FROM walmart GROUP BY category ORDER BY total_profit DESC;
        """, "bar"),

        ("Q7: Most common payment method per branch", """
            SELECT Branch, payment_method as preferred_payment_method
            FROM (
                SELECT Branch, payment_method, COUNT(*) as cnt,
                       ROW_NUMBER() OVER (PARTITION BY Branch ORDER BY COUNT(*) DESC) as rn
                FROM walmart GROUP BY Branch, payment_method
            ) t WHERE rn = 1;
        """, None),

        ("Q8: Morning / Afternoon / Evening Sales", """
            SELECT 
                CASE 
                    WHEN CAST(strftime('%H', time) AS INTEGER) < 12 THEN 'MORNING'
                    WHEN CAST(strftime('%H', time) AS INTEGER) BETWEEN 12 AND 17 THEN 'AFTERNOON'
                    ELSE 'EVENING'
                END AS shift,
                COUNT(*) as total_invoices
            FROM walmart GROUP BY shift;
        """, "bar"),

        ("Q9: Top 5 branches with highest revenue decrease (2022 vs 2023)", """
            SELECT Branch, revenue_2022, revenue_2023,
                   ROUND(((revenue_2022 - revenue_2023)*100.0 / revenue_2022), 2) as decrease_percent
            FROM (
                SELECT Branch,
                       SUM(CASE WHEN strftime('%Y', date)='2022' THEN unit_price*quantity ELSE 0 END) as revenue_2022,
                       SUM(CASE WHEN strftime('%Y', date)='2023' THEN unit_price*quantity ELSE 0 END) as revenue_2023
                FROM walmart GROUP BY Branch
            ) t 
            WHERE revenue_2022 > 0 
            ORDER BY decrease_percent DESC LIMIT 5;
        """, None),
    ]

    for title, query, chart_type in all_queries:
        with st.expander(f"**{title}**", expanded=False):
            st.code(query.strip(), language="sql")
            
            result = run_filtered_sql(query)
            
            if not result.empty:
                st.dataframe(result, use_container_width=True, hide_index=True)
                
                # Show chart if specified
                if chart_type == "bar" and len(result.columns) >= 2:
                    x_col = result.columns[0]
                    y_col = result.columns[1]
                    fig = px.bar(result, x=x_col, y=y_col, title=title, color=x_col if len(result.columns)>1 else None)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data returned.")

# ====================== TAB 3: CUSTOM SQL EXPLORER ======================
with tabs[2]:
    st.header("🔍 Custom SQL Query Explorer")
    st.info("Paste any SQL query here to test instantly.")

    custom_query = st.text_area(
        "Write or paste your SQL query:",
        value="SELECT payment_method, COUNT(*) as count, SUM(quantity) as qty FROM walmart GROUP BY payment_method",
        height=120
    )

    if st.button("🚀 Run Custom Query"):
        result = run_filtered_sql(custom_query)
        if not result.empty:
            st.dataframe(result, use_container_width=True, hide_index=True)
            st.success(f"✅ Query executed successfully! {len(result)} rows returned.")
        else:
            st.warning("Query returned no results or had an error.")

st.caption("✅ Clean UI with Charts | All 9 Questions Included | Branch Filter Applied Everywhere")