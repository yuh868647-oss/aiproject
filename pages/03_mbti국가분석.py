```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="세계 MBTI 탐험",
    page_icon="🌎",
    layout="wide"
)

# ==========================================
# 2. 제목 및 소개
# ==========================================

st.title("🌎 세계 MBTI 탐험")

st.markdown("""
### 🧭 세계 여러 나라의 MBTI 유형을 알아보자!
국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 확인할 수 있어요.
""")

st.divider()

# ==========================================
# 3. CSV 데이터 불러오기
# ==========================================

DATA_FILE = Path(__file__).parent / "countriesMBTI_16types (1).csv"


@st.cache_data
def load_data():

    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")

    # 국가 컬럼 확인
    if "Country" not in df.columns:
        raise ValueError("CSV 파일에 Country 컬럼이 없습니다.")

    # MBTI 컬럼 추출
    mbti_columns = [
        col for col in df.columns
        if col != "Country"
    ]

    # 숫자형 데이터 변환
    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 결측치 제거
    df = df.dropna(
        subset=mbti_columns
    )

    return df, mbti_columns


try:

    df, mbti_columns = load_data()

except FileNotFoundError:

    st.error(
        "❌ CSV 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 CSV 파일을 넣어주세요."
    )

    st.stop()

except Exception as e:

    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

    st.stop()


# ==========================================
# 4. 국가 선택
# ==========================================

countries = sorted(
    df["Country"].dropna().unique().tolist()
)

if len(countries) == 0:
    st.error("분석할 국가 데이터가 없습니다.")
    st.stop()

# 대한민국을 기본 선택
default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요!",
    countries,
    index=default_index
)


# ==========================================
# 5. 선택한 국가의 MBTI 데이터 분석
# ==========================================

country_data = df[
    df["Country"] == selected_country
].iloc[0]

# 비율을 퍼센트로 변환
mbti_data = (
    country_data[mbti_columns]
    .astype(float) * 100
)

# 높은 순서대로 정렬
mbti_data = mbti_data.sort_values(
    ascending=False
)

# 1위 MBTI
top_mbti = mbti_data.index[0]

top_value = mbti_data.iloc[0]


# ==========================================
# 6. 주요 통계 표시
# ==========================================

st.divider()

st.subheader(
    f"📊 {selected_country} MBTI 분석 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🌍 선택 국가",
        selected_country
    )

with col2:
    st.metric(
        "🏆 가장 높은 MBTI",
        top_mbti
    )

with col3:
    st.metric(
        "📈 최고 비율",
        f"{top_value:.2f}%"
    )


# ==========================================
# 7. 막대그래프 그리기
# ==========================================

st.divider()

st.subheader("🎨 MBTI 16가지 유형별 비율")

# 그래프 크기
fig, ax = plt.subplots(
    figsize=(12, 8)
)

# ------------------------------------------
# 색상 설정
# ------------------------------------------

# 1위는 빨간색
first_color = "#E53935"

# 나머지 15개는 파란색 그라데이션
blue_colors = cm.Blues(
    [
        0.85 - i * (0.50 / 14)
        for i in range(15)
    ]
)

# 전체 색상
colors = [
    first_color
] + list(blue_colors)


# ------------------------------------------
# 막대그래프 생성
# ------------------------------------------

bars = ax.barh(
    mbti_data.index,
    mbti_data.values,
    color=colors,
    height=0.7,
    edgecolor="white"
)


# 높은 순위가 위에 오도록 설정
ax.invert_yaxis()


# ------------------------------------------
# 그래프 꾸미기
# ------------------------------------------

ax.set_title(
    f"{selected_country} MBTI Distribution",
    fontsize=17,
    pad=20
)

ax.set_xlabel(
    "비율 (%)",
    fontsize=12
)

ax.set_ylabel(
    "MBTI 유형",
    fontsize=12
)

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.3
)

ax.set_axisbelow(True)

# 오른쪽 숫자 표시 공간 확보
max_value = mbti_data.max()

ax.set_xlim(
    0,
    max_value * 1.2
)


# ------------------------------------------
# 막대 끝에 비율 표시
# ------------------------------------------

for bar, value in zip(
    bars,
    mbti_data.values
):

    ax.text(
        bar.get_width() + max_value * 0.015,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.2f}%",
        va="center",
        fontsize=9
    )


# 그래프 여백 정리
fig.tight_layout()


# Streamlit에 그래프 출력
st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# ==========================================
# 8. 상세 데이터 표
# ==========================================

st.divider()

with st.expander("📋 MBTI 유형별 상세 비율 보기"):

    result = pd.DataFrame({

        "순위": range(1, len(mbti_data) + 1),

        "MBTI 유형": mbti_data.index,

        "비율": [
            f"{value:.2f}%"
            for value in mbti_data.values
        ]

    })

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 9. 분석 결과 안내
# ==========================================

st.divider()

st.success(
    f"🏆 {selected_country}에서 가장 높은 비율을 "
    f"차지하는 MBTI는 {top_mbti}입니다! "
    f"({top_value:.2f}%)"
)

st.info(
    "💡 빨간색은 해당 국가의 1위 MBTI이며, "
    "파란색 그라데이션은 나머지 유형을 나타냅니다."
)

st.caption(
    "※ 제공된 CSV 데이터를 바탕으로 분석한 결과입니다. "
    "국가 전체 인구의 실제 성격 분포를 확정하는 통계는 아닙니다."
)

st.caption("🌎 World MBTI Explorer | Made with Streamlit")
```
