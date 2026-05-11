import streamlit as st
import numpy as np
import pandas as pd
import joblib
import os
import time
import plotly.graph_objects as go
import plotly.express as px
from keras.models import load_model

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DDoS Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #161d2e;
    --accent-cyan: #00f5d4;
    --accent-red: #ff4757;
    --accent-yellow: #ffd32a;
    --accent-blue: #0652DD;
    --text-primary: #e8eaf0;
    --text-muted: #6b7280;
    --border: rgba(0,245,212,0.15);
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

/* Hide streamlit branding */
#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── HERO ── */
.hero-container {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(0,245,212,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #00f5d4, #0099ff, #00f5d4);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s infinite linear;
    margin: 0;
    line-height: 1.1;
}
@keyframes shimmer {
    0% { background-position: 0% }
    100% { background-position: 200% }
}
.hero-sub {
    font-family: 'Space Mono', monospace;
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-top: 0.5rem;
    letter-spacing: 1px;
}
.hero-badge {
    display: inline-block;
    background: rgba(0,245,212,0.1);
    border: 1px solid rgba(0,245,212,0.3);
    color: var(--accent-cyan);
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    padding: 4px 12px;
    border-radius: 20px;
    margin-top: 1rem;
    letter-spacing: 2px;
}

/* ── CARDS ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: border-color 0.3s;
}
.metric-card:hover { border-color: rgba(0,245,212,0.4); }
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent-cyan);
    font-family: 'Space Mono', monospace;
    line-height: 1;
}
.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* ── RESULT ALERT ── */
.result-safe {
    background: linear-gradient(135deg, rgba(0,245,212,0.08), rgba(0,245,212,0.03));
    border: 2px solid var(--accent-cyan);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    text-align: center;
}
.result-attack {
    background: linear-gradient(135deg, rgba(255,71,87,0.1), rgba(255,71,87,0.03));
    border: 2px solid var(--accent-red);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    text-align: center;
    animation: pulse-red 1.5s infinite;
}
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,71,87,0.3); }
    50% { box-shadow: 0 0 20px 4px rgba(255,71,87,0.15); }
}
.result-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin: 0.3rem 0;
}
.result-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

/* ── INPUTS ── */
.stSlider > div > div { color: var(--accent-cyan) !important; }
.stSelectbox label, .stSlider label, .stNumberInput label {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #00f5d4, #0099ff) !important;
    color: #0a0e1a !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 2px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(0,245,212,0.3) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px;
    color: var(--text-muted) !important;
    border-radius: 7px !important;
    padding: 0.4rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,245,212,0.1) !important;
    color: var(--accent-cyan) !important;
}

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent-cyan);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem 0;
}

