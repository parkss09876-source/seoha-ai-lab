import streamlit as st
import google.generativeai as genai
import json
import streamlit.components.v1 as components

CHAT_LOG_FILE = "수학방_대화기록.json"

st.set_page_config(layout="wide")
st.title("🧮 말랑말랑 마법 수학방 4.5")

# 1. 모델 초기화 (세션 재사용 및 강력한 금지 명령어)
if "math_model" not in st.session_state:
    genai.configure(api_key=st.secrets["API_KEY"])
    system_instruction = """
    너는 8살 서하의 '수학적 상상력 요정 큐비'야. 다음 원칙을 반드시 지켜.
    1. 시각화(깨봉수학): 숫자를 무조건 그림(이모티콘)으로 번역해. 덧셈/뺄셈/곱셈/나눗셈을 모두 시각적으로 설명해.
    2. 문제 풀이 튜터: 서하의 요청에 따라 문제를 내고 채점해. 틀리면 다시 그림 힌트를 줘.
    3. 상호작용: 항상 서하의 생각을 묻고, 스스로 깨닫게 유도해.
    4. 도구 안내: 개념이 어려우면 지오지브라, Polypad, 구슬 도구를 활용하게 가이드해 줘.
    5. [매우 중요] 절대 "안녕, 서하! 나는 너의 수학적 상상력 요정 큐비야!" 같은 인사말을 반복하지 마. 서하의 질문에 대한 답변과 본론만 바로 말해.
    """
    st.session_state.math_model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)

if "math_messages" not in st.session_state:
    st.session_state.math_messages = [] 

# 2. 상단: 수학 학습 도구 (수평 배치)
st.subheader("🛠️ 수학 학습 도구 상자")
t1, t2, t3 = st.columns(3)
with t1: st.link_button("🎨 도형 실험실 (지오지브라)", "https://www.geogebra.org/geometry", use_container_width=True)
with t2: st.link_button("🍕 분수/수 타일 (Polypad)", "https://mathigon.org/polypad", use_container_width=True)
with t3: st.link_button("🧮 구슬 도구 (Number Rack)", "https://apps.mathlearningcenter.org/number-rack/", use_container_width=True)

st.markdown("---")

# 3. 하단: 대화 영역
st.subheader("💬 큐비와 대화하기")

# 스크롤 가능한 대화 기록 영역
chat_container = st.container(height=500)
with chat_container:
    # ✨ [핵심 수정] 대화창 맨 꼭대기에 보이지 않는 깃발(투명 앵커)을 꽂습니다.
    st.markdown("<div id='top-of-chat'></div>", unsafe_allow_html=True)
    
    messages = st.session_state.math_messages
    pairs = []
    
    # 질문(User)과 답변(Assistant)을 한 세트(Pair)로 묶기
    for i in range(0, len(messages), 2):
        q = messages[i]
        a = messages[i+1] if i+1 < len(messages) else None
        pairs.append((q, a))
        
    # 최신 대화 세트가 맨 위로 오도록 역순으로 출력
    for q, a in reversed(pairs):
        with st.chat_message(q["role"]):
            st.markdown(q["content"])
        if a:
            with st.chat_message(a["role"]):
                st.markdown(a["content"])

    # ✨ [핵심 수정] 자바스크립트가 무조건 저 'top-of-chat' 깃발을 쳐다보게 만듭니다.
    components.html(
        """
        <script>
            setTimeout(function() {
                var parentDoc = window.parent.document;
                // 투명 깃발의 ID를 정확히 찾아냅니다.
                var target = parentDoc.getElementById('top-of-chat');
                if (target) {
                    // 깃발 위치로 화면을 강제 이동시킵니다.
                    target.scrollIntoView({behavior: 'smooth', block: 'start'});
                }
            }, 150);
        </script>
        """,
        height=0
    )

# 4. 하단 입력창 고정
if text_prompt := st.chat_input("큐비에게 질문하세요!"):
    st.session_state.math_messages.append({"role": "user", "content": text_prompt})
    
    with st.spinner("큐비가 열심히 생각 중... 💭"):
        try:
            response = st.session_state.math_model.generate_content(text_prompt)
            st.session_state.math_messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.math_messages.append({"role": "assistant", "content": "앗! 큐비가 마법 계산을 너무 많이 해서 잠깐 쉬고 싶대. 1분만 기다려줄래? 🧮✨"})
    
    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.math_messages, f, ensure_ascii=False, indent=4)
    st.rerun()