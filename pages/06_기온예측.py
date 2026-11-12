
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression


# ----------------------------------
# 1. 페이지 기본 설정
# ----------------------------------

st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 예측")
st.write(
    "과거 기온 데이터를 분석하고 "
    "선형회귀 알고리즘으로 미래 기온을 예측해 봐요!"
)

st.divider()


# ----------------------------------
# 2. CSV 파일 불러오기
# ----------------------------------

# 현재 파일이 pages 폴더에 있으므로
# 상위 폴더에서 CSV 파일을 찾습니다.

csv_path = (
    Path(__file__).resolve().parent.parent
    / "temperature.csv"
)

if not csv_path.exists():
    # 혹시 파이썬 파일과 CSV가 같은 폴더에 있는 경우
    csv_path = (
        Path(__file__).resolve().parent
        / "temperature.csv"
    )

if not csv_path.exists():
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다. "
        "프로젝트 최상위 폴더에 CSV 파일을 넣어주세요."
    )
    st.stop()


# 한글 CSV 인코딩 처리

try:
    try:
        df = pd.read_csv(csv_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()


# ----------------------------------
# 3. 날짜 데이터 처리
# ----------------------------------

required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일에 '일시'와 '평균기온(℃)' "
        "컬럼이 있는지 확인해주세요."
    )
    st.stop()


# Oct-07 형식의 날짜 처리
# 데이터의 연도 순서를 이용하여 1907~2026년 복원

date_parts = df["일시"].astype(str).str.strip().str.extract(
    r"^([A-Za-z]{3})-(\d{2})$"
)

month_dict = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

df["월"] = date_parts[0].map(month_dict)
year_numbers = pd.to_numeric(date_parts[1], errors="coerce")

valid = df["월"].notna() & year_numbers.notna()

df = df.loc[valid].copy()
year_numbers = year_numbers.loc[valid].astype(int)

# 연도가 99에서 00으로 바뀔 때 세기를 증가시킵니다.
years = []
century = 1900
previous_year = int(year_numbers.iloc[0])

for i, yy in enumerate(year_numbers):
    yy = int(yy)

    if i > 0 and yy < previous_year:
        century += 100

    years.append(century + yy)
    previous_year = yy

df["연도"] = years

df["평균기온(℃)"] = pd.to_numeric(
    df["평균기온(℃)"],
    errors="coerce"
)

df = df.dropna(
    subset=["연도", "월", "평균기온(℃)"]
)

df["연도"] = df["연도"].astype(int)
df["월"] = df["월"].astype(int)

df = df.sort_values(["연도", "월"])

# ----------------------------------
# 4. 사용자 입력
# ----------------------------------

st.subheader("🔍 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    month_names = {
        1: "1월", 2: "2월", 3: "3월",
        4: "4월", 5: "5월", 6: "6월",
        7: "7월", 8: "8월", 9: "9월",
        10: "10월", 11: "11월", 12: "12월"
    }

    selected_month = st.selectbox(
        "예측하고 싶은 월을 선택하세요",
        options=list(range(1, 13)),
        format_func=lambda x: month_names[x]
    )

with col2:
    latest_year = int(df["연도"].max())

    prediction_year = st.number_input(
        "예측할 연도를 입력하세요",
        min_value=latest_year + 1,
        max_value=2200,
        value=latest_year + 1,
        step=1
    )

st.divider()


# ----------------------------------
# 5. 선택한 월의 데이터 추출
# ----------------------------------

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.error("선형회귀 분석을 위한 데이터가 부족합니다.")
    st.stop()


# ----------------------------------
# 6. 선형회귀 알고리즘 학습
# ----------------------------------

# X: 연도
# y: 평균기온

# 큰 연도 숫자로 인한 계산을 간단하게 하기 위해
# 첫 번째 관측 연도를 기준으로 변환합니다.

base_year = int(month_df["연도"].min())