/* ── MODEL SELECTOR ── */
.model-chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    margin: 2px;
}
.chip-rf   { background: rgba(0,245,212,0.1); border:1px solid rgba(0,245,212,0.3); color:#00f5d4; }
.chip-lstm { background: rgba(0,153,255,0.1); border:1px solid rgba(0,153,255,0.3); color:#0099ff; }
.chip-hybrid { background: rgba(255,215,42,0.1); border:1px solid rgba(255,215,42,0.3); color:#ffd32a; }

/* ── CONFIDENCE BAR ── */
.conf-bar-wrap { margin: 0.4rem 0; }
.conf-label {
    display: flex;
    justify-content: space-between;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-bottom: 3px;
}
.conf-bar-bg {
    background: rgba(255,255,255,0.06);
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}

/* ── DATA TABLE ── */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px; }

/* ── UPLOAD ZONE ── */
.uploadedFile { background: var(--bg-card) !important; border: 1px solid var(--border) !important; }

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--accent-cyan) !important; }
</style>
""", unsafe_allow_html=True)


# ── MODEL LOADING ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_all_models():
    models = {}
    artefacts = {}
    base = 'saved_models'
    try:
        models['rf']     = joblib.load(f'{base}/rf_model.pkl')
        models['lstm']   = load_model(f'{base}/lstm_model.keras')
        models['hybrid'] = load_model(f'{base}/hybrid_rf_lstm_model.keras')
        artefacts['scaler']       = joblib.load(f'{base}/scaler.pkl')
        artefacts['leaf_scaler']  = joblib.load(f'{base}/leaf_scaler.pkl')
        artefacts['le']           = joblib.load(f'{base}/label_encoder.pkl')
        artefacts['top_features'] = joblib.load(f'{base}/top_features.pkl')
        return models, artefacts, None
    except Exception as e:
        return None, None, str(e)

models, artefacts, load_error = load_all_models()

# ── PREDICTION HELPERS ────────────────────────────────────────────────────────
def predict_rf(X, models, artefacts):
    X_fs = X[artefacts['top_features']].values
    pred  = models['rf'].predict(X_fs)
    proba = models['rf'].predict_proba(X_fs)
    return pred, proba

def predict_lstm(X, models, artefacts):
    X_fs   = X[artefacts['top_features']].values
    X_3d   = X_fs.reshape(X_fs.shape[0], 1, X_fs.shape[1])
    proba  = models['lstm'].predict(X_3d, verbose=0)
    pred   = np.argmax(proba, axis=1)
    return pred, proba

def predict_hybrid(X, models, artefacts):
    X_fs     = X[artefacts['top_features']].values
    leaves   = models['rf'].apply(X_fs).astype(np.float32)
    leaves   = artefacts['leaf_scaler'].transform(leaves)
    X_3d     = leaves.reshape(leaves.shape[0], 1, leaves.shape[1])
    proba    = models['hybrid'].predict(X_3d, verbose=0)
    pred     = np.argmax(proba, axis=1)
    return pred, proba

def scale_input(df, artefacts):
    return pd.DataFrame(
        artefacts['scaler'].transform(df),
        columns=df.columns
    )

MODEL_INFO = {
    'Random Forest':   {'key': 'rf',     'color': '#00f5d4', 'chip': 'chip-rf',     'fn': predict_rf},
    'LSTM':            {'key': 'lstm',   'color': '#0099ff', 'chip': 'chip-lstm',   'fn': predict_lstm},
    'Hybrid RF-LSTM':  {'key': 'hybrid', 'color': '#ffd32a', 'chip': 'chip-hybrid', 'fn': predict_hybrid},
}

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <p style="font-family:'Space Mono',monospace;font-size:0.7rem;letter-spacing:3px;
              color:#00f5d4;text-transform:uppercase;margin:0 0 0.5rem 0;">
        ◈ NETWORK THREAT INTELLIGENCE
    </p>
    <h1 class="hero-title">DDoS Shield</h1>
    <p class="hero-sub">// REAL-TIME DISTRIBUTED DENIAL-OF-SERVICE DETECTION ENGINE</p>
    <div>
        <span class="hero-badge">RF MODEL</span>
        <span class="hero-badge" style="margin-left:8px;">LSTM MODEL</span>
        <span class="hero-badge" style="margin-left:8px;">HYBRID RF-LSTM</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MODEL LOAD STATUS ─────────────────────────────────────────────────────────
if load_error:
    st.error(f"⚠️ Model files not found: {load_error}")
    st.info("📁 Place your `saved_models/` folder in the same directory as `app.py` and restart.")
    st.markdown("""
    **Expected files:**
    ```
    saved_models/
    ├── rf_model.pkl
    ├── lstm_model.keras
    ├── hybrid_rf_lstm_model.keras
    ├── scaler.pkl
    ├── leaf_scaler.pkl
    ├── label_encoder.pkl
    └── top_features.pkl
    ```
    """)
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 1.5rem 0;">
        <div style="font-size:2.5rem;">🛡️</div>
        <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                    letter-spacing:3px;color:#00f5d4;text-transform:uppercase;">
            DDoS Shield v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">⚙ Configuration</div>', unsafe_allow_html=True)

    selected_model = st.selectbox(
        "Detection Model",
        list(MODEL_INFO.keys()),
        index=2,
        help="Hybrid RF-LSTM generally achieves the highest accuracy."
    )

    st.markdown('<div class="section-header">📊 Model Performance</div>', unsafe_allow_html=True)

    perf_path = 'saved_models/model_performance.csv'
    if os.path.exists(perf_path):
        perf_df = pd.read_csv(perf_path, index_col=0)
        st.dataframe(
            perf_df[['Accuracy','F1-Score','ROC-AUC']].style.format("{:.4f}"),
            use_container_width=True
        )
    else:
        st.caption("model_performance.csv not found.")

    st.markdown('<div class="section-header">ℹ About</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.78rem;color:#6b7280;line-height:1.7;">
    Trained on the <strong style="color:#e8eaf0;">BCCC-CPacket Cloud DDoS 2024</strong> dataset.
    Three architectures available:<br><br>
    <span class="model-chip chip-rf">Random Forest</span> — fast, interpretable<br>
    <span class="model-chip chip-lstm">LSTM</span> — sequence-aware<br>
    <span class="model-chip chip-hybrid">Hybrid RF-LSTM</span> — best accuracy
    </div>
    """, unsafe_allow_html=True)

