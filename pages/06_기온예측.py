
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 평균기온 예측")
st.write(
    "3가지 머신러닝 회귀 알고리즘으로 "
    "미래의 기온을 예측하고 결과를 비교해 보세요!"
)

st.divider()


# ==========================================
# 2. CSV 파일 불러오기
# ==========================================

csv_path = (
    Path(__file__).resolve().parent.parent
    / "temperature.csv"
)

if not csv_path.exists():
    csv_path = (
        Path(__file__).resolve().parent
        / "temperature.csv"
    )

if not csv_path.exists():
    st.error("temperature.csv 파일을 찾을 수 없습니다.")
    st.stop()

try:
    try:
        df = pd.read_csv(csv_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

except Exception as e:
    st.error(f"CSV 파일 오류: {e}")
    st.stop()


# ==========================================
# 3. 날짜 데이터 처리
# ==========================================

required_columns = ["일시", "평균기온(℃)"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 컬럼명을 확인해주세요.")
    st.stop()

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

year_numbers = pd.to_numeric(
    date_parts[1],
    errors="coerce"
)

valid = df["월"].notna() & year_numbers.notna()

df = df.loc[valid].copy()
year_numbers = year_numbers.loc[valid].astype(int)

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


# ==========================================
# 4. 사용자 입력
# ==========================================

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
        "예측할 월을 선택하세요",
        list(range(1, 13)),
        format_func=lambda x: month_names[x]
    )

with col2:

    latest_year = int(df["연도"].max())

    prediction_year = st.number_input(
        "예측할 연도",
        min_value=latest_year + 1,
        max_value=2200,
        value=latest_year + 1,
        step=1
    )


# ==========================================
# 5. 알고리즘 선택
# ==========================================

st.subheader("🤖 회귀 알고리즘 선택")

algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택하세요.",
    [
        "선형회귀 (Linear Regression)",
        "다항회귀 (Polynomial Regression)",
        "랜덤 포레스트 회귀 (Random Forest)"
    ]
)

algorithm_info = {
    "선형회귀 (Linear Regression)": (
        "데이터의 전체적인 경향을 직선으로 학습합니다."
    ),
    "다항회귀 (Polynomial Regression)": (
        "데이터의 비선형적인 관계를 2차 곡선으로 학습합니다."
    ),
    "랜덤 포레스트 회귀 (Random Forest)": (
        "여러 의사결정나무의 예측 결과를 종합합니다."
    )
}

st.info(algorithm_info[algorithm])

st.divider()


# ==========================================
# 6. 선택한 월의 데이터 추출
# ==========================================

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 3:
    st.error("분석에 필요한 데이터가 부족합니다.")
    st.stop()


# ==========================================
# 7. 학습 데이터 준비
# ==========================================

# 기준 연도를 빼서 계산값을 안정적으로 처리

base_year = int(month_df["연도"].min())

X = (
    month_df["연도"].values - base_year
).reshape(-1, 1)

y = month_df["평균기온(℃)"].values

predict_X = np.array([
    [prediction_year - base_year]
])


# ==========================================
# 8. 세 가지 회귀 모델 생성
# ==========================================

models = {

    "선형회귀 (Linear Regression)": (
        LinearRegression()
    ),

    "다항회귀 (Polynomial Regression)": (
        make_pipeline(
            PolynomialFeatures(degree=2),
            LinearRegression()
        )
    ),

    "랜덤 포레스트 회귀 (Random Forest)": (
        RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
    )
}


# ==========================================
# 9. 세 가지 모델 학습 및 예측
# ==========================================

results = {}
fitted_values = {}

for name, model in models.items():

    # 모델 학습
    model.fit(X, y)

    # 미래 기온 예측
    prediction = model.predict(predict_X)[0]

    # 과거 데이터에 대한 학습 결과
    fitted = model.predict(X)

    # 결정계수
    score = model.score(X, y)

    results[name] = {
        "예측 기온": prediction,
        "결정계수 R²": score
    }

    fitted_values[name] = fitted


# ==========================================
# 10. 선택한 모델 가져오기
# ==========================================

selected_model = models[algorithm]

predicted_temp = results[algorithm]["예측 기온"]

selected_fitted = fitted_values[algorithm]

r2 = results[algorithm]["결정계수 R²"]


# ==========================================
# 11. 회귀선 데이터 생성
# ==========================================

line_start = int(month_df["연도"].min())

line_end = int(max(
    month_df["연도"].max(),
    prediction_year
))

