"""
================================================================================
[강의용 시각화 자료] 7단계: Gemini 봇 + 파일 검색(File Search) 구조도
================================================================================

이 코드는 "파일 검색(RAG)" 기능이 추가된 챗봇입니다.
사용자가 파일을 업로드하면, Gemini가 그 내용을 읽고 답변합니다.

[사용자 (User)]
      |
      | 1. 파일 업로드 (PDF, TXT 등)
      v
[Streamlit 앱] ---------------------------------------------------------+
|                                                                       |
|  2. 파일 저장소(FileSearchStore) 생성 및 파일 업로드                  |
|     client.file_search_stores.upload_to_file_search_store()           |
|                                                                       |
|  3. 메시지 입력 ("이 문서 요약해줘")                                  |
|                                                                       |
|  4. Gemini API 호출 (도구 포함)                                       |
|     generate_content_stream(..., config={tools: [file_search]})       |
|                                                                       |
+-----------------------------------------------------------------------+
      |
      | 5. 요청 (Request + File Context)
      v
[Google Gemini AI 서버]
      |
      | 6. 파일 검색 및 답변 생성 (RAG)
      |
      | 7. 응답 스트림 (Response Stream)
      v
[Streamlit 앱]
      |
      | 8. 답변 출력 및 근거(Citation) 표시
      v
[화면 표시]

================================================================================
"""

# 2025-1123-7_gemini_bot_plus_file_search.py
#
# [파일 검색 추가] File Search API를 연동하여 문서 기반 대화하기
#
# 실행:
# 1. pip install google-genai
# 2. streamlit run 2025-1123-7_gemini_bot_plus_file_search.py

import streamlit as st
from google import genai
from google.genai import types
import os
import time
import tempfile
import sys

# --- 1. API 키 설정 ---
with st.sidebar:
    st.subheader("🔑 Google API 키 설정")
    api_key = st.text_input(
        "Google AI Studio API Key를 입력하세요.", 
        type="password",
        help="[Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받으세요."
    )
    if not api_key:
        st.error("API 키를 입력해야 챗봇이 작동합니다.")
        st.stop()

# --- 2. Gemini 클라이언트 로드 (캐싱) ---
@st.cache_resource
def load_client(key):
    print("--- [알림] Gemini 클라이언트(Client)를 로드합니다... ---")
    try:
        client = genai.Client(api_key=key)
        print("--- 클라이언트 로드 완료 ---")
        return client
    except Exception as e:
        st.error(f"클라이언트 로드 중 오류 발생: {e}")
        st.stop()

client = load_client(api_key)
MODEL_NAME = 'gemini-2.5-flash'

# --- 3. 세션 상태 초기화 ---
if "history" not in st.session_state:
    st.session_state.history = []
    print("새로운 채팅 기록(history list)을 시작합니다.")

if "file_search_store" not in st.session_state:
    st.session_state.file_search_store = None

# --- 4. 사이드바: 파일 업로드 및 설정 ---
with st.sidebar:
    st.header("📂 파일 업로드 (File Search)")
    uploaded_files = st.file_uploader(
        "PDF, TXT 등의 파일을 업로드하세요", 
        accept_multiple_files=True
    )

    if uploaded_files and st.button("파일 처리 시작"):
        with st.spinner("파일을 Gemini에게 학습시키는 중입니다..."):
            try:
                # 1. 저장소 생성 (없으면 생성)
                if st.session_state.file_search_store is None:
                    print("--- 새 파일 저장소 생성 중 ---")
                    st.session_state.file_search_store = client.file_search_stores.create(
                        config={'display_name': f'Streamlit_Store_{int(time.time())}'}
                    )
                    print(f"저장소 생성 완료: {st.session_state.file_search_store.name}")

                # 2. 파일 업로드 및 처리
                for uploaded_file in uploaded_files:
                    # 임시 파일로 저장 (한글 파일명 오류 방지를 위해 안전한 이름 사용)
                    file_extension = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    print(f"파일 업로드 시작: {uploaded_file.name}")
                    
                    # Gemini에 업로드 (upload_to_file_search_store 사용)
                    operation = client.file_search_stores.upload_to_file_search_store(
                        file=tmp_path,
                        file_search_store_name=st.session_state.file_search_store.name,
                        config={'display_name': uploaded_file.name}
                    )
                    
                    # 처리 대기
                    while not operation.done:
                        time.sleep(1)
                        operation = client.operations.get(operation)
                    
                    print(f"파일 처리 완료: {uploaded_file.name}")
                    st.toast(f"✅ {uploaded_file.name} 학습 완료!")
                    
                    # 임시 파일 삭제
                    os.remove(tmp_path)
                
                st.success("모든 파일 처리가 완료되었습니다! 이제 질문해 보세요.")
                
            except Exception as e:
                st.error(f"파일 처리 중 오류 발생: {e}")
                print(f"파일 처리 오류: {e}")

    # 현재 연결된 저장소 표시
    if st.session_state.file_search_store:
        st.info(f"📚 연결된 저장소:\n{st.session_state.file_search_store.display_name}")

    st.divider()
    
    # --- 이미지 생성 설정 ---
    st.subheader("🎨 이미지 생성 설정")
    image_model_name = st.selectbox(
        "이미지 생성 모델 선택",
        ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"],
        index=0
    )
    
    # 이미지 생성 버튼 (사이드바) - 제거됨
    # generate_btn = st.button("🖼️ 이미지 생성 (Generate Image)")


