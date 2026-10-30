
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from urllib.parse import quote

st.set_page_config(
    page_title="Seoul 1 Night 2 Days Tour",
    page_icon="🗺️",
    layout="wide"
)

def google_maps(query):
    return "https://www.google.com/maps/search/?api=1&query=" + quote(query)


# 관광지 TOP 10
spots = [
    {"day": "1일차", "time": "09:00–10:15", "name": "경복궁", "english": "Gyeongbokgung Palace", "lat": 37.5796, "lon": 126.9770, "stay": "1시간 15분", "detail": "조선 왕조의 대표 궁궐. 근정전과 경회루 주변을 관람합니다.", "move": "일정 시작"},
    {"day": "1일차", "time": "10:40–11:20", "name": "덕수궁", "english": "Deoksugung Palace", "lat": 37.5658, "lon": 126.9751, "stay": "40분", "detail": "대한제국의 역사를 간직한 궁궐과 돌담길을 둘러봅니다.", "move": "경복궁에서 도보·대중교통 약 20~25분"},
    {"day": "1일차", "time": "11:50–12:40", "name": "창덕궁", "english": "Changdeokgung Palace", "lat": 37.5794, "lon": 126.9910, "stay": "50분", "detail": "유네스코 세계유산 궁궐입니다. 후원은 별도 예약·관람시간 확인이 필요합니다.", "move": "덕수궁에서 대중교통 약 20~25분"},
    {"day": "1일차", "time": "13:50–14:25", "name": "종묘", "english": "Jongmyo Shrine", "lat": 37.5745, "lon": 126.9940, "stay": "35분", "detail": "조선 왕실의 제례 공간으로 유네스코 세계유산입니다.", "move": "인사동 점심 장소에서 도보·대중교통 약 10~15분"},
    {"day": "1일차", "time": "14:40–15:25", "name": "창경궁", "english": "Changgyeonggung Palace", "lat": 37.5788, "lon": 126.9949, "stay": "45분", "detail": "전통 궁궐 건축과 정원을 감상합니다.", "move": "종묘에서 도보 약 10~15분"},
    {"day": "1일차", "time": "15:55–16:45", "name": "동대문디자인플라자", "english": "Dongdaemun Design Plaza (DDP)", "lat": 37.5671, "lon": 127.0095, "stay": "50분", "detail": "독특한 곡선형 건축물과 디자인 전시 공간을 둘러봅니다.", "move": "창경궁에서 대중교통·택시 약 15~20분"},
    {"day": "1일차", "time": "17:15–19:00", "name": "명동", "english": "Myeong-dong", "lat": 37.5636, "lon": 126.9869, "stay": "1시간 45분", "detail": "쇼핑거리와 다양한 먹거리를 즐기며 1일차를 마무리합니다.", "move": "DDP에서 대중교통 약 15~20분"},
    {"day": "2일차", "time": "09:00–10:30", "name": "N서울타워", "english": "N Seoul Tower", "lat": 37.5512, "lon": 126.9882, "stay": "1시간 30분", "detail": "남산에서 서울 전경을 감상합니다. 케이블카·순환버스 운행을 확인하세요.", "move": "명동 숙소에서 남산 이동"},
    {"day": "2일차", "time": "11:15–12:45", "name": "국립중앙박물관", "english": "National Museum of Korea", "lat": 37.5239, "lon": 126.9803, "stay": "1시간 30분", "detail": "한국의 역사와 예술을 만날 수 있는 대표 박물관입니다.", "move": "남산에서 대중교통·택시 약 25~35분"},
    {"day": "2일차", "time": "14:15–17:30", "name": "코엑스·별마당도서관", "english": "COEX & Starfield Library", "lat": 37.5125, "lon": 127.0588, "stay": "3시간 15분", "detail": "별마당도서관과 코엑스몰을 둘러보고 쇼핑·휴식을 즐깁니다.", "move": "국립중앙박물관에서 대중교통 약 30~40분"},
]


# 식당 추천
meals = [
    {
        "day": "1일차",
        "time": "08:00–08:50",
        "meal": "아침",
        "name": "이삭토스트 경복궁역점",
        "area": "경복궁역·서촌",
        "why": "경복궁 입장 전에 빠르게 아침을 먹기 좋은 토스트 전문점입니다.",
        "link": google_maps("이삭토스트 경복궁역점 서울")
    },
    {
        "day": "1일차",
        "time": "12:45–13:40",
        "meal": "점심",
        "name": "인사도담",
        "area": "인사동",
        "why": "창덕궁에서 종묘로 이동하는 동선에 있는 한식당입니다.",
        "link": google_maps("인사도담 서울 인사동")
    },
    {
        "day": "1일차",
        "time": "18:00–19:00",
        "meal": "저녁",
        "name": "명동교자",
        "area": "명동",
        "why": "명동 관광을 마친 뒤 칼국수와 만두 등으로 저녁을 먹기 편리합니다.",
        "link": google_maps("명동교자 본점 서울")
    },
    {
        "day": "2일차",
        "time": "08:00–08:45",
        "meal": "아침",
        "name": "미성옥",
        "area": "명동",
        "why": "이른 시간부터 운영하는 설렁탕 식당으로 남산 이동 전 식사하기 좋습니다.",
        "link": google_maps("미성옥 명동 설렁탕 서울")
    },
    {
        "day": "2일차",
        "time": "12:50–13:50",
        "meal": "점심",
        "name": "나무와",
        "area": "이촌동·국립중앙박물관 주변",
        "why": "박물관 관람 후 가까운 이촌동에서 식사하고 코엑스로 이동합니다.",
        "link": google_maps("나무와 이촌동 서울")
    },
    {
        "day": "2일차",
        "time": "17:30–19:00",
        "meal": "저녁",
        "name": "플랜튜드 코엑스점",
        "area": "코엑스몰",
        "why": "코엑스몰 안에 있는 비건 식당으로 마지막 관광 후 이동 부담이 적습니다.",
        "link": google_maps("플랜튜드 코엑스점 서울")
    },
]