line_years = np.linspace(
    line_start,
    line_end,
    300
)

line_X = (
    line_years - base_year
).reshape(-1, 1)

line_temps = selected_model.predict(line_X)


# ==========================================
# 12. 선택한 알고리즘 그래프
# ==========================================

st.subheader(
    f"📈 {selected_month}월 평균기온 분석"
)

st.write(f"선택 알고리즘: **{algorithm}**")

fig = go.Figure()


# 실제값과 예측값 사이의 오차

residual_x = []
residual_y = []

for year, actual, fitted in zip(
    month_df["연도"],
    y,
    selected_fitted
):

    residual_x.extend([
        year, year, None
    ])

    residual_y.extend([
        actual, fitted, None
    ])


fig.add_trace(
    go.Scatter(
        x=residual_x,
        y=residual_y,
        mode="lines",
        name="실제값과 모델 예측값의 오차",
        line=dict(
            color="gray",
            width=1,
            dash="dot"
        ),
        hoverinfo="skip"
    )
)


# 실제 기온

fig.add_trace(
    go.Scatter(
        x=month_df["연도"],
        y=y,
        mode="markers",
        name="실제 평균기온",
        marker=dict(
            color="#2878D0",
            size=8
        )
    )
)


# 선택한 알고리즘의 회귀 예측선

fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_temps,
        mode="lines",
        name="선택한 알고리즘의 예측선",
        line=dict(
            color="#E74C3C",
            width=3
        )
    )
)


# 미래 예측값

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
        )
    )
)


