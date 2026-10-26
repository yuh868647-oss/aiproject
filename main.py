import streamlit as st 
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('이름을 입력해주세요!')
b=st.selectbox('좋아하는 음식을 선택해주세요!',['마라탕','마라샹궈','아이스크림'])
if st.button('인사말 생성'):
  st.write('반갑습니다!')
  st.info(a+'유하늘님! 안녕하세요!')
  st.warning(b+'마라탕을 좋아하시나봐요! 저도 좋아해요!')
  st.error('잘부탁드려요!')
  st.balloons()
