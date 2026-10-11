import streamlit as st
import requests

st.set_page_config(page_title="Bet Value Analyzer Auto", layout="centered")

st.title("⚽ Auto Bet Analyzer (1X2 & Golos)")
st.markdown("Análise automática de valor para 1X2 e Mais/Menos 2.5 Golos.")

if "historico" not in st.session_state:
    st.session_state.historico = []

# --- 1. CONFIGURAÇÕES NA BARRA LATERAL ---
st.sidebar.header("⚙️ Configurações")
api_key_input = st.sidebar.text_input("Insere a tua API Key:", type="password")
banca_total = st.sidebar.number_input("Banca Total (€):", min_value=1.0, value=100.0, step=10.0)

if not api_key_input:
    st.warning("⚠️ Insere a tua API Key na barra lateral para carregar os desportos.")
else:
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
        futebol_ligas = [s for s in sports_data if "soccer" in s['key']]
        opcoes_ligas = {s['title']: s['key'] for s in futebol_ligas}
        
        if not opcoes_ligas:
            st.info("Não existem ligas de futebol disponíveis na API neste momento.")
        else:
            liga_nome = st.selectbox("Escolhe a Competição Disponível:", list(opcoes_ligas.keys()))
            liga_key = opcoes_ligas[liga_nome]
            
            # Pedido à API incluindo h2h (1X2) e totals (Golos)
            odds_url = f"https://api.the-odds-api.com/v4/sports/{liga_key}/odds/"
            odds_params = {
                "apiKey": api_key_input.strip(),
                "regions": "eu",
                "markets": "h2h,totals", # Inclui 1X2 e Totais de Golos
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
                    
                    # Variáveis para guardar as melhores odds de cada mercado
                    melhor_odd_home = 0
                    melhor_odd_away = 0
                    melhor_odd_over25 = 0
                    melhor_odd_under25 = 0
                    
                    for bookmaker in bookmakers:
                        for market in bookmaker.get('markets', []):
                            # Mercado 1X2 (h2h)
                            if market['key'] == 'h2h':
                                for outcome in market['outcomes']:
                                    if outcome['name'] == home and outcome['price'] > melhor_odd_home:
                                        melhor_odd_home = outcome['price']
                                    elif outcome['name'] == away and outcome['price'] > melhor_odd_away:
                                        melhor_odd_away = outcome['price']
                            
                            # Mercado de Golos (totals - linha de 2.5)
                            elif market['key'] == 'totals':
                                for outcome in market['outcomes']:
                                    if outcome.get('point') == 2.5:
                                        if outcome['name'] == 'Over' and outcome['price'] > melhor_odd_over25:
                                            melhor_odd_over25 = outcome['price']
                                        elif outcome['name'] == 'Under' and outcome['price'] > melhor_odd_under25:
                                            melhor_odd_under25 = outcome['price']
                    
                    # Mostrar as melhores odds encontradas no mercado para este jogo
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text(f"1X2 - {home}: {melhor_odd_home if melhor_odd_home > 0 else '-'}")
                        st.text(f"1X2 - {away}: {melhor_odd_away if melhor_odd_away > 0 else '-'}")
                    with col2:
                        st.text(f"Mais de 2.5: {melhor_odd_over25 if melhor_odd_over25 > 0 else '-'}")
                        st.text(f"Menos de 2.5: {melhor_odd_under25 if melhor_odd_under25 > 0 else '-'}")
                    
                    # Simulação de oportunidade de valor para teste automático
                    if melhor_odd_over25 > 1.90:
                        st.success(f"🔥 Oportunidade detetada: Mais de 2.5 Golos (@{melhor_odd_over25})")
                        stake = banca_total * 0.02
                        if st.button(f"Registar: {home} vs {away} (Over 2.5)", key=f"btn_over_{jogo['id']}"):
                            st.session_state.historico.append({
                                "jogo": f"{home} vs {away}",
                                "mercado": "Mais de 2.5 Golos",
                                "odd": melhor_odd_over25,
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
