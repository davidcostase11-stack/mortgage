import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Simulador de Crédito Habitação", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f5;
    }
    .stNumberInput {
        margin-bottom: -10px;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #dddfe2;
        text-align: center;
    }
    .metric-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #65676b;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1c1e21;
    }
    .metric-delta {
        font-size: 1rem;
        font-weight: 700;
        margin-top: 5px;
    }
    .delta-down { color: #0084ff; }
    .delta-up { color: #fa3e3e; }
    .delta-none { color: #65676b; }
    </style>
""", unsafe_allow_html=True)

# --- Mortgage Calculation Function ---
def calculate_mortgage(P, annual_rate, n):
    if n <= 0: return 0
    r = (annual_rate / 100) / 12
    if r == 0: return P / n
    return (P * r * (1 + r)**n) / ((1 + r)**n - 1)

def format_euro(val):
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

# --- Sidebar Inputs ---
st.title("🏠 Simulador de Comparação de Crédito")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Dados Atuais")
    debt = st.number_input("Dívida Atual (€)", value=150000, step=1000)
    months = st.number_input("Meses Restantes", value=360, step=12)
    spread = st.number_input("Spread (%)", value=1.0, step=0.05, format="%.2f")
    actual_euribor = st.number_input("Euribor Atual (%)", value=3.5, step=0.01, format="%.2f")

with col2:
    st.subheader("Novo Cenário")
    new_euribor = st.number_input("Nova Euribor Prevista (%)", value=2.5, step=0.01, format="%.2f")

with col3:
    st.subheader("Amortização")
    repay_amt = st.number_input("Valor a Amortizar (€)", value=10000, step=500)

st.markdown("---")

# --- Calculations ---
current_rate = spread + actual_euribor
new_rate = spread + new_euribor

p1 = calculate_mortgage(debt, current_rate, months)
p2 = calculate_mortgage(debt, new_rate, months)
p3 = calculate_mortgage(max(0, debt - repay_amt), new_rate, months)

d2 = p2 - p1
d3 = p3 - p1

# --- Display Results ---
res_col1, res_col2, res_col3 = st.columns(3)

with res_col1:
    st.markdown(f"""
        <div class="metric-card" style="border-top: 5px solid #0084ff;">
            <div class="metric-title">Situação Atual</div>
            <div class="metric-value">{format_euro(p1)}</div>
            <div class="metric-delta delta-none">Referência</div>
            <p style="font-size: 0.8rem; color: #65676b; margin-top:10px;">Dívida Total @ {current_rate:.2f}%</p>
        </div>
    """, unsafe_allow_html=True)

with res_col2:
    delta_class = "delta-down" if d2 < 0 else "delta-up" if d2 > 0 else "delta-none"
    delta_prefix = "+" if d2 > 0 else ""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Simulação Nova Taxa</div>
            <div class="metric-value">{format_euro(p2)}</div>
            <div class="metric-delta {delta_class}">{delta_prefix}{format_euro(d2)}</div>
            <p style="font-size: 0.8rem; color: #65676b; margin-top:10px;">Dívida Total @ {new_rate:.2f}%</p>
        </div>
    """, unsafe_allow_html=True)

with res_col3:
    delta_class = "delta-down" if d3 < 0 else "delta-up" if d3 > 0 else "delta-none"
    delta_prefix = "+" if d3 > 0 else ""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Nova Taxa + Amortização</div>
            <div class="metric-value">{format_euro(p3)}</div>
            <div class="metric-delta {delta_class}">{delta_prefix}{format_euro(d3)}</div>
            <p style="font-size: 0.8rem; color: #65676b; margin-top:10px;">Dívida: {format_euro(max(0, debt-repay_amt))} @ {new_rate:.2f}%</p>
        </div>
    """, unsafe_allow_html=True)
