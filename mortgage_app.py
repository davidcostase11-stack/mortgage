import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Simulador de Crédito Habitação", layout="wide")

# --- Custom Styling to match HTML version ---
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f5;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #dddfe2;
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        border-color: #0084ff;
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #65676b;
        text-transform: uppercase;
        margin-bottom: 15px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1c1e21;
        margin-bottom: 10px;
    }
    .metric-delta {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }
    .delta-down { background: #e7f3ff; color: #0084ff; }
    .delta-up { background: #ffebe9; color: #fa3e3e; }
    .delta-none { background: #eeeeee; color: #65676b; }
    
    .sub-detail {
        font-size: 0.75rem;
        color: #65676b;
        margin-top: 15px;
    }
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

# --- App Title ---
st.title("🏠 Simulador de Crédito Habitação")

# --- Global Input Section ---
st.markdown("### 1. Dados Base do Empréstimo")
col1, col2, col3, col4 = st.columns(4)

with col1:
    debt = st.number_input("Dívida Atual (€)", value=150000, step=1000)
with col2:
    months = st.number_input("Meses Restantes", value=360, step=12)
with col3:
    spread = st.number_input("Spread (%)", value=1.0, step=0.05, format="%.2f")
with col4:
    actual_euribor = st.number_input("Euribor Atual (%)", value=2.0, step=0.01, format="%.2f")

# --- Tabs ---
tab1, tab2 = st.tabs(["📊 Simulador Personalizado", "📅 Projeções de Mercado (BCE)"])

# --- TAB 1: Custom Simulator ---
with tab1:
    st.markdown("### 2. Simulação de Cenários")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        new_euribor = st.number_input("Nova Euribor Prevista (%)", value=2.5, step=0.01, format="%.2f")
    with c_col2:
        repay_amt = st.number_input("Valor a Amortizar (€)", value=10000, step=500)

    # Calculations
    current_rate = spread + actual_euribor
    new_rate = spread + new_euribor
    
    p1 = calculate_mortgage(debt, current_rate, months)
    p2 = calculate_mortgage(debt, new_rate, months)
    p3 = calculate_mortgage(max(0, debt - repay_amt), new_rate, months)
    
    d2 = p2 - p1
    d3 = p3 - p1

    # Results Row
    st.markdown("<br>", unsafe_allow_html=True)
    res_col1, res_col2, res_col3 = st.columns(3)

    with res_col1:
        st.markdown(f"""
            <div class="metric-card" style="border: 2px solid #0084ff;">
                <div class="metric-title">Situação Atual</div>
                <div class="metric-value">{format_euro(p1)}</div>
                <div class="metric-delta delta-none">Referência</div>
                <div class="sub-detail">Dívida Total @ {current_rate:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with res_col2:
        d2_class = "delta-down" if d2 < 0 else "delta-up" if d2 > 0 else "delta-none"
        d2_prefix = "+" if d2 > 0 else ""
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Simulação Nova Taxa</div>
                <div class="metric-value">{format_euro(p2)}</div>
                <div class="metric-delta {d2_class}">{d2_prefix}{format_euro(d2)}</div>
                <div class="sub-detail">Dívida Total @ {new_rate:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with res_col3:
        d3_class = "delta-down" if d3 < 0 else "delta-up" if d3 > 0 else "delta-none"
        d3_prefix = "+" if d3 > 0 else ""
        reduced_debt = max(0, debt - repay_amt)
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Nova Taxa + Amortização</div>
                <div class="metric-value">{format_euro(p3)}</div>
                <div class="metric-delta {d3_class}">{d3_prefix}{format_euro(d3)}</div>
                <div class="sub-detail">Dívida: {format_euro(reduced_debt)} @ {new_rate:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

# --- TAB 2: Market Projections ---
with tab2:
    st.info("ℹ️ Projeções baseadas nos alvos mais prováveis das próximas reuniões do BCE (via ecb-watch.eu).")
    
    # ECB Data
    projections = [
        {"date": "10 Junho 2026", "rate": 2.25, "prob": "90.0%"},
        {"date": "22 Julho 2026", "rate": 2.50, "prob": "64.8%"},
        {"date": "09 Setembro 2026", "rate": 2.75, "prob": "44.1%"},
        {"date": "28 Outubro 2026", "rate": 2.75, "prob": "43.6%"}
    ]

    # Table Header
    st.markdown("""
        <table style="width:100%; border-collapse: collapse; margin-top: 20px;">
            <tr style="border-bottom: 2px solid #dddfe2; color: #65676b; font-size: 0.9rem;">
                <th style="text-align:left; padding: 12px;">Data da Reunião</th>
                <th style="text-align:left; padding: 12px;">Euribor Projetada</th>
                <th style="text-align:left; padding: 12px;">Prestação Mensal</th>
                <th style="text-align:left; padding: 12px;">Diferença</th>
            </tr>
    """, unsafe_allow_html=True)

    # Table Rows
    current_rate = spread + actual_euribor
    p_baseline = calculate_mortgage(debt, current_rate, months)

    for proj in projections:
        proj_total_rate = spread + proj['rate']
        p_proj = calculate_mortgage(debt, proj_total_rate, months)
        diff = p_proj - p_baseline
        
        diff_color = "#fa3e3e" if diff > 0.01 else "#0084ff" if diff < -0.01 else "#65676b"
        diff_prefix = "+" if diff > 0.01 else ""

        st.markdown(f"""
            <tr style="border-bottom: 1px solid #dddfe2;">
                <td style="padding: 16px 12px;"><b>{proj['date']}</b><br><small style="color:#65676b">Prob: {proj['prob']}</small></td>
                <td style="padding: 16px 12px;"><b>{proj['rate']:.2f}%</b><br><small style="color:#65676b">Total: {proj_total_rate:.2f}%</small></td>
                <td style="padding: 16px 12px; font-weight: 700;">{format_euro(p_proj)}</td>
                <td style="padding: 16px 12px; font-weight: 700; color: {diff_color};">{diff_prefix}{format_euro(diff)}</td>
            </tr>
        """, unsafe_allow_html=True)

    st.markdown("</table>", unsafe_allow_html=True)
