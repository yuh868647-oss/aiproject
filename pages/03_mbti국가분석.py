```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="세계 MBTI 탐험",
    page_icon="🌎",
    layout="wide"
)

# 데이터 불러오기
DATA_FILE = Path(__file__).parent / "countriesMBTI_16types (1).csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    mbti_columns = [col for col in df.columns if col != "Country"]
    return df, mbti_columns

st.title("🌎 세계 MBTI 탐험")
st.markdown("### 국가별 MBTI 유형 분포를 알아보자!")

# 데이터 로딩
try:
    df, mbti_columns = load_data()
except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. app.py와 같은 폴더에 넣어주세요.")
    st.stop()

# 국가 선택
countries = sorted(df["Country"].dropna().unique())

selected_country = st.selectbox(
    "🗺️ 국가를 선택하세요!",
    countries,
    index=countries.index("South Korea")
    if "South Korea" in countries else 0
)

# 선택한 국가 데이터
country_data = df[df["Country"] == selected_country].iloc[0]

# MBTI 비율 계산 및 내림차순 정렬
mbti_data = country_data[mbti_columns].astype(float) * 100
mbti_data = mbti_data.sort_values(ascending=False)

# 최고 비율 MBTI
top_mbti = mbti_data.idxmax()
top_value = mbti_data.max()

# 주요 정보 표시
col1, col2, col3 = st.columns(3)

col1.metric("🌍 선택 국가", selected_country)
col2.metric("🏆 1위 MBTI", top_mbti)
col3.metric("📊 최고 비율", f"{top_value:.2f}%")

st.divider()

# 그래프 제목
st.subheader(f"📊 {selected_country}의 MBTI 비율")

# 그래프 생성
fig, ax = plt.subplots(figsize=(11, 7))

# 1위 빨간색, 나머지 파란색 그라데이션
blue_colors = cm.Blues(
    [0.88 - i * (0.55 / 14) for i in range(15)]
)

colors = ["#E53935"] + list(blue_colors)

# 막대그래프
bars = ax.barh(
    mbti_data.index,
    mbti_data.values,
    color=colors,
    height=0.7
)

# 높은 순서대로 위에서부터 표시
ax.invert_yaxis()

# 그래프 설정
ax.set_xlabel("MBTI 비율 (%)", fontsize=12)
ax.set_ylabel("MBTI 유형", fontsize=12)
ax.set_title(
    f"{selected_country} MBTI Distribution",
    fontsize=16
)

ax.grid(axis="x", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

# 막대 끝에 비율 표시
for bar, value in zip(bars, mbti_data.values):
    ax.text(
        bar.get_width() + 0.1,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}%",
        va="center",
        fontsize=9
    )

fig.tight_layout()

# Streamlit에 그래프 출력
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# 상세 데이터
with st.expander("📋 MBTI 유형별 상세 비율 확인"):
    result = pd.DataFrame({
        "MBTI 유형": mbti_data.index,
        "비율": [f"{v:.2f}%" for v in mbti_data.values]
    })

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

st.success(
    f"🏆 {selected_country}에서 가장 높은 비율을 차지하는 유형은 "
    f"{top_mbti}입니다! ({top_value:.2f}%)"
)

st.caption("※ 제공된 CSV 데이터를 기반으로 분석한 결과입니다.")
```
