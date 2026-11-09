
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# --------------------------------------
# 1. 페이지 설정
# --------------------------------------

st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하면 전체 연도의 최고기온과 최저기온을 비교할 수 있어요!")

# --------------------------------------
# 2. 데이터 불러오기
# --------------------------------------

@st.cache_data
def load_data():

    file_path = Path(__file__).parent / "temperature.csv"

    # 한글 인코딩 자동 처리
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 날짜 데이터 확인
    df["일시"] = df["일시"].astype(str).str.strip()

    # 영문 월 이름
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    # 월과 두 자리 연도 분리
    parts = df["일시"].str.extract(
        r"^([A-Za-z]{3})-(\d{2})$"
    )

    if parts.isnull().any().any():
        raise ValueError("날짜 형식을 확인해 주세요.")

    df["월"] = parts[0].map(month_dict)

    if df["월"].isnull().any():
        raise ValueError("인식할 수 없는 월 데이터가 있습니다.")

    # 연도 복원
    # 데이터는 1907년 10월부터 시간순으로 정렬되어 있음
    years = []
    previous_year = None

    for value in parts[1]:
        short_year = int(value)

        if previous_year is None:
            year = 1900 + short_year
        else:
            year = (previous_year // 100) * 100 + short_year

            # 연도가 99에서 00으로 넘어가는 경우
            if year < previous_year:
                year += 100

        years.append(year)
        previous_year = year

    df["연도"] = years

    # 기온 데이터 숫자 변환
    temp_columns = [
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
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# --------------------------------------
# 3. 월 선택
# --------------------------------------

st.subheader("📅 분석할 월을 선택하세요")

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

selected_month = st.selectbox(
    "월 선택",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x],
    index=0
)


# --------------------------------------
# 4. 선택한 월의 데이터 추출
# --------------------------------------

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

# 결측치 제외
month_df = month_df.dropna(
    subset=["최고기온(℃)", "최저기온(℃)"],
    how="all"
)


# --------------------------------------
# 5. 기온 그래프 작성
# --------------------------------------

if month_df.empty:

    st.warning("선택한 월에 분석할 데이터가 없습니다.")

else:

    fig = go.Figure()

    # 최고기온 그래프 - 연핑크
    fig.add_trace(
        go.Scatter(
            x=month_df["연도"],
            y=month_df["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#FFB6C1",
                width=3
            ),
            marker=dict(
                size=6,
                color="#FFB6C1"
            ),
            connectgaps=False
        )
    )

    # 최저기온 그래프 - 하늘색
    fig.add_trace(
        go.Scatter(
            x=month_df["연도"],
            y=month_df["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#87CEEB",
                width=3
            ),
            marker=dict(
                size=6,
                color="#87CEEB"
            ),
            connectgaps=False
        )
    )

    # 그래프 제목과 축 설정
    fig.update_layout(
        title={
            "text": "월별 기온분석",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="연도",
        yaxis_title="온도(℃)",
        legend=dict(
            title="기온 구분",
            orientation="h",
            y=1.12,
            x=0.5,
            xanchor="center"
        ),
        hovermode="x unified",
        template="plotly_white",
        height=550
    )

    fig.update_xaxes(
        showgrid=True,
        dtick=10
    )

    fig.update_yaxes(
        showgrid=True,
        zeroline=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# --------------------------------------
# 6. 주요 통계 정보
# --------------------------------------

st.subheader("📊 선택한 월의 기온 통계")

col1, col2, col3 = st.columns(3)

max_temp = month_df["최고기온(℃)"].max()
min_temp = month_df["최저기온(℃)"].min()

avg_max = month_df["최고기온(℃)"].mean()
avg_min = month_df["최저기온(℃)"].mean()

with col1:
    st.metric(
        "역대 최고기온",
        f"{max_temp:.1f}℃" if pd.notna(max_temp) else "-"
    )

with col2:
    st.metric(
        "역대 최저기온",
        f"{min_temp:.1f}℃" if pd.notna(min_temp) else "-"
    )

with col3:
    st.metric(
        "분석 연도 수",
        f"{len(month_df)}년"
    )


# --------------------------------------
# 7. 상세 데이터 표
# --------------------------------------

st.subheader("📋 연도별 상세 기온 데이터")

result = month_df[
    ["연도", "최고기온(℃)", "최저기온(℃)"]
].copy()

result.columns = [
    "연도",
    "최고기온",
    "최저기온"
]

st.dataframe(
    result,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------
# 8. 데이터 다운로드
# --------------------------------------

csv_data = result.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 분석 결과 CSV 다운로드",
    data=csv_data,
    file_name=f"{selected_month}월_기온분석.csv",
    mime="text/csv"
)

st.caption("※ 원본 데이터의 결측값은 그래프와 통계에서 제외됩니다.")