# ── MAIN TABS ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["  🔍  SINGLE FLOW  ", "  📂  BATCH ANALYSIS  ", "  📈  MODEL INSIGHTS  "])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — SINGLE FLOW
# ════════════════════════════════════════════════════════════════════
with tab1:
    top_features = artefacts['top_features']

    st.markdown('<div class="section-header">🌐 Network Flow Parameters</div>', unsafe_allow_html=True)
    st.caption("Manually enter network flow feature values for real-time classification.")

    # Build input grid
    feature_inputs = {}
    cols_per_row = 5
    rows = [top_features[i:i+cols_per_row] for i in range(0, len(top_features), cols_per_row)]

    for row in rows:
        cols = st.columns(len(row))
        for col, feat in zip(cols, row):
            with col:
                feature_inputs[feat] = st.number_input(
                    feat, value=0.0, format="%.6f", key=f"feat_{feat}",
                    label_visibility="visible"
                )

    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        run_single = st.button("⚡ ANALYSE FLOW", key="single_run")

    if run_single:
        input_df = pd.DataFrame([feature_inputs])

        # Fill missing columns with 0 for scaler
        all_cols = artefacts['scaler'].feature_names_in_ if hasattr(artefacts['scaler'], 'feature_names_in_') else top_features
        for c in all_cols:
            if c not in input_df.columns:
                input_df[c] = 0.0
        input_df = input_df[all_cols]

        with st.spinner("Analysing network flow..."):
            time.sleep(0.6)
            try:
                X_scaled_input = scale_input(input_df, artefacts)
                predict_fn = MODEL_INFO[selected_model]['fn']
                preds, probas = predict_fn(X_scaled_input, models, artefacts)

                pred_label = artefacts['le'].inverse_transform(preds)[0]
                confidence = float(np.max(probas[0])) * 100
                color      = MODEL_INFO[selected_model]['color']
                is_attack  = pred_label.lower() != 'benign'

                # Result banner
                if is_attack:
                    st.markdown(f"""
                    <div class="result-attack">
                        <div style="font-size:2.5rem;">🚨</div>
                        <div class="result-title" style="color:#ff4757;">ATTACK DETECTED</div>
                        <div style="font-size:1.1rem;font-weight:600;color:#ff6b81;margin:0.3rem 0;">
                            {pred_label}
                        </div>
                        <div class="result-sub">Confidence: {confidence:.1f}% | Model: {selected_model}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-safe">
                        <div style="font-size:2.5rem;">✅</div>
                        <div class="result-title" style="color:#00f5d4;">TRAFFIC NORMAL</div>
                        <div style="font-size:1rem;color:#6b7280;margin:0.3rem 0;">Benign Flow</div>
                        <div class="result-sub">Confidence: {confidence:.1f}% | Model: {selected_model}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("")

                # Confidence breakdown
                st.markdown('<div class="section-header">📊 Class Probability Breakdown</div>', unsafe_allow_html=True)
                classes = artefacts['le'].classes_
                proba_vals = probas[0]

                sorted_idx = np.argsort(proba_vals)[::-1]
                for i in sorted_idx:
                    cls_name = classes[i]
                    pct = proba_vals[i] * 100
                    bar_color = '#ff4757' if cls_name.lower() != 'benign' else '#00f5d4'
                    st.markdown(f"""
                    <div class="conf-bar-wrap">
                        <div class="conf-label">
                            <span>{cls_name}</span>
                            <span>{pct:.2f}%</span>
                        </div>
                        <div class="conf-bar-bg">
                            <div class="conf-bar-fill"
                                 style="width:{pct:.1f}%;background:{bar_color};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Gauge chart
                st.markdown("")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=confidence,
                    number={'suffix': '%', 'font': {'size': 36, 'color': color,
                                                     'family': 'Space Mono'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#6b7280',
                                 'tickfont': {'color': '#6b7280', 'size': 10}},
                        'bar':  {'color': color},
                        'bgcolor': 'rgba(0,0,0,0)',
                        'bordercolor': 'rgba(255,255,255,0.05)',
                        'steps': [
                            {'range': [0, 50],  'color': 'rgba(255,71,87,0.08)'},
                            {'range': [50, 80], 'color': 'rgba(255,215,42,0.08)'},
                            {'range': [80, 100],'color': 'rgba(0,245,212,0.08)'},
                        ],
                        'threshold': {'line': {'color': color, 'width': 3},
                                      'thickness': 0.8, 'value': confidence}
                    },
                    title={'text': "Prediction Confidence",
                           'font': {'color': '#6b7280', 'size': 13, 'family': 'Space Mono'}}
                ))
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e8eaf0',
                    height=260,
                    margin=dict(t=40, b=10, l=30, r=30)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            except Exception as e:
                st.error(f"Prediction failed: {e}")

