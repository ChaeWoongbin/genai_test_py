import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# .env 파일에서 환경 변수 로드
load_dotenv('api_key.env')

# --- 설정 및 초기화 ---

@st.cache_resource
def get_gemini_client():
    """Gemini 클라이언트를 초기화하고 캐시합니다."""
    try:
        # API 키가 환경 변수로 설정되어 있는지 확인
        if not os.getenv("GEMINI_API_KEY"):
             st.error("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
             st.stop()
        
        return genai.Client()
    except Exception as e:
        st.error(f"Gemini 클라이언트 초기화 오류: {e}")
        st.stop()
        return None # 오류 발생 시 None 반환

client = get_gemini_client()

# 페이지 설정
st.set_page_config(
    page_title="Gemini Streamlit 챗봇",
    layout="centered"
)
st.title("Gemini Streamlit 챗봇 🎈")

# 모델 선택
MODEL_NAME = "gemini-2.5-flash"

# 대화 기록 초기화
# Streamlit의 session_state를 사용하여 앱 재실행 시에도 대화 내용을 유지합니다.
if "chat_session" not in st.session_state:
    # 채팅 서비스 초기화
    st.session_state.chat_session = client.chats.create(model=MODEL_NAME)
    # 초기 대화 메시지 기록 (옵션)
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}]

# --- 대화 내용 표시 ---

# session_state에 저장된 모든 메시지를 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 사용자 입력 및 응답 생성 ---

# 사용자 입력 받기
if prompt := st.chat_input("여기에 질문을 입력하세요..."):
    # 1. 사용자 메시지를 화면에 즉시 표시하고 기록에 추가
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 챗봇 응답을 위한 자리 표시자 생성
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            message_placeholder = st.empty()
            full_response = ""

            # 3. Gemini API 호출 및 스트리밍
            try:
                # 채팅 세션을 통해 메시지 전송 및 응답 스트림 받기
                response_stream = st.session_state.chat_session.send_message_stream(prompt)
                
                for chunk in response_stream:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌") # 응답이 오는 동안 커서처럼 표시
                
                message_placeholder.markdown(full_response) # 최종 응답 출력

                # 4. 챗봇의 최종 응답을 기록에 추가
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_message = f"Gemini API 호출 중 오류가 발생했습니다: {e}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})