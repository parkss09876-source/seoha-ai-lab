import streamlit as st

st.set_page_config(page_title="서하 AI 연구소", page_icon="🚀", layout="wide")

# 1. 방 이름표 등록 (보물상자 방 추가됨!)
qna_room = st.Page("서하_궁금증방.py", title="💡 궁금증 해소방", icon="💡")
english_room = st.Page("서하_영어방.py", title="🔤 마법 영어 기지", icon="🔤")
math_room = st.Page("서하_수학방.py", title="🧮 마법 수학방", icon="🧮") 
treasure_room = st.Page("서하_보물상자.py", title="🎁 마법 보물상자", icon="🎁") # <-- 보물상자 방 추가!
test_room = st.Page("서하_테스트방.py", title="🧪 요정의 실험실 (테스트)", icon="🧪")
admin_room = st.Page("모듈_할아버지/할아버지_상황실.py", title="👴 할아버지 관제탑", icon="🔒")

# 2. 엘리베이터 메뉴판 조립
pg = st.navigation(
    {
        "🚀 탐험 구역": [qna_room, english_room, math_room, treasure_room], # 탐험 구역에 보물상자 배치
        "🛠️ 개발자 구역": [test_room],
        "⚙️ 관리자 구역": [admin_room]
    }
)

pg.run()