# --- 메인 패널: 채팅 및 이미지 결과 ---

st.title("Gemini Chat")

# --- 이전 대화 기록 표시 ---
# 인덱스를 사용하여 중간에 이미지를 삽입할 수 있도록 함
for i, message in enumerate(st.session_state.history):
    role = message["role"]
    
    # 1. 이미지 메시지 처리
    if role == "image":
        with st.chat_message("ai"):
            st.image(
                message["data"], 
                caption=message["caption"],
                use_column_width=True
            )
            
    # 2. 텍스트 메시지 처리 (user/model)
    else:
        ui_role = "ai" if role == "model" else "user"
        with st.chat_message(ui_role):
            st.markdown(message["parts"][0]["text"])
            
            # AI 답변인 경우, 하단에 '이미지 생성' 버튼 추가
            if role == "model":
                # 버튼을 두 개로 나누어 배치 (단일 문맥 vs 전체 문맥)
                c1, c2 = st.columns(2)
                gen_current = c1.button("🎨 이 내용만 그리기", key=f"gen_cur_{i}")
                gen_full = c2.button("🎨 전체 맥락 그리기", key=f"gen_full_{i}")

                if gen_current or gen_full:
                    with st.spinner(f"Creating image using {image_model_name}..."):
                        try:
                            # 문맥 선택 로직
                            if gen_current:
                                # 현재 메시지(버튼이 있는 메시지)만 문맥으로 사용
                                target_context = [st.session_state.history[i]]
                            else:
                                # 처음부터 현재 메시지까지의 전체 문맥 사용
                                target_context = st.session_state.history[:i+1]

                            context_text = ""
                            for msg in target_context:
                                if msg["role"] != "image": # 이미지는 텍스트 문맥에서 제외
                                    r = "User" if msg["role"] == "user" else "AI"
                                    t = msg["parts"][0]["text"]
                                    context_text += f"{r}: {t}\n"
                            
                            # 프롬프트 생성 (교수님 화이트보드 스타일)
                            prompt_request = f"""
                            Analyze the following conversation and describe the key visual elements in a single, detailed English sentence.
                            Transform this into a professor's whiteboard image. Use diagrams, arrows, boxes, and captions to visually explain key concepts. Use colors as well.
                            
                            Conversation:
                            {context_text}
                            
                            Output ONLY the description in English.
                            """
                            
                            prompt_response = client.models.generate_content(
                                model=MODEL_NAME,
                                contents=prompt_request
                            )
                            image_description = prompt_response.text.strip()
                            
                            # 모델에 따른 이미지 내 텍스트 언어 설정
                            if "flash" in image_model_name:
                                lang_instruction = "IMPORTANT: All text, labels, and captions within the image MUST be in English."
                            else:
                                lang_instruction = "IMPORTANT: All text, labels, and captions within the image MUST be in Korean."
                            
                            # 이미지 생성
                            final_prompt = f"Create an image of {image_description}. {lang_instruction}"
                            print(f"이미지 생성 요청 ({image_model_name}): {final_prompt}")
                            
                            image_response = client.models.generate_content(
                                model=image_model_name, 
                                contents=final_prompt
                            )
                            
                            # 이미지 저장 및 표시
                            if image_response.parts:
                                for part in image_response.parts:
                                    if part.inline_data:
                                        # history에 이미지 메시지 삽입
                                        st.session_state.history.insert(i + 1, {
                                            "role": "image",
                                            "data": part.inline_data.data,
                                            "caption": f"Generated by {image_model_name}"
                                        })
                                        st.rerun() # 화면 갱신하여 이미지 표시
                                        break
                            else:
                                st.warning("이미지가 생성되지 않았습니다.")

                        except Exception as e:
                            st.error(f"이미지 생성 실패: {e}")

