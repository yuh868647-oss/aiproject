
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Seoul Top 10 Tourist Spots",
    page_icon="🗺️",
    layout="wide"
)

# 서울 주요 관광지 TOP 10
places = [
    {"rank": 1, "name": "Gyeongbokgung Palace", "korean": "경복궁", "category": "역사·문화", "lat": 37.5796, "lon": 126.9770, "note": "조선 왕조의 대표 궁궐"},
    {"rank": 2, "name": "Changdeokgung Palace", "korean": "창덕궁", "category": "역사·문화", "lat": 37.5794, "lon": 126.9910, "note": "유네스코 세계문화유산"},
    {"rank": 3, "name": "Deoksugung Palace", "korean": "덕수궁", "category": "역사·문화", "lat": 37.5658, "lon": 126.9751, "note": "대한제국의 역사를 만나는 궁궐"},
    {"rank": 4, "name": "Changgyeonggung Palace", "korean": "창경궁", "category": "역사·문화", "lat": 37.5788, "lon": 126.9949, "note": "아름다운 정원이 있는 궁궐"},
    {"rank": 5, "name": "National Museum of Korea", "korean": "국립중앙박물관", "category": "박물관", "lat": 37.5239, "lon": 126.9803, "note": "한국의 역사와 문화를 만나는 박물관"},
    {"rank": 6, "name": "Jongmyo Shrine", "korean": "종묘", "category": "역사·문화", "lat": 37.5745, "lon": 126.9940, "note": "조선 왕실의 제례 공간"},
    {"rank": 7, "name": "Myeong-dong", "korean": "명동", "category": "쇼핑·음식", "lat": 37.5636, "lon": 126.9869, "note": "쇼핑과 길거리 음식의 명소"},
    {"rank": 8, "name": "N Seoul Tower", "korean": "N서울타워", "category": "전망·명소", "lat": 37.5512, "lon": 126.9882, "note": "서울의 아름다운 전경을 감상"},
    {"rank": 9, "name": "COEX & Starfield Library", "korean": "코엑스·별마당도서관", "category": "쇼핑·문화", "lat": 37.5125, "lon": 127.0588, "note": "쇼핑과 독특한 도서관 공간"},
    {"rank": 10, "name": "Dongdaemun Design Plaza", "korean": "동대문디자인플라자", "category": "건축·문화", "lat": 37.5671, "lon": 127.0095, "note": "독특한 건축물과 전시 공간"},
]

df = pd.DataFrame(places)

# 제목
st.title("🗺️ Seoul Top 10 Tourist Spots")
st.subheader("Discover the best places in Seoul!")
st.write("외국인 관광객을 위한 서울의 대표 관광지 10곳을 만나보세요.")

st.info("📍 지도에서 서울의 주요 관광지 위치를 확인할 수 있습니다.")

# 지도와 상세정보
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📍 Tourist Map")

    st.map(
        df,
        latitude="lat",
        longitude="lon",
        size=100,
        color="#E45756"
    )

with col2:
    st.subheader("🔎 Find Tourist Spots")

    category = st.selectbox(
        "관광지 종류 선택",
        ["전체"] + list(df["category"].unique())
    )

    if category == "전체":
        filtered = df
    else:
        filtered = df[df["category"] == category]

    selected = st.selectbox(
        "관광지 선택",
        filtered["name"].tolist()
    )

    place = filtered[filtered["name"] == selected].iloc[0]

    st.markdown(f"### {place['korean']}")
    st.write(f"**English:** {place['name']}")
    st.write(f"**분류:** {place['category']}")
    st.write(place["note"])

    google_url = (
        "https://www.google.com/maps/search/?api=1&query="
        + str(place["lat"])
        + ","
        + str(place["lon"])
    )

    st.link_button(
        "🌏 Google Maps에서 보기",
        google_url
    )

# 관광지 전체 목록
st.divider()
st.subheader("🏙️ Seoul Top 10")

for i in range(0, len(places), 2):
    cols = st.columns(2)

    for col, place in zip(cols, places[i:i+2]):
        with col:
            st.markdown(
                f"**{place['rank']}. {place['korean']}**"
            )
            st.caption(place["name"])
            st.write(place["note"])

# 출처
with st.expander("📚 관광지 선정 기준"):
    st.write(
        "2025년 외국인 관광객 입장객 통계와 "
        "서울시 외국인 관광객 방문 분석을 참고한 목록입니다. "
        "상위 6곳은 입장객 순위, 나머지 4곳은 추가 인기 관광지입니다."
    )

st.caption("Made with Streamlit 🧡")
