import streamlit as st
import pandas as pd
import os

# --------------------------------------------------
# 페이지 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="수능 연도별 응시현황",
    page_icon="📊",
    layout="wide"
)

st.title("📊 대학수학능력시험 연도별 응시현황")
st.write("학년도를 선택하면 해당 연도의 지원인원, 응시인원, 응시율을 확인할 수 있어요.")

# --------------------------------------------------
# CSV 파일 불러오기
# app.py와 같은 폴더에 CSV 파일을 넣어주세요.
# --------------------------------------------------
@st.cache_data
def load_data():
    file_name = "한국교육과정평가원_대학수학능력시험 연도별 응시현황_20251231(2).csv"

    if not os.path.exists(file_name):
        return None

    # 공공데이터 CSV의 한글 인코딩(cp949)을 우선 사용
    try:
        data = pd.read_csv(file_name, encoding="cp949")
    except UnicodeDecodeError:
        try:
            data = pd.read_csv(file_name, encoding="euc-kr")
        except UnicodeDecodeError:
            data = pd.read_csv(file_name, encoding="utf-8-sig")

    # 열 이름 앞뒤 공백 제거
    data.columns = data.columns.str.strip()

    # 숫자 데이터 변환
    numeric_columns = ["학년도", "지원인원(명)", "응시인원(명)", "응시율(퍼센트)"]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["시험일정"] = data["시험일정"].astype(str)

    # 필수 데이터가 없는 행 제거
    data = data.dropna(subset=numeric_columns)

    return data


df = load_data()

if df is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info(
        "app.py와 같은 폴더에 다음 CSV 파일을 넣어주세요.\n\n"
        "한국교육과정평가원_대학수학능력시험 연도별 응시현황_20251231(2).csv"
    )
    st.stop()

if df.empty:
    st.error("분석할 데이터가 없습니다. CSV 파일의 내용을 확인해주세요.")
    st.stop()

# --------------------------------------------------
# 학년도 선택
# --------------------------------------------------
years = sorted(df["학년도"].dropna().astype(int).unique().tolist(), reverse=True)

selected_year = st.selectbox(
    "🗓️ 확인하고 싶은 학년도를 선택하세요.",
    years
)

selected_data = df[df["학년도"] == selected_year].copy()
selected_data = selected_data.sort_values("시험일정")

st.subheader(f"🎓 {selected_year}학년도 수능 응시현황")

# --------------------------------------------------
# 선택한 학년도 데이터 표시
# 1994학년도처럼 시험 기록이 여러 개인 경우 각각 표시
# --------------------------------------------------
if len(selected_data) == 1:
    row = selected_data.iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("📝 지원인원", f"{int(row['지원인원(명)']):,}명")
    col2.metric("✏️ 응시인원", f"{int(row['응시인원(명)']):,}명")
    col3.metric("📈 응시율", f"{row['응시율(퍼센트)']:.1f}%")

    st.caption(f"시험일정: {row['시험일정']}")

else:
    st.info(
        f"{selected_year}학년도에는 시험 기록이 {len(selected_data)}개 있습니다. "
        "각 시험일정별로 구분하여 표시합니다."
    )

    for _, row in selected_data.iterrows():
        st.markdown(f"**시험일정: {row['시험일정']}**")
        col1, col2, col3 = st.columns(3)
        col1.metric("📝 지원인원", f"{int(row['지원인원(명)']):,}명")
        col2.metric("✏️ 응시인원", f"{int(row['응시인원(명)']):,}명")
        col3.metric("📈 응시율", f"{row['응시율(퍼센트)']:.1f}%")

# --------------------------------------------------
# 지원인원 / 응시인원 막대그래프
# --------------------------------------------------
st.divider()
st.subheader("📊 지원인원과 응시인원 비교")

count_chart = selected_data[["시험일정", "지원인원(명)", "응시인원(명)"]].copy()
count_chart = count_chart.set_index("시험일정")
count_chart.columns = ["지원인원", "응시인원"]

st.bar_chart(
    count_chart,
    use_container_width=True,
    height=400
)

# --------------------------------------------------
# 응시율 막대그래프
# --------------------------------------------------
st.divider()
st.subheader("📈 학년도별 시험일정 응시율")

rate_chart = selected_data[["시험일정", "응시율(퍼센트)"]].copy()
rate_chart = rate_chart.set_index("시험일정")
rate_chart.columns = ["응시율(%)"]

st.bar_chart(
    rate_chart,
    use_container_width=True,
    height=300
)

# --------------------------------------------------
# 상세 데이터 표
# --------------------------------------------------
st.divider()
st.subheader("📋 선택한 학년도 상세 데이터")

display_data = selected_data[
    ["학년도", "시험일정", "지원인원(명)", "응시인원(명)", "응시율(퍼센트)"]
].copy()

display_data.columns = [
    "학년도",
    "시험일정",
    "지원인원(명)",
    "응시인원(명)",
    "응시율(%)"
]

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

st.caption("자료: 한국교육과정평가원 대학수학능력시험 연도별 응시현황")

