
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

st.set_page_config(page_title="붓꽃 품종 예측기", page_icon="🌸", layout="wide")

st.title("🌸 붓꽃 품종 예측기")
st.write("꽃잎 길이와 너비를 입력하면 KNN 알고리즘으로 붓꽃 품종을 예측해요.")

DATA_PATH = Path(__file__).resolve().parent / "iris.csv"
FEATURES = ["꽃잎 길이", "꽃잎 너비"]
TARGET = "품종"


@st.cache_data
def load_data(path):
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            data = pd.read_csv(path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 인코딩을 읽을 수 없습니다.")

    required = FEATURES + [TARGET]
    missing = [col for col in required if col not in data.columns]

    if missing:
        raise ValueError(f"필요한 컬럼이 없습니다: {missing}")

    data = data[required].copy()

    for col in FEATURES:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=required)

    if data.empty:
        raise ValueError("분석할 데이터가 없습니다.")

    return data


if not DATA_PATH.exists():
    st.error("iris.csv 파일을 app.py와 같은 폴더에 넣어주세요.")
    st.stop()

try:
    df = load_data(DATA_PATH)
except Exception as error:
    st.error(f"데이터 오류: {error}")
    st.stop()


# 입력 범위 설정
length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())
width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

st.info(
    f"📌 입력 가능 범위\n\n"
    f"꽃잎 길이: {length_min:.1f} ~ {length_max:.1f} cm\n\n"
    f"꽃잎 너비: {width_min:.1f} ~ {width_max:.1f} cm"
)


# KNN 모델 생성
X = df[FEATURES]
y = df[TARGET].astype(str)

k = min(5, len(df))

model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=k))
])

model.fit(X, y)


# 사용자 입력
st.subheader("1. 꽃잎 크기 입력하기")

col1, col2 = st.columns(2)

with col1:
    input_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=float(np.clip(4.5, length_min, length_max)),
        step=0.1,
        format="%.1f"
    )

with col2:
    input_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=float(np.clip(1.5, width_min, width_max)),
        step=0.1,
        format="%.1f"
    )


# 품종 예측
query = np.array([[input_length, input_width]])
prediction = model.predict(query)[0]

st.subheader("2. 예측 결과")

st.success(f"🔍 예측된 붓꽃 품종은 {prediction} 입니다!")


# 가장 가까운 이웃 5개 확인
scaler = model.named_steps["scaler"]
knn = model.named_steps["knn"]

distances, neighbor_indices = knn.kneighbors(
    scaler.transform(query),
    n_neighbors=k
)

neighbor_labels = y.iloc[neighbor_indices[0]].reset_index(drop=True)
vote_counts = neighbor_labels.value_counts()

st.write(f"**가장 가까운 {k}개 데이터의 품종 투표 결과**")

vote_df = (
    vote_counts.rename_axis("품종")
    .reset_index(name="이웃 개수")
    .sort_values(["이웃 개수", "품종"], ascending=[False, True])
)

st.dataframe(vote_df, use_container_width=True, hide_index=True)

st.caption(
    f"가장 가까운 {k}개 중 "
    f"{int(vote_counts.get(prediction, 0))}개가 "
    f"{prediction}이어서 이 품종으로 예측했어요."
)


with st.expander("가장 가까운 이웃 데이터 자세히 보기"):
    neighbor_detail = df.iloc[neighbor_indices[0]][
        FEATURES + [TARGET]
    ].copy()

    neighbor_detail.insert(0, "거리(표준화 기준)", distances[0])
    neighbor_detail = neighbor_detail.reset_index(drop=True)

    st.dataframe(
        neighbor_detail,
        use_container_width=True,
        hide_index=True
    )


# 그래프 시각화
st.subheader("3. 품종별 분류 영역 시각화")

st.write(
    "배경색은 품종별 예측 영역이고, "
    "초록색 별은 사용자가 입력한 위치예요."
)

x_margin = (length_max - length_min) * 0.08
y_margin = (width_max - width_min) * 0.08

x_values = np.linspace(
    length_min - x_margin,
    length_max + x_margin,
    220
)

y_values = np.linspace(
    width_min - y_margin,
    width_max + y_margin,
    180
)

xx, yy = np.meshgrid(x_values, y_values)
grid = np.column_stack([xx.ravel(), yy.ravel()])

grid_predictions = model.predict(grid)

class_names = sorted(y.unique())
class_to_number = {
    name: i for i, name in enumerate(class_names)
}

zz = np.array([
    class_to_number[name] for name in grid_predictions
]).reshape(xx.shape)


fig, ax = plt.subplots(figsize=(10, 6))

cmap = plt.get_cmap("Pastel1", len(class_names))

ax.contourf(
    xx,
    yy,
    zz,
    levels=np.arange(-0.5, len(class_names) + 0.5, 1),
    cmap=cmap,
    alpha=0.55
)


# 품종별 기존 데이터 표시
markers = ["o", "s", "^", "D", "P"]

for i, class_name in enumerate(class_names):

    subset = df[df[TARGET].astype(str) == class_name]

    ax.scatter(
        subset["꽃잎 길이"],
        subset["꽃잎 너비"],
        label=class_name,
        s=48,
        alpha=0.85,
        marker=markers[i % len(markers)],
        edgecolors="white",
        linewidths=0.5
    )


# 가장 가까운 데이터 5개 강조
nearest = df.iloc[neighbor_indices[0]]

ax.scatter(
    nearest["꽃잎 길이"],
    nearest["꽃잎 너비"],
    s=150,
    facecolors="none",
    edgecolors="black",
    linewidths=1.8,
    label=f"가까운 이웃 {k}개"
)


# 사용자 입력값: 초록색 별
ax.scatter(
    input_length,
    input_width,
    marker="*",
    s=420,
    color="green",
    edgecolors="black",
    linewidths=0.8,
    label=f"입력값 → {prediction}",
    zorder=10
)


ax.set_xlabel("꽃잎 길이 (cm)")
ax.set_ylabel("꽃잎 너비 (cm)")
ax.set_title("꽃잎 크기에 따른 KNN 품종 분류 영역")

ax.grid(alpha=0.2)
ax.legend()
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)


# 분류 원리 설명
st.subheader("4. 어떻게 품종을 예측할까요?")

st.markdown(f"""
1. 입력한 꽃잎 길이와 너비를 기존 데이터와 비교해요.
2. 두 측정 변수의 차이를 줄이기 위해 표준화해요.
3. 입력값과 가장 가까운 데이터 **{k}개**를 찾아요.
4. 가장 많이 나타난 품종을 최종 예측 결과로 선택해요.

초록색 별 주변에 어떤 품종의 데이터가 모여 있는지,
그리고 별이 어떤 분류 영역에 위치하는지 확인해 보세요.

이번 입력값은 **{prediction}**으로 분류되었어요!
""")

st.caption(
    "참고: 꽃잎 길이와 너비 두 가지 특성만 사용한 예측 모델입니다."
)

