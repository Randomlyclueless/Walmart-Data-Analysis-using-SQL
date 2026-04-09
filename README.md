# 🛒 Walmart Sales Data Analysis (SQL Project)

## 📌 Project Overview
An end-to-end SQL analysis of Walmart's retail transaction data across **100 branches** and **98 cities**, covering **9,969 total transactions**. The project uncovers actionable insights across payment behavior, product performance, customer ratings, and revenue trends.

**Key Findings at a Glance:**
- 💳 **Ewallet dominates** — preferred payment method in 72% of branches
- 🛍️ **Fashion & Home categories** drive ~78% of total profit ($384,528 combined out of ~$476,139)
- 🕐 **Afternoon is peak shopping time** — 46.5% of all transactions happen between 12–5 PM
- ⭐ **Ratings range from 4.99 to 6.81** across cities — Huntsville leads, Rowlett trails
- 📉 **4 branches saw 100% revenue drop** from 2022 to 2023 — a major red flag
- 🏆 **Perfect 10.0 rating** achieved by WALM034 (Health & Beauty)

---

## 🎯 Objectives
- Analyze transaction patterns across branches
- Identify customer payment preferences
- Evaluate product category performance
- Understand sales trends by time and location
- Calculate profit contributions by category

---

## 🛠️ Tech Stack
- SQL (MySQL)
- Dataset: Walmart Sales Data
- Tools: MySQL Workbench / SQLite / Any SQL Environment

---

## 📂 Dataset Description
The dataset contains transactional sales data including:
- Branch
- City
- Category
- Payment Method
- Quantity
- Unit Price
- Profit Margin
- Rating
- Date
- Time

---

## 🔍 SQL Analysis

### Basic Queries

#### View Sample Data
```sql
SELECT * FROM walmart LIMIT 10;
```

#### Count Transactions by Payment Method
```sql
SELECT payment_method, COUNT(*) 
FROM walmart
GROUP BY payment_method;
```

#### Count Total Branches
```sql
SELECT COUNT(DISTINCT Branch) 
FROM walmart;
```

---

## 📊 Business Problems & Solutions

### Q1: Payment Methods Analysis
Find different payment methods, number of transactions, and total quantity sold.

```sql
SELECT 
    payment_method,
    COUNT(*) AS total_transactions,
    SUM(quantity) AS total_quantity
FROM walmart
GROUP BY payment_method;
```

**Output:**

| payment_method | total_transactions | total_quantity |
|---|---|---|
| Cash | 1832 | 4984 |
| Credit card | 4256 | 9567 |
| Ewallet | 3881 | 8932 |

---

### Q2: Highest Rated Category per Branch
```sql
SELECT Branch, category, avg_rating
FROM (
    SELECT 
        Branch,
        category,
        AVG(rating) AS avg_rating,
        ROW_NUMBER() OVER (PARTITION BY Branch ORDER BY AVG(rating) DESC) AS rnk
    FROM walmart
    GROUP BY Branch, category
) t
WHERE rnk = 1;
```

**Logic:**
- Calculate average rating per category per branch
- Rank categories inside each branch
- Select highest ranked category

**Sample Highlights:**
- WALM034 — Health and Beauty — ⭐ **10.0** (Perfect score)
- WALM060 — Health and Beauty — ⭐ 9.9
- WALM027 — Health and Beauty — ⭐ 9.7

---

### Q3: Busiest Day per Branch
```sql
SELECT Branch, day_name, total_transactions
FROM (
    SELECT 
        Branch,
        DAYNAME(date) AS day_name,
        COUNT(*) AS total_transactions,
        ROW_NUMBER() OVER (
            PARTITION BY Branch 
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM walmart
    GROUP BY Branch, DAYNAME(date)
) t
WHERE rn = 1;
```

**Sample Highlights:**
- WALM058 — Sunday — **47 transactions** (highest single-day peak)
- WALM030 — Wednesday — **44 transactions**
- WALM009 — Saturday — **41 transactions**

---

### Q4: Total Quantity Sold per Payment Method
```sql
SELECT 
    payment_method,
    SUM(quantity) AS total_quantity_sold
FROM walmart
GROUP BY payment_method
ORDER BY total_quantity_sold DESC;
```

---

### Q5: Rating Analysis per City
```sql
SELECT 
    City,
    ROUND(AVG(rating), 2) AS avg_rating,
    MIN(rating) AS min_rating,
    MAX(rating) AS max_rating
FROM walmart
GROUP BY City;
```

