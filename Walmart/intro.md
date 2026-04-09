# 🛠️ Project Setup & Data Pipeline

## 1. Create Python Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

```bash
.\venv\Scripts\Activate
```

---

## 2. Install Dependencies & Download Dataset

Install Kaggle and download the dataset directly:

```bash
pip install kaggle
```

```bash
kaggle datasets download -d najir0123/walmart-10k-sales-datasets --unzip
```

> 📦 Dataset URL: [Walmart 10K Sales Dataset](https://www.kaggle.com/datasets/najir0123/walmart-10k-sales-datasets)

---

## 3. Data Preprocessing (Python + Pandas)

After loading the dataset, two key preprocessing steps are applied:

**Step 1 — Clean the `unit_price` column**

The `unit_price` column contains values formatted with a `$` dollar sign. We strip it and convert to float:

```python
import pandas as pd

df = pd.read_csv('walmart.csv')

df['unit_price'] = df['unit_price'].str.replace('$', '').astype(float)
```

**Step 2 — Create a new `total` column**

```python
df['total'] = df['unit_price'] * df['quantity']
```

---

## 4. Connect Python to MySQL

Install the required libraries:

```bash
pip install pymysql sqlalchemy
```

Create a MySQL connection using SQLAlchemy:

```python
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://username:password@localhost:3306/walmart_db')
```

> 🔁 Replace `username`, `password`, and `walmart_db` with your actual MySQL credentials and database name.

Push the cleaned DataFrame directly into MySQL:

```python
df.to_sql('walmart', con=engine, if_exists='replace', index=False)

print("Data loaded successfully!")
```

---

## 5. You're Ready!

Once the data is loaded into MySQL, open your SQL client (MySQL Workbench / DBeaver / CLI) and start running the queries from `sql_commands.md`.