# 호텔 추천
hotels = [
    {
        "name": "솔라리아 니시테츠 호텔 서울 명동",
        "why": "명동 중심에 있어 1일차 일정을 마친 뒤 이동이 편리합니다.",
        "link": google_maps("Solaria Nishitetsu Hotel Seoul Myeongdong")
    },
    {
        "name": "호텔 미드시티 명동",
        "why": "명동·을지로 사이의 중심 입지로 대중교통 이용에 편리합니다.",
        "link": google_maps("Hotel Midcity Myeongdong Seoul")
    },
    {
        "name": "호텔 그레이스리 서울",
        "why": "시청역과 가까워 명동 및 도심 관광지 이동에 편리합니다.",
        "link": google_maps("Hotel Gracery Seoul")
    },
]


# 메인 화면
st.title("🗺️ 서울 주요 관광지 TOP 10 | 1박 2일")
st.subheader("오전 9시부터 오후 7시까지 즐기는 서울 여행")
st.write("관광지 지도, 시간표, 식당과 호텔 추천 링크를 한 페이지에서 확인하세요.")

st.warning(
    "일정이 촘촘한 압축 코스입니다. 특히 1일차에는 궁궐 4곳과 DDP·명동을 방문하므로 "
    "실제 이동 상황에 따라 관람 시간을 줄이거나 일부 장소를 다음 방문으로 미루는 것이 좋습니다."
)

st.info(
    "궁궐·종묘는 휴관일과 관람 방식이 서로 다릅니다. 방문 날짜를 정한 뒤 공식 운영시간, "
    "휴관일, 입장 마감 및 창덕궁 후원 예약 여부를 반드시 확인하세요."
)


# Folium 지도
st.subheader("📍 관광지와 식사 장소 지도")

map_choice = st.radio(
    "지도에 표시할 일정",
    ["전체", "1일차", "2일차"],
    horizontal=True
)

map_obj = folium.Map(
    location=[37.5665, 126.9900],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)

day_colors = {
    "1일차": "blue",
    "2일차": "green"
}


# 하루별 관광지 이동 순서 선으로 표시
for route_day, route_color in [
    ("1일차", "#2878B5"),
    ("2일차", "#24965A")
]:
    route_spots = [
        x for x in spots if x["day"] == route_day
    ]

    if map_choice == "전체" or map_choice == route_day:
        folium.PolyLine(
            [(x["lat"], x["lon"]) for x in route_spots],
            color=route_color,
            weight=4,
            opacity=0.75,
            tooltip=f"{route_day} 관광 순서"
        ).add_to(map_obj)


# 관광지 마커
for s in spots:

    if map_choice != "전체" and s["day"] != map_choice:
        continue

    popup = f"""
    <div style="width:245px">
      <h4>{s['day']} · {s['time']}</h4>
      <b>{s['name']}</b><br>{s['english']}
      <p>{s['detail']}</p>
      <a href="{google_maps(s['english'] + ' Seoul')}" target="_blank">
        Google Maps 길찾기 ↗
      </a>
    </div>
    """

    folium.Marker(
        [s["lat"], s["lon"]],
        tooltip=f"{s['day']} {s['time']} | {s['name']}",
        popup=folium.Popup(popup, max_width=290),
        icon=folium.Icon(
            color=day_colors[s["day"]],
            icon="camera",
            prefix="fa"
        )
    ).add_to(map_obj)


# 식당 위치 마커
meal_pins = [
    ("1일차", "아침 · 이삭토스트", 37.5775, 126.9725),
    ("1일차", "점심 · 인사도담", 37.5748, 126.9855),
    ("1일차", "저녁 · 명동교자", 37.5628, 126.9858),
    ("2일차", "아침 · 미성옥", 37.5637, 126.9858),
    ("2일차", "점심 · 나무와", 37.5215, 126.9730),
    ("2일차", "저녁 · 플랜튜드", 37.5125, 127.0588),
]

