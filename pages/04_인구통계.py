import re
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------
# 서울시 연령별 인구 분석 앱
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

AGE_LABELS = [
    "0~9세", "10~19세", "20~29세", "30~39세",
    "40~49세", "50~59세", "60~69세", "70~79세",
    "80~89세", "90~99세", "100세 이상"
]

# 성별에 따라 그래프 색상 변경
SEX_COLORS = {
    "전체": "#4169E1",  # 파란색
    "남": "#FF1493",    # 핫핑크
    "여": "#2EAD63"     # 초록색
}

PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_DIR / "population.csv"


# ---------------------------------------------------------
# CSV 데이터 불러오기
# ---------------------------------------------------------

@st.cache_data
def load_population_data(file_path: str):
    """한글 CSV 파일을 여러 인코딩으로 읽습니다."""
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


# ---------------------------------------------------------
# 숫자 데이터 정리
# ---------------------------------------------------------

def clean_number(value):
    """쉼표가 있는 인구 값을 정수로 변환합니다."""
    if pd.isna(value):
        return None

    cleaned = str(value).replace(",", "").strip()

    if cleaned in ("", "-", "—"):
        return None

    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------
# 연도와 성별에 맞는 연령대 열 찾기
# ---------------------------------------------------------

def get_age_columns(data, year, sex):
    """선택한 연도와 성별에 해당하는 연령대별 열을 찾습니다."""
    selected_columns = []

    for age in AGE_LABELS:

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
# 제목 및 파일 불러오기
# ---------------------------------------------------------

st.title("🌸 서울시 연령별 인구 분석")

st.caption(
    "서울시 자치구의 연령별 인구 분포와 "
    "지역별 인구 순위를 살펴보세요."
)

if not CSV_PATH.exists():
    st.error(
        "population.csv 파일을 찾을 수 없습니다.\n\n"
        f"찾으려는 위치: {CSV_PATH}\n\n"
        "CSV 파일이 Pages 폴더가 아닌 "
        "프로젝트 최상위 폴더에 있는지 확인해 주세요."
    )
    st.stop()

try:
    df, used_encoding = load_population_data(str(CSV_PATH))

except Exception as error:
    st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다: {error}")
    st.stop()

if "행정구역" not in df.columns:
    st.error("CSV 파일에서 '행정구역' 열을 찾을 수 없습니다.")
    st.stop()


# ---------------------------------------------------------
# 자치구 데이터 준비
# 서울시 전체 행은 자치구 순위에서 제외
# ---------------------------------------------------------

df["행정구역"] = df["행정구역"].astype(str).str.strip()

df["자치구"] = df["행정구역"].str.extract(
    r"서울특별시\s*(.*?)\s*\(\d+\)",
    expand=False
)

district_df = df[
    df["자치구"].notna()
    & (df["자치구"].str.strip() != "")
].copy()

district_df["자치구"] = district_df["자치구"].str.strip()


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

if district_df.empty:
    st.error("서울시 자치구 데이터를 찾을 수 없습니다.")
    st.stop()


# ---------------------------------------------------------
# 사이드바: 분석 조건 선택
# ---------------------------------------------------------

st.sidebar.header("📊 분석 조건")

all_areas = (
    df["행정구역"]
    .dropna()
    .astype(str)
    .tolist()
)

selected_district_label = st.sidebar.selectbox(
    "꺾은선 그래프 행정구역 선택",
    all_areas,
    index=0
)

selected_sex = st.sidebar.selectbox(
    "성별 선택",
    ["전체", "남", "여"],
    format_func=lambda value: {
        "전체": "전체",
        "남": "남성",
        "여": "여성"
    }[value]
)

selected_year = st.sidebar.selectbox(
    "연도 선택",
    years,
    index=len(years) - 1,
    format_func=lambda year: f"{year}년"
)


# ---------------------------------------------------------
# 연령대 선택
# ---------------------------------------------------------

age_columns = get_age_columns(
    df,
    selected_year,
    selected_sex
)

if not age_columns:
    st.error(
        f"{selected_year}년 {selected_sex} "
        "연령별 인구 열을 찾지 못했습니다. "
        "CSV의 열 이름을 확인해 주세요."
    )
    st.stop()

available_ages = [age for age, _ in age_columns]

selected_compare_age = st.sidebar.selectbox(
    "자치구 순위 그래프 연령대 선택",
    available_ages,
    index=0
)


