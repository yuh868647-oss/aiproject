import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------------------
# 1. 페이지 설정
# -----------------------------------------
st.set_page_config(
    page_title="세계 MBTI 탐험",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 세계 MBTI 탐험")
st.write("국가를 선택하면 MBTI 16가지 유형별 비율을 확인할 수 있어요!")

# -----------------------------------------
# 2. 데이터 불러오기
# -----------------------------------------
DATA_FILE = Path(__file__).parent / "countriesMBTI_16types.csv"


@st.cache_data
def load_data(file_path):

    data = pd.read_csv(
        file_path,
        encoding="utf-8-sig"
    )

    if "Country" not in data.columns:
        raise ValueError("Country 컬럼이 없습니다.")

    mbti_cols = [
        col for col in data.columns
        if col != "Country"
    ]

    if len(mbti_cols) != 16:
        raise ValueError("MBTI 컬럼이 16개가 아닙니다.")

    for col in mbti_cols:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data = data.dropna(subset=mbti_cols)

    data["Country"] = data["Country"].astype(str).str.strip()

    return data, mbti_cols


try:
    df, mbti_columns = load_data(str(DATA_FILE))

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.stop()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# -----------------------------------------
# 3. 국가 선택
# -----------------------------------------
countries = sorted(df["Country"].unique().tolist())

if not countries:
    st.error("국가 데이터가 없습니다.")
    st.stop()

default_index = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "🗺️ 국가를 선택하세요!",
    countries,
    index=default_index
)


# -----------------------------------------
# 4. 선택 국가 데이터 분석
# -----------------------------------------
selected_rows = df[
    df["Country"] == selected_country
]

if selected_rows.empty:
    st.error("선택한 국가의 데이터가 없습니다.")
    st.stop()

country_data = selected_rows.iloc[0]

# 비율을 퍼센트로 변환
mbti_data = (
    country_data[mbti_columns].astype(float) * 100
)

# 높은 순서대로 정렬
mbti_data = mbti_data.sort_values(
    ascending=False
)

# 1위 유형
top_mbti = mbti_data.index[0]
top_value = float(mbti_data.iloc[0])


# -----------------------------------------
# 5. 주요 통계
# -----------------------------------------
st.divider()

st.subheader(
    f"📊 {selected_country} MBTI 분석"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "🌍 선택 국가",
    selected_country
)

col2.metric(
    "🏆 1위 MBTI",
    top_mbti
)

col3.metric(
    "📈 최고 비율",
    f"{top_value:.2f}%"
)


# -----------------------------------------
# 6. 막대그래프
# -----------------------------------------
st.divider()

st.subheader("🎨 MBTI 16가지 유형별 비율")

fig, ax = plt.subplots(figsize=(11, 7))


# 1위 빨간색
first_color = "#E53935"

# 나머지 15개 파란색 그라데이션
blue_palette = plt.get_cmap("Blues")

blue_colors = [
    blue_palette(
        0.88 - i * (0.55 / 14)
    )
    for i in range(15)
]

colors = [first_color] + blue_colors


# 막대그래프 생성
bars = ax.barh(
    mbti_data.index.tolist(),
    mbti_data.values.tolist(),
    color=colors,
    height=0.72
)

# 높은 순위가 위로 오도록 설정
ax.invert_yaxis()


# 그래프 제목 및 축
ax.set_title(
    f"{selected_country} MBTI 비율",
    fontsize=16,
    pad=14
)

ax.set_xlabel("비율 (%)")
ax.set_ylabel("MBTI 유형")

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.3
)

ax.set_axisbelow(True)


# 그래프 오른쪽 여백
max_value = float(mbti_data.max())

ax.set_xlim(
    0,
    max_value * 1.20 if max_value > 0 else 1
)


# 막대 끝에 비율 표시
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


fig.tight_layout()

# Streamlit 출력
st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# -----------------------------------------
# 7. 상세 데이터 표
# -----------------------------------------
st.divider()

with st.expander("📋 MBTI 유형별 상세 비율 보기"):

    result = pd.DataFrame({
        "순위": range(1, len(mbti_data) + 1),
        "MBTI 유형": mbti_data.index.tolist(),
        "비율(%)": [
            f"{value:.2f}%"
            for value in mbti_data.values
        ]
    })

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------------------
# 8. 분석 결과
# -----------------------------------------
st.success(
    f"🏆 {selected_country}의 1위 MBTI는 "
    f"{top_mbti}입니다! ({top_value:.2f}%)"
)

st.info(
    "💡 빨간색은 1위, 파란색 그라데이션은 "
    "나머지 MBTI 유형을 의미합니다."
)

st.caption(
    "※ 제공된 CSV 데이터를 기반으로 분석한 결과입니다."
)

st.caption(
    "🌎 World MBTI Explorer | Made with Streamlit"
)