# ════════════════════════════════════════════════════════════════════
# TAB 2 — BATCH ANALYSIS
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📂 Batch CSV Upload</div>', unsafe_allow_html=True)
    st.caption("Upload a CSV file with network flow features for bulk classification.")

    uploaded = st.file_uploader(
        "Drop your CSV here", type=['csv'],
        help="CSV must contain the same features used during training."
    )

    if uploaded:
        try:
            raw_df = pd.read_csv(uploaded)
            raw_df.columns = raw_df.columns.str.strip()
            st.success(f"✅ Loaded {len(raw_df):,} rows × {raw_df.shape[1]} columns")

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown("**Preview (first 5 rows)**")
                st.dataframe(raw_df.head(), use_container_width=True)

            # Check features
            missing_feats = [f for f in top_features if f not in raw_df.columns]
            if missing_feats:
                st.warning(f"⚠️ Missing features: {missing_feats}. They will be filled with 0.")
                for f in missing_feats:
                    raw_df[f] = 0.0

            col_run1, col_run2, col_run3 = st.columns([1,2,1])
            with col_run2:
                run_batch = st.button("⚡ RUN BATCH ANALYSIS", key="batch_run")

            if run_batch:
                with st.spinner(f"Running {selected_model} on {len(raw_df):,} flows..."):
                    time.sleep(0.5)

                    # Scale
                    all_cols = artefacts['scaler'].feature_names_in_ \
                               if hasattr(artefacts['scaler'], 'feature_names_in_') \
                               else top_features
                    for c in all_cols:
                        if c not in raw_df.columns:
                            raw_df[c] = 0.0
                    input_df = raw_df[all_cols].copy()
                    input_df = input_df.fillna(0.0)
                    X_scaled_batch = scale_input(input_df, artefacts)

                    predict_fn = MODEL_INFO[selected_model]['fn']
                    preds_batch, probas_batch = predict_fn(X_scaled_batch, models, artefacts)
                    labels_batch = artefacts['le'].inverse_transform(preds_batch)
                    confidence_batch = np.max(probas_batch, axis=1) * 100

                    result_df = raw_df.copy()
                    result_df['Predicted_Label'] = labels_batch
                    result_df['Confidence_%']    = confidence_batch.round(2)
                    result_df['Is_Attack']       = result_df['Predicted_Label'].str.lower() != 'benign'

                    # ── SUMMARY METRICS ──
                    n_total   = len(result_df)
                    n_attack  = result_df['Is_Attack'].sum()
                    n_benign  = n_total - n_attack
                    avg_conf  = confidence_batch.mean()

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.markdown(f"""<div class="metric-card">
                            <div class="metric-value">{n_total:,}</div>
                            <div class="metric-label">Total Flows</div></div>""",
                            unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"""<div class="metric-card">
                            <div class="metric-value" style="color:#ff4757;">{n_attack:,}</div>
                            <div class="metric-label">Attack Flows</div></div>""",
                            unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"""<div class="metric-card">
                            <div class="metric-value">{n_benign:,}</div>
                            <div class="metric-label">Benign Flows</div></div>""",
                            unsafe_allow_html=True)
                    with c4:
                        st.markdown(f"""<div class="metric-card">
                            <div class="metric-value">{avg_conf:.1f}%</div>
                            <div class="metric-label">Avg Confidence</div></div>""",
                            unsafe_allow_html=True)

                    st.markdown("")

                    # ── CHARTS ──
                    col_ch1, col_ch2 = st.columns(2)

                    with col_ch1:
                        label_counts = pd.Series(labels_batch).value_counts()
                        colors_pie = ['#ff4757' if l.lower() != 'benign' else '#00f5d4'
                                      for l in label_counts.index]
                        fig_pie = go.Figure(go.Pie(
                            labels=label_counts.index,
                            values=label_counts.values,
                            hole=0.55,
                            marker_colors=colors_pie,
                            textfont=dict(family='Space Mono', size=11),
                        ))
                        fig_pie.update_layout(
                            title=dict(text='Traffic Classification', font=dict(color='#e8eaf0', size=13,
                                                                                 family='Space Mono')),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#e8eaf0',
                            legend=dict(font=dict(color='#6b7280', size=10)),
                            height=300,
                            margin=dict(t=40, b=10, l=10, r=10)
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)

                    with col_ch2:
                        fig_hist = go.Figure(go.Histogram(
                            x=confidence_batch,
                            nbinsx=20,
                            marker_color='#0099ff',
                            marker_line_color='rgba(0,153,255,0.3)',
                            marker_line_width=1,
                            opacity=0.85
                        ))
                        fig_hist.update_layout(
                            title=dict(text='Confidence Distribution', font=dict(color='#e8eaf0', size=13,
                                                                                   family='Space Mono')),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#e8eaf0',
                            xaxis=dict(title='Confidence %', color='#6b7280', gridcolor='rgba(255,255,255,0.05)'),
                            yaxis=dict(title='Count',        color='#6b7280', gridcolor='rgba(255,255,255,0.05)'),
                            height=300,
                            margin=dict(t=40, b=40, l=40, r=10)
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)

                    # ── RESULTS TABLE ──
                    st.markdown('<div class="section-header">📋 Prediction Results</div>',
                                unsafe_allow_html=True)
                    display_cols = top_features[:3] + ['Predicted_Label', 'Confidence_%', 'Is_Attack']
                    display_cols = [c for c in display_cols if c in result_df.columns]
                    st.dataframe(result_df[display_cols], use_container_width=True, height=300)

                    # ── DOWNLOAD ──
                    csv_out = result_df.to_csv(index=False).encode('utf-8')
                    col_dl1, col_dl2, col_dl3 = st.columns([1,2,1])
                    with col_dl2:
                        st.download_button(
                            label="⬇ DOWNLOAD RESULTS CSV",
                            data=csv_out,
                            file_name='ddos_predictions.csv',
                            mime='text/csv'
                        )
        except Exception as e:
            st.error(f"Error processing file: {e}")
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem;border:2px dashed rgba(0,245,212,0.15);
                    border-radius:12px;color:#6b7280;">
            <div style="font-size:2.5rem;margin-bottom:1rem;">📂</div>
            <div style="font-family:'Space Mono',monospace;font-size:0.8rem;letter-spacing:1px;">
                DROP A CSV FILE TO BEGIN BATCH ANALYSIS
            </div>
            <div style="font-size:0.75rem;margin-top:0.5rem;">
                Supports unlimited rows — results downloadable as CSV
            </div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 — MODEL INSIGHTS
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🏆 Model Comparison</div>', unsafe_allow_html=True)

    perf_path = 'saved_models/model_performance.csv'
    if os.path.exists(perf_path):
        perf_df = pd.read_csv(perf_path, index_col=0)
        numeric_cols = perf_df.select_dtypes(include=np.number).columns.tolist()

        # Bar chart comparison
        metrics_to_plot = [c for c in ['Accuracy','Precision','Recall','F1-Score','ROC-AUC']
                           if c in numeric_cols]
        model_colors = ['#00f5d4', '#0099ff', '#ffd32a']

        fig_bar = go.Figure()
        for i, (idx, row) in enumerate(perf_df.iterrows()):
            fig_bar.add_trace(go.Bar(
                name=str(idx),
                x=metrics_to_plot,
                y=[row[m] for m in metrics_to_plot],
                marker_color=model_colors[i % len(model_colors)],
                marker_line_color='rgba(0,0,0,0.2)',
                marker_line_width=1,
                opacity=0.9,
                text=[f'{row[m]:.4f}' for m in metrics_to_plot],
                textposition='outside',
                textfont=dict(family='Space Mono', size=9, color='#e8eaf0')
            ))
        fig_bar.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf0',
            xaxis=dict(color='#6b7280', gridcolor='rgba(255,255,255,0.04)'),
            yaxis=dict(color='#6b7280', gridcolor='rgba(255,255,255,0.04)',
                       range=[0, 1.12]),
            legend=dict(font=dict(color='#e8eaf0', family='Space Mono', size=11),
                        bgcolor='rgba(0,0,0,0.3)', bordercolor='rgba(255,255,255,0.1)'),
            height=380,
            margin=dict(t=20, b=40, l=40, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Radar chart
        st.markdown('<div class="section-header">🕸 Performance Radar</div>', unsafe_allow_html=True)
        radar_metrics = [c for c in ['Accuracy','Precision','Recall','F1-Score','ROC-AUC']
                         if c in numeric_cols]
        fig_radar = go.Figure()
        fill_colors = [
            'rgba(0,245,212,0.08)',
            'rgba(0,153,255,0.08)',
            'rgba(255,215,42,0.08)',
        ]
        for i, (idx, row) in enumerate(perf_df.iterrows()):
            vals = [row[m] for m in radar_metrics] + [row[radar_metrics[0]]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=radar_metrics + [radar_metrics[0]],
                fill='toself',
                name=str(idx),
                line_color=model_colors[i % len(model_colors)],
                fillcolor=fill_colors[i % len(fill_colors)],
                opacity=0.9
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0,1], color='#6b7280',
                                gridcolor='rgba(255,255,255,0.06)'),
                angularaxis=dict(color='#6b7280', gridcolor='rgba(255,255,255,0.06)')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Space Mono', color='#e8eaf0', size=11),
            legend=dict(font=dict(color='#e8eaf0', family='Space Mono', size=11),
                        bgcolor='rgba(0,0,0,0.3)'),
            height=380,
            margin=dict(t=20, b=20, l=60, r=60)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Raw table
        st.markdown('<div class="section-header">📋 Full Metrics Table</div>', unsafe_allow_html=True)
        st.dataframe(perf_df.style.format({c: '{:.4f}' for c in numeric_cols})
                               .highlight_max(axis=0, color='rgba(0,245,212,0.2)'),
                     use_container_width=True)
    else:
        st.info("model_performance.csv not found in saved_models/.")

    # Feature importance
    st.markdown('<div class="section-header">🔬 Top Features Used</div>', unsafe_allow_html=True)
    top_feats = artefacts['top_features']
    if hasattr(models['rf'], 'feature_importances_'):
        importances = models['rf'].feature_importances_
        feat_df = pd.DataFrame({'Feature': top_feats, 'Importance': importances}).sort_values(
            'Importance', ascending=True
        )
        fig_feat = go.Figure(go.Bar(
            x=feat_df['Importance'],
            y=feat_df['Feature'],
            orientation='h',
            marker=dict(
                color=feat_df['Importance'],
                colorscale=[[0,'#0099ff'],[1,'#00f5d4']],
                line_color='rgba(0,0,0,0.1)',
                line_width=1
            ),
            text=[f'{v:.4f}' for v in feat_df['Importance']],
            textposition='outside',
            textfont=dict(family='Space Mono', size=9, color='#6b7280')
        ))
        fig_feat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf0',
            xaxis=dict(color='#6b7280', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(color='#e8eaf0', gridcolor='rgba(255,255,255,0.03)'),
            height=360,
            margin=dict(t=10, b=30, l=160, r=60)
        )
        st.plotly_chart(fig_feat, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="
    text-align: center;
    padding: 2rem 1rem 1.5rem 1rem;
    background: linear-gradient(135deg, rgba(0,245,212,0.03), rgba(0,153,255,0.03));
    border: 1px solid rgba(0,245,212,0.08);
    border-radius: 12px;
    margin-top: 1rem;
">
    <div style="
        font-family: 'Space Mono', monospace;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #00f5d4, #0099ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    ">
        Faiza Muhammad Tukur
    </div>
    <div style="
        font-family: 'Space Mono', monospace;
        font-size: 0.68rem;
        color: #6b7280;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    ">
        DDoS Shield &nbsp;·&nbsp; Network Threat Intelligence Engine
    </div>
    <div style="
        font-size: 0.72rem;
        color: #4b5563;
        font-family: 'Space Mono', monospace;
        letter-spacing: 1px;
    ">
        © 2026 Faiza Muhammad Tukur. All rights reserved. &nbsp;™
    </div>
    <div style="
        margin-top: 0.8rem;
        font-size: 0.65rem;
        color: #374151;
        font-family: 'Space Mono', monospace;
        letter-spacing: 1px;
    ">
        Built with ❤ using Random Forest · LSTM · Hybrid RF-LSTM
    </div>
</div>
""", unsafe_allow_html=True)
