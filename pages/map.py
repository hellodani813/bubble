import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math

# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="나의 필터 버블 지도",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 파스텔 디자인 시스템
# =========================================================
PASTEL = {
    "bg":        "#FFF9FB",   # 메인 배경 (아주 연한 라벤더-핑크)
    "card":      "#FFFFFF",
    "lavender":  "#C7B8FF",
    "mint":      "#A8E6CF",
    "peach":     "#FFD3B6",
    "pink":      "#FFC8DD",
    "sky":       "#B5D8FA",
    "yellow":    "#FFE5A0",
    "coral":     "#FFAAA5",
    "text":      "#5B5170",   # 부드러운 보랏빛 그레이
    "text_soft": "#8B82A8",
    "border":    "#EFE9F7",
    "muted":     "#D8D4E8"
}

# 카테고리별 파스텔 색상
CAT_COLORS = {
    "스포츠":   "#B5D8FA",   # 베이비 블루
    "정치":     "#FFAAA5",   # 코랄
    "게임":     "#C7B8FF",   # 라벤더
    "연예":     "#FFC8DD",   # 베이비 핑크
    "사건사고": "#FFD3B6",   # 피치
    "교육":     "#A8E6CF"    # 민트
}

CAT_ICONS = {
    "스포츠": "⚽", "정치": "🗳️", "게임": "🎮",
    "연예": "🎤", "사건사고": "🚨", "교육": "📚"
}

categories = ["스포츠", "정치", "게임", "연예", "사건사고", "교육"]

