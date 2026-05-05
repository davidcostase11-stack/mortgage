import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Simulador de Crédito Habitação", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f5;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #dddfe2;
        text-align: center;
        margin-bottom: 20px;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #65676b;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1c1e21;
        margin-bottom: 5px;
    }
    .metric-delta {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }
    .delta-down { background: #e7f3ff; color: #0084ff; }
    .delta-up { background: #ffebe9; color: #fa3e3e; }
    .delta-none { background: #eeeeee; color: #65676b; }
    
    .sub-detail {
        font-size: 0.7rem;
        color: #65676b;
    }
    .section-header {
        margin-top: 30px;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #dddfe2;
        color: #65676b;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Calculation Function ---
def calculate_mortgage(P, annual_rate, n):
    if n <= 0: return 0
    r = (annual_rate / 100) / 12
    if r == 0: return P / n
    return (P * r * (1 + r)**n) / ((1 + r)**n - 1)

def format_euro(val):
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

# --- UI ---
st.title("🏠 Simulador de Crédito Habitação")

# --- 1. Base Inputs ---
st.markdown('<div class="section-header">1. Dados do Empréstimo Atual</div>', unsafe_allow_html=True)
i_col1, i_col2, i_col3, i_col4 = st.columns(4)
with i_col1:
    debt = st.number_input("Dívida Atual (€)", value=150000, step=1000)
with i_col2:
    months = st.number_input("Meses Restantes", value=360, step=12)
with i_col3:
    spread = st.number_input("Spread (%)", value=1.0, step=0.05, format="%.2f")
with i_col4:
    actual_euribor = st.number_input("Euribor Atual (%)", value=2.0, step=0.01, format="%.2f")

current_rate = spread + actual_euribor
p_baseline = calculate_mortgage(debt, current_rate, months)

# --- 2. Custom Simulation ---
st.markdown('<div class="section-header">2. Simulação Personalizada</div>', unsafe_allow_html=True)
s_col1, s_col2 = st.columns(2)
with s_col1:
    new_euribor = st.number_input("Nova Euribor Prevista (%)", value=2.5, step=0.01, format="%.2f")
with s_col2:
    repay_amt = st.number_input("Valor a Amortizar (€)", value=10000, step=500)

sim_rate = spread + new_euribor
p_rate_only = calculate_mortgage(debt, sim_rate, months)
p_repay = calculate_mortgage(max(0, debt - repay_amt), sim_rate, months)

# Cards Row 1
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card" style="border: 2px solid #0084ff;"><div class="metric-title">Situação Atual</div><div class="metric-value">{format_euro(p_baseline)}</div><div class="metric-delta delta-none">Referência</div><div class="sub-detail">Taxa Total: {current_rate:.2f}%</div></div>', unsafe_allow_html=True)
with c2:
    diff = p_rate_only - p_baseline
    d_class = "delta-up" if diff > 0.01 else "delta-down" if diff < -0.01 else "delta-none"
    d_prefix = "+" if diff > 0.01 else ""
    st.markdown(f'<div class="metric-card"><div class="metric-title">Nova Taxa</div><div class="metric-value">{format_euro(p_rate_only)}</div><div class="metric-delta {d_class}">{d_prefix}{format_euro(diff)}</div><div class="sub-detail">Taxa Total: {sim_rate:.2f}%</div></div>', unsafe_allow_html=True)
with c3:
    diff = p_repay - p_baseline
    d_class = "delta-up" if diff > 0.01 else "delta-down" if diff < -0.01 else "delta-none"
    d_prefix = "+" if diff > 0.01 else ""
    st.markdown(f'<div class="metric-card"><div class="metric-title">Taxa + Amortização</div><div class="metric-value">{format_euro(p_repay)}</div><div class="metric-delta {d_class}">{d_prefix}{format_euro(diff)}</div><div class="sub-detail">Dívida: {format_euro(max(0, debt-repay_amt))}</div></div>', unsafe_allow_html=True)

# --- 3. Market Projections ---
st.markdown('<div class="section-header">3. Projeções de Mercado (BCE)</div>', unsafe_allow_html=True)
st.info("ℹ️ Baseado nos alvos mais prováveis das próximas reuniões do BCE.")

projections = [
    {"date": "10 Junho 2026", "rate": 2.25, "prob": "90%"},
    {"date": "22 Julho 2026", "rate": 2.50, "prob": "65%"},
    {"date": "09 Setembro 2026", "rate": 2.75, "prob": "44%"},
    {"date": "28 Outubro 2026", "rate": 2.75, "prob": "44%"}
]

p_cols = st.columns(4)
for i, proj in enumerate(projections):
    with p_cols[i]:
        p_rate = spread + proj['rate']
        p_val = calculate_mortgage(debt, p_rate, months)
        p_diff = p_val - p_baseline
        pd_class = "delta-up" if p_diff > 0.01 else "delta-down" if p_diff < -0.01 else "delta-none"
        pd_prefix = "+" if p_diff > 0.01 else ""
        
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title" style="height:auto; margin-bottom:5px;">{proj['date']}</div>
                <div style="font-size:0.7rem; color:#65676b; margin-bottom:10px;">Probabilidade: {proj['prob']}</div>
                <div class="metric-value" style="font-size:1.3rem;">{format_euro(p_val)}</div>
                <div class="metric-delta {pd_class}">{pd_prefix}{format_euro(p_diff)}</div>
                <div class="sub-detail">Euribor: {proj['rate']:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
