
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

plt.rcParams['font.family'] = 'DejaVu Sans'

st.set_page_config(page_title="AssetFlow - Rebalancing Report", layout="wide")
st.title("Asset Rebalancing Simulation")

# Asset input
st.header("1. Asset Composition Input")
default_data = {
    "Asset Type": ["Cash", "Savings", "KR_Stock", "ETF", "Crypto", "Other"],
    "Amount (KRW10K)": [1000, 3000, 7000, 4000, 2000, 500],
}
df_input = pd.DataFrame(default_data)
edited_df = st.data_editor(df_input, num_rows="dynamic")

# Add total row
total = edited_df["Amount (KRW10K)"].sum()
edited_df["Portion (%)"] = round((edited_df["Amount (KRW10K)"] / total) * 100, 1)
total_row = pd.DataFrame([{"Asset Type": "Total", "Amount (KRW10K)": total, "Portion (%)": edited_df["Portion (%)"].sum()}])
df_display = pd.concat([edited_df, total_row], ignore_index=True)

# Pie chart
st.header("2. Asset Composition Visualization")
filtered_df = edited_df[edited_df["Asset Type"] != "Total"]
fig, ax = plt.subplots()
ax.pie(filtered_df["Amount (KRW10K)"], labels=filtered_df["Asset Type"], autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

# Model selection
st.header("3. Choose a Model Portfolio")
model_option = st.selectbox("Select a portfolio model", ["Income", "Growth", "Balanced"])

model_dict = {
    "Income": {"Cash": 40, "Savings": 0, "KR_Stock": 15, "ETF": 40, "Crypto": 5},
    "Growth": {"Cash": 10, "Savings": 0, "KR_Stock": 40, "ETF": 30, "Crypto": 20},
    "Balanced": {"Cash": 20, "Savings": 0, "KR_Stock": 30, "ETF": 40, "Crypto": 10},
}

selected_model = model_dict[model_option]

# Rebalancing simulation
st.header("4. Rebalancing Simulation Result")
user_assets = dict(zip(filtered_df["Asset Type"], filtered_df["Amount (KRW10K)"]))
total_user_assets = sum(user_assets.values())
user_percent = {k: round(v / total_user_assets * 100, 1) for k, v in user_assets.items()}

comparison_data = []
for asset in user_assets:
    user_p = user_percent.get(asset, 0)
    model_p = selected_model.get(asset, 0)
    diff = round(user_p - model_p, 1)
    action = "-"
    if diff > 0:
        action = f"{round((diff/100)*total_user_assets)} sell"
    elif diff < 0:
        action = f"{round((-diff/100)*total_user_assets)} buy"
    
    comparison_data.append({
        "Asset Type": asset,
        "Current (%)": user_p,
        f"{model_option} Model (%)": model_p,
        "Gap (%)": diff,
        "Suggested Action": action
    })

df_compare = pd.DataFrame(comparison_data)
st.dataframe(df_compare)

# PDF Report
st.header("5. Download Rebalancing Report (PDF)")
if st.button("Download PDF"):
    path = "rebalancing_report.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, f"Rebalancing Report ({model_option} Portfolio)")
    c.setFont("Helvetica", 10)
    x_offset = 40
    y_offset = height - 80
    line_height = 20

    for i, col in enumerate(df_compare.columns):
        c.drawString(x_offset + i * 100, y_offset, str(col))
    y_offset -= line_height

    for _, row in df_compare.iterrows():
        for i, item in enumerate(row):
            c.drawString(x_offset + i * 100, y_offset, str(item))
        y_offset -= line_height
        if y_offset < 50:
            c.showPage()
            y_offset = height - 50

    c.save()
    with open(path, "rb") as f:
        st.download_button("Download PDF", f, file_name="Rebalancing_Report.pdf")