# =========================================================
# 커스텀 CSS — 파스텔톤
# =========================================================
st.markdown(f"""
<style>
    .stApp {{ background-color: {PASTEL["bg"]}; }}
    .main .block-container {{ padding-top: 2rem; max-width: 1200px; }}

    /* 헤로 배너 — 파스텔 그라데이션 */
    .map-hero {{
        background: linear-gradient(135deg, #FCE7F3 0%, #E0E7FF 50%, #DBEAFE 100%);
        padding: 28px 32px;
        border-radius: 20px;
        margin-bottom: 24px;
        border: 1px solid {PASTEL["border"]};
    }}
    .map-hero h1 {{
        color: {PASTEL["text"]} !important;
        font-size: 26px; font-weight: 700; margin: 0 0 8px 0;
        letter-spacing: -0.5px;
    }}
    .map-hero p {{
        color: {PASTEL["text_soft"]}; font-size: 14px;
        margin: 0; line-height: 1.6;
    }}

    /* 카드 공통 */
    .pastel-card {{
        background: {PASTEL["card"]};
        border: 1px solid {PASTEL["border"]};
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 16px;
    }}

    .card-title {{
        font-size: 15px; font-weight: 700;
        color: {PASTEL["text"]};
        margin-bottom: 14px;
        display: flex; align-items: center; gap: 8px;
    }}

    /* 미니 메트릭 카드 */
    .stat-card {{
        background: {PASTEL["card"]};
        border: 1px solid {PASTEL["border"]};
        border-radius: 16px;
        padding: 16px 18px;
        text-align: left;
    }}
    .stat-card .stat-label {{
        font-size: 11px; font-weight: 600;
        color: {PASTEL["text_soft"]};
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    .stat-card .stat-value {{
        font-size: 26px; font-weight: 700;
        color: {PASTEL["text"]};
        margin-top: 4px;
    }}
    .stat-card .stat-sub {{
        font-size: 11px; color: {PASTEL["text_soft"]};
        margin-top: 2px;
    }}

    /* 컬러 도트 */
    .color-dot {{
        display: inline-block;
        width: 12px; height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
    }}

    /* 범례 행 */
    .legend-row {{
        display: flex; align-items: center;
        font-size: 13px; color: {PASTEL["text"]};
        padding: 6px 0;
    }}

    /* 상태 배지 */
    .status-badge {{
        display: inline-block;
        padding: 5px 12px;
        border-radius: 12px;
        font-size: 12px; font-weight: 600;
        margin: 3px 4px 3px 0;
    }}
    .badge-hot  {{ background: #FEE2E2; color: #9F1239; }}
    .badge-warm {{ background: #FFEDD5; color: #9A3412; }}
    .badge-cool {{ background: #DBEAFE; color: #1E40AF; }}
    .badge-gray {{ background: #F3F4F6; color: #6B7280; }}

    /* 인사이트 박스 */
    .insight-box {{
        background: #FAF5FF;
        border-left: 4px solid {PASTEL["lavender"]};
        border-radius: 12px;
        padding: 14px 16px;
        margin: 10px 0;
        font-size: 13px; line-height: 1.6;
        color: {PASTEL["text"]};
    }}
    .insight-box.warn {{
        background: #FFF7ED;
        border-left-color: {PASTEL["peach"]};
    }}
    .insight-box.good {{
        background: #F0FDF4;
        border-left-color: {PASTEL["mint"]};
    }}

    /* 버튼 */
    .stButton > button {{
        border-radius: 12px;
        font-weight: 600; font-size: 13px;
        border: 1px solid {PASTEL["border"]};
        background: {PASTEL["card"]};
        color: {PASTEL["text"]};
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background: #FAF5FF;
        border-color: {PASTEL["lavender"]};
        color: {PASTEL["text"]};
    }}
    .stButton > button[kind="primary"] {{
        background: {PASTEL["lavender"]};
        color: white;
        border: none;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: #B0A0F5;
        color: white;
    }}

    /* 빈 상태 */
    .empty-state {{
        background: {PASTEL["card"]};
        border: 2px dashed {PASTEL["muted"]};
        border-radius: 20px;
        padding: 50px 30px;
        text-align: center;
        color: {PASTEL["text_soft"]};
    }}
    .empty-state .ico {{ font-size: 48px; margin-bottom: 12px; }}
    .empty-state .ttl {{ font-size: 17px; font-weight: 700; color: {PASTEL["text"]}; margin-bottom: 8px; }}
    .empty-state .msg {{ font-size: 13px; line-height: 1.6; }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 세션 상태 확인 (메인 페이지에서 공유)
# =========================================================
if "weights" not in st.session_state:
    st.session_state.weights = {cat: 1 for cat in categories}
if "click_history" not in st.session_state:
    st.session_state.click_history = []

history = st.session_state.click_history
weights = st.session_state.weights
total_clicks = len(history)
counts = {cat: history.count(cat) for cat in categories}

# =========================================================
# 헤로
# =========================================================
st.markdown("""
<div class="map-hero">
  <h1>🗺️ 나의 필터 버블 지도</h1>
  <p>알고리즘이 나를 어떤 정보에 묶어두고 있는지, 어떤 분야를 가려두고 있는지<br>
  네트워크 지도로 한눈에 확인해 봅시다.</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 빈 상태 처리
# =========================================================
if total_clicks == 0:
    st.markdown("""
    <div class="empty-state">
      <div class="ico">🌸</div>
      <div class="ttl">아직 그릴 지도가 없어요</div>
      <div class="msg">
        메인 페이지로 돌아가 기사를 몇 개 클릭해 보세요.<br>
        클릭 기록이 쌓이면 여기에 나만의 필터 버블 지도가 나타납니다.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# =========================================================
# 상단 통계 카드
# =========================================================
dominant_cat = max(counts, key=counts.get) if any(counts.values()) else "-"
diversity = sum(1 for c in counts.values() if c > 0)
missed_count = sum(1 for c in counts.values() if c == 0)

# 다양성 지수 (Shannon entropy 기반, 0~100 정규화)
if total_clicks > 0:
    probs = [c/total_clicks for c in counts.values() if c > 0]
    entropy = -sum(p * math.log(p) for p in probs) if probs else 0
    max_entropy = math.log(len(categories))
    diversity_score = int((entropy / max_entropy) * 100) if max_entropy > 0 else 0
else:
    diversity_score = 0

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(f"""
    <div class="stat-card">
      <div class="stat-label">총 클릭</div>
      <div class="stat-value">{total_clicks}</div>
      <div class="stat-sub">개의 기사를 읽었어요</div>
    </div>""", unsafe_allow_html=True)
with s2:
    st.markdown(f"""
    <div class="stat-card">
      <div class="stat-label">집중 분야</div>
      <div class="stat-value" style="font-size:20px;">{CAT_ICONS.get(dominant_cat,'')} {dominant_cat}</div>
      <div class="stat-sub">{counts.get(dominant_cat,0)}회 클릭됨</div>
    </div>""", unsafe_allow_html=True)
with s3:
    st.markdown(f"""
    <div class="stat-card">
      <div class="stat-label">탐색 다양성</div>
      <div class="stat-value">{diversity_score}<span style="font-size:14px; color:{PASTEL['text_soft']};">/100</span></div>
      <div class="stat-sub">{diversity}/6 카테고리 탐색</div>
    </div>""", unsafe_allow_html=True)
with s4:
    st.markdown(f"""
    <div class="stat-card">
      <div class="stat-label">사각지대</div>
      <div class="stat-value">{missed_count}<span style="font-size:14px; color:{PASTEL['text_soft']};">개</span></div>
      <div class="stat-sub">아직 안 본 분야</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# =========================================================
# 네트워크 그래프 빌드
# =========================================================
def build_bubble_map():
    # 노드 위치 — 중심 + 카테고리 원형 배치
    # 클릭이 많을수록 중심에 가깝게 (알고리즘에 끌려감)
    pos = {"나": (0, 0)}
    for i, cat in enumerate(categories):
        angle = 2 * math.pi * i / len(categories) - math.pi / 2
        if counts[cat] >= 3:   r = 0.55
        elif counts[cat] >= 1: r = 0.95
        else:                  r = 1.45
        pos[cat] = (r * math.cos(angle), r * math.sin(angle))

    # 카테고리 간 전이 집계
    transitions = {}
    for i in range(len(history) - 1):
        a, b = history[i], history[i + 1]
        if a != b:
            key = tuple(sorted([a, b]))
            transitions[key] = transitions.get(key, 0) + 1

    fig = go.Figure()

    # 1) 전이 엣지 (회색 점선)
    for (a, b), w in transitions.items():
        x0, y0 = pos[a]; x1, y1 = pos[b]
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode='lines',
            line=dict(width=1 + w * 1.0, color=PASTEL["muted"], dash='dot'),
            opacity=0.7, hoverinfo='skip', showlegend=False
        ))

    # 2) 나 → 카테고리 엣지 (카테고리 컬러)
    for cat in categories:
        if counts[cat] == 0:
            continue
        x0, y0 = pos["나"]; x1, y1 = pos[cat]
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode='lines',
            line=dict(width=2 + counts[cat] * 1.8, color=CAT_COLORS[cat]),
            opacity=0.55, hoverinfo='skip', showlegend=False
        ))

    # 3) 카테고리 노드
    node_x, node_y, node_text, node_size, node_color, node_line, node_hover = [], [], [], [], [], [], []
    for cat in categories:
        x, y = pos[cat]
        node_x.append(x); node_y.append(y)
        node_text.append(f"{CAT_ICONS[cat]}<br><b>{cat}</b><br><span style='font-size:10px'>{counts[cat]}회</span>")
        node_size.append(60 + counts[cat] * 14)
        if counts[cat] == 0:
            node_color.append("#F3EFFA")          # 미탐색 — 회색빛 연보라
            node_line.append(PASTEL["muted"])
        else:
            node_color.append(CAT_COLORS[cat])
            node_line.append("white")
        status = '집중 소비' if counts[cat] >= 3 else ('일반 소비' if counts[cat] >= 1 else '미탐색')
        node_hover.append(
            f"<b>{CAT_ICONS[cat]} {cat}</b><br>"
            f"클릭: {counts[cat]}회<br>"
            f"가중치: {weights[cat]}<br>"
            f"상태: {status}"
        )

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        marker=dict(size=node_size, color=node_color,
                    line=dict(width=3, color=node_line)),
        text=node_text, textposition="middle center",
        textfont=dict(size=11, color=PASTEL["text"], family='Pretendard'),
        hovertext=node_hover, hoverinfo='text', showlegend=False
    ))

    # 4) 중심 "나" 노드
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode='markers+text',
        marker=dict(size=78, color="white",
                    line=dict(width=4, color=PASTEL["lavender"])),
        text=["<b>🙋‍♀️<br>나</b>"], textposition="middle center",
        textfont=dict(size=12, color=PASTEL["text"], family='Pretendard'),
        hoverinfo='skip', showlegend=False
    ))

    fig.update_layout(
        showlegend=False, height=520,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor=PASTEL["bg"], paper_bgcolor=PASTEL["bg"],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.8, 1.8]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[-1.8, 1.8], scaleanchor="x", scaleratio=1)
    )
    return fig, transitions

