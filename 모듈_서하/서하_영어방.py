import streamlit as st
import google.generativeai as genai
import json
import streamlit.components.v1 as components
from gtts import gTTS
import io
import re

CHAT_LOG_GEN = "영어방_일반_대화기록.json"
CHAT_LOG_STRICT = "영어방_전용_대화기록.json"

st.set_page_config(layout="wide")
st.title("🔤 반짝반짝 영어 마법방 4.5")

# 1. 두 가지 모드의 모델 초기화
if "models_loaded" not in st.session_state:
    genai.configure(api_key=st.secrets["API_KEY"])
    
    sys_gen = """
    너는 8살 서하의 '친절한 영어 여행 가이드 앨리'야.
    한국어로 질문하면 한국어로 다정하게 대답해주고, 영어에 대해 친절하게 설명해줘.
    상황에 맞는 재미있는 표현과 이모티콘을 사용해. 절대 인사말을 반복하지 마.
    """
    st.session_state.model_gen = genai.GenerativeModel('gemini-2.5-flash', system_instruction=sys_gen)
    
    sys_strict = """
    
    You are Ally, a gentle and encouraging English tutor for 8-year-old Seoha. 
    CRITICAL RULES:
    1. You MUST answer ONLY in very simple, basic English.
    2. NEVER use the Korean language. No Korean translations at all.
    3. [CORRECTION RULE]: If Seoha says something grammatically incorrect or awkward, do NOT scold or say "That is wrong." 
       Instead, reply to the content first, then naturally rephrase it correctly like this: "That's a great thought! You could also say: [Correct sentence]."
    4. Keep sentences very short and easy.
    5. Use emojis.
    6. No repetitive greetings. Start your answer directly.
    """
    st.session_state.model_strict = genai.GenerativeModel('gemini-2.5-flash', system_instruction=sys_strict)
    st.session_state.models_loaded = True

if "msg_gen" not in st.session_state: st.session_state.msg_gen = []
if "msg_strict" not in st.session_state: st.session_state.msg_strict = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None # ✨ 무한반복 방지용 상태 추가

# 2. 상단: 영어 학습 도구
st.subheader("🛠️ 영어 학습 도구 상자")
t1, t2, t3 = st.columns(3)
with t1: st.link_button("🦉 듀올링고 (Duolingo)", "https://www.duolingo.com/", use_container_width=True)
with t2: st.link_button("⭐ 스타폴 (Starfall)", "https://www.starfall.com/", use_container_width=True)
with t3: st.link_button("📺 EBSe (EBS 초등)", "https://www.ebse.co.kr/", use_container_width=True)

st.markdown("---")

tab1, tab2 = st.tabs(["💬 일반 대화방 (한국어 해설 가능)", "🚫🇰🇷 100% 영어 전용방 (English Only)"])

# ==========================================
# [탭 1] 일반 대화방
# ==========================================
with tab1:
    chat_container_gen = st.container(height=400)
    with chat_container_gen:
        st.markdown("<div id='top-gen'></div>", unsafe_allow_html=True)
        pairs_gen = []
        for i in range(0, len(st.session_state.msg_gen), 2):
            q = st.session_state.msg_gen[i]
            a = st.session_state.msg_gen[i+1] if i+1 < len(st.session_state.msg_gen) else None
            pairs_gen.append((q, a))
            
        for q, a in reversed(pairs_gen):
            with st.chat_message(q["role"]): st.markdown(q["content"])
            if a:
                with st.chat_message(a["role"]): st.markdown(a["content"])

    if text_gen := st.chat_input("앨리에게 자유롭게 물어봐!", key="input_gen"):
        st.session_state.msg_gen.append({"role": "user", "content": text_gen})
        with st.spinner("앨리가 친절하게 설명 준비 중... 💭"):
            try:
                res = st.session_state.model_gen.generate_content(text_gen)
                st.session_state.msg_gen.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.session_state.msg_gen.append({"role": "assistant", "content": f"앗! 에러가 났어요: {e}"})
        with open(CHAT_LOG_GEN, "w", encoding="utf-8") as f:
            json.dump(st.session_state.msg_gen, f, ensure_ascii=False, indent=4)
        st.rerun()

# ==========================================
# [탭 2] 100% 영어 전용방 (무한 반복 버그 수정)
# ==========================================
with tab2:
    audio_strict = st.audio_input("🎤 서하의 목소리로 앨리에게 말하기", key="audio_strict")
    text_strict = st.chat_input("Talk to Ally in English!", key="input_strict")

    chat_container_strict = st.container(height=400)
    with chat_container_strict:
        st.markdown("<div id='top-strict'></div>", unsafe_allow_html=True)
        pairs_strict = []
        for i in range(0, len(st.session_state.msg_strict), 2):
            q = st.session_state.msg_strict[i]
            a = st.session_state.msg_strict[i+1] if i+1 < len(st.session_state.msg_strict) else None
            pairs_strict.append((q, a))
            
        for idx, (q, a) in enumerate(reversed(pairs_strict)):
            with st.chat_message(q["role"]): st.markdown(q["content"])
            if a:
                with st.chat_message(a["role"]): 
                    st.markdown(a["content"])
                    # 에러 메시지일 때는 소리로 읽지 않도록 방어 코드 추가
                    if idx == 0 and "에러" not in a["content"]:
                        try:
                            clean_text = re.sub(r'[^\x00-\x7F]+', '', a["content"])
                            tts = gTTS(text=clean_text, lang='en', tld='us')
                            audio_fp = io.BytesIO()
                            tts.write_to_fp(audio_fp)
                            st.audio(audio_fp, format="audio/mp3", autoplay=True)
                        except Exception:
                            pass

    # ✨ [버그 수정 로직] 동일한 음성이 계속 처리되는 것을 막습니다.
    process_audio = False
    if audio_strict and audio_strict.getvalue() != st.session_state.last_audio:
        process_audio = True
        st.session_state.last_audio = audio_strict.getvalue()

    if text_strict or process_audio:
        if text_strict:
            st.session_state.msg_strict.append({"role": "user", "content": text_strict})
            prompt = text_strict
        elif process_audio:
            st.session_state.msg_strict.append({"role": "user", "content": "🎤 (목소리로 질문했어요!)"})
            prompt = [
                "Listen to this voice message and reply in simple English for an 8-year-old. No Korean.",
                {"mime_type": "audio/wav", "data": audio_strict.getvalue()}
            ]

        with st.spinner("Ally is listening... 💭"):
            try:
                res = st.session_state.model_strict.generate_content(prompt)
                st.session_state.msg_strict.append({"role": "assistant", "content": res.text})
            except Exception as e:
                # ✨ 무작정 덮지 않고, 정확한 에러 이유를 출력하여 디버깅을 돕습니다.
                st.session_state.msg_strict.append({"role": "assistant", "content": f"앗! 음성 처리 중 에러가 발생했어요. (상세 오류: {e})"})
        
        with open(CHAT_LOG_STRICT, "w", encoding="utf-8") as f:
            json.dump(st.session_state.msg_strict, f, ensure_ascii=False, indent=4)
        st.rerun()

components.html(
    """
    <script>
        setTimeout(function() {
            var parentDoc = window.parent.document;
            var target1 = parentDoc.getElementById('top-gen');
            if (target1) { target1.scrollIntoView({behavior: 'smooth', block: 'start'}); }
            var target2 = parentDoc.getElementById('top-strict');
            if (target2) { target2.scrollIntoView({behavior: 'smooth', block: 'start'}); }
        }, 150);
    </script>
    """,
    height=0
)