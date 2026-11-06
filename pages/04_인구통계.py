import re
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------
# 서울시 자치구·성별·연도별 연령 인구 분석
#
# 프로젝트/
# ├── population.csv
# ├── requirements.txt
# └── Pages/
#     └── app.py
# ---------------------------------------------------------

st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="🌸",
    layout="wide"
)

PINK = "#FF1493"

# CSV 파일 위치 설정
PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_DIR / "population.csv"


@st.cache_data
def load_population_data(file_path: str):
    """한글 CSV 인코딩을 순서대로 시도해 읽습니다."""
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]
    last_error = None

    for encoding in encodings:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            data.columns = [str(col).strip() for col in data.columns]
            return data, encoding
        except (UnicodeDecodeError, UnicodeError) as error:
            last_error = error

    raise UnicodeError(
        "CSV 파일의 인코딩을 읽을 수 없습니다. "
        "CP949 또는 UTF-8 형식인지 확인해 주세요."
    ) from last_error


def clean_number(value):
    """쉼표가 포함된 인구 문자열을 숫자로 변환합니다."""
    if pd.isna(value):
        return None

    cleaned = str(value).replace(",", "").strip()

    if cleaned in ("", "-", "—"):
        return None

    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return None


def get_age_columns(data, year, sex):
    """선택한 연도·성별의 연령대 열을 찾습니다."""
    age_labels = [
        "0~9세", "10~19세", "20~29세", "30~39세",
        "40~49세", "50~59세", "60~69세", "70~79세",
        "80~89세", "90~99세", "100세 이상"
    ]

    selected_columns = []

    for age in age_labels:

        if sex == "전체":
            expected = f"{year}년_거주자_{age}"
        else:
            expected = f"{year}년_{sex}_거주자_{age}"

        if expected in data.columns:
            selected_columns.append((age, expected))
            continue

        normalized_expected = re.sub(r"\s+", "", expected)
        found = None

        for col in data.columns:
            if re.sub(r"\s+", "", str(col)) == normalized_expected:
                found = col
                break

        if found is not None:
            selected_columns.append((age, found))

    return selected_columns


# ---------------------------------------------------------
# 화면 제목
# ---------------------------------------------------------

st.title("🌸 서울시 연령별 인구 분석")

st.caption(
    "행정구역, 성별, 연도를 선택해 "
    "연령대별 인구 분포를 확인해 보세요."
)


# ---------------------------------------------------------
# CSV 파일 확인
# ---------------------------------------------------------

if not CSV_PATH.exists():
    st.error(
        "population.csv 파일을 찾을 수 없습니다.\n\n"
        f"찾으려는 위치: {CSV_PATH}\n\n"
        "population.csv 파일이 Pages 폴더가 아닌 "
        "프로젝트 최상위 폴더에 있는지 확인해 주세요."
    )
    st.stop()


# ---------------------------------------------------------
# 데이터 불러오기
# ---------------------------------------------------------

try:
    df, used_encoding = load_population_data(str(CSV_PATH))

except Exception as error:
    st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다: {error}")
    st.stop()


if "행정구역" not in df.columns:
    st.error("CSV 파일에서 '행정구역' 열을 찾을 수 없습니다.")
    st.stop()


# ---------------------------------------------------------
# 행정구역 목록
# ---------------------------------------------------------

