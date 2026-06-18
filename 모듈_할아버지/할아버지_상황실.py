import streamlit as st
import json
import os

# --- 설정 및 데이터 경로 ---
TREASURE_FILE = "보물상자_데이터.json"
ENG_FILE = "영어방_대화기록.json"
MATH_FILE = "수학방_대화기록.json"

st.title("👴 할아버지 관제탑 (상황실)")
st.info("서하의 보물상자 현황과 각 방의 요정 대화 기록을 한눈에 확인합니다.")
st.markdown("---")

# 3개의 탭으로 화면을 깔끔하게 분리
tab1, tab2, tab3 = st.tabs(["🎁 보물상자 현황", "🔤 영어방 요정 대화", "🧮 수학방 요정 대화"])

# --- [탭 1] 보물상자 현황 ---
with tab1:
    st.subheader("📊 보물상자 현황판")
    if os.path.exists(TREASURE_FILE):
        with open(TREASURE_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    if not data:
        st.write("아직 등록된 보물이 없습니다.")
    else:
        st.metric("총 등록된 보물 수", f"{len(data)}개")
        for i, item in enumerate(reversed(data)):
            with st.expander(f"[{item.get('date', '')}] {item.get('title', '')} - {item.get('category', '')}", expanded=(i==0)):
                if item.get("image_path") and os.path.exists(item.get("image_path")):
                    st.image(item["image_path"], width=400)
                if item.get("content"):
                    st.info(item["content"])

# --- [탭 2] 영어방 대화 기록 ---
with tab2:
    st.subheader("💬 영어 요정 엘리와의 대화")
    if os.path.exists(ENG_FILE):
        with open(ENG_FILE, "r", encoding="utf-8") as f:
            try:
                eng_data = json.load(f)
                for msg in eng_data:
                    # 요정의 첫 인사말은 제외하고 실제 대화만 출력
                    if msg["role"] == "user":
                        st.markdown(f"**👦 서하:** {msg['content']}")
                    else:
                        st.markdown(f"**🧚‍♀️ 엘리:** {msg['content']}")
                    st.markdown("---")
            except json.JSONDecodeError:
                st.write("기록을 읽을 수 없습니다.")
    else:
        st.write("아직 대화 기록이 없습니다.")

# --- [탭 3] 수학방 대화 기록 ---
with tab3:
    st.subheader("💬 수학 요정 큐비와의 대화")
    if os.path.exists(MATH_FILE):
        with open(MATH_FILE, "r", encoding="utf-8") as f:
            try:
                math_data = json.load(f)
                for msg in math_data:
                    if msg["role"] == "user":
                        st.markdown(f"**👦 서하:** {msg['content']}")
                    else:
                        st.markdown(f"**🧚‍♂️ 큐비:** {msg['content']}")
                    st.markdown("---")
            except json.JSONDecodeError:
                st.write("기록을 읽을 수 없습니다.")
    else:
        st.write("아직 대화 기록이 없거나 파일이 연동되지 않았습니다.")