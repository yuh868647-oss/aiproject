
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ======================================
# 1. 페이지 설정
# ======================================

st.set_page_config(
    page_title="서울 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 분석 대시보드")
st.write("서울의 기온 변화를 그래프로 확인해 보세요!")

# ======================================
# 2. CSV 데이터 불러오기
# ======================================

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더에서 CSV 찾기
    file_path = Path(__file__).parent.parent / "temperature.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}"
        )

    # 한글 인코딩 처리
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 날짜 정리
    df["일시"] = df["일시"].astype(str).str.strip()

    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    parts = df["일시"].str.extract(
        r"^([A-Za-z]{3})-(\d{2})$"
    )

    if parts.isnull().any().any():
        raise ValueError("날짜 형식을 확인해 주세요.")

    df["월"] = parts[0].map(month_dict)

    if df["월"].isnull().any():
        raise ValueError("잘못된 월 데이터가 있습니다.")

    # 연도 복원
    # 자료는 1907년 10월부터 시간순으로 정렬되어 있음
    years = []
    previous_year = None

    for value in parts[1]:
        short_year = int(value)

        if previous_year is None:
            year = 1900 + short_year
        else:
            year = (
                (previous_year // 100) * 100
                + short_year
            )

            if year < previous_year:
                year += 100

        years.append(year)
        previous_year = year

    df["연도"] = years

    # 기온 데이터 숫자 변환
    temp_columns = [
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in temp_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러올 수 없습니다: {e}")
    st.stop()


month_names = [
    "1월", "2월", "3월", "4월",
    "5월", "6월", "7월", "8월",
    "9월", "10월", "11월", "12월"
]


# ======================================
# 3. 기능 1: 월별 평균기온 그래프
# ======================================

st.header("📈 1. 서울 월별 평균기온")

st.write(
    "전체 관측 기간의 자료를 이용하여 "
    "1월부터 12월까지 월별 평균기온을 비교합니다."
)

monthly_avg = (
    df.groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(range(1, 13))
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=month_names,
        y=monthly_avg.values,
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color="#FF9999",
            width=4
        ),
        marker=dict(
            size=10,
            color="#FF9999"
        )
    )
)

fig1.update_layout(
    title=dict(
        text="서울 월별 평균기온",
        x=0.5
    ),
    xaxis_title="월",
    yaxis_title="온도(℃)",
    template="plotly_white",
    height=450,
    hovermode="x unified",
    showlegend=True
)

fig1.update_xaxes(
    categoryorder="array",
    categoryarray=month_names
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# 월별 평균기온 표
with st.expander("월별 평균기온 데이터 보기"):
    avg_table = pd.DataFrame({
        "월": month_names,
        "평균기온(℃)": monthly_avg.round(2).values
    })

    st.dataframe(
        avg_table,
        use_container_width=True,
        hide_index=True
    )


# ======================================
# 4. 기능 2, 3: 연도별 기온 비교
# ======================================

st.divider()

st.header("📊 2. 연도별 최고기온과 최저기온 비교")

st.write(
    "연도를 하나 선택하거나 두 개 선택하여 "
    "월별 최고기온과 최저기온을 비교해 보세요."
)

# 데이터에 존재하는 연도
available_years = sorted(
    df["연도"].unique().tolist()
)

# 연도 선택 방식
compare_type = st.radio(
    "분석 방법 선택",
    ["연도 1개 분석", "연도 2개 비교"],
    horizontal=True
)

# --------------------------------------
# 연도 1개 선택
# --------------------------------------

if compare_type == "연도 1개 분석":

    selected_year = st.selectbox(
        "분석할 연도를 선택하세요.",
        available_years,
        index=len(available_years) - 1
    )

    selected_df = df[
        df["연도"] == selected_year
    ].copy()

    # 월별 데이터
    yearly_data = (
        selected_df.groupby("월")[
            ["최고기온(℃)", "최저기온(℃)"]
        ]
        .mean()
        .reindex(range(1, 13))
    )

    fig2 = go.Figure()

    # 최고기온 - 연핑크
    fig2.add_trace(
        go.Scatter(
            x=month_names,
            y=yearly_data["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#FFB6C1",
                width=3
            ),
            marker=dict(size=8)
        )
    )

    # 최저기온 - 하늘색
    fig2.add_trace(
        go.Scatter(
            x=month_names,
            y=yearly_data["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#87CEEB",
                width=3
            ),
            marker=dict(size=8)
        )
    )

    fig2.update_layout(
        title=dict(
            text=f"{selected_year}년 최고기온과 최저기온",
            x=0.5
        ),
        xaxis_title="월",
        yaxis_title="온도(℃)",
        template="plotly_white",
        height=500,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=1.12,
            x=0.5,
            xanchor="center"
        )
    )

    fig2.update_xaxes(
        categoryorder="array",
        categoryarray=month_names
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# --------------------------------------
# 연도 2개 선택
# --------------------------------------

else:

    selected_years = st.multiselect(
        "비교할 연도 2개를 선택하세요.",
        options=available_years,
        default=available_years[-2:],
        max_selections=2
    )

    if len(selected_years) != 2:

        st.info("비교할 연도를 정확히 2개 선택해 주세요.")

    else:

        selected_years = sorted(selected_years)

        fig3 = go.Figure()

        # 연도별 색상
        colors = [
            {
                "max": "#FFB6C1",
                "min": "#87CEEB"
            },
            {
                "max": "#E75480",
                "min": "#4682B4"
            }
        ]

        # 두 연도 데이터 그래프
        for i, year in enumerate(selected_years):

            year_df = df[
                df["연도"] == year
            ].copy()

            yearly_data = (
                year_df.groupby("월")[
                    ["최고기온(℃)", "최저기온(℃)"]
                ]
                .mean()
                .reindex(range(1, 13))
            )

            # 최고기온
            fig3.add_trace(
                go.Scatter(
                    x=month_names,
                    y=yearly_data["최고기온(℃)"],
                    mode="lines+markers",
                    name=f"{year}년 최고기온",
                    line=dict(
                        color=colors[i]["max"],
                        width=3
                    ),
                    marker=dict(size=7)
                )
            )

            # 최저기온
            fig3.add_trace(
                go.Scatter(
                    x=month_names,
                    y=yearly_data["최저기온(℃)"],
                    mode="lines+markers",
                    name=f"{year}년 최저기온",
                    line=dict(
                        color=colors[i]["min"],
                        width=3,
                        dash="dash"
                    ),
                    marker=dict(size=7)
                )
            )

        fig3.update_layout(
            title=dict(
                text=(
                    f"{selected_years[0]}년과 "
                    f"{selected_years[1]}년 기온 비교"
                ),
                x=0.5
            ),
            xaxis_title="월",
            yaxis_title="온도(℃)",
            template="plotly_white",
            height=550,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                y=1.15,
                x=0.5,
                xanchor="center"
            )
        )

        fig3.update_xaxes(
            categoryorder="array",
            categoryarray=month_names
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )


# ======================================
# 5. 데이터 정보
# ======================================

st.divider()

st.subheader("📋 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 데이터",
        f"{len(df):,}개"
    )

with col2:
    st.metric(
        "분석 시작 연도",
        f"{min(available_years)}년"
    )

with col3:
    st.metric(
        "분석 마지막 연도",
        f"{max(available_years)}년"
    )

st.caption(
    "※ 기온은 원본 데이터에 기록된 월별 관측값을 사용합니다. "
    "월별 평균 계산 시 결측값은 자동으로 제외됩니다."
)
