import streamlit as st
import pandas as pd
from pathlib import Path

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
# CSV 파일 경로 자동 찾기
# app.py와 같은 폴더 또는 상위 폴더에서 검색
# --------------------------------------------------
CSV_FILE_NAME = "한국교육과정평가원_대학수학능력시험 연도별 응시현황_20251231(2).csv"

def find_csv_file():
    app_folder = Path(__file__).resolve().parent

    # app.py가 루트 폴더에 있거나 pages 폴더 안에 있는 경우 모두 대응
    search_folders = [
        app_folder,
        app_folder.parent,
        Path.cwd(),
        Path.cwd().parent
    ]

    checked = []
    for folder in search_folders:
        folder = folder.resolve()
        if folder not in checked:
            checked.append(folder)

    # 먼저 정확한 파일명으로 검색
    for folder in checked:
        candidate = folder / CSV_FILE_NAME
        if candidate.is_file():
            return candidate, checked

    # 파일명이 조금 달라진 경우에도 수능 응시현황 CSV를 찾아봄
    for folder in checked:
        if folder.is_dir():
            matches = list(folder.glob("*대학수학능력시험*응시현황*.csv"))
            if matches:
                return matches[0], checked

    return None, checked


@st.cache_data
def load_data(file_path):
    # 한글 CSV 인코딩 자동 대응
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]
    last_error = None

    for encoding in encodings:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError as error:
            last_error = error
    else:
        raise ValueError(f"CSV 인코딩을 확인할 수 없습니다: {last_error}")

    # 열 이름 앞뒤 공백 제거
    data.columns = data.columns.astype(str).str.strip()

    required_columns = [
        "학년도",
        "시험일정",
        "지원인원(명)",
        "응시인원(명)",
        "응시율(퍼센트)"
    ]

    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(
            "CSV 파일에 필요한 열이 없습니다: " + ", ".join(missing_columns)
        )

    # 숫자 데이터 변환
    numeric_columns = [
        "학년도",
        "지원인원(명)",
        "응시인원(명)",
        "응시율(퍼센트)"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["시험일정"] = data["시험일정"].fillna("").astype(str)
    data = data.dropna(subset=numeric_columns)

    return data


csv_path, checked_folders = find_csv_file()

if csv_path is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("다음 폴더에서 CSV 파일을 검색했습니다.")

    for folder in checked_folders:
        st.code(str(folder))

    st.warning("CSV 파일을 GitHub 저장소에 업로드했는지 확인해주세요.")
    st.write("권장 폴더 구성:")
    st.code(
        "프로젝트 폴더/\n"
        "├── app.py\n"
        "├── requirements.txt\n"
        "└── 한국교육과정평가원_대학수학능력시험 연도별 응시현황_20251231(2).csv"
    )
    st.stop()

try:
    df = load_data(str(csv_path))
except Exception as error:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {error}")
    st.stop()

if df.empty:
    st.error("분석할 데이터가 없습니다. CSV 파일의 내용을 확인해주세요.")
    st.stop()

# --------------------------------------------------
# 학년도 선택
# --------------------------------------------------
years = sorted(
    df["학년도"].dropna().astype(int).unique().tolist(),
    reverse=True
)

selected_year = st.selectbox(
    "🗓️ 확인하고 싶은 학년도를 선택하세요.",
    years
)

selected_data = df[df["학년도"] == selected_year].copy()
selected_data = selected_data.sort_values("시험일정")

st.subheader(f"🎓 {selected_year}학년도 수능 응시현황")

# --------------------------------------------------
# 선택한 학년도 데이터 표시
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

count_chart = selected_data[
    ["시험일정", "지원인원(명)", "응시인원(명)"]
].copy()

count_chart = count_chart.set_index("시험일정")
count_chart.columns = ["지원인원", "응시인원"]

st.bar_chart(count_chart, height=400)

# --------------------------------------------------
# 응시율 막대그래프
# --------------------------------------------------
st.divider()
st.subheader("📈 응시율")

rate_chart = selected_data[
    ["시험일정", "응시율(퍼센트)"]
].copy()

rate_chart = rate_chart.set_index("시험일정")
rate_chart.columns = ["응시율(%)"]

st.bar_chart(rate_chart, height=300)

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

st.dataframe(display_data, use_container_width=True, hide_index=True)

st.caption("자료: 한국교육과정평가원 대학수학능력시험 연도별 응시현황")