districts = (
    df["행정구역"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)

if not districts:
    st.error("선택할 행정구역 데이터가 없습니다.")
    st.stop()


# ---------------------------------------------------------
# 사이드바 설정
# ---------------------------------------------------------

st.sidebar.header("📊 그래프 설정")

selected_district = st.sidebar.selectbox(
    "행정구역 선택",
    districts,
    index=0
)

selected_sex_label = st.sidebar.selectbox(
    "성별 선택",
    ["전체", "남", "여"],
    format_func=lambda value: {
        "전체": "전체",
        "남": "남성",
        "여": "여성"
    }[value]
)


# ---------------------------------------------------------
# 연도 자동 추출
# ---------------------------------------------------------

years = sorted({
    int(match.group(1))
    for col in df.columns
    if (match := re.match(r"^\s*(\d{4})년_", str(col)))
})

if not years:
    st.error("연도별 데이터 열을 찾을 수 없습니다.")
    st.stop()


selected_year = st.sidebar.selectbox(
    "연도 선택",
    years,
    index=len(years) - 1,
    format_func=lambda year: f"{year}년"
)


# ---------------------------------------------------------
# 선택한 행정구역 데이터 가져오기
# ---------------------------------------------------------

district_row = df[
    df["행정구역"].astype(str).str.strip() == selected_district
]

if district_row.empty:
    st.error("선택한 행정구역의 데이터를 찾을 수 없습니다.")
    st.stop()


# ---------------------------------------------------------
# 연령별 인구 열 찾기
# ---------------------------------------------------------

age_columns = get_age_columns(
    df,
    selected_year,
    selected_sex_label
)

if not age_columns:
    st.error(
        f"{selected_year}년 {selected_sex_label} "
        "연령별 인구 열을 찾지 못했습니다. "
        "CSV의 열 이름을 확인해 주세요."
    )
    st.stop()


row = district_row.iloc[0]

ages = [age for age, _ in age_columns]

population = [
    clean_number(row[col])
    for _, col in age_columns
]


# ---------------------------------------------------------
# 그래프용 데이터 만들기
# ---------------------------------------------------------

chart_df = pd.DataFrame({
    "연령": ages,
    "인구수": population
})

missing_count = int(chart_df["인구수"].isna().sum())

chart_df = chart_df.dropna(subset=["인구수"])

if chart_df.empty:
    st.warning("선택한 조건에 표시할 인구 데이터가 없습니다.")
    st.stop()

chart_df["인구수"] = chart_df["인구수"].astype(int)


# ---------------------------------------------------------
# 요약 통계
# ---------------------------------------------------------

total_population = int(chart_df["인구수"].sum())

peak_row = chart_df.loc[chart_df["인구수"].idxmax()]

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "연령대 인구 합계",
    f"{total_population:,}명"
)

metric2.metric(
    "인구가 가장 많은 연령대",
    peak_row["연령"]
)

metric3.metric(
    "해당 연령대 인구",
    f"{int(peak_row['인구수']):,}명"
)


# ---------------------------------------------------------
# 그래프 제목
# ---------------------------------------------------------

sex_title = {
    "전체": "전체",
    "남": "남성",
    "여": "여성"
}[selected_sex_label]

st.subheader(
    f"📈 {selected_district} · {sex_title} · "
    f"{selected_year}년 연령별 인구"
)


# ---------------------------------------------------------
# 세로축 최대값 계산
# ---------------------------------------------------------

max_population = int(chart_df["인구수"].max())

y_axis_max = max(
    100000,
    ((max_population // 100000) + 1) * 100000
)


# ---------------------------------------------------------
# Plotly 꺾은선 그래프
# ---------------------------------------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=chart_df["연령"],
        y=chart_df["인구수"],
        mode="lines+markers",
        name="인구수",

        line=dict(
            color=PINK,
            width=4
        ),

        marker=dict(
            color=PINK,
            size=9
        ),

        hovertemplate=(
            "%{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)


# ---------------------------------------------------------
# 그래프 디자인
# ---------------------------------------------------------

fig.update_layout(
    height=570,
    template="plotly_white",

    font=dict(
        family=(
            "'Malgun Gothic', 'Apple SD Gothic Neo', "
            "'Noto Sans CJK KR', sans-serif"
        ),
        size=13,
        color="#333333"
    ),

    margin=dict(
        l=25,
        r=25,
        t=30,
        b=30
    ),

    hovermode="x unified",
    showlegend=False,

    xaxis=dict(
        title="나이 (10세 단위)",
        type="category",
        categoryorder="array",
        categoryarray=ages,
        tickmode="array",
        tickvals=ages,
        ticktext=ages,
        showgrid=True,
        gridcolor="#E8E8E8",
        gridwidth=1,
        showline=True,
        linecolor="#999999"
    ),

    yaxis=dict(
        title="인구수 (명)",
        rangemode="tozero",
        range=[0, y_axis_max],
        tickmode="linear",
        tick0=0,
        dtick=100000,
        tickformat=",",
        ticksuffix="명",
        showgrid=True,
        gridcolor="#D9D9D9",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="#999999"
    )
)


# ---------------------------------------------------------
# Streamlit 화면에 그래프 출력
# ---------------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)


# ---------------------------------------------------------
# 결측값 안내
# ---------------------------------------------------------

if missing_count > 0:
    st.info(
        f"표시할 수 없는 결측값 {missing_count}개는 "
        "그래프에서 제외했습니다."
    )


# ---------------------------------------------------------
# 상세 데이터 표
# ---------------------------------------------------------

with st.expander("📋 그래프에 사용된 연령별 인구 데이터 보기"):

    display_df = chart_df.copy()

    display_df["인구수"] = display_df["인구수"].map(
        lambda value: f"{value:,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# 하단 안내
# ---------------------------------------------------------

st.caption(
    f"CSV 인코딩: {used_encoding.upper()} · "
    "가로축: 10세 단위 · "
    "세로축: 100,000명 단위 · "
    "그래프 색상: 핫핑크"
)
