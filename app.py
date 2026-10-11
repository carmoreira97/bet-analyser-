import streamlit as st
import requests

st.set_page_config(page_title="Bet Value Debug", layout="centered")

st.title("⚽ Debug API de Odds")

api_key_input = st.sidebar.text_input("Insere a tua API Key:", type="password")
liga_escolhida = st.sidebar.selectbox(
    "Escolhe a Liga:",
    {
        "Liga Portugal": "soccer_portugal_primeira_liga",
        "Premier League": "soccer_epl"
    }
)

if not api_key_input:
    st.warning("Insere a API Key na barra lateral.")
else:
    url = f"https://api.the-odds-api.com/v4/sports/{liga_escolhida}/odds/"
    params = {
        "apiKey": api_key_input.strip(), # .strip() remove espaços acidentais nas pontas
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
    }

    response = requests.get(url, params=params)
    
    # Vamos mostrar o estado exato da resposta para percebermos o problema
    st.text(f"Código de Estado do Servidor: {response.status_code}")
    
    if response.status_code == 200:
        dados_jogos = response.json()
        st.success(f"Sucesso! Encontrados {len(dados_jogos)} jogos.")
        for jogo in dados_jogos:
            st.write(f"🏠 {jogo['home_team']} vs ✈️ {jogo['away_team']}")
    else:
        st.error("O servidor rejeitou o pedido.")
        # Mostra a mensagem exata enviada pela The Odds API
        st.code(response.text)
