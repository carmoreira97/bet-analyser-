import streamlit as st
import requests

st.set_page_config(page_title="Bet Value Analyzer Auto", layout="centered")

st.title("⚽ Auto Bet Analyzer")
st.markdown("Análise automática de valor com dados em direto.")

if "historico" not in st.session_state:
    st.session_state.historico = []

# --- 1. CONFIGURAÇÕES NA BARRA LATERAL ---
st.sidebar.header("⚙️ Configurações")
api_key_input = st.sidebar.text_input("Insere a tua API Key:", type="password")
banca_total = st.sidebar.number_input("Banca Total (€):", min_value=1.0, value=100.0, step=10.0)

if not api_key_input:
    st.warning("⚠️ Insere a tua API Key na barra lateral para carregar os desportos.")
else:
    # Passo A: Buscar todos os desportos/ligas disponíveis na API automaticamente
    sports_url = "https://api.the-odds-api.com/v4/sports"
    sports_params = {"apiKey": api_key_input.strip()}
    
    @st.cache_data(ttl=3600)
    def carregar_desportos(url, params):
        res = requests.get(url, params=params)
        if res.status_code == 200:
            return res.json()
        return None

    with st.spinner("A carregar ligas disponíveis..."):
        sports_data = carregar_desportos(sports_url, sports_params)

    if sports_data is None:
        st.error("Erro ao validar a API Key. Verifica se foi copiada corretamente.")
    else:
        # Filtrar apenas ligas de Futebol (Soccer)
        futebol_ligas = [s for s in sports_data if "soccer" in s['key']]
        
        # Criar dicionário com o nome bonito e a chave real da API
        opcoes_ligas = {s['title']: s['key'] for s in futebol_ligas}
        
        if not opcoes_ligas:
            st.info("Não existem ligas de futebol disponíveis na API neste momento.")
        else:
            liga_nome = st.selectbox("Escolhe a Competição Disponível:", list(opcoes_ligas.keys()))
            liga_key = opcoes_ligas[liga_nome]
            
            # Passo B: Carregar as odds da liga selecionada
            odds_url = f"https://api.the-odds-api.com/v4/sports/{liga_key}/odds/"
            odds_params = {
                "apiKey": api_key_input.strip(),
                "regions": "eu",
                "markets": "h2h",
                "oddsFormat": "decimal",
            }
            
            @st.cache_data(ttl=600)
            def carregar_odds(url, params):
                res = requests.get(url, params=params)
                if res.status_code == 200:
                    return res.json()
                return None

            with st.spinner(f"A carregar jogos para {liga_nome}..."):
                dados_jogos = carregar_odds(odds_url, odds_params)

            if dados_jogos is None:
                st.error("Erro ao carregar os jogos desta liga.")
            elif len(dados_jogos) == 0:
                st.info("Não há jogos agendados para esta liga nas próximas horas.")
            else:
                st.subheader(f"📊 Jogos em Direto: {liga_nome} ({len(dados_jogos)})")
                
                for jogo in dados_jogos:
                    home = jogo['home_team']
                    away = jogo['away_team']
                    bookmakers = jogo.get('bookmakers', [])
                    
                    if not bookmakers:
                        continue
                        
                    st.markdown(f"**🏠 {home} vs ✈️ {away}**")
                    
                    melhor_odd_home = 0
                    melhor_odd_away = 0
                    
                    for bookmaker in bookmakers:
                        for market in bookmaker.get('markets', []):
                            if market['key'] == 'h2h':
                                for outcome in market['outcomes']:
                                    if outcome['name'] == home and outcome['price'] > melhor_odd_home:
                                        melhor_odd_home = outcome['price']
                                    elif outcome['name'] == away and outcome['price'] > melhor_odd_away:
                                        melhor_odd_away = outcome['price']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text(f"Melhor Odd {home}: {melhor_odd_home}")
                    with col2:
                        st.text(f"Melhor Odd {away}: {melhor_odd_away}")
                    
                    # Simulação de EV para teste
                    if melhor_odd_home > 2.00:
                        st.success(f"✅ Oportunidade detetada em {home} (@{melhor_odd_home})")
                        stake = banca_total * 0.02
                        if st.button(f"Registar: {home}", key=f"btn_{jogo['id']}"):
                            st.session_state.historico.append({
                                "jogo": f"{home} vs {away}",
                                "mercado": f"Vitória {home}",
                                "odd": melhor_odd_home,
                                "investido": round(stake, 2)
                            })
                            st.toast("Aposta registada!", icon="🎯")
                    
                    st.divider()

# --- 2. HISTÓRICO ---
st.subheader("📈 O teu Histórico")
if len(st.session_state.historico) > 0:
    for i, aposta in enumerate(st.session_state.historico):
        st.markdown(f"**{i+1}. {aposta['jogo']}** | {aposta['mercado']} @ {aposta['odd']} | **{aposta['investido']}€**")
    if st.button("Limpar Histórico"):
        st.session_state.historico = []
        st.rerun()
else:
    st.text("Sem apostas registadas.")
