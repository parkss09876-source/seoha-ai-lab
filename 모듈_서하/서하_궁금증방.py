import streamlit as st
import google.generativeai as genai
import json
import streamlit.components.v1 as components

CHAT_LOG_FILE = "궁금증방_대화기록.json"

st.set_page_config(layout="wide")
st.title("🤔 척척박사 궁금증 해소방 4.5")

# 1. 모델 초기화 (세션 재사용 및 지식 요정 설정)
if "wisdom_model" not in st.session_state:
    genai.configure(api_key=st.secrets["API_KEY"])
    system_instruction = """
    너는 8살 서하의 '세상 모든 걸 아는 지식 요정 척척이'야. 다음 원칙을 반드시 지켜.
    1. 눈높이 설명: 8살 아이가 이해할 수 있는 쉬운 단어와 친근한 비유를 사용해.
    2. 호기심 확장: 서하가 질문한 것에서 더 나아가, 연관된 재미있는 사실을 하나씩 더 알려줘.
    3. 스스로 생각하기: 정답을 바로 다 말해주기보다, 서하가 스스로 추측해 볼 수 있도록 질문을 섞어줘.
    4. 안전한 정보: 아이에게 유익하고 따뜻한 내용의 정보를 제공해.
    5. [매우 중요] 절대 "안녕, 서하! 나는 너의 지식 요정 척척이야!" 같은 인사말을 반복하지 마. 서하의 질문에 대한 답변과 본론만 바로 말해.
    """
    st.session_state.wisdom_model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)

if "wisdom_messages" not in st.session_state:
    st.session_state.wisdom_messages = [] 

# 2. 상단: 지식 탐구 도구 (수평 배치)
st.subheader("🛠️ 지식 탐구 도구 상자")
t1, t2, t3 = st.columns(3)
with t1: st.link_button("🌍 구글 어스 (세계 여행)", "https://earth.google.com/", use_container_width=True)
with t2: st.link_button("🌌 스텔라리움 (별자리)", "https://stellarium-web.org/", use_container_width=True)
with t3: st.link_button("🔬 과학 백과 (위키키즈)", "https://kids.britannica.com/", use_container_width=True)

st.markdown("---")

# 3. 하단: 대화 영역
st.subheader("💬 척척이와 대화하기")

# 스크롤 가능한 대화 기록 영역
chat_container = st.container(height=500)
with chat_container:
    st.markdown("<div id='top-of-chat'></div>", unsafe_allow_html=True)
    
    messages = st.session_state.wisdom_messages
    pairs = []
    
    for i in range(0, len(messages), 2):
        q = messages[i]
        a = messages[i+1] if i+1 < len(messages) else None
        pairs.append((q, a))
        
    for q, a in reversed(pairs):
        with st.chat_message(q["role"]):
            st.markdown(q["content"])
        if a:
            with st.chat_message(a["role"]):
                st.markdown(a["content"])

    components.html(
        """
        <script>
            setTimeout(function() {
                var parentDoc = window.parent.document;
                var target = parentDoc.getElementById('top-of-chat');
                if (target) {
                    target.scrollIntoView({behavior: 'smooth', block: 'start'});
                }
            }, 150);
        </script>
        """,
        height=0
    )

# 4. 하단 입력창 고정
if text_prompt := st.chat_input("궁금한 걸 척척이에게 물어봐!"):
    st.session_state.wisdom_messages.append({"role": "user", "content": text_prompt})
    
    with st.spinner("척척이가 지식의 도서관을 뒤지는 중... 💭"):
        try:
            response = st.session_state.wisdom_model.generate_content(text_prompt)
            st.session_state.wisdom_messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.wisdom_messages.append({"role": "assistant", "content": "앗! 지식이 너무 많아서 정리가 조금 필요해. 1분만 기다려줄래? 🧐✨"})
    
    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.wisdom_messages, f, ensure_ascii=False, indent=4)
    st.rerun()