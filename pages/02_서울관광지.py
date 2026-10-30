
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Seoul Tourist Map",
    page_icon="🗺️",
    layout="wide"
)

# 서울 관광지 TOP 10
places = [
    {"rank": 1, "name": "Gyeongbokgung Palace", "korean": "경복궁", "category": "History", "lat": 37.5796, "lon": 126.9770, "description": "조선 왕조의 대표 궁궐"},
    {"rank": 2, "name": "Changdeokgung Palace", "korean": "창덕궁", "category": "History", "lat": 37.5794, "lon": 126.9910, "description": "유네스코 세계문화유산"},
    {"rank": 3, "name": "Deoksugung Palace", "korean": "덕수궁", "category": "History", "lat": 37.5658, "lon": 126.9751, "description": "대한제국의 역사를 간직한 궁궐"},
    {"rank": 4, "name": "Changgyeonggung Palace", "korean": "창경궁", "category": "History", "lat": 37.5788, "lon": 126.9949, "description": "아름다운 정원이 있는 궁궐"},
    {"rank": 5, "name": "National Museum of Korea", "korean": "국립중앙박물관", "category": "Museum", "lat": 37.5239, "lon": 126.9803, "description": "한국의 역사와 문화를 만나는 박물관"},
    {"rank": 6, "name": "Jongmyo Shrine", "korean": "종묘", "category": "History", "lat": 37.5745, "lon": 126.9940, "description": "조선 왕실의 제례 공간"},
    {"rank": 7, "name": "Myeong-dong", "korean": "명동", "category": "Shopping", "lat": 37.5636, "lon": 126.9869, "description": "쇼핑과 길거리 음식의 명소"},
    {"rank": 8, "name": "N Seoul Tower", "korean": "N서울타워", "category": "Landmark", "lat": 37.5512, "lon": 126.9882, "description": "서울의 아름다운 전경을 감상"},
    {"rank": 9, "name": "COEX & Starfield Library", "korean": "코엑스·별마당도서관", "category": "Shopping", "lat": 37.5125, "lon": 127.0588, "description": "쇼핑과 독특한 도서관 공간"},
    {"rank": 10, "name": "Dongdaemun Design Plaza", "korean": "동대문디자인플라자", "category": "Culture", "lat": 37.5671, "lon": 127.0095, "description": "독특한 건축물과 전시 공간"},
]

df = pd.DataFrame(places)

# 제목
st.title("🗺️ Seoul Top 10 Tourist Spots")
st.subheader("Discover the best places in Seoul!")
st.write("서울을 방문하는 외국인 관광객을 위한 관광 안내 지도입니다.")

st.info("📍 지도에서 관광지를 클릭해 상세 정보를 확인해 보세요!")

# 관광지 종류 필터
categories = ["All"] + sorted(df["category"].unique().tolist())
selected_category = st.selectbox(
    "🔎 Choose Tourist Category",
    categories
)

if selected_category == "All":
    filtered = df
else:
    filtered = df[df["category"] == selected_category]

# Folium 지도 생성
st.subheader("📍 Interactive Seoul Map")

m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 관광지 마커 추가
for _, place in filtered.iterrows():

    google_url = (
        "https://www.google.com/maps/search/?api=1&query="
        f"{place['lat']},{place['lon']}"
    )

    popup_html = f"""
    <div style="width:220px">
        <h4>{place['rank']}. {place['korean']}</h4>
        <b>{place['name']}</b>
        <p>{place['description']}</p>
        <a href="{google_url}" target="_blank">
            Open Google Maps
        </a>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=place["korean"],
        popup=folium.Popup(
            popup_html,
            max_width=280
        ),
        icon=folium.Icon(
            color="red",
            icon="info-sign"
        )
    ).add_to(m)

# Streamlit 화면에 지도 출력
st_folium(
    m,
    width=None,
    height=600,
    use_container_width=True,
    returned_objects=[]
)

st.caption("💡 지도 마커를 클릭하면 관광지 정보를 볼 수 있습니다.")

# 관광지 상세 정보
st.divider()
st.subheader("🌏 Tourist Information")

spot_names = [
    f"{row['rank']}. {row['korean']} - {row['name']}"
    for _, row in filtered.iterrows()
]

if spot_names:
    selected = st.selectbox(
        "관광지 선택",
        spot_names
    )

    index = spot_names.index(selected)
    place = filtered.iloc[index]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"### {place['korean']}")
        st.write(f"**English:** {place['name']}")
        st.write(f"**Category:** {place['category']}")
        st.write(place["description"])

    with col2:
        url = (
            "https://www.google.com/maps/search/?api=1&query="
            f"{place['lat']},{place['lon']}"
        )

        st.link_button(
            "🌐 Open Google Maps",
            url
        )

# 전체 관광지 목록
st.divider()
st.subheader("🏙️ Top 10 Tourist Attractions")

for i in range(0, len(places), 2):
    cols = st.columns(2)

    for col, place in zip(cols, places[i:i+2]):
        with col:
            st.markdown(
                f"**{place['rank']}. {place['korean']}**"
            )
            st.caption(place["name"])
            st.write(place["description"])

# 출처 및 안내
with st.expander("📚 About this list"):
    st.write(
        "2025년 외국인 관광객 입장 통계와 서울시 외국인 관광 분석을 "
        "참고한 관광지 목록입니다. 1~6번과 7~10번은 선정 기준이 다르므로 "
        "공식 통합 순위는 아닙니다."
    )

st.caption("Made with Streamlit + Folium 💙")