**Output Highlights (98 cities):**

| City | Avg Rating | Min | Max |
|---|---|---|---|
| Austin | 7.00 | 4 | 9.3 |
| Huntsville | 6.81 | 4 | 9.7 |
| Pflugerville | 6.73 | 3 | 9.9 |
| Port Arthur | 5.30 | 3 | 9.2 |
| Rowlett | 4.99 | 3 | 9.8 |

---

### Q6: Total Profit per Category
```sql
SELECT 
    category,
    ROUND(SUM(unit_price * quantity * profit_margin), 2) AS total_profit
FROM walmart
GROUP BY category
ORDER BY total_profit DESC;
```

**Output:**

| Category | Total Profit |
|---|---|
| Fashion accessories | $192,314.89 |
| Home and lifestyle | $192,213.64 |
| Electronic accessories | $30,772.49 |
| Food and beverages | $21,552.86 |
| Sports and travel | $20,613.81 |
| Health and beauty | $18,671.73 |

> 💡 Fashion & Home combined account for **~78% of total profit**

---

### Q7: Most Common Payment Method per Branch
```sql
SELECT Branch, payment_method
FROM (
    SELECT 
        Branch,
        payment_method,
        COUNT(*) AS cnt,
        ROW_NUMBER() OVER (
            PARTITION BY Branch 
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM walmart
    GROUP BY Branch, payment_method
) t
WHERE rn = 1;
```

**Results across 100 branches:**
- 🔵 Ewallet — **72 branches** (72%)
- 🟢 Credit card — **26 branches** (26%)
- 🟡 Cash — **2 branches** (2%)

---

### Q8: Sales Categorization by Time
```sql
SELECT 
    CASE 
        WHEN HOUR(time) < 12 THEN 'MORNING'
        WHEN HOUR(time) BETWEEN 12 AND 17 THEN 'AFTERNOON'
        ELSE 'EVENING'
    END AS shift,
    COUNT(*) AS total_invoices
FROM walmart
GROUP BY shift;
```

**Output:**

| Shift | Total Invoices | Share |
|---|---|---|
| Afternoon | 4,636 | 46.5% |
| Evening | 3,246 | 32.6% |
| Morning | 2,087 | 20.9% |

> 💡 Nearly **half of all sales** happen in the afternoon (12–5 PM)

---

### Q9: Revenue Decrease Analysis (2022 vs 2023)
```sql
SELECT 
    Branch,
    revenue_2022,
    revenue_2023,
    (revenue_2022 - revenue_2023) / revenue_2022 AS decrease_ratio
FROM (
    SELECT 
        Branch,
        SUM(CASE WHEN YEAR(date) = 2022 THEN total_price ELSE 0 END) AS revenue_2022,
        SUM(CASE WHEN YEAR(date) = 2023 THEN total_price ELSE 0 END) AS revenue_2023
    FROM walmart
    GROUP BY Branch
) t
WHERE revenue_2022 > 0
ORDER BY decrease_ratio DESC
LIMIT 5;
```

**Output:**

| Branch | Revenue 2022 | Revenue 2023 | Drop |
|---|---|---|---|
| WALM020 | $42 | $0 | 100% |
| WALM022 | $184 | $0 | 100% |
| WALM077 | $142.15 | $0 | 100% |
| WALM098 | $150 | $0 | 100% |
| WALM084 | $755 | $48 | 93.6% |

> ⚠️ **4 branches went completely dark in 2023** — possible closures or data gaps worth investigating

---

## 📊 Key Insights
- **Ewallet is king** — 72% of branches prefer it as their top payment method
- **Afternoon drives nearly half of all revenue** — staffing and promotions should peak 12–5 PM
- **Fashion & Home categories are the profit engines** — contributing ~78% of total profit ($384K of $476K)
- **Health & Beauty gets the best ratings** — topped most-liked categories in multiple branches, including a perfect 10.0
- **4 branches had zero revenue in 2023** — flagged for investigation
- **Ratings are narrow across cities** — averaging between 5.0–7.0, suggesting room for service improvement

---

## 🚀 Conclusion
This project demonstrates how SQL can be used to analyze retail data and generate actionable insights. It highlights the importance of data-driven decision-making in business — from identifying peak sales hours to spotting underperforming branches before they become a bigger problem.

---

## 📌 Future Scope
- Build interactive dashboards using Power BI or Tableau
- Integrate with backend systems (Flask / Spring Boot)
- Automate reporting pipelines
- Apply machine learning for predictive analysis

---