# =========================================================
# 1. 연령대별 인구 분포 꺾은선 그래프
# =========================================================

st.header("1. 연령대별 인구 분포 📈")

st.caption(
    "선택한 행정구역의 연령대별 인구를 "
    "꺾은선 그래프로 확인합니다."
)

selected_row = df[
    df["행정구역"] == selected_district_label
]

if selected_row.empty:

    st.warning("선택한 행정구역의 데이터를 찾을 수 없습니다.")

else:

    row = selected_row.iloc[0]

    ages = [age for age, _ in age_columns]

    population = [
        clean_number(row[col])
        for _, col in age_columns
    ]

    chart_df = pd.DataFrame({
        "연령": ages,
        "인구수": population
    })

    missing_count = int(chart_df["인구수"].isna().sum())

    chart_df = chart_df.dropna(subset=["인구수"])

    if chart_df.empty:

        st.warning("선택한 조건에 표시할 인구 데이터가 없습니다.")

    else:

        chart_df["인구수"] = chart_df["인구수"].astype(int)

        total_population = int(chart_df["인구수"].sum())

        peak_row = chart_df.loc[
            chart_df["인구수"].idxmax()
        ]

        # 주요 인구 통계
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

        sex_title = {
            "전체": "전체",
            "남": "남성",
            "여": "여성"
        }[selected_sex]

        # 성별에 따른 선 색상
        line_color = SEX_COLORS[selected_sex]

        max_population = int(chart_df["인구수"].max())

        y_axis_max = max(
            100000,
            ((max_population // 100000) + 1) * 100000
        )

        fig_line = go.Figure()

        fig_line.add_trace(
            go.Scatter(
                x=chart_df["연령"],
                y=chart_df["인구수"],
                mode="lines+markers",
                name=f"{sex_title} 인구수",

                line=dict(
                    color=line_color,
                    width=4
                ),

                marker=dict(
                    color=line_color,
                    size=9
                ),

                hovertemplate=(
                    "%{x}<br>"
                    "인구수: %{y:,.0f}명"
                    "<extra></extra>"
                )
            )
        )

        fig_line.update_layout(
            height=540,
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
                t=25,
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
                gridcolor="#E8E8E8"
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
                gridcolor="#D9D9D9"
            )
        )

        st.plotly_chart(
            fig_line,
            use_container_width=True
        )

        if missing_count > 0:
            st.info(
                f"결측값 {missing_count}개는 "
                "꺾은선 그래프에서 제외했습니다."
            )

        with st.expander(
            "📋 선택한 행정구역의 연령별 인구 데이터 보기"
        ):

            display_df = chart_df.copy()

            display_df["인구수"] = display_df["인구수"].map(
                lambda value: f"{value:,}명"
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )


# =========================================================
# 2. 연령대별 인구가 많은 자치구 막대그래프
# =========================================================

st.divider()

st.header("2. 연령대별 인구가 많은 자치구 찾기 🏆")

st.caption(
    "연도와 성별을 선택하고 연령대를 고르면 "
    "해당 연령대 인구가 많은 자치구 순위를 보여줍니다."
)

# 선택한 연령대의 실제 CSV 열
age_column_map = dict(age_columns)

compare_column = age_column_map[selected_compare_age]

# 자치구별 인구 데이터 가져오기
ranking_df = district_df[
    ["자치구", compare_column]
].copy()

ranking_df["인구수"] = ranking_df[
    compare_column
].apply(clean_number)

ranking_df = ranking_df.dropna(
    subset=["인구수"]
)

ranking_df["인구수"] = ranking_df["인구수"].astype(int)

ranking_df = ranking_df.drop(
    columns=[compare_column]
)

# 인구가 많은 순서대로 정렬
ranking_df = ranking_df.sort_values(
    "인구수",
    ascending=False
).reset_index(drop=True)

ranking_df.insert(
    0,
    "순위",
    range(1, len(ranking_df) + 1)
)


if ranking_df.empty:

    st.warning(
        "선택한 연령대의 자치구별 인구 데이터가 없습니다."
    )

else:

    top_district = ranking_df.iloc[0]

    # 1위 자치구 통계
    rank_col1, rank_col2, rank_col3 = st.columns(3)

    rank_col1.metric(
        "인구가 가장 많은 자치구",
        top_district["자치구"]
    )

    rank_col2.metric(
        "선택한 연령대",
        selected_compare_age
    )

    rank_col3.metric(
        "인구수",
        f"{int(top_district['인구수']):,}명"
    )

    # 가로 막대그래프
    # 작은 값부터 넣으면 큰 값이 위쪽에 표시됨
    bar_df = ranking_df.sort_values(
        "인구수",
        ascending=True
    )

    bar_color = SEX_COLORS[selected_sex]

    fig_bar = go.Figure()

    fig_bar.add_trace(
        go.Bar(
            x=bar_df["인구수"],
            y=bar_df["자치구"],
            orientation="h",

            marker_color=bar_color,

            text=bar_df["인구수"].map(
                lambda value: f"{value:,}명"
            ),

            textposition="outside",
            cliponaxis=False,

            hovertemplate=(
                "%{y}<br>"
                "인구수: %{x:,.0f}명"
                "<extra></extra>"
            )
        )
    )

    fig_bar.update_layout(
        height=760,
        template="plotly_white",

        title=dict(
            text=(
                f"{selected_year}년 {sex_title} "
                f"{selected_compare_age} 인구 자치구 순위"
            ),
            x=0.02
        ),

        font=dict(
            family=(
                "'Malgun Gothic', 'Apple SD Gothic Neo', "
                "'Noto Sans CJK KR', sans-serif"
            ),
            size=12,
            color="#333333"
        ),

        margin=dict(
            l=20,
            r=80,
            t=65,
            b=30
        ),

        xaxis=dict(
            title="인구수 (명)",
            tickformat=",",
            showgrid=True,
            gridcolor="#E5E5E5",
            rangemode="tozero"
        ),

        yaxis=dict(
            title="행정구역",
            categoryorder="array",
            categoryarray=bar_df["자치구"].tolist()
        ),

        showlegend=False
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # 순위표
    with st.expander("📋 자치구별 인구 순위표 보기"):

        ranking_display = ranking_df.copy()

        ranking_display["인구수"] = (
            ranking_display["인구수"].map(
                lambda value: f"{value:,}명"
            )
        )

        st.dataframe(
            ranking_display,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# 3. 추가 기능 추천
# =========================================================

st.divider()

st.header("💡 이 데이터로 더 만들 수 있는 기능")

recommendations = [

    (
        "1. 연도별 인구 변화 비교",
        "2020~2025년 사이 자치구와 연령대별 인구가 "
        "얼마나 늘거나 줄었는지 선그래프로 비교해요. "
        "인구가 빠르게 증가하거나 감소한 지역을 찾을 수 있어요."
    ),

    (
        "2. 서울시 자치구 인구 히트맵",
        "행은 자치구, 열은 연령대로 놓고 인구가 많은 곳과 "
        "적은 곳을 색으로 표현해요. "
        "25개 자치구의 특징을 한눈에 비교하기 좋아요."
    ),

    (
        "3. 남녀 인구 비교 및 성비 분석",
        "같은 자치구와 연령대에서 남녀 인구를 나란히 보여줘요. "
        "어느 연령대에서 남녀 인구 차이가 큰지 확인할 수 있어요."
    ),

    (
        "4. 자치구별 고령층·청소년 인구 순위",
        "예를 들어 60세 이상 또는 10~19세 인구를 합산해 "
        "자치구 순위를 만들어요. "
        "다만 이 데이터는 10세 단위이므로 "
        "정확히 65세 이상 같은 구간은 계산할 수 없어요."
    ),

    (
        "5. 연령별 인구 피라미드",
        "남성은 왼쪽, 여성은 오른쪽으로 막대를 그려 "
        "자치구의 연령 구조를 비교해요. "
        "지역별 인구 구성의 차이를 이해하기 쉬워요."
    ),

    (
        "6. 연령대별 인구 비율 보기",
        "인구수뿐 아니라 전체 인구 중 각 연령대가 "
        "차지하는 비율(%)을 계산해요. "
        "인구 규모가 다른 자치구도 공정하게 비교할 수 있어요."
    )
]

for title, description in recommendations:

    with st.expander(title):
        st.write(description)


# =========================================================
# 하단 안내
# =========================================================

st.caption(
    f"데이터 인코딩: {used_encoding.upper()} · "
    f"데이터 연도: {min(years)}~{max(years)}년 · "
    f"분석 대상: 서울시 {len(district_df)}개 자치구"
)
