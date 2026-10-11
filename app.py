import streamlit as st

# Configuração da página para visualização otimizada no telemóvel
st.set_page_config(page_title="Bet Value Analyzer", layout="centered")

st.title("⚽ Bet Value Analyzer")
st.markdown("Análise de valor, gestão de banca e histórico para telemóvel.")

# Inicializar o histórico na sessão do Streamlit se não existir
if "historico" not in st.session_state:
    st.session_state.historico = []

# --- 1. CONFIGURAÇÃO DA BANCA E FILTROS ---
st.sidebar.header("⚙️ Definições")
banca_total = st.sidebar.number_input("Banca Total (€):", min_value=1.0, value=100.0, step=10.0)
min_ev_filtro = st.sidebar.slider("Filtrar EV Mínimo (%):", min_value=0, max_value=20, value=5)

# --- 2. SUGESTÕES DO DIA ---
st.subheader("📊 Sugestões com Valor Detetado")

jogos_dia = [
    {
        "jogo": "SL Benfica vs Vitória SC", 
        "mercado": "Vitória SC +2.0 AH", 
        "odd": 1.85, 
        "prob_real": 0.65
    },
    {
        "jogo": "Sporting CP vs Famalicão", 
        "mercado": "Mais de 2.5 Golos", 
        "odd": 1.90, 
        "prob_real": 0.58
    },
    {
        "jogo": "FC Porto vs Gil Vicente", 
        "mercado": "Hipótese Dupla (X2)", 
        "odd": 2.05, 
        "prob_real": 0.52
    }
]

for item in jogos_dia:
    ev = (item["odd"] * item["prob_real"]) - 1
    ev_pct = ev * 100
    
    if ev_pct >= min_ev_filtro:
        with st.container():
            st.markdown(f"**{item['jogo']}**")
            col1, col2 = st.columns(2)
            with col1:
                st.text(f"Mercado: {item['mercado']}")
                st.text(f"Odd: {item['odd']}")
            with col2:
                st.success(f"✅ VALOR: +{ev_pct:.1f}% EV")
            
            b = item["odd"] - 1
            p = item["prob_real"]
            q = 1 - p
            kelly_frac = ((b * p - q) / b) * 0.25 if b > 0 else 0
            kelly_frac = max(0, kelly_frac)
            sugestao_valor = banca_total * kelly_frac
            
            st.info(f"💡 Stake recomendada (Kelly Qtr): **{sugestao_valor:.2f}€** ({kelly_frac*100:.1f}% da banca)")
            
            if st.button(f"Registar Aposta: {item['jogo']}", key=f"btn_{item['jogo']}"):
                st.session_state.historico.append({
                    "jogo": item['jogo'],
                    "mercado": item['mercado'],
                    "odd": item['odd'],
                    "investido": round(sugestao_valor, 2)
                })
                st.toast("Aposta registada com sucesso!", icon="🎯")
            
            st.divider()

# --- 3. CALCULADORA MANUAL DE VALOR & KELLY ---
st.subheader("⚙️ Calculador Manual & Critério de Kelly")
odd_casa = st.number_input("Insere a Odd da Casa:", min_value=1.01, value=2.00, step=0.01)
prob_estimada = st.slider("A tua Probabilidade Estimada (%):", min_value=1, max_value=100, value=50)

if st.button("Calcular Vantagem e Stake", use_container_width=True):
    prob_decimal = prob_estimada / 100
    ev_manual = (odd_casa * prob_decimal) - 1
    ev_manual_pct = ev_manual * 100
    
    b = odd_casa - 1
    kelly_frac = ((b * prob_decimal - (1 - prob_decimal)) / b) * 0.25 if b > 0 else 0
    kelly_frac = max(0, kelly_frac)
    stake_manual = banca_total * kelly_frac
    
    if ev_manual > 0:
        st.success(f"💡 **Com Valor!** EV: **+{ev_manual_pct:.2f}%** | Stake Segura (Kelly): **{stake_manual:.2f}€**")
    else:
        st.warning(f"⚠️ **Sem Valor.** EV: **{ev_manual_pct:.2f}%** (Não recomendado apostar).")

# --- 4. HISTÓRICO DE APOSTAS ---
st.subheader("📈 Histórico de Apostas Registadas")
if len(st.session_state.historico) > 0:
    for i, aposta in enumerate(st.session_state.historico):
        st.markdown(f"**{i+1}. {aposta['jogo']}** | {aposta['mercado']} @ {aposta['odd']} | Investido: **{aposta['investido']}€**")
    
    if st.button("Limpar Histórico"):
        st.session_state.historico = []
        st.rerun()
else:
    st.text("Ainda não tens apostas registadas nesta sessão.")