# =========================================================
# 메인 레이아웃 — 지도 + 사이드 정보
# =========================================================
map_col, side_col = st.columns([2, 1], gap="large")

with map_col:
    st.markdown('<div class="pastel-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🌐 나의 정보 소비 네트워크</div>', unsafe_allow_html=True)
    fig, transitions = build_bubble_map()
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with side_col:
    # 범례
    st.markdown('<div class="pastel-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🧭 지도 보는 법</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:13px; color:{PASTEL['text']}; line-height:1.8;">
      <div class="legend-row">
        <span class="color-dot" style="background:{PASTEL['lavender']};"></span>
        가운데 = <b>나</b>
      </div>
      <div class="legend-row">
        <span class="color-dot" style="background:#FFAAA5;"></span>
        가까운 노드 = 자주 본 분야
      </div>
      <div class="legend-row">
        <span class="color-dot" style="background:#F3EFFA; border:1px solid {PASTEL['muted']};"></span>
        멀고 흐린 노드 = 안 본 분야
      </div>
      <div class="legend-row">
        <span style="display:inline-block; width:18px; height:2px; background:{PASTEL['muted']}; margin-right:8px;"></span>
        점선 = 카테고리 간 이동
      </div>
      <div class="legend-row">
        <span style="display:inline-block; width:18px; height:3px; background:{PASTEL['coral']}; margin-right:8px;"></span>
        굵은 선 = 강한 알고리즘 끌림
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 카테고리 상태 요약
    st.markdown('<div class="pastel-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎨 카테고리별 상태</div>', unsafe_allow_html=True)
    for cat in sorted(categories, key=lambda c: -counts[c]):
        c = counts[cat]
        if c >= 3:    badge_cls, badge_txt = "badge-hot", "집중"
        elif c >= 2:  badge_cls, badge_txt = "badge-warm", "자주"
        elif c >= 1:  badge_cls, badge_txt = "badge-cool", "가끔"
        else:         badge_cls, badge_txt = "badge-gray", "미탐색"
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:8px 0; border-bottom:1px solid {PASTEL['border']};">
          <span style="font-size:13px; color:{PASTEL['text']};">
            <span class="color-dot" style="background:{CAT_COLORS[cat]};"></span>
            {CAT_ICONS[cat]} {cat}
          </span>
          <span>
            <span style="font-size:12px; color:{PASTEL['text_soft']}; margin-right:6px;">{c}회</span>
            <span class="status-badge {badge_cls}">{badge_txt}</span>
          </span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 인사이트 분석
# =========================================================
st.markdown('<div class="pastel-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">💡 지도가 알려주는 것들</div>', unsafe_allow_html=True)

hot_cats = [c for c in categories if counts[c] >= 3]
missed_cats = [c for c in categories if counts[c] == 0]

# 가장 자주 오간 경로
top_path = None
if transitions:
    (a, b), w = max(transitions.items(), key=lambda x: x[1])
    top_path = (a, b, w)

ic1, ic2 = st.columns(2)
with ic1:
    if hot_cats:
        cats_txt = ", ".join([f"{CAT_ICONS[c]} {c}" for c in hot_cats])
        st.markdown(f"""
        <div class="insight-box warn">
          <b>🎯 알고리즘의 집중 타깃</b><br>
          {cats_txt} 분야에서 3회 이상 클릭이 발생했습니다.
          알고리즘이 이 분야를 강하게 학습하고 비슷한 콘텐츠 위주로 추천 중이에요.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="insight-box good">
          <b>🌿 균형 잡힌 소비</b><br>
          아직 특정 분야로 쏠리지 않은 건강한 정보 소비 패턴입니다.
        </div>
        """, unsafe_allow_html=True)

    if top_path:
        a, b, w = top_path
        st.markdown(f"""
        <div class="insight-box">
          <b>🔁 가장 잦은 이동 경로</b><br>
          {CAT_ICONS[a]} <b>{a}</b> ↔ {CAT_ICONS[b]} <b>{b}</b> ({w}회)<br>
          이 두 분야가 서로를 강화하는 추천 루프를 형성하고 있어요.
        </div>
        """, unsafe_allow_html=True)

with ic2:
    if missed_cats:
        cats_txt = ", ".join([f"{CAT_ICONS[c]} {c}" for c in missed_cats])
        st.markdown(f"""
        <div class="insight-box warn">
          <b>🌫️ 알고리즘이 가린 영역</b><br>
          {cats_txt} 분야는 아직 한 번도 클릭하지 않았어요.
          이 분야의 중요한 정보가 가려지고 있을 가능성이 있습니다.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="insight-box good">
          <b>🌈 모든 분야 탐색 완료</b><br>
          6개 카테고리를 모두 한 번 이상 살펴봤어요. 멋진 정보 다이어트입니다!
        </div>
        """, unsafe_allow_html=True)

    # 다양성 점수 코멘트
    if diversity_score >= 70:
        msg, cls = "정보 소비가 매우 다양하게 분산되어 있어요. 이상적인 상태입니다.", "good"
    elif diversity_score >= 40:
        msg, cls = "어느 정도 다양성을 유지하고 있지만, 일부 분야로 쏠림이 시작됐어요.", ""
    else:
        msg, cls = "정보 소비가 한쪽으로 크게 치우쳐 있어요. 새로운 분야를 탐색해 보세요.", "warn"
    st.markdown(f"""
    <div class="insight-box {cls}">
      <b>📊 다양성 지수 {diversity_score}/100</b><br>{msg}
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 하단 액션 버튼
# =========================================================
b1, b2, b3 = st.columns([1, 1, 1])
with b1:
    if st.button("🏠 메인 페이지로", use_container_width=True):
        st.switch_page("app.py")
with b2:
    if st.button("🔄 지도 새로고침", use_container_width=True):
        st.rerun()
with b3:
    if st.button("🌱 모든 기록 초기화", type="primary", use_container_width=True):
        st.session_state.weights = {cat: 1 for cat in categories}
        st.session_state.click_history = []
        if "escape_mode" in st.session_state:
            st.session_state.escape_mode = False
            st.session_state.escape_clicks = []
            st.session_state.pre_escape_snapshot = None
        st.rerun()
