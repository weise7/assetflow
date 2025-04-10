
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="AssetFlow - 자산 리밸런싱 리포트", layout="wide")

st.title("자산 리밸런싱 시뮬레이션")

# 자산 입력
st.header("1. 자산 구성 입력")
default_data = {
    "자산유형": ["현금", "예금/적금", "국내주식", "해외ETF", "코인"],
    "금액(만원)": [1000, 3000, 7000, 4000, 2000],
}
df_input = pd.DataFrame(default_data)
edited_df = st.data_editor(df_input, num_rows="dynamic")

# 자산 시각화
st.header("2. 자산 구성 시각화")
total_assets = edited_df["금액(만원)"].sum()
edited_df["비중(%)"] = round((edited_df["금액(만원)"] / total_assets) * 100, 1)

fig, ax = plt.subplots()
ax.pie(edited_df["금액(만원)"], labels=edited_df["자산유형"], autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

# 모델 포트폴리오 선택
st.header("3. 모델 포트폴리오 선택")
model_option = st.selectbox("원하는 포트폴리오 모델을 선택하세요", ["인컴형", "성장형", "균형형"])

model_dict = {
    "인컴형": {"현금": 40, "예금/적금": 0, "국내주식": 15, "해외ETF": 40, "코인": 5},
    "성장형": {"현금": 10, "예금/적금": 0, "국내주식": 40, "해외ETF": 30, "코인": 20},
    "균형형": {"현금": 20, "예금/적금": 0, "국내주식": 30, "해외ETF": 40, "코인": 10},
}

selected_model = model_dict[model_option]

# 리밸런싱 시뮬레이션
st.header("4. 리밸런싱 시뮬레이션 결과")
user_assets = dict(zip(edited_df["자산유형"], edited_df["금액(만원)"]))
total_user_assets = sum(user_assets.values())
user_percent = {k: round(v / total_user_assets * 100, 1) for k, v in user_assets.items()}

comparison_data = []
for asset in user_assets:
    user_p = user_percent.get(asset, 0)
    model_p = selected_model.get(asset, 0)
    diff = round(user_p - model_p, 1)
    action = "-"
    if diff > 0:
        action = f"{round((diff/100)*total_user_assets)}만원 매도"
    elif diff < 0:
        action = f"{round((-diff/100)*total_user_assets)}만원 매수"
    
    comparison_data.append({
        "자산유형": asset,
        "현재 비중(%)": user_p,
        f"{model_option} 비중(%)": model_p,
        "차이(%)": diff,
        "시뮬레이션 액션": action
    })

df_compare = pd.DataFrame(comparison_data)
st.dataframe(df_compare)

# PDF 저장
st.header("5. 리포트 PDF 저장")
if st.button("PDF 다운로드"):
    path = "rebalancing_report.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, f"리밸런싱 리포트 ({model_option} 기준)")
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
        st.download_button("리포트 PDF 다운로드", f, file_name="리밸런싱_리포트.pdf")
