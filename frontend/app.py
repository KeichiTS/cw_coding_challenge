import streamlit as st
import requests
import os

st.set_page_config(page_title="InfinitePay Agent", page_icon="https://www.rw-designer.com/icon-view/20374.png")
st.title("InfinitePay Swarm Agent")

API_URL = os.getenv("API_URL", "http://backend:8000/api/chat") 

if "user_id" not in st.session_state:
    st.session_state.user_id = "client789"  

st.sidebar.write(f"User ID: `{st.session_state.user_id}`")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua dúvida ou problema..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Consultando o Swarm..."):
            try:

                response = requests.post(API_URL, json={"message": prompt}) 
                
                if response.status_code == 200:
                    data = response.json()
                    bot_response = data.get("response", {}).get("raw", "Resposta processada.")
                    
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    st.error(f"Erro {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Erro de conexão com o backend: {e}")