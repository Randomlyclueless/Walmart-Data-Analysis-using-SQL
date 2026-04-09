# 🛒 Walmart SQL Commands

## Basic Queries

```sql
SELECT * FROM walmart LIMIT 10;
```

```sql
SELECT 
    payment_method, COUNT(*) 
FROM walmart
GROUP BY payment_method;
```

```sql
SELECT COUNT(DISTINCT Branch);
```

---

## Business Problems & Solutions

### Q1: Find different payment methods, number of transactions, and quantity sold

```sql
SELECT 
    payment_method,
    COUNT(*),
    SUM(quantity) 
FROM walmart
GROUP BY payment_method;
```

**Output:**

| payment_method | count(*) | sum(quantity) |
|---|---|---|
| Cash | 1832 | 4984 |
| Credit card | 4256 | 9567 |
| Ewallet | 3881 | 8932 |

---

### Q2: Identify the highest rated category in each branch

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

**How this works:**
1. Calculate avg rating per category per branch
2. Rank categories inside each branch
3. Pick only rank = 1 (highest)

---

### Q3: Identify busiest day for each branch based on number of transactions

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

---

### Q4: Calculate total quantity of items sold per payment method

```sql
SELECT 
    payment_method,
    SUM(quantity) AS total_quantity_sold
FROM walmart
GROUP BY payment_method
ORDER BY total_quantity_sold DESC;
```

---

### Q5: Describe the average, minimum, and max rating for each city

```sql
SELECT 
    City AS city,
    ROUND(AVG(rating), 2) AS avg_rating,
    MIN(rating) AS min_rating,
    MAX(rating) AS max_rating
FROM walmart
GROUP BY City;
```

---

### Q6: Calculate total profit for each category

> Total profit = `unit_price * quantity * profit_margin`

```sql
SELECT 
    category,
    ROUND(SUM(unit_price * quantity * profit_margin), 2) AS total_profit
FROM walmart
GROUP BY category
ORDER BY total_profit DESC;
```

---

### Q7: Determine the most common payment method for each branch

```sql
SELECT Branch, payment_method AS preferred_payment_method
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

---

### Q8: Categorize sales into MORNING, AFTERNOON, EVENING shifts

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

---

### Q9: Identify 5 branches with highest revenue decrease (2022 vs 2023)

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