fig.update_layout(
    title=(
        f"{selected_month}월 "
        f"{algorithm} 예측 그래프"
    ),
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    height=580,
    hovermode="closest",
    legend=dict(
        orientation="h",
        y=-0.25,
        x=0.5,
        xanchor="center"
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


# ==========================================
# 13. 선택한 알고리즘 예측 결과
# ==========================================

st.subheader("🎯 선택한 알고리즘의 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "예측 평균기온",
        f"{predicted_temp:.2f} ℃"
    )

with col2:
    st.metric(
        "결정계수 R²",
        f"{r2:.4f}"
    )

with col3:
    st.metric(
        "분석 데이터 개수",
        f"{len(month_df)}개"
    )


# ==========================================
# 14. 세 가지 알고리즘 예측 결과 비교
# ==========================================

st.divider()

st.header("🏆 3가지 알고리즘 예측 결과 비교")

st.write(
    f"{prediction_year}년 {selected_month}월의 "
    "기온을 세 가지 알고리즘으로 각각 예측한 결과입니다."
)


comparison_df = pd.DataFrame([
    {
        "알고리즘": name,
        "예측 기온(℃)": round(
            data["예측 기온"], 2
        ),
        "결정계수 R²": round(
            data["결정계수 R²"], 4
        )
    }
    for name, data in results.items()
])


# 비교 표

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 15. 예측 기온 비교 막대그래프
# ==========================================

compare_fig = go.Figure()

colors = [
    "#2878D0",
    "#2EAD78",
    "#E67E22"
]

compare_fig.add_trace(
    go.Bar(
        x=comparison_df["알고리즘"],
        y=comparison_df["예측 기온(℃)"],
        marker_color=colors,
        text=[
            f"{v:.2f}℃"
            for v in comparison_df["예측 기온(℃)"]
        ],
        textposition="outside"
    )
)

compare_fig.update_layout(
    title=f"{prediction_year}년 {selected_month}월 알고리즘별 예측 기온",
    xaxis_title="회귀 알고리즘",
    yaxis_title="예측 평균기온 (℃)",
    template="plotly_white",
    height=450,
    showlegend=False
)

compare_fig.update_yaxes(
    zeroline=True
)

st.plotly_chart(
    compare_fig,
    use_container_width=True
)


# ==========================================
# 16. 결정계수 비교
# ==========================================

st.subheader("📊 알고리즘별 결정계수 비교")

r2_fig = go.Figure()

r2_fig.add_trace(
    go.Bar(
        x=comparison_df["알고리즘"],
        y=comparison_df["결정계수 R²"],
        marker_color=colors,
        text=[
            f"{v:.4f}"
            for v in comparison_df["결정계수 R²"]
        ],
        textposition="outside"
    )
)

r2_fig.update_layout(
    title="학습 데이터에 대한 알고리즘별 설명력",
    xaxis_title="회귀 알고리즘",
    yaxis_title="결정계수 R²",
    template="plotly_white",
    height=400,
    showlegend=False
)

st.plotly_chart(
    r2_fig,
    use_container_width=True
)


# ==========================================
# 17. 알고리즘별 설명
# ==========================================

st.divider()

st.header("📚 회귀 알고리즘 알아보기")


with st.expander(
    "① 선형회귀 (Linear Regression)",
    expanded=(algorithm == "선형회귀 (Linear Regression)")
):

    st.write(
        "선형회귀는 실제 데이터와 가장 가까운 "
        "직선을 찾아 미래의 값을 예측합니다."
    )

    st.latex(r"Y = aX + b")

    st.markdown("""
    - X: 연도
    - Y: 평균기온
    - a: 기울기
    - b: 절편

    **특징**

    데이터가 직선 형태의 추세를 보일 때 유용합니다.
    계산이 간단하고 결과를 이해하기 쉽습니다.
    """)


with st.expander(
    "② 다항회귀 (Polynomial Regression)",
    expanded=(algorithm == "다항회귀 (Polynomial Regression)")
):

    st.write(
        "다항회귀는 직선 대신 곡선으로 데이터의 "
        "관계를 표현합니다. 이번 앱에서는 2차 다항회귀를 사용합니다."
    )

    st.latex(r"Y = aX^2 + bX + c")

    st.markdown("""
    **특징**

    - 곡선 형태의 데이터 패턴을 학습합니다.
    - 상승과 하락이 함께 나타나는 경향을 표현할 수 있습니다.
    - 미래로 멀리 예측할 경우 곡선이 급격하게 변할 수 있습니다.
    """)


with st.expander(
    "③ 랜덤 포레스트 회귀 (Random Forest)",
    expanded=(algorithm == "랜덤 포레스트 회귀 (Random Forest)")
):

    st.write(
        "랜덤 포레스트는 여러 개의 의사결정나무를 만들고 "
        "각 나무의 예측 결과를 평균 내어 최종 기온을 예측합니다."
    )

    st.markdown("""
    **작동 원리**

    1. 과거 데이터에서 여러 학습용 표본을 구성합니다.
    2. 각각의 의사결정나무가 데이터의 패턴을 학습합니다.
    3. 각 나무가 기온을 예측합니다.
    4. 여러 예측값의 평균을 최종 결과로 사용합니다.

    **특징**

    - 복잡한 데이터 패턴을 학습할 수 있습니다.
    - 직선이나 곡선으로 표현하기 어려운 관계도 학습합니다.
    - 일반적인 결정트리 기반 모델은 학습 데이터의 범위를 벗어난
      미래 연도에서 새로운 추세를 외삽하지 못합니다.
    """)


# ==========================================
# 18. 선형회귀와 오차의 원리
# ==========================================

with st.expander("④ 회귀 알고리즘은 어떻게 오차를 줄일까요?"):

    st.write(
        "선형회귀는 실제 관측값과 예측값의 차이를 "
        "계산하고, 오차 제곱의 합이 최소가 되는 직선을 찾습니다."
    )

    st.latex(
        r"\sum_{i=1}^{n}(Y_i-\hat{Y}_i)^2"
    )

    st.markdown("""
    - 파란색 점: 실제 기온
    - 예측선: 알고리즘이 학습한 결과
    - 회색 점선: 실제 기온과 예측 기온의 차이

    오차가 작을수록 학습 데이터에 더 잘 맞는 결과입니다.
    """)


# ==========================================
# 19. 분석 시 주의사항
# ==========================================

st.divider()

st.subheader("💡 분석 결과를 해석할 때 주의할 점")

st.markdown("""
1. 결정계수(R²)는 학습에 사용한 과거 데이터에 대한 설명력입니다.
2. R²가 높다고 미래 예측이 반드시 정확한 것은 아닙니다.
3. 랜덤 포레스트는 과거 데이터 범위를 넘어선 예측에 한계가 있습니다.
4. 다항회귀도 먼 미래를 예측할 때 실제와 큰 차이가 발생할 수 있습니다.
5. 기온은 온실가스, 도시화, 해류, 강수량 등 다양한 요인의 영향을 받습니다.
""")

st.info(
    "세 알고리즘은 서로 다른 방식으로 데이터를 학습합니다. "
    "따라서 동일한 월과 예측 연도를 선택해도 "
    "서로 다른 예측 기온이 나올 수 있습니다."
)

st.caption(
    "🌡️ 서울 월별 평균기온 분석 및 머신러닝 예측"
)
