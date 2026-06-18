import streamlit as st
import google.generativeai as genai
import json

CHAT_LOG_FILE = "영어방_대화기록.json"

st.set_page_config(layout="wide")
st.title("🔤 반짝반짝 마법 영어방 1.3 🧚‍♀️")

# 1. 모델 초기화 최적화 (세션에 저장하여 재사용)
if "english_model" not in st.session_state:
    genai.configure(api_key=st.secrets["API_KEY"])
    system_instruction = """
    너는 8살 서하의 친절한 '영어 마법 요정 엘리(Elly)'야. 다음 원칙을 반드시 지켜.
    1. 눈높이 대화: 서하가 아주 쉬운 영어나 한글로 말해도 친절하게 대답해 줘. 
    2. 이중 언어 & 미국식 발음: 영어 단어나 문장을 알려줄 때는 반드시 읽는 방법(한국어 발음)과 뜻을 이모티콘과 함께 설명해 줘. 
       **중요: 발음을 한글로 적어줄 때는 한국 정규 교육과정의 '미국식 표준 영어'를 기준으로 부드럽게 적어줘.**
       (예: Water -> [워러/워터] 💧, Rabbit -> [래빗] 🐰, Tomato -> [토메이로] 🍅)
    3. 칭찬 요정: 서하가 영어를 한 마디라도 쓰면 폭풍 칭찬을 해줘.
    4. 도구 안내: 오른쪽 도구 상자들을 어떻게 활용하면 재밌는지 가이드해 줘.
    """
    st.session_state.english_model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)

if "english_messages" not in st.session_state:
    st.session_state.english_messages = [{"role": "assistant", "content": "Hello, Seoha! 안녕 서하야! 나는 영어 요정 엘리야! 오른쪽 버튼을 눌러서 재밌는 영어 놀이를 시작해볼까?"}]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💬 엘리와 영어로 수다떨기")
    # 대화 기록 표시
    for message in reversed(st.session_state.english_messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if text_prompt := st.chat_input("엘리에게 한국어나 영어로 말해보세요!"):
        st.session_state.english_messages.append({"role": "user", "content": text_prompt})
        with st.spinner("엘리가 영어 마법을 준비 중... ✨"):
            try:
                # 세션에 저장된 모델 사용
                response = st.session_state.english_model.generate_content(text_prompt)
                st.session_state.english_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.session_state.english_messages.append({"role": "assistant", "content": "앗! 엘리가 마법을 너무 많이 써서 조금 지쳤어. 딱 1분만 기다렸다가 다시 말해줄래? 🧚‍♀️✨"})
        
        with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.english_messages, f, ensure_ascii=False, indent=4)
        st.rerun()

with col2:
    st.subheader("🛠️ 서하의 영어 탐험 도구")
    st.info("버튼을 누르면 재미있는 영어 세상이 열립니다!")
    
    st.link_button("🦉 듀올링고 (Duolingo) - 게임처럼 재밌는 영어", "https://www.duolingo.com/")
    st.link_button("⭐ 스타폴 (Starfall) - 파닉스 노래 놀이터", "https://www.starfall.com/")
    st.link_button("📺 EBSe (EBS 초등) - 국가대표 영어 방송", "https://www.ebse.co.kr/")