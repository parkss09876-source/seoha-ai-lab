import streamlit as st
import google.generativeai as genai
import json
import os

DATA_FILE = "통신_창고.json"
CHAT_LOG_FILE = "궁금증방_대화기록.json"

st.title("💡 무엇이든 물어보세요! (궁금증 해소방)")
st.markdown("---")

# 1. 모델 초기화 최적화 (세션에 저장하여 재사용)
if "genai_model" not in st.session_state:
    genai.configure(api_key=st.secrets["API_KEY"])
    # 모델을 한 번만 생성하여 세션에 보관합니다.
    st.session_state.genai_model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction="너는 8살 아이 '서하'의 모든 궁금증을 풀어주는 다정하고 똑똑한 요정 '코스모'야. 우주, 과학, 역사, 인문, 사회, 일상생활 등 서하가 무엇을 묻든 아주 친절하고 알기 쉽게 대답해 줘. 단, 정답을 한 번에 주지 말고 서하가 스스로 생각하고 추리할 수 있도록 재미있는 힌트와 소크라테스식 꼬리 질문을 던져줘."
    )
    # STT용 모델도 함께 저장
    st.session_state.stt_model = genai.GenerativeModel('gemini-2.5-flash')

# 할아버지 전갈 표시
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        stored_data = json.load(f)
        grandpa_msg = stored_data.get("grandpa_message", "")
    if grandpa_msg:
        st.success(f"👴 **할아버지의 실시간 응원 전갈:**\n\n {grandpa_msg}")

if "qna_messages" not in st.session_state:
    st.session_state.qna_messages = [{"role": "assistant", "content": "안녕, 서하야! 나는 무엇이든 다 알고 있는 요정 '코스모'야. 오늘 어떤 것이 가장 궁금해?"}]

st.subheader("🗣️ 마이크로 코스모에게 물어보기")
audio_file = st.audio_input("마이크를 누르고 말씀하세요!")
st.markdown("---")

# 대화 기록 표시
for message in reversed(st.session_state.qna_messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 음성 입력 처리
if audio_file:
    audio_bytes = audio_file.read()
    if "last_processed_audio_qna" not in st.session_state or st.session_state.last_processed_audio_qna != audio_bytes:
        st.session_state.last_processed_audio_qna = audio_bytes
        
        with st.spinner("서하의 목소리를 예쁜 글로 적고 있어요... ✍️"):
            # 저장된 세션 모델 사용
            stt_response = st.session_state.stt_model.generate_content([{"mime_type": "audio/wav", "data": audio_bytes}, "말하는 내용을 텍스트로만 정확히 받아적어주세요."])
            transcribed_text = stt_response.text.strip()
        
        st.session_state.qna_messages.append({"role": "user", "content": f"🎙️ **{transcribed_text}**"})
        
        with st.spinner("코스모가 요정의 백과사전을 찾아보고 있어... 📖"):
            # 저장된 세션 모델 사용
            response = st.session_state.genai_model.generate_content(transcribed_text)
            st.session_state.qna_messages.append({"role": "assistant", "content": response.text})
        
        with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.qna_messages, f, ensure_ascii=False, indent=4)
        st.rerun()

# 텍스트 입력 처리
if text_prompt := st.chat_input("글자로 물어봐도 좋아요!"):
    st.session_state.qna_messages.append({"role": "user", "content": text_prompt})
    # 저장된 세션 모델 사용
    response = st.session_state.genai_model.generate_content(text_prompt)
    st.session_state.qna_messages.append({"role": "assistant", "content": response.text})
    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.qna_messages, f, ensure_ascii=False, indent=4)
    st.rerun()