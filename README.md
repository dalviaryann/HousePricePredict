# 🏠 Mumbai House Price Predictor

A machine learning web application that predicts house prices across Mumbai using a Random Forest model trained on 76,000+ real property listings.

Built by **Aryan Hemant Dalvi** · [GitHub](https://github.com/dalviaryann)

---

## 📌 Problem Statement

The Mumbai real estate market is one of the most complex and expensive in India. Buyers and renters often struggle to determine whether a property is fairly priced, or which location offers the best value for their budget.

This project solves that by:
- Predicting the price of any property in Mumbai based on its features
- Comparing what the same budget gets you across different locations
- Suggesting the best value areas based on your budget

---

## 📂 Dataset

- **Source:** Mumbai House Prices Dataset
- **Size:** 76,038 listings
- **Features:**

| Column | Description |
|---|---|
| `bhk` | Number of bedrooms |
| `type` | Property type (Apartment, Villa, etc.) |
| `locality` | Specific locality name |
| `area` | Carpet area in sq. ft. |
| `price` | Listed price |
| `price_unit` | Unit of price (Cr / L) |
| `region` | Broader region in Mumbai |
| `status` | Ready to move / Under construction |
| `age` | New / Resale |

---

## 🔍 Exploratory Data Analysis (EDA)

Key findings from the dataset:

- **Price units were inconsistent** — some listings in Crore (Cr), others in Lakh (L). All prices were normalised to Lakhs for consistency.
- **Locality had 9,782 unique values** — too high cardinality for ML. Replaced with `region` (228 unique values).
- **Price range after conversion:** ₹4.49L — ₹6,000L
- **Outliers detected** — top and bottom 1% of prices removed using IQR method, resulting in a clean range of ₹19.7L — ₹1,000L
- **No missing values** in the dataset — no imputation required
- **Region is the strongest predictor** of price, followed by area and BHK

---

## ⚙️ Data Preprocessing

1. Converted all prices to Lakhs (₹)
2. Dropped `locality` (too many unique values) and replaced with `region`
3. Removed top and bottom 1% outliers
4. Applied `StandardScaler` on numeric features (`bhk`, `area`)
5. Applied `OneHotEncoder` with `handle_unknown='infrequent_if_exist'` on categorical features (`type`, `region`, `status`, `age`)
6. Used `sklearn Pipeline` to chain preprocessing and model

---

## 🤖 Model

### Why Random Forest?

| | Linear Regression | Random Forest |
|---|---|---|
| Handles non-linear patterns | ❌ | ✅ |
| Resistant to outliers | ❌ | ✅ |
| Captures location complexity | ❌ | ✅ |
| Accuracy on this dataset | 81.96% | **82.79%** |

### Model Configuration

```python
RandomForestRegressor(
    n_estimators=150,   # 150 decision trees
    max_depth=20,       # max depth per tree
    min_samples_leaf=3, # prevents overfitting
    n_jobs=-1,          # uses all CPU cores
    random_state=42
)
```

### Train / Test Split
- **Training:** 59,653 samples (80%)
- **Testing:** 14,914 samples (20%)

---

## 📊 Results

| Metric | Score |
|---|---|
| **R² Score** | 0.8279 |
| **Mean Absolute Error** | ₹33.43 Lakhs |
| **RMSE** | ₹59.70 Lakhs |

> The model explains **82.79%** of price variation across Mumbai. On average, predictions are within ₹33L of the actual price — reasonable given Mumbai's wide price range (₹19.7L — ₹1,000L).

---

## 🌐 Web Application

Built with Flask, the app includes:

- 🔐 **Login / Signup** — user authentication with SQLite
- 🏠 **Price Prediction** — predict price for any Mumbai property
- 📍 **Location Comparison** — see what your budget gets across different regions (USP)
- 💰 **Budget Optimizer** — find areas that give maximum area for your budget
- 📋 **Search History** — every prediction saved per user
- ℹ️ **About** — model details, tech stack, and performance metrics

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| ML Model | Scikit-learn Random Forest |
| Database | SQLite |
| Frontend | HTML + CSS |
| Model Serialization | Joblib |
| Data Processing | Pandas, NumPy |

---

## 🚀 How to Run

```bash
# 1. Clone the repository
git clone https://github.com/dalviaryann/mumbai-house-predictor.git
cd mumbai-house-predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open your browser at `http://127.0.0.1:5000`

---

## 📁 Project Structure

```
mumbai_house_predictor/
│
├── app.py                  ← Flask backend
├── train_model.py          ← Model training script
│
├── templates/
│   ├── base.html           ← Shared layout
│   ├── landing.html        ← Landing page
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html      ← Price prediction
│   ├── compare.html        ← Location comparison
│   ├── optimizer.html      ← Budget optimizer
│   ├── history.html        ← Search history
│   └── about.html
│
├── static/
│   └── css/
│       └── style.css
│
├── model_rf.pkl            ← Trained Random Forest model
├── metadata.pkl            ← Dropdown options
├── database.db             ← SQLite database
└── requirements.txt
```

---

## 📝 Requirements

```
flask
pandas
numpy
scikit-learn==1.8.0
joblib
```

---

## 👤 Author

**Aryan Hemant Dalvi**  
[GitHub](https://github.com/dalviaryann)

---

*Mini Project · Machine Learning · Mumbai House Price Prediction*
