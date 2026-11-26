import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="수능 연도별 응시현황", page_icon="📊", layout="wide")
st.title("📊 대학수학능력시험 연도별 응시현황")
st.write("학년도를 선택하면 해당 연도의 수치와 전체 학년도별 변화 추이를 확인할 수 있어요.")

CSV_FILE_NAME = "한국교육과정평가원_대학수학능력시험 연도별 응시현황_20251231(2).csv"

def find_csv_file():
    app_folder = Path(__file__).resolve().parent
    folders = [app_folder, app_folder.parent, Path.cwd(), Path.cwd().parent]
    checked = []
    for folder in folders:
        folder = folder.resolve()
        if folder not in checked:
            checked.append(folder)
    for folder in checked:
        candidate = folder / CSV_FILE_NAME
        if candidate.is_file():
            return candidate, checked
    for folder in checked:
        if folder.is_dir():
            matches = list(folder.glob("*대학수학능력시험*응시현황*.csv"))
            if matches:
                return matches[0], checked
    return None, checked

@st.cache_data
def load_data(file_path):
    last_error = None
    for encoding in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            data = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError as error:
            last_error = error
    else:
        raise ValueError(f"CSV 인코딩을 확인할 수 없습니다: {last_error}")

    data.columns = data.columns.astype(str).str.strip()
    required = ["학년도", "시험일정", "지원인원(명)", "응시인원(명)", "응시율(퍼센트)"]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError("CSV 파일에 필요한 열이 없습니다: " + ", ".join(missing))

    for column in ["학년도", "지원인원(명)", "응시인원(명)", "응시율(퍼센트)"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data["시험일정"] = data["시험일정"].fillna("").astype(str)
    data = data.dropna(subset=["학년도", "지원인원(명)", "응시인원(명)", "응시율(퍼센트)"])
    data["학년도"] = data["학년도"].astype(int)
    return data

csv_path, checked_folders = find_csv_file()
if csv_path is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("다음 폴더에서 CSV 파일을 검색했습니다.")
    for folder in checked_folders:
        st.code(str(folder))
    st.info("CSV 파일을 app.py와 같은 폴더 또는 app.py의 상위 폴더에 업로드해주세요.")
    st.stop()

try:
    df = load_data(str(csv_path))
except Exception as error:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {error}")
    st.stop()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
    st.stop()

years = sorted(df["학년도"].unique().tolist(), reverse=True)
selected_year = st.selectbox("🗓️ 확인하고 싶은 학년도를 선택하세요.", years)
selected_data = df[df["학년도"] == selected_year].sort_values("시험일정").copy()
st.subheader(f"🎓 {selected_year}학년도 수능 응시현황")

if len(selected_data) == 1:
    row = selected_data.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("📝 지원인원", f"{int(row['지원인원(명)']):,}명")
    c2.metric("✏️ 응시인원", f"{int(row['응시인원(명)']):,}명")
    c3.metric("📈 응시율", f"{row['응시율(퍼센트)']:.1f}%")
    st.caption(f"시험일정: {row['시험일정']}")
else:
    st.info(f"{selected_year}학년도에는 시험 기록이 {len(selected_data)}개 있습니다.")
    for _, row in selected_data.iterrows():
        st.markdown(f"**시험일정: {row['시험일정']}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("📝 지원인원", f"{int(row['지원인원(명)']):,}명")
        c2.metric("✏️ 응시인원", f"{int(row['응시인원(명)']):,}명")
        c3.metric("📈 응시율", f"{row['응시율(퍼센트)']:.1f}%")

st.divider()
st.subheader("📈 전체 학년도별 지원인원·응시인원·응시율 선 그래프")
st.caption("파란색 선: 지원인원 · 빨간색 선: 응시인원 · 초록색 선: 응시율. 선택한 학년도는 큰 점으로 강조됩니다.")

chart_data = df.sort_values(["학년도", "시험일정"]).copy()
marker_sizes = [12 if year == selected_year else 5 for year in chart_data["학년도"]]
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(
    x=chart_data["학년도"], y=chart_data["지원인원(명)"],
    mode="lines+markers", name="지원인원",
    line=dict(color="#2878B5", width=3), marker=dict(size=marker_sizes)
), secondary_y=False)
fig.add_trace(go.Scatter(
    x=chart_data["학년도"], y=chart_data["응시인원(명)"],
    mode="lines+markers", name="응시인원",
    line=dict(color="#E45756", width=3), marker=dict(size=marker_sizes)
), secondary_y=False)
fig.add_trace(go.Scatter(
    x=chart_data["학년도"], y=chart_data["응시율(퍼센트)"],
    mode="lines+markers", name="응시율",
    line=dict(color="#2CA25F", width=3, dash="dash"), marker=dict(size=marker_sizes)
), secondary_y=True)

fig.update_layout(
    height=600, hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=60, b=20)
)
fig.update_xaxes(title_text="학년도", dtick=2)
fig.update_yaxes(title_text="지원인원 / 응시인원 (명)", secondary_y=False)
fig.update_yaxes(title_text="응시율 (%)", secondary_y=True)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📋 선택한 학년도 상세 데이터")
display_data = selected_data[["학년도", "시험일정", "지원인원(명)", "응시인원(명)", "응시율(퍼센트)"]].copy()
display_data.columns = ["학년도", "시험일정", "지원인원(명)", "응시인원(명)", "응시율(%)"]
st.dataframe(display_data, use_container_width=True, hide_index=True)
st.caption("자료: 한국교육과정평가원 대학수학능력시험 연도별 응시현황")