for day, label, lat, lon in meal_pins:

    if map_choice != "전체" and day != map_choice:
        continue

    folium.Marker(
        [lat, lon],
        tooltip=label,
        popup=label + " (대략적인 위치)",
        icon=folium.Icon(
            color="orange",
            icon="cutlery",
            prefix="fa"
        )
    ).add_to(map_obj)


# 지도 출력
st_folium(
    map_obj,
    use_container_width=True,
    height=590,
    returned_objects=[]
)

st.caption(
    "파란 마커/선은 1일차, 초록 마커/선은 2일차 관광지, "
    "주황 마커는 식사 장소입니다. 식당 좌표는 지역 기준의 대략적인 표시입니다."
)


# 일정표
st.subheader("🗓️ 지도 아래에서 보는 1박 2일 일정표")

for day in ["1일차", "2일차"]:

    st.markdown(f"### {day}")

    records = []

    # 식사 일정
    for meal in meals:

        if meal["day"] == day:
            records.append({
                "시간": meal["time"],
                "구분": f"🍽️ {meal['meal']}",
                "장소": meal["name"],
                "지역·설명": f"{meal['area']} — {meal['why']}",
                "링크": meal["link"]
            })

    # 관광 일정
    for s in spots:

        if s["day"] == day:
            records.append({
                "시간": s["time"],
                "구분": "📍 관광",
                "장소": s["name"],
                "지역·설명": f"{s['detail']} / 이동: {s['move']}",
                "링크": google_maps(s["english"] + " Seoul")
            })

    records.sort(key=lambda r: r["시간"])

    st.dataframe(
        pd.DataFrame(records),
        use_container_width=True,
        hide_index=True,
        column_config={
            "링크": st.column_config.LinkColumn(
                "지도 링크",
                display_text="지도 열기 ↗"
            )
        }
    )


# 식당 추천 카드
st.subheader("🍽️ 식당 추천 및 링크")

st.write(
    "아래 식당은 일정 동선에 맞춰 고른 예시입니다. "
    "방문 당일 영업시간·휴무·메뉴·대기 여부를 링크에서 확인하세요."
)

for day in ["1일차", "2일차"]:

    st.markdown(f"**{day} 식사 장소**")

    day_meals = [
        x for x in meals if x["day"] == day
    ]

    cols = st.columns(3)

    for col, meal in zip(cols, day_meals):

        with col:

            with st.container(border=True):

                st.markdown(
                    f"**{meal['meal']} · {meal['time']}**"
                )

                st.markdown(f"### {meal['name']}")

                st.caption(meal["area"])

                st.write(meal["why"])

                st.link_button(
                    "식당 위치·후기 보기 ↗",
                    meal["link"],
                    use_container_width=True
                )


# 호텔 추천
st.subheader("🏨 호텔 추천 및 링크")

st.write(
    "명동·을지로는 1일차 명동 일정 후 쉬기 좋고, "
    "2일차 남산과 도심 이동에도 편리한 숙박 지역입니다."
)

hotel_cols = st.columns(3)

for col, hotel in zip(hotel_cols, hotels):

    with col:

        with st.container(border=True):

            st.markdown(f"**{hotel['name']}**")

            st.write(hotel["why"])

            st.link_button(
                "호텔 위치·정보 보기 ↗",
                hotel["link"],
                use_container_width=True
            )

st.caption(
    "호텔 가격과 객실 가능 여부는 날짜·인원에 따라 달라집니다. "
    "미성년자는 숙박업소별 보호자 동의 및 투숙 규정이 다르므로 "
    "보호자와 함께 예약 전에 확인하세요."
)


# 여행 안내
with st.expander("📌 여행 전 꼭 확인할 사항"):

    st.markdown("""
    1. **궁궐 휴관일:** 경복궁·창덕궁·덕수궁·창경궁과 종묘의 휴관일 및 관람 방식은 서로 다릅니다.
    2. **창덕궁 후원:** 후원 관람은 별도 예약과 지정 시간이 필요할 수 있어 기본 일정에는 포함하지 않았습니다.
    3. **이동:** 지도 경로는 관광 순서를 시각화한 것이며 실제 도로 경로가 아닙니다. 네이버지도·카카오맵으로 대중교통과 도보 길찾기를 확인하세요.
    4. **식당:** 식당 링크는 지도 검색 링크입니다. 당일 영업시간, 메뉴, 가격, 대기 상황을 확인하세요.
    5. **호텔:** 숙박 날짜와 인원을 입력해 가격·객실·취소 조건을 비교하세요.
    6. **시간 관리:** 1일차가 특히 빠듯합니다. 대기나 이동 지연이 생기면 궁궐 관람 시간을 조정하세요.
    """)


st.markdown(
    "참고: 서울시 공식 관광 안내의 추천 코스와 관광지 정보를 참고해 구성했습니다. "
    "[서울 공식 관광 가이드](https://english.visitseoul.net/) · "
    "[서울 관광 안내 코스](https://english.seoul.go.kr/)"
)

st.caption("Made with Streamlit + Folium 💙")