X = (
    month_df["연도"].values - base_year
).reshape(-1, 1)

y = month_df["평균기온(℃)"].values

# 선형회귀 모델 생성
model = LinearRegression()

# 과거 데이터 학습
model.fit(X, y)

# 예측
predict_X = np.array([
    [prediction_year - base_year]
])

predicted_temp = model.predict(predict_X)[0]

# 결정계수
r2 = model.score(X, y)

# 회귀식 계수
slope = model.coef_[0]
intercept = model.intercept_


# ----------------------------------
# 7. 회귀 직선 데이터 생성
# ----------------------------------

# 실제 데이터와 예측 연도를 모두 포함하는 직선

line_start = min(
    int(month_df["연도"].min()),
    int(prediction_year)
)

line_end = max(
    int(month_df["연도"].max()),
    int(prediction_year)
)

line_years = np.linspace(
    line_start,
    line_end,
    200
)

line_X = (
    line_years - base_year
).reshape(-1, 1)

line_temps = model.predict(line_X)


# 실제 데이터의 회귀 예측값
fitted_temps = model.predict(X)


# ----------------------------------
# 8. 그래프 그리기
# ----------------------------------

st.subheader(
    f"📈 {selected_month}월 평균기온 분석 및 예측"
)

fig = go.Figure()


# ① 실제 관측값과 회귀선 사이의 오차 표시

residual_x = []
residual_y = []

for year, actual, fitted in zip(
    month_df["연도"],
    y,
    fitted_temps
):
    residual_x.extend([year, year, None])
    residual_y.extend([actual, fitted, None])

fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="실제값과 회귀선의 오차",
        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),
        hoverinfo="skip"
    )
)


# ② 실제 관측 기온

fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=y,
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#2878D0",
            size=8
        ),
        hovertemplate=(
            "연도: %{x}년<br>"
            "실제 평균기온: %{y:.2f}℃"
            "<extra></extra>"
        )
    )
)


# ③ 선형회귀 직선

fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_temps,
        mode="lines",
        name="선형회귀 예측 직선",
        line=dict(
            color="#E74C3C",
            width=3
        ),
        hovertemplate=(
            "연도: %{x:.0f}년<br>"
            "회귀선 기온: %{y:.2f}℃"
            "<extra></extra>"
        )
    )
)


# ④ 미래 예측 기온

fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[predicted_temp],
        mode="markers",
        name="미래 예측 기온",
        marker=dict(
            color="#F39C12",
            size=18,
            symbol="star",
            line=dict(
                color="black",
                width=1
            )
        ),
        hovertemplate=(
            "예측 연도: %{x}년<br>"
            "예측 평균기온: %{y:.2f}℃"
            "<extra></extra>"
        )
    )
)


# 그래프 설명

equation_text = (
    f"기온 = {intercept:.3f} "
    f"+ ({slope:.4f} × (연도 - {base_year}))"
)

fig.add_annotation(
    x=0.02,
    y=0.97,
    xref="paper",
    yref="paper",
    text=equation_text,
    showarrow=False,
    align="left",
    bgcolor="white",
    bordercolor="#AAAAAA",
    borderwidth=1,
    font=dict(size=12)
)


fig.update_layout(
    title=f"{selected_month}월 연도별 평균기온과 선형회귀 분석",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="closest",
    template="plotly_white",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5
    )
)

fig.update_xaxes(
    dtick=10,
    showgrid=True
)

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ----------------------------------
# 9. 예측 결과 출력
# ----------------------------------

st.subheader("🎯 기온 예측 결과")

result1, result2, result3 = st.columns(3)

with result1:
    st.metric(
        label=f"{prediction_year}년 {selected_month}월 예측 기온",
        value=f"{predicted_temp:.2f} ℃"
    )

with result2:
    st.metric(
        label="선형회귀 기울기",
        value=f"{slope:.4f}",
        help="1년이 지날 때 회귀선이 변화하는 기온"
    )

