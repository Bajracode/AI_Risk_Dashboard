import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
import matplotlib.pyplot as plt

# === PAGE CONFIG ===
st.set_page_config(page_title="AI Risk Intelligence Dashboard", layout="wide")

# === HEADER ===
st.title("📊 AI-Powered Business Risk Intelligence Dashboard (2025)")
st.markdown(
    """
Welcome to the **AI-Powered Business Risk Intelligence Dashboard**.  
Detect anomalies in datasets using AI models such as **Isolation Forest** and **Local Outlier Factor (LOF)**.  

👉 Upload your own dataset (`CSV`) or choose a sample dataset.  
👉 Explore anomalies with interactive visualizations.  
    """
)

# === DATASET SELECTION ===
st.subheader("📂 Select Dataset")
dataset_choice = st.radio("Choose a dataset:", ["Upload CSV", "Sample: Fraud", "Sample: Transactions", "Sample: IoT"])

df = pd.DataFrame()  # placeholder

if dataset_choice == "Upload CSV":
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        st.info("Please upload a CSV file to continue.")
        st.stop()
else:
    rng = np.random.RandomState(42)
    if dataset_choice == "Sample: Fraud":
        df = pd.DataFrame({
            "transaction_amount": rng.normal(200, 50, 300),
            "transaction_time": rng.randint(0, 24, 300),
            "merchant_id": rng.randint(1, 20, 300)
        })
    elif dataset_choice == "Sample: Transactions":
        df = pd.DataFrame({
            "transaction_amount": rng.normal(100, 20, 400),
            "transaction_time": rng.randint(0, 24, 400),
            "merchant_id": rng.randint(1, 50, 400)
        })
    else:  # Sample: IoT
        df = pd.DataFrame({
            "sensor_reading": rng.normal(75, 10, 250),
            "timestamp": rng.randint(0, 100, 250),
            "device_id": rng.randint(1, 30, 250)
        })

if df.empty:
    st.info("No data available yet. Please upload a CSV or choose a sample dataset.")
    st.stop()

# === MODEL SELECTION ===
st.subheader("⚙️ Anomaly Detection Settings")
model_choice = st.selectbox("Choose Model", ["Isolation Forest", "Local Outlier Factor"])

# Run anomaly detection
numeric_df = df.select_dtypes(include=[np.number])

if model_choice == "Isolation Forest":
    model = IsolationForest(contamination=0.05, random_state=42)
    preds = model.fit_predict(numeric_df)
else:
    n_neighbors = min(20, max(2, len(df) - 1))  # adjust for small datasets
    model = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.05)
    preds = model.fit_predict(numeric_df)

df["Anomaly"] = np.where(preds == -1, "Yes", "No")

# === SUMMARY METRICS ===
st.subheader("📊 Summary Metrics")
total_rows = len(df)
anomalies = df["Anomaly"].value_counts().get("Yes", 0)
anomaly_pct = (anomalies / total_rows) * 100 if total_rows > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Records", total_rows)
col2.metric("Anomalies Detected", anomalies)
col3.metric("Anomaly %", f"{anomaly_pct:.2f}%")

# === VISUALIZATIONS ===
st.subheader("📈 Visualizations")

# 1. Scatter plot: Transaction datasets
if {"transaction_time", "transaction_amount"}.issubset(df.columns):
    st.markdown("**Scatter Plot: Transaction Time vs Amount**")
    fig, ax = plt.subplots()
    normal = df[df["Anomaly"] == "No"]
    anomaly = df[df["Anomaly"] == "Yes"]
    ax.scatter(normal["transaction_time"], normal["transaction_amount"], c="blue", label="Normal", alpha=0.6)
    ax.scatter(anomaly["transaction_time"], anomaly["transaction_amount"], c="red", label="Anomaly", alpha=0.8)
    ax.set_xlabel("Transaction Time")
    ax.set_ylabel("Transaction Amount")
    ax.legend()
    st.pyplot(fig)

# 2. Bar chart: Anomalies per merchant (if available)
if "merchant_id" in df.columns:
    st.markdown("**Bar Chart: Anomalies per Merchant**")
    counts = df[df["Anomaly"] == "Yes"]["merchant_id"].value_counts()
    if not counts.empty:
        fig, ax = plt.subplots()
        counts.plot(kind="bar", ax=ax, color="red")
        ax.set_ylabel("Number of Anomalies")
        ax.set_xlabel("Merchant ID")
        st.pyplot(fig)

# 3. Time series: anomalies over time
if "transaction_time" in df.columns:
    st.markdown("**Line Chart: Anomalies over Time**")
    time_series = df.groupby("transaction_time")["Anomaly"].apply(lambda x: (x == "Yes").sum())
    fig, ax = plt.subplots()
    time_series.plot(ax=ax, marker="o", color="orange")
    ax.set_ylabel("Anomalies Count")
    ax.set_xlabel("Transaction Time")
    st.pyplot(fig)
elif "timestamp" in df.columns:
    st.markdown("**Line Chart: Anomalies over Timestamps**")
    time_series = df.groupby("timestamp")["Anomaly"].apply(lambda x: (x == "Yes").sum())
    fig, ax = plt.subplots()
    time_series.plot(ax=ax, marker="o", color="green")
    ax.set_ylabel("Anomalies Count")
    ax.set_xlabel("Timestamp")
    st.pyplot(fig)

# 4. Pie chart: anomaly distribution
st.markdown("**Pie Chart: Anomaly Distribution**")
fig, ax = plt.subplots()
colors = ["blue" if label == "No" else "red" for label in df["Anomaly"].unique()]
df["Anomaly"].value_counts().plot.pie(autopct="%1.1f%%", colors=colors, ax=ax)
ax.set_ylabel("")
st.pyplot(fig)

# === RESULTS TABLE ===
st.subheader("📋 Full Results")
st.dataframe(df)

# === DOWNLOAD BUTTON ===
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download Results", data=csv, file_name="anomaly_results.csv", mime="text/csv")