# --- 새 사용자 입력 처리 ---
if prompt := st.chat_input("메시지를 입력하세요..."):
    
    # 1. 사용자 메시지 표시 및 history에 추가
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.history.append({"role": "user", "parts": [{"text": prompt}]})

    # 2. Gemini의 스트리밍 응답 처리
    with st.chat_message("ai"):
        message_placeholder = st.empty()
        
        with st.spinner("Gemini가 생각 중입니다... 🤔"):
            try:
                # API 호출용 history 준비 (이미지 메시지 제외)
                api_history = [msg for msg in st.session_state.history if msg["role"] != "image"]

                # 도구 및 시스템 프롬프트 설정
                tool_config = None
                # [수정] 기본 시스템 프롬프트를 한국어로 설정하여 한국어 답변 유도
                system_instruction = "당신은 유능한 AI 어시스턴트입니다. 사용자의 질문에 대해 항상 '한국어'로 답변하세요."
                
                # 디버깅: 파일 검색 저장소 상태 확인
                print(f"DEBUG: file_search_store status: {st.session_state.get('file_search_store')}")

                if st.session_state.file_search_store:
                    # 파일 검색 도구 정의
                    tools = [
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[st.session_state.file_search_store.name]
                            )
                        )
                    ]
                    # 시스템 프롬프트 강화: 도구 사용 강제 (한국어)
                    system_instruction += " 당신에게는 사용자가 업로드한 문서를 검색할 수 있는 '파일 검색 도구(File Search tool)'가 있습니다. 사용자가 문서 내용에 대해 질문하면, 반드시 이 도구를 사용하여 정보를 찾고 답변하세요. '파일을 볼 수 없다'거나 '텍스트만 처리한다'는 말은 절대 하지 마세요."
                    
                    tool_config = types.GenerateContentConfig(
                        tools=tools,
                        system_instruction=system_instruction
                    )
                    print(f"--- 파일 검색 도구 사용: {st.session_state.file_search_store.name} ---")
                else:
                    tool_config = types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )

                # 스트리밍 요청
                response_stream = client.models.generate_content_stream(
                    model=MODEL_NAME,
                    contents=api_history, # 필터링된 history 사용
                    config=tool_config
                )
                
                full_response = ""
                
                # 스트림 청크 처리
                for chunk in response_stream:
                    chunk_text = chunk.text if hasattr(chunk, 'text') and chunk.text else ""
                    if chunk_text:
                        full_response += chunk_text
                        message_placeholder.markdown(full_response + "▌")
                
                # 최종 응답 표시
                message_placeholder.markdown(full_response)
                print(f"스트리밍 응답 완료. 총 길이: {len(full_response)}")

                # history에 추가
                st.session_state.history.append({
                    "role": "model",
                    "parts": [{"text": full_response}]
                })
                
                # --- 버튼 추가 (방금 생성된 메시지용) ---
                # 주의: 여기서 버튼을 클릭하면 rerun이 발생하고, 
                # 위쪽의 for loop에서 동일한 key를 가진 버튼이 클릭된 것으로 처리되어 로직이 실행됨.
                i = len(st.session_state.history) - 1
                c1, c2 = st.columns(2)
                c1.button("🎨 이 내용만 그리기", key=f"gen_cur_{i}")
                c2.button("🎨 전체 맥락 그리기", key=f"gen_full_{i}")
                    
            except Exception as e:
                st.error(f"응답 생성 중 오류: {e}")
                print(f"오류 상세: {e}")
                import traceback
                traceback.print_exc()
