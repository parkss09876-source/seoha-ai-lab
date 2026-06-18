import streamlit as st
import json
import os
from datetime import datetime

# --- 1. 초기 설정: 데이터 저장소 준비 ---
DATA_FILE = "보물상자_데이터.json"
IMAGE_DIR = "images"

# 이미지를 저장할 폴더가 없으면 자동으로 만들기
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# 데이터를 저장할 JSON 파일이 없으면 빈 형태로 만들기
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# 화면 넓게 쓰기
st.set_page_config(layout="wide")
st.title("🎁 서하의 마법 보물상자 방")

col1, col2 = st.columns([1, 1])

# --- 왼쪽 화면: 📥 보물 등록하기 (입력 영역) ---
with col1:
    st.subheader("📥 오늘의 보물 등록하기")
    st.info("서하의 소중한 기억과 생각들을 이곳에 담아주세요!")
    
    with st.form("treasure_form", clear_on_submit=True):
        # 지휘관님의 요청대로 '예쁜 글쓰기'로 카테고리 변경
        category = st.radio(
            "어떤 보물인가요?",
            ["🎨 그림일기 사진", "📝 짧은 일기", "✍️ 예쁜 글쓰기", "🦖 좋아하는 캐릭터"],
            horizontal=True
        )
        
        title = st.text_input("보물의 이름 (제목을 지어주세요)")
        content = st.text_area("내용을 적어주세요 (사진만 올릴 때는 비워둬도 괜찮아요)")
        uploaded_file = st.file_uploader("사진을 올려주세요 (선택사항)", type=["jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button("✨ 보물상자에 쏙! 넣기")
        
        if submitted and title:
            # 1. 현재 날짜와 시간 가져오기
            now = datetime.now()
            date_str = now.strftime("%Y년 %m월 %d일")
            
            image_path = ""
            if uploaded_file is not None:
                # 2. 이미지 파일 이름이 겹치지 않게 시간표시를 붙여서 폴더에 저장
                file_name = f"{now.strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                image_path = os.path.join(IMAGE_DIR, file_name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            # 3. JSON에 저장할 뼈대(딕셔너리) 만들기
            new_treasure = {
                "date": date_str,
                "category": category,
                "title": title,
                "content": content,
                "image_path": image_path
            }
            
            # 4. 기존 데이터 불러와서 새 보물 추가하고 다시 저장하기
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            data.append(new_treasure)
            
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            st.success("🎉 마법 보물상자에 안전하게 저장되었어요!")
            st.rerun() # 저장 후 화면 깔끔하게 새로고침

# --- 오른쪽 화면: 🔮 보물 상자 열어보기 (전시 영역) ---
with col2:
    st.subheader("🔮 보물 상자 열어보기")
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if not data:
        st.write("아직 저장된 보물이 없어요. 왼쪽에서 첫 번째 보물을 넣어주세요!")
    else:
        # 최근에 등록한 보물이 맨 위에 보이도록 목록을 뒤집어서(reversed) 보여주기
        for item in reversed(data):
            with st.container():
                st.markdown(f"### {item['title']}")
                st.caption(f"🏷️ {item['category']} | 🗓️ {item['date']}")
                
                # 사진이 있으면 큼직하게 보여주기
                if item["image_path"] and os.path.exists(item["image_path"]):
                    st.image(item["image_path"], use_container_width=True)
                
                # 글 내용이 있으면 예쁜 박스 안에 보여주기
                if item["content"]:
                    st.info(item["content"])
                
                st.markdown("---")