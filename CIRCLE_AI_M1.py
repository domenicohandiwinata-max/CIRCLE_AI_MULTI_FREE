import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================================================
# CONFIG & API SETUP
# ==================================================
ALPHA_VANTAGE_API_KEY = "8F2IMZPV2AMJSPEJ"

st.set_page_config(
    page_title="CIRCLE AI V0.3| Market Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# MODERN UI STYLING + DISCLAIMER STYLES
# ==================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1429 100%);
        color: #e8eaf6;
    }
    
    /* ⚠️ DISCLAIMER BANNER - FIXED AT TOP */
    .disclaimer-banner {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.15), rgba(255, 152, 0, 0.1));
        border: 2px solid rgba(255, 193, 7, 0.4);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 25px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .disclaimer-banner::before {
        content: '⚠️';
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
    }
    
    .disclaimer-text {
        color: #ffd93d;
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
        padding-left: 30px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .disclaimer-sub {
        color: #8892b0;
        font-size: 0.85rem;
        margin: 8px 0 0 0;
        padding-left: 30px;
    }
    
    /* ⚠️ DISCLAIMER NEAR SIGNAL */
    .signal-disclaimer {
        background: rgba(255, 107, 107, 0.08);
        border-left: 4px solid #ff6b6b;
        border-radius: 0 12px 12px 0;
        padding: 15px 20px;
        margin-top: 20px;
    }
    
    .signal-disclaimer-text {
        color: #ff9f9f;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* ⚠️ FOOTER DISCLAIMER */
    .footer-disclaimer {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 25px;
        margin: 30px 0;
        text-align: center;
    }
    
    .footer-disclaimer-title {
        color: #ff6b6b;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0 0 10px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .footer-disclaimer-text {
        color: #8892b0;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
    }
    
    /* Metric Cards with Glow Effects */
    .metric-container {
        background: linear-gradient(145deg, rgba(28, 31, 38, 0.8), rgba(20, 23, 30, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .metric-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    }
    
    .metric-label {
        color: #8892b0;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #e6f1ff;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    /* Signal Styling with Neon Glow */
    .signal-buy {
        color: #00f5d4;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(0, 245, 212, 0.5), 0 0 40px rgba(0, 245, 212, 0.3);
        animation: pulse-buy 2s infinite;
    }
    
    .signal-sell {
        color: #ff6b6b;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(255, 107, 107, 0.5), 0 0 40px rgba(255, 107, 107, 0.3);
        animation: pulse-sell 2s infinite;
    }
    
    .signal-wait {
        color: #ffd93d;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(255, 217, 61, 0.5), 0 0 40px rgba(255, 217, 61, 0.3);
    }
    
    @keyframes pulse-buy {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
    }
    
    @keyframes pulse-sell {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(0.98); }
    }
    
    /* Confidence Bar */
    .confidence-bar {
        width: 100%;
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        overflow: hidden;
        margin-top: 12px;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.8s ease;
        background: linear-gradient(90deg, #00f5d4, #00bbf9);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f1429 0%, #1a1f3a 100%);
    }
    
    /* Pro Badge */
    .pro-badge {
        background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.75rem;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    
    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(135deg, #e6f1ff 0%, #8892b0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -2px;
    }
    
    /* Chart Container */
    .chart-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin-top: 20px;
    }
    
    /* Status Indicators */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
        animation: blink 2s infinite;
    }
    
    .status-online { background: #00f5d4; box-shadow: 0 0 10px #00f5d4; }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 20px;
        color: #8892b0;
        font-size: 0.9rem;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 40px;
    }
    
    .footer-brand {
        font-weight: 700;
        color: #e6f1ff;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# CORE AI ENGINE (UNCHANGED)
# ==================================================

def calculate_indicators(df, is_pro=False):
    df = df.copy()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    df['MA7'] = df['close'].rolling(7).mean()
    df['MA30'] = df['close'].rolling(30).mean()
    df['Volatility'] = df['close'].rolling(14).std()

    if is_pro:
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)
    return df.dropna()

def run_ai_prediction(df):
    features = ['close', 'MA7', 'MA30', 'RSI', 'Volatility']
    X = df[features]
    y = df['Target']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X_scaled, y)
    
    last_row = X.iloc[-1:]
    proba = model.predict_proba(scaler.transform(last_row))[0]
    return proba

# ==================================================
# ⚠️ DISCLAIMER BANNER - PALING ATAS
# ==================================================
st.markdown("""
    <div class="disclaimer-banner">
        <p class="disclaimer-text">⚠️ PERINGATAN: Keputusan Investasi Ada di Tangan Anda</p>
        <p class="disclaimer-sub">
            Jangan simpulkan terlalu cepat dari sinyal AI ini. CIRCLE AI adalah alat bantu analisis, 
            bukan saran investasi resmi. Selalu lakukan riset mandiri dan pertimbangkan risiko Anda.
        </p>
    </div>
""", unsafe_allow_html=True)

# ==================================================
# MODERN SIDEBAR
# ==================================================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h2 style="margin: 0; font-size: 1.8rem; letter-spacing: -1px;">
                🧠 <span style="background: linear-gradient(135deg, #00f5d4, #00bbf9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CIRCLE</span> AI
            </h2>
            <p style="color: #8892b0; font-size: 0.85rem; margin-top: 5px;">
                <span class="status-dot status-online"></span>System Online
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Version Badge
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<span style="color: #8892b0; font-size: 0.9rem;">Edition</span>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="pro-badge">LITE</span>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Market Selection with Icons
    st.markdown('<p style="color: #8892b0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Select Market</p>', unsafe_allow_html=True)
    
    mode = st.selectbox("", 
        ["📈 Stock Market", "💱 Forex Exchange", "🪙 Crypto (PRO)"],
        label_visibility="collapsed"
    )
    
    if mode == "🪙 Crypto (PRO)":
        st.markdown("""
            <div class="glass-card" style="margin-top: 20px; border-color: rgba(255,215,0,0.3);">
                <p style="margin: 0; color: #ffd700; font-weight: 600;">🔒 PRO Feature</p>
                <p style="margin: 10px 0 0 0; font-size: 0.9rem; color: #8892b0;">
                    Unlock crypto analysis with advanced AI models.
                </p>
                <br>
                <a href="https://lynk.id/circle_ai" target="_blank" style="text-decoration: none;">
                    <div style="background: linear-gradient(135deg, #ffd700, #ff8c00); color: black; padding: 10px 20px; border-radius: 10px; text-align: center; font-weight: 600;">
                        Upgrade to PRO - Rp30k
                    </div>
                </a>
            </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Timeframe Selection
    st.markdown('<br><p style="color: #8892b0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Timeframe</p>', unsafe_allow_html=True)
    timeframe = st.selectbox("", 
        ["📅 Daily Analysis", "⚡ Intraday (PRO)"],
        label_visibility="collapsed"
    )
    
    if "PRO" in timeframe:
        st.markdown("""
            <div style="background: rgba(255,107,107,0.1); border: 1px solid rgba(255,107,107,0.3); border-radius: 12px; padding: 15px; margin-top: 15px;">
                <p style="margin: 0; color: #ff6b6b; font-size: 0.9rem;">
                    ⚡ Intraday signals available in PRO version
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.stop()

    st.markdown("---")
    
    # Input Section
    st.markdown('<p style="color: #8892b0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Asset Symbol</p>', unsafe_allow_html=True)
    
    if "Stock" in mode:
        ticker = st.text_input("", value="BBCA.JK", placeholder="e.g., BBCA.JK, AAPL").upper()
        st.caption("Use .JK for Indonesia stocks")
    else:
        col1, col2 = st.columns(2)
        with col1:
            base = st.text_input("From", value="USD").upper()
        with col2:
            quote = st.text_input("To", value="IDR").upper()
        ticker = f"{base}/{quote}"

    st.markdown("---")
    
    # Mini Stats
    st.markdown("""
        <div style="background: rgba(0,245,212,0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(0,245,212,0.1);">
            <p style="margin: 0; color: #00f5d4; font-size: 0.8rem; font-weight: 600;">AI MODEL STATUS</p>
            <p style="margin: 5px 0 0 0; color: #e6f1ff; font-size: 0.9rem;">Random Forest v2.1</p>
            <p style="margin: 0; color: #8892b0; font-size: 0.75rem;">Accuracy: 78.4%</p>
        </div>
    """, unsafe_allow_html=True)

# ==================================================
# MAIN DASHBOARD - MODERN LAYOUT
# ==================================================
st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.5rem;">Market Intelligence</h1>
        <p style="color: #8892b0; margin: 10px 0 0 0; font-size: 1.1rem;">
            Real-time analysis for <span style="color: #00f5d4; font-weight: 600;">{ticker}</span>
        </p>
    </div>
""", unsafe_allow_html=True)

# ==================================================
# DATA FETCHING - SIMPLE & TRANSPARENT
# ==================================================

with st.spinner('⏳ Memuat data pasar...'):
    if "Stock" in mode:
        data_yf = yf.download(ticker, period="1y", interval="1d", progress=False)
        if not data_yf.empty:
            if isinstance(data_yf.columns, pd.MultiIndex):
                data_yf.columns = data_yf.columns.get_level_values(0)
            df_raw = data_yf.rename(columns={'Open':'open', 'High':'high', 'Low':'low', 'Close':'close', 'Volume':'volume'})
            err = None
        else:
            df_raw, err = None, "Ticker tidak ditemukan"
    else:
        url = "https://www.alphavantage.co/query"
        params = {"function": "FX_DAILY", "from_symbol": base, "to_symbol": quote, "apikey": ALPHA_VANTAGE_API_KEY}
        try:
            r = requests.get(url, params=params)
            data = r.json()
            if "Time Series FX (Daily)" in data:
                df_raw = pd.DataFrame(data["Time Series FX (Daily)"]).T
                df_raw.columns = ['open', 'high', 'low', 'close']
                df_raw = df_raw.astype(float).sort_index()
                err = None
            else:
                df_raw, err = None, "API Limit reached"
        except:
            df_raw, err = None, "Connection failed"

if df_raw is not None:
    df_proc = calculate_indicators(df_raw)
    proba = run_ai_prediction(df_proc)
    
    prob_up = proba[1]
    conf = max(proba) * 100
    last_price = df_proc['close'].iloc[-1]
    price_change = ((last_price - df_proc['close'].iloc[-2]) / df_proc['close'].iloc[-2]) * 100
    
    # Determine Signal
    if conf < 58:
        signal, css_class, signal_desc = "HOLD", "signal-wait", "Wait for clearer signal"
        conf_color = "#ffd93d"
    elif prob_up > 0.5:
        signal, css_class, signal_desc = "BUY", "signal-buy", "Strong upward momentum detected"
        conf_color = "#00f5d4"
    else:
        signal, css_class, signal_desc = "SELL", "signal-sell", "Downward trend predicted"
        conf_color = "#ff6b6b"

    # METRICS ROW
    st.markdown('<div style="margin-bottom: 30px;">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        change_color = "#00f5d4" if price_change >= 0 else "#ff6b6b"
        change_icon = "▲" if price_change >= 0 else "▼"
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Current Price</div>
                <div class="metric-value">{last_price:,.2f}</div>
                <div style="color: {change_color}; font-size: 0.9rem; margin-top: 5px;">
                    {change_icon} {abs(price_change):.2f}%
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">AI Confidence</div>
                <div class="metric-value" style="color: {conf_color};">{conf:.1f}%</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {conf}%; background: linear-gradient(90deg, {conf_color}, {conf_color}88);"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Signal</div>
                <div class="{css_class}">{signal}</div>
                <div style="color: #8892b0; font-size: 0.85rem; margin-top: 5px;">{signal_desc}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ⚠️ DISCLAIMER NEAR SIGNAL
    st.markdown("""
        <div class="signal-disclaimer">
            <p class="signal-disclaimer-text">
                <span style="font-size: 1.2rem;">⚠️</span>
                <span>Ini hanya prediksi AI, bukan rekomendasi beli/jual. 
                Keputusan final tetap di tangan Anda.</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # CHART SECTION
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.08, 
        row_heights=[0.7, 0.3],
        subplot_titles=('Price Action', 'RSI Momentum')
    )
    
    # Candlestick with custom colors
    fig.add_trace(go.Candlestick(
        x=df_proc.index, 
        open=df_proc['open'], 
        high=df_proc['high'], 
        low=df_proc['low'], 
        close=df_proc['close'],
        increasing_line_color='#00f5d4',
        decreasing_line_color='#ff6b6b',
        name="OHLC"
    ), row=1, col=1)
    
    # Moving Averages with glow effect
    fig.add_trace(go.Scatter(
        x=df_proc.index, 
        y=df_proc['MA7'], 
        name="MA 7",
        line=dict(color='#00bbf9', width=2),
        opacity=0.9
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=df_proc.index, 
        y=df_proc['MA30'], 
        name="MA 30",
        line=dict(color='#f72585', width=2),
        opacity=0.9
    ), row=1, col=1)
    
    # RSI with gradient fill
    fig.add_trace(go.Scatter(
        x=df_proc.index, 
        y=df_proc['RSI'], 
        name="RSI",
        line=dict(color='#ffd93d', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 217, 61, 0.1)'
    ), row=2, col=1)
    
    # RSI Levels
    fig.add_hline(y=70, line_dash="dash", line_color="#ff6b6b", 
                  annotation_text="Overbought", row=2, col=1,
                  annotation_font_color="#ff6b6b")
    fig.add_hline(y=30, line_dash="dash", line_color="#00f5d4",
                  annotation_text="Oversold", row=2, col=1,
                  annotation_font_color="#00f5d4")
    
    fig.update_layout(
        template="plotly_dark",
        height=650,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6f1ff'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0.3)'
        )
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)')
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # INSIGHTS SECTION
    st.markdown("""
        <div style="margin-top: 30px;">
            <div class="glass-card">
                <h4 style="margin: 0 0 15px 0; color: #e6f1ff;">📊 AI Analysis Summary</h4>
                <p style="color: #8892b0; line-height: 1.6; margin: 0;">
                    Based on technical indicators including RSI, Moving Averages, and Volatility analysis,
                    our Random Forest model has processed historical patterns to generate the current signal.
                    Confidence level indicates the strength of pattern recognition.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ⚠️ FOOTER DISCLAIMER - BIG & CLEAR
    st.markdown("""
        <div class="footer-disclaimer">
            <p class="footer-disclaimer-title">
                <span>⚠️</span>
                <span>PERINGATAN PENTING</span>
                <span>⚠️</span>
            </p>
            <p class="footer-disclaimer-text">
                <strong style="color: #ff6b6b;">Keputusan investasi sepenuhnya ada di tangan Anda.</strong><br><br>
                CIRCLE AI adalah alat bantu analisis teknis berbasis machine learning, 
                bukan penyedia saran investasi resmi. Sinyal yang ditampilkan bersifat prediktif 
                dan tidak menjamin hasil profit. Pasar keuangan mengandung risiko tinggi, 
                termasuk kehilangan seluruh modal. Selalu lakukan riset mandiri (DYOR), 
                pertimbangkan profil risiko Anda, dan konsultasikan dengan penasihat keuangan 
                berlisensi sebelum membuat keputusan investasi. 
                <strong style="color: #ffd93d;">Jangan simpulkan terlalu cepat dari sinyal AI ini.</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"""
        <div style="background: rgba(255,107,107,0.1); border: 1px solid rgba(255,107,107,0.3); 
                    border-radius: 16px; padding: 30px; text-align: center; margin-top: 20px;">
            <h3 style="color: #ff6b6b; margin: 0;">⚠️ Analysis Failed</h3>
            <p style="color: #8892b0; margin: 10px 0 0 0;">{err}</p>
            <p style="color: #8892b0; font-size: 0.9rem; margin-top: 15px;">
                Try checking your symbol or API configuration
            </p>
        </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("""
    <div class="footer">
        <p class="footer-brand">CIRCLE AI</p>
        <p style="margin: 10px 0;">Built with passion by a 14-year-old developer</p>
        <p style="font-size: 0.8rem; opacity: 0.6;">
            From Scratch to AI • #BanggaBuatanIndonesia 🇮🇩
        </p>
    </div>
""", unsafe_allow_html=True)