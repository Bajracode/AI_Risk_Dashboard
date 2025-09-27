import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

# === MAIN APP ===
st.set_page_config(page_title="AI-Powered Business Risk Intelligence Dashboard", layout="wide")

st.header("📊 AI-Powered Business Risk Intelligence Dashboard (2025)")
st.write("Upload a dataset or use the sample to run anomaly detection.")

# File uploader
uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    rng = np.random.RandomState(42)
    df = pd.DataFrame({
        "transaction_amount": rng.normal(100, 20, 200),
        "transaction_time": rng.randint(0, 24, 200),
        "merchant_id": rng.randint(1, 50, 200)
    })

# Dataset Preview
st.subheader("Dataset Preview")
st.dataframe(df.head())

# Model Selection
model_choice = st.selectbox("Choose Model", ["Isolation Forest", "Local Outlier Factor"])

if model_choice == "Isolation Forest":
    model = IsolationForest(contamination=0.05, random_state=42)
    preds = model.fit_predict(df.select_dtypes(include=[np.number]))
else:
    model = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
    preds = model.fit_predict(df.select_dtypes(include=[np.number]))

# Add anomaly results
df["Anomaly"] = np.where(preds == -1, "Yes", "No")

# Show results
st.subheader("Anomaly Detection Results")
st.dataframe(df)

# Optional: SHAP Explainability
try:
    import shap
    import matplotlib.pyplot as plt
    if model_choice == "Isolation Forest":
        st.subheader("Model Explainability (SHAP)")
        explainer = shap.Explainer(model, df.select_dtypes(include=[np.number]))
        shap_values = explainer(df.select_dtypes(include=[np.number]))
        fig, ax = plt.subplots()
        shap.summary_plot(shap_values, df.select_dtypes(include=[np.number]), show=False)
        st.pyplot(fig)
except ModuleNotFoundError:
    st.info("Install matplotlib + shap to enable explainability.")

# Download button
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download Results", data=csv, file_name="anomaly_results.csv", mime="text/csv")

