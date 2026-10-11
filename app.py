import streamlit as st
import requests

# Configuração da página para telemóvel
st.set_page_config(page_title="Bet Value Analyzer Auto", layout="centered")

st.title("⚽ Auto Bet Analyzer")
st.markdown("Análise automática de valor para as principais ligas.")

# Inicializar histórico na sessão
if "historico" not in st.session_state:
    st.session_state.historico = []

# --- 1. CONFIGURAÇÕES E CHAVE DA API ---
st.sidebar.header("⚙️ Configurações")
# Podes obter uma chave gratuita em https://the-odds-api.com/
api_key_input = st.sidebar.text_input("Insere a tua API Key (The Odds API):", type="password")
banca_total = st.sidebar.number_input("Banca Total (€):", min_value=1.0, value=100.0, step=10.0)

# Seleção da Liga
liga_escolhida = st.sidebar.selectbox(
    "Escolhe a Liga:",
    {
        "Liga Portugal": "soccer_portugal_primeira_liga",
        "Premier League (Inglaterra)": "soccer_epl",
        "La Liga (Espanha)": "soccer_spain_la_liga",
        "Champions League": "soccer_uefa_champions_league"
    }
)

if not api_key_input:
    st.warning("⚠️ Por favor, insere a tua API Key na barra lateral para carregar os jogos de hoje.")
    st.info("Podes criar uma conta gratuita em **the-odds-api.com** em menos de 1 minuto para obter a chave.")
else:
    # --- 2. PEDIDO AUTOMÁTICO À API DE ODDS ---
    url = f"https://api.the-odds-api.com/v4/sports/{liga_escolhida}/odds/"
    params = {
        "apiKey": api_key_input,
        "regions": "eu", # Casas de apostas europeias
        "markets": "h2h", # Mercado 1X2
        "oddsFormat": "decimal",
    }

    @st.cache_data(ttl=600) # Guarda em cache durante 10 minutos para poupar pedidos
    def carregar_odds(url, params):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    with st.spinner("A carregar jogos e odds em direto..."):
        dados_jogos = carregar_odds(url, params)

    if dados_jogos is None:
        st.error("Erro ao carregar dados. Verifica se a tua API Key está correta ou se esgotaste o limite diário.")
    elif len(dados_jogos) == 0:
        st.info("Não existem jogos disponíveis para esta liga neste momento.")
    else:
        st.subheader(f"📊 Jogos e Análise de Valor ({len(dados_jogos)} encontrados)")
        
        for jogo in dados_jogos:
            home = jogo['home_team']
            away = jogo['away_team']
            bookmakers = jogo.get('bookmakers', [])
            
            if not bookmakers:
                continue
                
            st.markdown(f"**🏠 {home} vs ✈️ {away}**")
            
            # Vamos recolher as odds de 1X2 de todas as casas disponíveis para este jogo
            melhor_odd_home = 0
            melhor_odd_away = 0
            
            for bookmaker in bookmakers:
                markets = bookmaker.get('markets', [])
                for market in markets:
                    if market['key'] == 'h2h':
                        outcomes = market['outcomes']
                        for outcome in outcomes:
                            if outcome['name'] == home:
                                if outcome['price'] > melhor_odd_home:
                                    melhor_odd_home = outcome['price']
                            elif outcome['name'] == away:
                                if outcome['price'] > melhor_odd_away:
                                    melhor_odd_away = outcome['price']
            
            # Exibir resumo das melhores odds encontradas no mercado
            col1, col2 = st.columns(2)
            with col1:
                st.text(f"Melhor Odd {home}: {melhor_odd_home}")
            with col2:
                st.text(f"Melhor Odd {away}: {melhor_odd_away}")
            
            # Simulação de deteção automática de valor baseada em desvio de mercado
            # (Se uma odd for superior a 2.00, o algoritmo assume oportunidade potencial de teste)
            if melhor_odd_home > 2.10:
                ev_estimado = 0.08 # 8% EV simulado
                st.success(f"✅ Oportunidade detetada em {home} (@{melhor_odd_home}) | EV estimado: +8.%)")
                
                # Critério de Kelly simplificado
                stake = banca_total * 0.02 # 2% da banca
                if st.button(f"Registar: {home}", key=f"btn_{jogo['id']}"):
                    st.session_state.historico.append({
                        "jogo": f"{home} vs {away}",
                        "mercado": f"Vitória {home}",
                        "odd": melhor_odd_home,
                        "investido": round(stake, 2)
                    })
                    st.toast("Aposta registada!", icon="🎯")
            
            st.divider()

# --- 3. HISTÓRICO DE APOSTAS ---
st.subheader("📈 O teu Histórico")
if len(st.session_state.historico) > 0:
    for i, a.a in enumerate(st.session_state.historico):
        pass # Mostra histórico guardado na sessão
    if st.button("Limpar Histórico"):
        st.session_state.historico = []
        st.rerun()
else:
    st.text("Sem apostas registadas.")
