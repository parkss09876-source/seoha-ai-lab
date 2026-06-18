import streamlit as st
import google.generativeai as genai
import json

CHAT_LOG_FILE = "테스트방_대화기록.json"

# 🧪 실험실 전용 간판
st.title("🧪 요정의 실험실 (테스트 구역)")
st.markdown("---")
st.info("💡 **이곳은 새로운 기능을 마음껏 고장내며(?) 테스트해 볼 수 있는 안전한 샌드박스입니다.**")

# 🎭 테스트용 모드 전환 스위치
play_mode = st.radio(
    "테스트할 모드를 선택하세요:",
    ["🗣️ 일반 대화 모드 (수다떨기)", "💃🕺 신나는 노래 & 역할극 모드"],
    horizontal=True
)

st.markdown("---")

genai.configure(api_key=st.secrets["API_KEY"])

# 🧠 선택한 모드에 따라 AI의 뇌 구조(명령어)가 즉시 바뀝니다.
if play_mode == "🗣️ 일반 대화 모드 (수다떨기)":
    system_instruction = "너는 8살 아이 '서하'의 다정하고 활기찬 AI 조수야. 서하가 말을 걸면 아주 친절하게 대답해주고, 꼬리 질문을 던져줘."
else:
    system_instruction = """너는 8살 아이 '서하'의 신나는 댄스 파트너이자 선생님이야!
    서하가 역할극 주제나 자기가 좋아하는 노래(예: 아기 상어, 뽀로로, 반짝반짝 작은별 등)를 말하면, 그 멜로디에 맞춰 부를 수 있는 짧고 쉬운 4줄짜리 영어 가사를 만들어줘. 
    노래 가사 곳곳에 💃🕺🎵 이모티콘을 듬뿍 넣어서 서하가 춤추고 싶게 만들어주고, 이어서 그 주제에 맞는 짧은 영어 역할극 대화를 이끌어줘. 한국어 해석도 달아줘."""

model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)
stt_model = genai.GenerativeModel('gemini-2.5-flash')

# 대화 기록 초기화 로직 (모드가 바뀌면 기억을 지우고 새로 시작)
if "test_messages" not in st.session_state or "test_mode" not in st.session_state or st.session_state.test_mode != play_mode:
    st.session_state.test_mode = play_mode
    if play_mode == "🗣️ 일반 대화 모드 (수다떨기)":
        welcome_msg = "[테스트 모드 A 가동] 안녕, 서하야! 무엇이든 편하게 물어보렴."
    else:
        welcome_msg = "[테스트 모드 B 가동] 🪩 서하야, 어떤 노래의 멜로디에 맞춰서 가사를 만들어줄까? (예: '아기 상어 노래에 맞춰서 병원 놀이 만들어줘!' 라고 말해봐!)"
        st.balloons()
    st.session_state.test_messages = [{"role": "assistant", "content": welcome_msg}]

# 🎙️ 마이크 및 텍스트 입력창
st.subheader(f"마이크 테스트: {play_mode.split()[1]}")
audio_file = st.audio_input("마이크를 누르고 말해보세요!")

for message in reversed(st.session_state.test_messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if audio_file:
    audio_bytes = audio_file.read()
    if "last_processed_audio_test" not in st.session_state or st.session_state.last_processed_audio_test != audio_bytes:
        st.session_state.last_processed_audio_test = audio_bytes
        
        with st.spinner("음성 인식 테스트 중... ✍️"):
            stt_response = stt_model.generate_content([{"mime_type": "audio/wav", "data": audio_bytes}, "말하는 내용을 텍스트로만 정확히 받아적어주세요."])
            transcribed_text = stt_response.text.strip()
        
        st.session_state.test_messages.append({"role": "user", "content": f"🎙️ **{transcribed_text}**"})
        
        with st.spinner("AI가 답변을 생성하는 중... 💭"):
            response = model.generate_content(transcribed_text)
        st.session_state.test_messages.append({"role": "assistant", "content": response.text})
        
        with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.test_messages, f, ensure_ascii=False, indent=4)
        st.rerun()

if text_prompt := st.chat_input("글자로 테스트해 보세요!"):
    st.session_state.test_messages.append({"role": "user", "content": text_prompt})
    response = model.generate_content(text_prompt)
    st.session_state.test_messages.append({"role": "assistant", "content": response.text})
    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.test_messages, f, ensure_ascii=False, indent=4)
    st.rerun()