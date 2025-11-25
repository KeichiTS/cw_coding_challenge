import streamlit as st
import requests
import os

st.set_page_config(page_title="InfinitePay Agent Swarm", page_icon="https://www.rw-designer.com/icon-view/20374.png")
st.title("InfinitePay Agent Swarm")

API_URL = os.getenv("API_URL", "http://localhost:8000/api/chat") 
HISTORY_URL = API_URL.replace("/chat", "/history")

st.sidebar.header("Simulação de Cliente")

if "user_id" not in st.session_state:
    st.session_state.user_id = "client789"
user_id_input = st.sidebar.text_input("User ID", value=st.session_state.user_id)
st.session_state.user_id = user_id_input

if "active_session" not in st.session_state:
    st.session_state.active_session = "chat_001"
    
session_input = st.sidebar.text_input("Session ID", value=st.session_state.active_session)

if st.sidebar.button("Load / Update Session"):
        
    st.session_state.active_session = session_input
    
    st.session_state.messages = []
    
    try:
        params = {"user_id": st.session_state.user_id}
        
        resp = requests.get(f"{HISTORY_URL}/{session_input}", params=params)
        
        if resp.status_code == 200:
            history_data = resp.json()
            
            new_messages = []
            for log in history_data:
                role = "user" if log["direction"] == "user" else "assistant"
                new_messages.append({"role": role, "content": log["message"]})
            
            st.session_state.messages = new_messages
            
            if not history_data:
                st.toast("Nenhum histórico encontrado para esta sessão.", icon="📭")
            else:
                st.toast("Histórico carregado com sucesso!", icon="✅")
        else:
            st.error(f"Erro ao buscar histórico: {resp.status_code}")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
    
    st.rerun()
    
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua dúvida ou problema..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("O Swarm de Agentes está processando..."):
            try:
                payload = {
                    "message": prompt,
                    "user_id": st.session_state.user_id,
                    "session_id": st.session_state.active_session
                }
                
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    bot_response = data.get("response", "Não houve resposta do agente.")
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    st.error(f"Erro {response.status_code}: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar ao backend. Verifique se o Docker ou Uvicorn está rodando.")
            except Exception as e:
                st.error(f"Erro inesperado: {e}")