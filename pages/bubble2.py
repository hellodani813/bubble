import streamlit as st
import random
import pandas as pd
import feedparser
import urllib.parse
import re
import html

# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="추천 알고리즘 버블 체험",
    page_icon="🫧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 커스텀 CSS — 가독성 강화
# =========================================================
st.markdown("""
<style>
    .main { background-color: #FAFAFC; }

    .hero-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 28px 32px;
        border-radius: 14px;
        color: white;
        margin-bottom: 20px;
    }
    .hero-banner h1 {
        color: white !important;
        margin: 0 0 8px 0;
        font-size: 28px;
        font-weight: 700;
    }
    .hero-banner p {
        color: rgba(255,255,255,0.92);
        margin: 0;
        font-size: 15px;
        line-height: 1.6;
    }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #111827;
        padding: 6px 0 12px 0;
        border-bottom: 2px solid #E5E7EB;
        margin-bottom: 14px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border-radius: 12px !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }

    .cat-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 8px;
        letter-spacing: 0.3px;
    }
    .cat-스포츠 { background:#DBEAFE; color:#1E40AF; }
    .cat-정치   { background:#FEE2E2; color:#991B1B; }
    .cat-게임   { background:#E0E7FF; color:#4338CA; }
    .cat-연예   { background:#FCE7F3; color:#9D174D; }
    .cat-사건사고 { background:#FEF3C7; color:#92400E; }
    .cat-교육   { background:#D1FAE5; color:#065F46; }

    .news-title {
        font-size: 15px;
        font-weight: 600;
        color: #1F2937;
        line-height: 1.45;
        min-height: 44px;
        margin-bottom: 6px;
    }
    .news-source {
        font-size: 11px;
        color: #6B7280;
        margin-bottom: 10px;
    }

    .bubble-card {
        padding: 16px 18px;
        border-radius: 12px;
        margin-bottom: 14px;
        border-left: 5px solid;
    }
    .bubble-lv1 { background:#ECFDF5; border-color:#10B981; }
    .bubble-lv2 { background:#FFFBEB; border-color:#F59E0B; }
    .bubble-lv3 { background:#FFF7ED; border-color:#F97316; }
    .bubble-lv4 { background:#FEF2F2; border-color:#EF4444; }
    .bubble-card .lv-label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        opacity: 0.7;
    }
    .bubble-card .lv-title {
        font-size: 17px;
        font-weight: 700;
        margin: 2px 0 4px 0;
        color: #111827;
    }
    .bubble-card .lv-desc {
        font-size: 13px;
        color: #4B5563;
        line-height: 1.5;
    }

    .stage-dots { display:flex; gap:6px; margin-top:10px; }
    .dot { flex:1; height:6px; border-radius:3px; background:#E5E7EB; }
    .dot.active-1 { background:#10B981; }
    .dot.active-2 { background:#F59E0B; }
    .dot.active-3 { background:#F97316; }
    .dot.active-4 { background:#EF4444; }

    .personality-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .personality-type {
        font-size: 22px;
        font-weight: 700;
        color: #4F46E5;
        margin-bottom: 6px;
    }
    .personality-desc {
        font-size: 13px;
        color: #4B5563;
        line-height: 1.6;
    }

    .mini-metric {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 12px 14px;
    }
    .mini-metric .label { font-size:11px; color:#6B7280; font-weight:600; }
    .mini-metric .value { font-size:22px; color:#111827; font-weight:700; margin-top:2px; }

    .escape-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 18px;
        height: 100%;
    }
    .escape-card .num {
        display:inline-block;
        width:28px; height:28px; border-radius:8px;
        background:#4F46E5; color:white;
        text-align:center; line-height:28px;
        font-weight:700; font-size:14px;
        margin-bottom: 10px;
    }
    .escape-card h4 { margin:4px 0 6px 0; font-size:15px; color:#111827; }
    .escape-card p { font-size:13px; color:#4B5563; line-height:1.6; margin:0; }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 카테고리 정의
# =========================================================
categories = ["스포츠", "정치", "게임", "연예", "사건사고", "교육"]

CAT_ICONS = {
    "스포츠": "⚽", "정치": "🗳️", "게임": "🎮",
    "연예": "🎤", "사건사고": "🚨", "교육": "📚"
}

# 구글 뉴스 검색에 최적화된 검색 키워드
CAT_QUERIES = {
    "스포츠": "스포츠",
    "정치":   "정치",
    "게임":   "게임",
    "연예":   "연예",
    "사건사고": "사건사고",
    "교육":   "교육"
}

# 버블 심화 시 추가될 자극적인 키워드
EXTREME_KEYWORDS = ["논란", "충격", "단독", "의혹", "분노"]

# =========================================================
# 세션 상태
# =========================================================
if "weights" not in st.session_state:
    st.session_state.weights = {cat: 1 for cat in categories}
if "click_history" not in st.session_state:
    st.session_state.click_history = []

# =========================================================
# 구글 뉴스 RSS 연동
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_google_news(category, is_extreme):
    """
    구글 뉴스 RSS에서 카테고리별 뉴스 제목을 가져옵니다.
    - 무료, API 키 불필요
    - is_extreme=True 이면 자극적인 키워드를 OR 조건으로 추가하여
      버블이 심해질수록 자극적인 기사가 노출되도록 설계
    """
    base_query = CAT_QUERIES.get(category, category)

    if is_extreme:
        # 예: "정치 (논란 OR 충격 OR 단독 OR 의혹 OR 분노)"
        extreme_part = " OR ".join(EXTREME_KEYWORDS)
        query = f"{base_query} ({extreme_part})"
    else:
        query = base_query

    # 한국어 한국 지역 결과
    encoded = urllib.parse.quote(query)
    url = (
        f"https://news.google.com/rss/search?"
        f"q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    )

    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return None

        items = []
        for entry in feed.entries[:25]:
            title = entry.get("title", "")
            # HTML 엔티티 정리
            title = html.unescape(title)
            # 구글 뉴스는 "제목 - 언론사" 형식 → 분리
            if " - " in title:
                title_part, source = title.rsplit(" - ", 1)
            else:
                title_part, source = title, "출처 미상"
            title_part = re.sub(r'<[^>]+>', '', title_part).strip()
            if title_part:
                items.append({"title": title_part, "source": source.strip()})
        return items if items else None
    except Exception:
        return None

# =========================================================
# 더미 데이터 (네트워크 실패 시 fallback)
# =========================================================
normal_titles = {
    "스포츠": ["손흥민, 경기 MVP 선정", "NBA 플레이오프 명승부", "프로야구 순위 경쟁 치열",
              "V리그 챔피언 결정전 프리뷰", "전국 체전 학생부 신기록 달성"],
    "정치":   ["정책 토론 주요 쟁점 정리", "사회 현안 논의 확대", "정부 새 정책 발표",
              "여야, 민생 법안 합의 시도", "이번 주 정당 지지율 여론조사"],
    "게임":   ["신작 게임 출시 기대감", "인기 게임 e스포츠 대회 개최", "게이밍 트렌드 변화 분석",
              "모바일 게임 매출 순위 업데이트", "인기 스트리머 합방 소식"],
    "연예":   ["인기 아이돌 성공적인 컴백", "화제의 웹드라마 전편 공개",
              "주말 예능 프로그램 시청률 1위", "K팝 아티스트 빌보드 차트 진입"],
    "교육":   ["AI 시대가 바꾸는 교실 풍경", "뇌과학 기반 효과적인 공부법 연구",
              "10년 뒤 미래 직업 변화 전망", "새 학기 달라지는 중학교 학교 규정"],
    "사건사고": ["경찰, 대규모 보이스피싱 일당 검거", "주말 고속도로 다중 추돌 사고",
                "전국 집중 호우 대비 태세", "건조한 날씨 산불 주의보 발령"]
}

extreme_titles = {
    "스포츠": ["충격! 대표팀 대참사", "역대급 오심 논란, 팬들 분노", "벤치클리어링 발발, 난장판 된 경기장"],
    "정치":   ["정치권 초비상 사태", "국민 여론 폭발, 대규모 시위 예고", "막말 논란에 정치권 발칵"],
    "게임":   ["역대급 게임 중독 논란 확산", "서버 터짐! 유저들 분노 폭발", "심각한 과금 유도 논란"],
    "연예":   ["연예계 발칵 뒤집힌 충격 소식", "팬들 멘붕, 단독 열애설 포착", "소속사 분쟁 심화"],
    "교육":   ["AI가 모든 교사를 완전히 대체한다?", "10년 후 멸종할 직업 리스트", "수능 전면 폐지론 대두"],
    "사건사고": ["충격 단독! 전 국민이 속고 있었다", "흉악 범죄 발생, 시민들 불안", "전 국민 경악한 유출 CCTV"]
}

def get_fallback_items(category, is_extreme):
    pool = extreme_titles[category] if is_extreme else normal_titles[category]
    return [{"title": t, "source": "예시 데이터"} for t in pool]

# =========================================================
# 알고리즘 로직
# =========================================================
def get_bubble_level():
    c = len(st.session_state.click_history)
    if c <= 2: return 1
    elif c <= 5: return 2
    elif c <= 9: return 3
    return 4

def get_feed():
    bubble_level = get_bubble_level()
    is_extreme = bubble_level >= 3

    weighted = []
    for cat in categories:
        weighted.extend([cat] * st.session_state.weights[cat])
    chosen = random.choices(weighted, k=6)
    cat_counts = {cat: chosen.count(cat) for cat in set(chosen)}

    feed = []
    for cat, count in cat_counts.items():
        pool = fetch_google_news(cat, is_extreme)
        if not pool or len(pool) < count:
            pool = get_fallback_items(cat, is_extreme)

        if count <= len(pool):
            sampled = random.sample(pool, count)
        else:
            sampled = random.choices(pool, k=count)

        for it in sampled:
            feed.append({
                "title": it["title"],
                "source": it["source"],
                "category": cat
            })
    random.shuffle(feed)
    return feed

def click_content(item):
    cat = item["category"]
    st.session_state.click_history.append(cat)
    st.session_state.weights[cat] += 3

def analyze_personality():
    history = st.session_state.click_history
    if not history:
        return "분석 대기 중", "콘텐츠를 클릭하면 분석이 시작됩니다.", "⏳"
    counts = {cat: history.count(cat) for cat in categories}
    dominant = max(counts, key=counts.get)
    if len(set(history)) >= 4:
        return "균형 탐색형", "다양한 분야의 관점을 고르게 탐색하는 건강한 성향입니다.", "🌍"
    labels = {
        "스포츠":   ("스포츠 몰입형", "⚽"),
        "정치":     ("이슈 집중형", "🗳️"),
        "게임":     ("몰입형 게이머", "🎮"),
        "연예":     ("트렌드 민감형", "🎤"),
        "사건사고": ("도파민 추구형", "🚨"),
        "교육":     ("지식 탐구형", "📚")
    }
    name, icon = labels[dominant]
    return name, f"현재 **{dominant}** 카테고리를 집중 소비 중입니다.", icon

# =========================================================
# 헤더
# =========================================================
st.markdown("""
<div class="hero-banner">
  <h1>🫧 추천 알고리즘과 필터 버블 체험</h1>
  <p>마음에 드는 기사를 계속 클릭해 보세요. AI가 여러분의 취향을 학습하여 점점 비슷한 뉴스만 보여줍니다.<br>
  나도 모르게 갇히는 <b>필터 버블</b>이 만들어지는 과정을 직접 체험해 봅시다.</p>
</div>
""", unsafe_allow_html=True)

# 상단 미니 메트릭
total_clicks = len(st.session_state.click_history)
bubble_level = get_bubble_level()
dominant_cat = max(st.session_state.weights, key=st.session_state.weights.get) if total_clicks else "-"
diversity = len(set(st.session_state.click_history))

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="mini-metric"><div class="label">총 클릭 수</div><div class="value">{total_clicks}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="mini-metric"><div class="label">버블 단계</div><div class="value">Lv. {bubble_level}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="mini-metric"><div class="label">우세 카테고리</div><div class="value" style="font-size:18px;">{CAT_ICONS.get(dominant_cat,"")} {dominant_cat}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="mini-metric"><div class="label">탐색 다양성</div><div class="value">{diversity} / 6</div></div>', unsafe_allow_html=True)

st.write("")

# =========================================================
# 2-컬럼 레이아웃
# =========================================================
left_col, right_col = st.columns([1.3, 1], gap="large")

# ---------- 좌측: 추천 피드 ----------
with left_col:
    st.markdown('<div class="section-title">📰 맞춤형 실시간 추천 피드</div>', unsafe_allow_html=True)

    with st.spinner("구글 뉴스에서 최신 기사를 불러오는 중..."):
        feed = get_feed()

    feed_col1, feed_col2 = st.columns(2, gap="medium")

    for i, item in enumerate(feed):
        target = feed_col1 if i % 2 == 0 else feed_col2
        with target:
            with st.container(border=True):
                cat = item["category"]
                icon = CAT_ICONS.get(cat, "📂")
                st.markdown(
                    f'<span class="cat-badge cat-{cat}">{icon} {cat}</span>',
                    unsafe_allow_html=True
                )
                st.markdown(f'<div class="news-title">{item["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="news-source">📡 {item["source"]}</div>', unsafe_allow_html=True)
                if st.button("기사 보기 →", key=f"btn_{i}_{total_clicks}", use_container_width=True):
                    click_content(item)
                    st.rerun()

# ---------- 우측: 실시간 분석 ----------
with right_col:
    st.markdown('<div class="section-title">🤖 실시간 AI 분석</div>', unsafe_allow_html=True)

    bubble_meta = {
        1: ("LEVEL 1", "균형 상태", "다양한 정보가 고르게 추천되고 있습니다.", "bubble-lv1"),
        2: ("LEVEL 2", "버블 형성 시작", "특정 분야의 추천 비율이 늘기 시작했습니다.", "bubble-lv2"),
        3: ("LEVEL 3", "버블 심화 (주의)", "자극적인 기사가 늘고, 다른 분야가 사라지고 있습니다.", "bubble-lv3"),
        4: ("LEVEL 4", "필터 버블 고착", "완전히 갇혔습니다. 좋아하는 정보만 보입니다.", "bubble-lv4"),
    }
    lv_label, lv_title, lv_desc, lv_class = bubble_meta[bubble_level]

    dots_html = ""
    for i in range(1, 5):
        active = f"active-{bubble_level}" if i <= bubble_level else ""
        dots_html += f'<div class="dot {active}"></div>'

    st.markdown(f"""
    <div class="bubble-card {lv_class}">
      <div class="lv-label">{lv_label}</div>
      <div class="lv-title">{lv_title}</div>
      <div class="lv-desc">{lv_desc}</div>
      <div class="stage-dots">{dots_html}</div>
    </div>
    """, unsafe_allow_html=True)

    ptype, desc, picon = analyze_personality()
    st.markdown(f"""
    <div class="personality-card">
      <div style="font-size:11px; color:#6B7280; font-weight:600;">디지털 성향 리포트</div>
      <div class="personality-type">{picon} {ptype}</div>
      <div class="personality-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    if total_clicks >= 5:
        st.warning(f"🚨 정보 환경이 **{dominant_cat}** 위주로 좁아지고 있습니다.")

    st.markdown("**📊 카테고리별 추천 강도**")
    df = pd.DataFrame({
        "카테고리": [f"{CAT_ICONS[c]} {c}" for c in st.session_state.weights.keys()],
        "추천 강도": list(st.session_state.weights.values())
    })
    st.bar_chart(df.set_index("카테고리"), height=240, color="#4F46E5")

# =========================================================
# 하단: 탈출 팁
# =========================================================
st.divider()
st.markdown('<div class="section-title">🛡️ 필터 버블에서 탈출하는 3가지 방법</div>', unsafe_allow_html=True)

e1, e2, e3 = st.columns(3, gap="medium")
with e1:
    st.markdown("""
    <div class="escape-card">
      <div class="num">1</div>
      <h4>🗑️ 시청·검색 기록 지우기</h4>
      <p>주기적으로 유튜브·포털 검색 기록과 쿠키를 삭제해 알고리즘을 초기화하세요.</p>
    </div>
    """, unsafe_allow_html=True)
with e2:
    st.markdown("""
    <div class="escape-card">
      <div class="num">2</div>
      <h4>🕵️ 시크릿 모드 사용</h4>
      <p>과거 데이터가 반영되지 않는 시크릿 브라우징으로 새로운 정보를 탐색하세요.</p>
    </div>
    """, unsafe_allow_html=True)
with e3:
    st.markdown("""
    <div class="escape-card">
      <div class="num">3</div>
      <h4>⚖️ 반대 의견 찾아보기</h4>
      <p>좋아하는 기사만 보지 말고, 일부러 다른 시각의 콘텐츠를 클릭해 보세요.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# =========================================================
# 핵심 키워드 + 리셋
# =========================================================
b1, b2 = st.columns([3, 1])
with b1:
    st.markdown("#### 🎓 오늘의 수업 핵심 키워드")
    st.success("✅ 필터 버블 (Filter Bubble) · ✅ 확증 편향 (Confirmation Bias) · ✅ 추천 알고리즘 윤리 · ✅ 디지털 리터러시")
with b2:
    st.write("")
    if st.button("🔄 기록 초기화 (버블 탈출)", type="primary", use_container_width=True):
        st.session_state.weights = {cat: 1 for cat in categories}
        st.session_state.click_history = []
        st.cache_data.clear()
        st.rerun()