with result3:
    st.metric(
        label="결정계수 R²",
        value=f"{r2:.4f}"
    )


if slope > 0:
    st.success(
        f"📈 장기적인 회귀 추세는 1년에 약 "
        f"{slope:.4f}℃ 상승하는 방향입니다."
    )

elif slope < 0:
    st.info(
        f"📉 장기적인 회귀 추세는 1년에 약 "
        f"{abs(slope):.4f}℃ 하락하는 방향입니다."
    )

else:
    st.info("회귀선은 수평에 가까운 형태입니다.")


# ----------------------------------
# 10. 선형회귀 알고리즘 설명
# ----------------------------------

st.divider()

st.header("📚 선형회귀 알고리즘 알아보기")

st.write(
    "선형회귀(Linear Regression)는 과거 데이터를 분석하여 "
    "변수 사이의 관계를 가장 잘 나타내는 직선을 찾고, "
    "그 직선을 이용해 새로운 값을 예측하는 머신러닝 알고리즘입니다."
)

st.subheader("① 선형회귀는 어떻게 작동할까요?")

st.write(
    "이번 앱에서는 연도를 입력값(X)으로, "
    "평균기온을 결과값(Y)으로 사용합니다."
)

st.latex(r"Y = aX + b")

st.markdown("""
- **X(독립변수)**: 연도
- **Y(종속변수)**: 평균기온
- **a(기울기)**: 연도가 변할 때 기온이 얼마나 변하는지 나타내는 값
- **b(절편)**: 기준점에서 회귀선이 시작하는 기온
""")

st.subheader("② 가장 적합한 직선 찾기")

st.write(
    "선형회귀는 실제 관측값과 직선이 예측한 값의 차이를 "
    "계산합니다. 이 차이를 오차(잔차)라고 합니다."
)

st.latex(
    r"\text{오차} = \text{실제 기온} - \text{예측 기온}"
)

st.latex(
    r"\text{최소화 목표} = \sum_{i=1}^{n}(Y_i-\hat{Y}_i)^2"
)

st.markdown("""
**최소제곱법이란?**

1. 과거의 실제 기온 데이터를 점으로 표시합니다.
2. 데이터의 전체적인 경향을 나타내는 직선을 찾습니다.
3. 각 점과 직선 사이의 세로 방향 오차를 계산합니다.
4. 오차를 제곱하여 모두 더합니다.
5. 이 합계가 가장 작아지도록 직선의 기울기와 절편을 결정합니다.
""")

st.info(
    "그래프에서 파란색 점은 실제 관측 기온, "
    "빨간색 직선은 선형회귀가 찾은 최적의 직선, "
    "회색 점선은 실제 기온과 회귀선 사이의 오차, "
    "주황색 별은 미래 예측 기온입니다."
)

st.subheader("③ 결정계수(R²)란?")

st.write(
    "결정계수는 선형회귀 모델이 과거 기온 데이터의 "
    "변동을 얼마나 설명하는지 나타내는 지표입니다."
)

st.markdown("""
- 1에 가까울수록 과거 데이터의 경향을 잘 설명합니다.
- 0에 가까울수록 설명력이 낮습니다.
- 높은 결정계수가 미래 예측의 정확성을 보장하지는 않습니다.
""")

st.subheader("④ 이번 분석에서 기억할 점")

st.write(
    "기온은 온실가스, 해류, 강수량, 도시화 등 "
    "다양한 요인의 영향을 받습니다. 이번 앱은 연도와 "
    "평균기온 사이의 선형적인 관계만 학습하므로, "
    "장기적인 예측값은 실제 미래 기온과 다를 수 있습니다."
)

st.caption(
    "※ 본 예측은 선택한 월의 과거 평균기온을 이용한 "
    "단순 선형회귀 분석 결과입니다."
)

st.divider()

st.caption(
    "🌡️ 서울 월별 평균기온 분석 및 예측 | "
    "Linear Regression"
)

