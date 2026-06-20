import streamlit as st
import random
import pandas as pd
import feedparser
import urllib.parse
import re
import html
from datetime import datetime

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
# 커스텀 CSS — 감성 파스텔톤 테마
# =========================================================
st.markdown("""
<style>
    /* ============ 전체 배경 ============ */
    .stApp { background-color: #FFFBF7; }
    .main  { background-color: #FFFBF7; }

    /* ============ Hero 배너 ============ */
    .hero-banner {
        background: linear-gradient(135deg, #FFD6E8 0%, #C8B6E2 50%, #B5D8E8 100%);
        padding: 28px 32px; border-radius: 18px; color: #5B4B7C; margin-bottom: 20px;
        border: 1px solid #F0E6F7;
    }
    .hero-banner h1 { color: #5B4B7C !important; margin: 0 0 8px 0; font-size: 28px; font-weight: 700; }
    .hero-banner p  { color: #6B5B8C; margin: 0; font-size: 15px; line-height: 1.6; }

    /* ============ 섹션 타이틀 ============ */
    .section-title {
        font-size: 18px; font-weight: 700; color: #5B4B7C;
        padding: 6px 0 12px 0; border-bottom: 2px solid #F0E6F7; margin-bottom: 14px;
    }

    /* ============ 카드 공통 ============ */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF; border-radius: 16px !important;
        border: 1px solid #F0E6F7 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(183, 148, 244, 0.15);
    }

    /* ============ 카테고리 뱃지 (파스텔) ============ */
    .cat-badge {
        display: inline-block; padding: 4px 12px; border-radius: 12px;
        font-size: 11px; font-weight: 600; margin-bottom: 8px; letter-spacing: 0.3px;
    }
    .cat-스포츠   { background:#D6EAFE; color:#5B7DB1; }
    .cat-정치     { background:#FFE0E0; color:#B86B7A; }
    .cat-게임     { background:#E2DBFA; color:#8B7AC8; }
    .cat-연예     { background:#FFE0EF; color:#C97AAB; }
    .cat-사건사고 { background:#FFEEDB; color:#C48C5B; }
    .cat-교육     { background:#D9F0E0; color:#6BA37A; }

    /* ============ 기사 카드 텍스트 ============ */
    .news-title {
        font-size: 15px; font-weight: 600; color: #3D3354;
        line-height: 1.45; min-height: 44px; margin-bottom: 6px;
    }
    .news-source { font-size: 11px; color: #9B8FB8; margin-bottom: 10px; }

    /* ============ 원문 링크 버튼 ============ */
    .news-link-btn {
        display: inline-block; width: 100%; text-align: center;
        padding: 8px 12px; background: #F8F4FF;
        color: #8B7AC8 !important; border: 1px solid #E2DBFA;
        border-radius: 10px; font-size: 13px; font-weight: 600;
        text-decoration: none !important; margin-top: 6px;
        transition: background 0.15s ease, border-color 0.15s ease;
        box-sizing: border-box;
    }
    .news-link-btn:hover {
        background: #EFE7FF; border-color: #B794F4; text-decoration: none !important;
    }

    /* ============ 관심 없음 버튼 영역 ============ */
    .skip-zone {
        background: #FFF4E6; border: 1.5px dashed #FFD4A3;
        border-radius: 16px; padding: 16px 18px; margin-top: 14px;
        text-align: center;
    }
    .skip-zone .ttl { font-size:13px; font-weight:700; color:#C48C5B; margin-bottom:6px; }
    .skip-zone .desc { font-size:12px; color:#A47C5B; line-height:1.5; }

    /* ============ 버블 단계 카드 ============ */
    .bubble-card {
        padding: 16px 18px; border-radius: 14px;
        margin-bottom: 14px; border-left: 5px solid;
    }
    .bubble-lv1 { background:#E8F5EC; border-color:#A8D8B5; }
    .bubble-lv2 { background:#FFF6E0; border-color:#FFD68A; }
    .bubble-lv3 { background:#FFE9D6; border-color:#FFB088; }
    .bubble-lv4 { background:#FFE0E0; border-color:#FFA8B8; }
    .bubble-card .lv-label { font-size:12px; font-weight:700; letter-spacing:0.5px; color:#7C6A8B; opacity:0.8; }
    .bubble-card .lv-title { font-size:17px; font-weight:700; margin:2px 0 4px 0; color:#5B4B7C; }
    .bubble-card .lv-desc  { font-size:13px; color:#6B5B8C; line-height:1.5; }

    /* ============ 단계 도트 ============ */
    .stage-dots { display:flex; gap:6px; margin-top:10px; }
    .dot { flex:1; height:6px; border-radius:3px; background:#F0E6F7; }
    .dot.active-1 { background:#A8D8B5; }
    .dot.active-2 { background:#FFD68A; }
    .dot.active-3 { background:#FFB088; }
    .dot.active-4 { background:#FFA8B8; }

    /* ============ 성향 카드 ============ */
    .personality-card {
        background: linear-gradient(135deg, #FAF4FF 0%, #FFFBF7 100%);
        border: 1px solid #F0E6F7; border-radius: 14px;
        padding: 18px; margin-bottom: 14px;
    }
    .personality-type { font-size:22px; font-weight:700; color:#8B7AC8; margin-bottom:6px; }
    .personality-desc { font-size:13px; color:#6B5B8C; line-height:1.6; }

    /* ============ 미니 메트릭 ============ */
    .mini-metric {
        background: #FFFFFF; border: 1px solid #F0E6F7; border-radius: 14px; padding: 12px 14px;
    }
    .mini-metric .label { font-size:11px; color:#9B8FB8; font-weight:600; }
    .mini-metric .value { font-size:22px; color:#5B4B7C; font-weight:700; margin-top:2px; }

    /* ============ 비중 가로 막대 ============ */
    .share-row {
        display:flex; align-items:center; gap:10px; margin-bottom:10px;
    }
    .share-label {
        width:90px; font-size:13px; font-weight:600; color:#5B4B7C; flex-shrink:0;
    }
    .share-bar-wrap {
        flex:1; background:#F8F4FF; height:22px; border-radius:11px; overflow:hidden;
    }
    .share-bar {
        height:100%;
        background: linear-gradient(90deg, #C8B6E2, #B794F4);
        border-radius:11px;
        transition: width 0.4s ease;
    }
    .share-value {
        width:80px; font-size:12px; font-weight:600; color:#5B4B7C; text-align:right; flex-shrink:0;
    }

    /* ============ 탈출 챌린지 Hero ============ */
    .escape-hero {
        background: linear-gradient(135deg, #C8EBD8 0%, #B5D8E8 100%);
        padding: 22px 26px; border-radius: 18px; color: #4A6B5B; margin-bottom: 18px;
        border: 1px solid #D9F0E0;
    }
    .escape-hero h2 { color:#4A6B5B !important; margin:0 0 6px 0; font-size:22px; font-weight:700; }
    .escape-hero p  { color:#5B7D6B; margin:0; font-size:14px; line-height:1.6; }

    /* ============ 탈출 진행도 ============ */
    .escape-progress-wrap {
        background:#FFFFFF; border:1px solid #D9F0E0; border-radius:14px;
        padding:16px 18px; margin-bottom:16px;
    }
    .escape-progress-label {
        display:flex; justify-content:space-between; align-items:center;
        font-size:13px; font-weight:600; color:#5B4B7C; margin-bottom:8px;
    }
    .escape-progress-bar {
        width:100%; height:12px; background:#F0F8F2; border-radius:6px; overflow:hidden;
    }
    .escape-progress-fill {
        height:100%; background:linear-gradient(90deg, #A8D8B5, #8BC9A1); border-radius:6px;
        transition: width 0.4s ease;
    }
    .escape-progress-meta { font-size:11px; color:#7BA38A; margin-top:6px; }

    /* ============ 안 본 카테고리 카드 ============ */
    .missed-card {
        background: #FFFFFF; border:1px solid #F0E6F7; border-left:4px solid #A8D8B5;
        border-radius:14px; padding:14px; margin-bottom:10px;
    }
    .missed-card .ttl { font-size:11px; color:#7BA38A; font-weight:700; letter-spacing:0.5px; }
    .missed-card .name { font-size:16px; font-weight:700; color:#5B4B7C; margin:2px 0 4px 0; }
    .missed-card .desc { font-size:12px; color:#9B8FB8; }

    /* ============ 탈출 성공 ============ */
    .escape-success {
        background: linear-gradient(135deg, #E8F5EC 0%, #FFF4E6 100%);
        border:2px solid #A8D8B5; border-radius:16px;
        padding:18px; text-align:center; margin-bottom:14px;
    }
    .escape-success .ttl { font-size:14px; color:#7BA38A; font-weight:700; }
    .escape-success .msg { font-size:18px; color:#4A6B5B; font-weight:700; margin-top:4px; }

    /* ============ 댓글 (생각 나누기) ============ */
    .reflect-question {
        background:#FAF4FF; border:1px solid #F0E6F7; border-radius:12px;
        padding:14px 16px; margin-bottom:10px;
    }
    .reflect-question .qnum {
        display:inline-block; background:#B794F4; color:#FFFFFF;
        font-size:11px; font-weight:700; padding:3px 10px; border-radius:8px;
        margin-right:8px; letter-spacing:0.3px;
    }
    .reflect-question .qcount {
        float:right; background:#FFE0EF; color:#C97AAB;
        font-size:11px; font-weight:600; padding:3px 10px; border-radius:12px;
    }
    .reflect-question .qtext {
        font-size:14px; font-weight:600; color:#5B4B7C; line-height:1.5;
    }
    .comment-card {
        background:#FFFFFF; border:1px solid #F0E6F7; border-radius:12px;
        padding:12px 14px; margin-bottom:8px;
    }
    .comment-head {
        display:flex; justify-content:space-between; align-items:center;
        margin-bottom:6px;
    }
    .comment-author { font-size:12px; font-weight:700; color:#8B7AC8; }
    .comment-time   { font-size:11px; color:#B5A8C9; }
    .comment-body {
        font-size:13px; color:#5B4B7C; line-height:1.6;
        white-space:pre-wrap; word-break:break-word;
    }
    .no-comments {
        text-align:center; padding:20px; color:#B5A8C9;
        font-size:12px; background:#FAF4FF; border-radius:12px;
        border:1px dashed #E2DBFA;
    }

    /* ============ 탈출 팁 카드 ============ */
    .escape-card {
        background: #FFFFFF; border: 1px solid #F0E6F7; border-radius: 14px;
        padding: 18px; height: 100%;
    }
    .escape-card .num {
        display:inline-block; width:28px; height:28px; border-radius:10px;
        background: linear-gradient(135deg, #C8B6E2, #B794F4);
        color:#FFFFFF; text-align:center; line-height:28px;
        font-weight:700; font-size:14px; margin-bottom: 10px;
    }
    .escape-card h4 { margin:4px 0 6px 0; font-size:15px; color:#5B4B7C; }
    .escape-card p  { font-size:13px; color:#7C6A8B; line-height:1.6; margin:0; }

    /* ============ Streamlit 기본 위젯 톤 보정 ============ */
    .stButton > button {
        border-radius: 12px; font-weight: 600; font-size: 13px;
        background: #F8F4FF; color: #8B7AC8;
        border: 1px solid #E2DBFA;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background: #EFE7FF; border-color: #B794F4;
        color: #7A66B8;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #C8B6E2, #B794F4);
        color: #FFFFFF !important;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #B794F4, #A47CE0);
    }

    /* alert 박스 톤 부드럽게 */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid #F0E6F7 !important;
    }

    /* expander, divider */
    hr { border-color: #F0E6F7 !important; }
    
    /* 헤딩 색 통일 */
    h1, h2, h3, h4, h5, h6 { color: #5B4B7C; }

    /* 캡션 */
    .stCaption, [data-testid="stCaptionContainer"] { color: #9B8FB8 !important; }
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

CAT_DESC = {
    "스포츠": "경기와 선수들의 활약, 건강한 경쟁의 세계",
    "정치":   "사회를 움직이는 정책과 시민의 목소리",
    "게임":   "디지털 문화와 e스포츠의 흐름",
    "연예":   "대중문화·음악·드라마 트렌드",
    "사건사고": "안전과 사회 이슈에 대한 경각심",
    "교육":   "배움과 미래를 위한 지식"
}

CAT_QUERIES = {c: c for c in categories}
EXTREME_KEYWORDS = ["논란", "충격", "단독", "의혹", "분노"]

# 파스텔 차트 컬러
PASTEL_PRIMARY = "#B794F4"   # 라벤더
PASTEL_GREEN   = "#A8D8B5"   # 민트
PASTEL_PEACH   = "#FFB088"   # 피치

REFLECT_QUESTIONS = [
    {"id": "q1", "text": "평소에 잘 안 보던 카테고리의 기사를 읽으니 어떤 느낌이 들었나요?"},
    {"id": "q2", "text": "알고리즘이 나에게 보여주지 않았던 정보 중에 중요한 내용이 있었나요?"},
    {"id": "q3", "text": "일상에서 어떻게 하면 필터 버블에 갇히지 않을 수 있을까요?"}
]

# =========================================================
# 세션 상태
# =========================================================
if "weights" not in st.session_state:
    st.session_state.weights = {cat: 1 for cat in categories}
if "click_history" not in st.session_state:
    st.session_state.click_history = []
if "escape_mode" not in st.session_state:
    st.session_state.escape_mode = False
if "escape_clicks" not in st.session_state:
    st.session_state.escape_clicks = []
if "pre_escape_snapshot" not in st.session_state:
    st.session_state.pre_escape_snapshot = None
if "comments" not in st.session_state:
    st.session_state.comments = {q["id"]: [] for q in REFLECT_QUESTIONS}
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
if "skip_count" not in st.session_state:
    st.session_state.skip_count = 0
if "current_feed" not in st.session_state:
    st.session_state.current_feed = None
if "escape_samples" not in st.session_state:
    st.session_state.escape_samples = {}

# =========================================================
# 구글 뉴스 RSS
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_google_news(category, is_extreme):
    base_query = CAT_QUERIES.get(category, category)
    if is_extreme:
        extreme_part = " OR ".join(EXTREME_KEYWORDS)
        query = f"{base_query} ({extreme_part})"
    else:
        query = base_query

    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    google_search_url = f"https://news.google.com/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"

    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return None
        items = []
        for entry in feed.entries[:25]:
            title = html.unescape(entry.get("title", ""))
            if " - " in title:
                title_part, source = title.rsplit(" - ", 1)
            else:
                title_part, source = title, "출처 미상"
            title_part = re.sub(r'<[^>]+>', '', title_part).strip()
            link = entry.get("link", "").strip() or google_search_url
            if title_part:
                items.append({"title": title_part, "source": source.strip(), "link": link})
        return items if items else None
    except Exception:
        return None

# =========================================================
# 더미 데이터
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
    "스포츠": ["충격! 대표팀 대참사", "역대급 오심 논란, 팬들 분노", "벤치클리어링 발발"],
    "정치":   ["정치권 초비상 사태", "국민 여론 폭발, 대규모 시위 예고", "막말 논란에 정치권 발칵"],
    "게임":   ["역대급 게임 중독 논란 확산", "서버 터짐! 유저들 분노 폭발", "심각한 과금 유도 논란"],
    "연예":   ["연예계 발칵 뒤집힌 충격 소식", "팬들 멘붕, 단독 열애설 포착", "소속사 분쟁 심화"],
    "교육":   ["AI가 모든 교사를 완전히 대체한다?", "10년 후 멸종할 직업 리스트", "수능 전면 폐지론 대두"],
    "사건사고": ["충격 단독! 전 국민이 속고 있었다", "흉악 범죄 발생, 시민들 불안", "전 국민 경악한 유출 CCTV"]
}

def get_fallback_items(category, is_extreme):
    pool = extreme_titles[category] if is_extreme else normal_titles[category]
    items = []
    for t in pool:
        q = urllib.parse.quote(t)
        link = f"https://news.google.com/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
        items.append({"title": t, "source": "예시 데이터", "link": link})
    return items

# =========================================================
# 알고리즘 로직
# =========================================================
def get_bubble_level():
    c = len(st.session_state.click_history)
    if c <= 2: return 1
    elif c <= 5: return 2
    elif c <= 9: return 3
    return 4

def build_feed():
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
        sampled = random.sample(pool, count) if count <= len(pool) else random.choices(pool, k=count)
        for it in sampled:
            feed.append({
                "title": it["title"], "source": it["source"],
                "link": it.get("link", "#"), "category": cat
            })
    random.shuffle(feed)
    return feed

def ensure_feed():
    if st.session_state.current_feed is None:
        st.session_state.current_feed = build_feed()
    return st.session_state.current_feed

def refresh_feed():
    st.session_state.current_feed = build_feed()

def click_content(item):
    cat = item["category"]
    st.session_state.click_history.append(cat)
    st.session_state.weights[cat] += 3
    refresh_feed()
    st.session_state.escape_samples = {}

def skip_feed():
    st.session_state.skip_count += 1
    if st.session_state.click_history:
        dominant = max(st.session_state.weights, key=st.session_state.weights.get)
        if st.session_state.weights[dominant] > 1:
            st.session_state.weights[dominant] = max(1, st.session_state.weights[dominant] - 1)
    refresh_feed()

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

def get_missed_categories():
    history = st.session_state.click_history
    counts = {cat: history.count(cat) for cat in categories}
    avg = max(1, len(history) / len(categories))
    return [c for c in categories if counts[c] < avg]

def get_escape_sample(cat):
    if cat not in st.session_state.escape_samples:
        pool = fetch_google_news(cat, is_extreme=False) or get_fallback_items(cat, False)
        st.session_state.escape_samples[cat] = (
            random.choice(pool) if pool else {"title": f"{cat} 분야 기사", "source": "예시", "link": "#"}
        )
    return st.session_state.escape_samples[cat]

def start_escape():
    st.session_state.pre_escape_snapshot = {
        "weights": dict(st.session_state.weights),
        "history": list(st.session_state.click_history),
        "dominant": max(st.session_state.weights, key=st.session_state.weights.get),
        "diversity": len(set(st.session_state.click_history))
    }
    st.session_state.escape_mode = True
    st.session_state.escape_clicks = []
    st.session_state.escape_samples = {}

def escape_click(category):
    st.session_state.escape_clicks.append(category)
    st.session_state.weights[category] += 2
    dominant = max(st.session_state.weights, key=st.session_state.weights.get)
    if dominant != category and st.session_state.weights[dominant] > 1:
        st.session_state.weights[dominant] = max(1, st.session_state.weights[dominant] - 2)
    st.session_state.click_history.append(category)
    refresh_feed()
    st.session_state.escape_samples = {}

def reset_all():
    st.session_state.weights = {cat: 1 for cat in categories}
    st.session_state.click_history = []
    st.session_state.escape_mode = False
    st.session_state.escape_clicks = []
    st.session_state.pre_escape_snapshot = None
    st.session_state.skip_count = 0
    st.session_state.current_feed = None
    st.session_state.escape_samples = {}
    st.cache_data.clear()

def add_comment(qid, author, body):
    if not body.strip():
        return False
    author = author.strip() if author.strip() else "익명의 학생"
    st.session_state.comments[qid].append({
        "author": author, "body": body.strip(),
        "time": datetime.now().strftime("%H:%M")
    })
    return True

def delete_comment(qid, index):
    if 0 <= index < len(st.session_state.comments[qid]):
        st.session_state.comments[qid].pop(index)

def render_comment_section(qid, qnum, qtext):
    count = len(st.session_state.comments[qid])
    st.markdown(f"""
    <div class="reflect-question">
      <span class="qnum">Q{qnum}</span>
      <span class="qcount">💬 {count}개의 생각</span>
      <div class="qtext" style="margin-top:6px;">{html.escape(qtext)}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form(key=f"form_{qid}", clear_on_submit=True):
        c1, c2 = st.columns([1, 3])
        with c1:
            nick = st.text_input("닉네임", value=st.session_state.nickname,
                                 key=f"nick_{qid}", placeholder="이름 또는 닉네임",
                                 label_visibility="collapsed")
        with c2:
            body = st.text_input("내 생각", key=f"body_{qid}",
                                 placeholder="자유롭게 내 생각을 적어보세요...",
                                 label_visibility="collapsed")
        submitted = st.form_submit_button("💬 생각 남기기", use_container_width=False)
        if submitted:
            if add_comment(qid, nick, body):
                if nick.strip():
                    st.session_state.nickname = nick.strip()
                st.rerun()
            else:
                st.warning("내용을 입력해 주세요.")

    comments = st.session_state.comments[qid]
    if not comments:
        st.markdown('<div class="no-comments">아직 작성된 생각이 없습니다. 첫 번째 의견을 남겨보세요!</div>',
                    unsafe_allow_html=True)
    else:
        for idx in range(len(comments) - 1, -1, -1):
            c = comments[idx]
            cc1, cc2 = st.columns([10, 1])
            with cc1:
                st.markdown(f"""
                <div class="comment-card">
                  <div class="comment-head">
                    <span class="comment-author">👤 {html.escape(c['author'])}</span>
                    <span class="comment-time">🕒 {c['time']}</span>
                  </div>
                  <div class="comment-body">{html.escape(c['body'])}</div>
                </div>
                """, unsafe_allow_html=True)
            with cc2:
                st.write("")
                if st.button("🗑️", key=f"del_{qid}_{idx}_{c['time']}", help="삭제"):
                    delete_comment(qid, idx)
                    st.rerun()
    st.write("")

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

total_clicks = len(st.session_state.click_history)
bubble_level = get_bubble_level()
dominant_cat = max(st.session_state.weights, key=st.session_state.weights.get) if total_clicks else "-"
diversity = len(set(st.session_state.click_history))

m1, m2, m3, m4, m5 = st.columns(5)
with m1: st.markdown(f'<div class="mini-metric"><div class="label">총 클릭 수</div><div class="value">{total_clicks}</div></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="mini-metric"><div class="label">버블 단계</div><div class="value">Lv. {bubble_level}</div></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="mini-metric"><div class="label">우세 카테고리</div><div class="value" style="font-size:18px;">{CAT_ICONS.get(dominant_cat,"")} {dominant_cat}</div></div>', unsafe_allow_html=True)
with m4: st.markdown(f'<div class="mini-metric"><div class="label">탐색 다양성</div><div class="value">{diversity} / 6</div></div>', unsafe_allow_html=True)
with m5: st.markdown(f'<div class="mini-metric"><div class="label">건너뛰기</div><div class="value">{st.session_state.skip_count}</div></div>', unsafe_allow_html=True)

st.write("")

# =========================================================
# 2-컬럼
# =========================================================
left_col, right_col = st.columns([1.3, 1], gap="large")

with left_col:
    st.markdown('<div class="section-title">📰 맞춤형 실시간 추천 피드</div>', unsafe_allow_html=True)
    st.caption("💡 **기사 보기** 버튼은 알고리즘 학습용, **원문 읽기** 버튼은 실제 뉴스 페이지로 이동합니다.")

    with st.spinner("구글 뉴스에서 최신 기사를 불러오는 중..."):
        feed = ensure_feed()

    feed_col1, feed_col2 = st.columns(2, gap="medium")
    for i, item in enumerate(feed):
        target = feed_col1 if i % 2 == 0 else feed_col2
        with target:
            with st.container(border=True):
                cat = item["category"]
                icon = CAT_ICONS.get(cat, "📂")
                st.markdown(f'<span class="cat-badge cat-{cat}">{icon} {cat}</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="news-title">{html.escape(item["title"])}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="news-source">📡 {html.escape(item["source"])}</div>', unsafe_allow_html=True)

                btn_key = f"btn_{i}_{cat}_{total_clicks}_{st.session_state.skip_count}"
                if st.button("기사 보기 → (알고리즘 학습)",
                             key=btn_key, use_container_width=True):
                    click_content(item)
                    st.rerun()

                link = item.get("link", "#")
                st.markdown(
                    f'<a class="news-link-btn" href="{html.escape(link)}" '
                    f'target="_blank" rel="noopener noreferrer">🔗 원문 읽기 (새 탭)</a>',
                    unsafe_allow_html=True
                )

    st.markdown(f"""
    <div class="skip-zone">
      <div class="ttl">😐 이 중에 관심 있는 기사가 없나요?</div>
      <div class="desc">버튼을 누르면 우세 카테고리의 추천 강도가 살짝 줄어들고 새 기사가 추천됩니다.<br>
      알고리즘에게 <b>"이건 별로다"</b>라는 부정 신호를 보내는 학습입니다.</div>
    </div>
    """, unsafe_allow_html=True)
    sk1, sk2, sk3 = st.columns([1, 2, 1])
    with sk2:
        if st.button("🔄 관심 있는 기사가 없어요 — 다른 기사 보기",
                     use_container_width=True,
                     key=f"skip_{st.session_state.skip_count}"):
            skip_feed()
            st.rerun()

with right_col:
    st.markdown('<div class="section-title">🤖 실시간 AI 분석</div>', unsafe_allow_html=True)
    bubble_meta = {
        1: ("LEVEL 1", "균형 상태", "다양한 정보가 고르게 추천되고 있습니다.", "bubble-lv1"),
        2: ("LEVEL 2", "버블 형성 시작", "특정 분야의 추천 비율이 늘기 시작했습니다.", "bubble-lv2"),
        3: ("LEVEL 3", "버블 심화 (주의)", "자극적인 기사가 늘고, 다른 분야가 사라지고 있습니다.", "bubble-lv3"),
        4: ("LEVEL 4", "필터 버블 고착", "완전히 갇혔습니다. 좋아하는 정보만 보입니다.", "bubble-lv4"),
    }
    lv_label, lv_title, lv_desc, lv_class = bubble_meta[bubble_level]
    dots_html = "".join([
        f'<div class="dot {"active-"+str(bubble_level) if i <= bubble_level else ""}"></div>'
        for i in range(1, 5)
    ])
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
      <div style="font-size:11px; color:#9B8FB8; font-weight:600;">디지털 성향 리포트</div>
      <div class="personality-type">{picon} {ptype}</div>
      <div class="personality-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    if total_clicks >= 5:
        st.warning(f"🚨 정보 환경이 **{dominant_cat}** 위주로 좁아지고 있습니다.")

    st.markdown("**📊 내가 학습시킨 키워드 분석**")
    click_counts = {cat: st.session_state.click_history.count(cat) for cat in categories}

    tab_w, tab_c, tab_p, tab_t = st.tabs(["추천 강도", "클릭 횟수", "비중", "추이"])

    with tab_w:
        st.caption("AI가 각 카테고리에 부여한 추천 가중치입니다. 클릭할수록 해당 카테고리가 커집니다.")
        df_w = pd.DataFrame({
            "카테고리": [f"{CAT_ICONS[c]} {c}" for c in categories],
            "추천 강도": [st.session_state.weights[c] for c in categories]
        })
        st.bar_chart(df_w.set_index("카테고리"), height=240, color=PASTEL_PRIMARY)

    with tab_c:
        st.caption("실제로 내가 클릭한 카테고리별 횟수입니다.")
        if total_clicks == 0:
            st.info("아직 클릭한 기사가 없습니다.")
        else:
            df_c = pd.DataFrame({
                "카테고리": [f"{CAT_ICONS[c]} {c}" for c in categories],
                "클릭 횟수": [click_counts[c] for c in categories]
            })
            st.bar_chart(df_c.set_index("카테고리"), height=240, color=PASTEL_GREEN)
            max_cat = max(click_counts, key=click_counts.get)
            min_cat = min(click_counts, key=click_counts.get)
            ic1, ic2 = st.columns(2)
            with ic1:
                st.markdown(f'<div class="mini-metric"><div class="label">가장 많이 본 카테고리</div><div class="value" style="font-size:15px;">{CAT_ICONS[max_cat]} {max_cat} ({click_counts[max_cat]}회)</div></div>', unsafe_allow_html=True)
            with ic2:
                st.markdown(f'<div class="mini-metric"><div class="label">가장 안 본 카테고리</div><div class="value" style="font-size:15px;">{CAT_ICONS[min_cat]} {min_cat} ({click_counts[min_cat]}회)</div></div>', unsafe_allow_html=True)

    with tab_p:
        st.caption("전체 클릭 중 각 카테고리가 차지하는 비율입니다.")
        if total_clicks == 0:
            st.info("아직 클릭한 기사가 없습니다.")
        else:
            sorted_cats = sorted(categories, key=lambda c: click_counts[c], reverse=True)
            html_rows = ""
            for c in sorted_cats:
                cnt = click_counts[c]
                pct = (cnt / total_clicks * 100) if total_clicks > 0 else 0
                html_rows += f"""
                <div class="share-row">
                  <div class="share-label">{CAT_ICONS[c]} {c}</div>
                  <div class="share-bar-wrap"><div class="share-bar" style="width:{pct:.1f}%;"></div></div>
                  <div class="share-value">{pct:.1f}% ({cnt}회)</div>
                </div>
                """
            st.markdown(html_rows, unsafe_allow_html=True)
            top_pct = (click_counts[sorted_cats[0]] / total_clicks * 100) if total_clicks else 0
            if top_pct >= 60:
                st.error(f"⚠️ 1위 카테고리가 전체의 {top_pct:.0f}%를 차지합니다. 편향이 심합니다.")
            elif top_pct >= 40:
                st.warning(f"📌 1위 카테고리가 {top_pct:.0f}%로 비중이 높습니다.")
            else:
                st.success(f"✅ 1위 카테고리가 {top_pct:.0f}%로 비교적 균형 잡혀 있습니다.")

    with tab_t:
        st.caption("클릭이 누적되면서 각 카테고리의 점유율이 어떻게 변했는지 보여줍니다.")
        if total_clicks == 0:
            st.info("아직 클릭한 기사가 없습니다.")
        else:
            rows = []
            cumulative = {c: 0 for c in categories}
            for step, cat in enumerate(st.session_state.click_history, start=1):
                cumulative[cat] += 1
                row = {"클릭 순서": step}
                for c in categories:
                    row[f"{CAT_ICONS[c]} {c}"] = cumulative[c]
                rows.append(row)
            df_t = pd.DataFrame(rows).set_index("클릭 순서")
            # 다중 라인용 파스텔 팔레트
            st.line_chart(df_t, height=260,
                          color=["#B794F4", "#FFB088", "#A8D8B5", "#FFA8B8", "#8BC4E8", "#FFD68A"])

# =========================================================
# 탈출 체험
# =========================================================
st.divider()
st.markdown("""
<div class="escape-hero">
  <h2>🪂 필터 버블 탈출 챌린지</h2>
  <p>알고리즘이 숨겨버린 다른 시각의 뉴스를 직접 찾아 클릭해 보세요.<br>
  <b>4가지 이상의 다양한 카테고리</b>를 탐색하면 필터 버블에서 탈출할 수 있습니다.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.escape_mode:
    info_col, btn_col = st.columns([2, 1])
    with info_col:
        if total_clicks == 0:
            st.info("🪴 먼저 위에서 기사 몇 개를 클릭해 본인의 알고리즘을 만들어 보세요. 그 후 탈출 체험이 의미 있어집니다.")
        elif diversity >= 4:
            st.success(f"✨ 이미 **{diversity}가지** 카테고리를 탐색했네요! 그래도 탈출 체험을 해보면 다양성의 가치를 더 잘 알 수 있어요.")
        else:
            st.warning(f"⚠️ 현재 **{diversity}가지** 카테고리만 보고 있어요. 탈출 챌린지를 시작해 시야를 넓혀봅시다.")
    with btn_col:
        st.write("")
        if st.button("🚀 탈출 챌린지 시작하기", type="primary", use_container_width=True,
                     disabled=(total_clicks == 0)):
            start_escape()
            st.rerun()

else:
    escape_diversity = len(set(st.session_state.escape_clicks))
    GOAL = 4
    progress_pct = min(100, int(escape_diversity / GOAL * 100))
    escaped = escape_diversity >= GOAL

    st.markdown(f"""
    <div class="escape-progress-wrap">
      <div class="escape-progress-label">
        <span>🎯 다양성 회복 진행도</span>
        <span style="color:#7BA38A;">{escape_diversity} / {GOAL} 카테고리</span>
      </div>
      <div class="escape-progress-bar">
        <div class="escape-progress-fill" style="width:{progress_pct}%;"></div>
      </div>
      <div class="escape-progress-meta">탈출 클릭 수: {len(st.session_state.escape_clicks)}회 · 목표: 서로 다른 {GOAL}개 카테고리 탐색</div>
    </div>
    """, unsafe_allow_html=True)

    if escaped:
        snap = st.session_state.pre_escape_snapshot
        st.markdown("""
        <div class="escape-success">
          <div class="ttl">🎉 CHALLENGE COMPLETED</div>
          <div class="msg">필터 버블 탈출 성공! 다양한 시각을 회복했습니다.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### 📊 Before vs After 비교")
        before_dom = snap["dominant"]
        after_dom = max(st.session_state.weights, key=st.session_state.weights.get)
        before_div = snap["diversity"]
        after_div = len(set(st.session_state.click_history))

        ba1, ba2 = st.columns(2)
        with ba1:
            st.markdown(f"""
            <div class="mini-metric">
              <div class="label">BEFORE — 탈출 전</div>
              <div class="value" style="font-size:16px;">우세: {CAT_ICONS.get(before_dom,'')} {before_dom}</div>
              <div style="font-size:12px; color:#9B8FB8; margin-top:4px;">탐색 다양성: {before_div} / 6</div>
            </div>
            """, unsafe_allow_html=True)
        with ba2:
            st.markdown(f"""
            <div class="mini-metric" style="border-color:#A8D8B5;">
              <div class="label" style="color:#7BA38A;">AFTER — 탈출 후</div>
              <div class="value" style="font-size:16px;">우세: {CAT_ICONS.get(after_dom,'')} {after_dom}</div>
              <div style="font-size:12px; color:#7BA38A; margin-top:4px;">탐색 다양성: {after_div} / 6 ↑</div>
            </div>
            """, unsafe_allow_html=True)

        comp_df = pd.DataFrame({
            "카테고리": [f"{CAT_ICONS[c]} {c}" for c in categories],
            "Before": [snap["weights"][c] for c in categories],
            "After":  [st.session_state.weights[c] for c in categories]
        }).set_index("카테고리")
        st.bar_chart(comp_df, height=260, color=["#C8B6E2", "#A8D8B5"])

        st.markdown("##### 🧠 함께 생각해 봐요")
        st.caption("아래 질문에 자유롭게 본인의 생각을 남겨보세요. 친구들의 의견도 확인할 수 있어요.")

        total_comments = sum(len(v) for v in st.session_state.comments.values())
        if total_comments > 0:
            st.markdown(f"📊 지금까지 **{total_comments}개의 생각**이 모였어요!")

        for idx, q in enumerate(REFLECT_QUESTIONS, start=1):
            render_comment_section(q["id"], idx, q["text"])

        st.divider()
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("🔁 다시 탈출 챌린지 도전", use_container_width=True):
                st.session_state.escape_mode = False
                st.session_state.escape_clicks = []
                st.session_state.escape_samples = {}
                st.rerun()
        with rc2:
            if st.button("🌱 모든 기록 초기화", type="primary", use_container_width=True):
                reset_all()
                st.rerun()

    else:
        missed = get_missed_categories()
        if not missed:
            missed = [c for c in categories if c not in st.session_state.escape_clicks[-2:]]

        st.markdown("##### 🔍 알고리즘이 가렸던 다른 시각들")
        st.caption("아래 카테고리는 여러분이 평소에 잘 보지 않은 분야입니다. 한 번 클릭해 새로운 관점을 만나보세요.")

        miss_cols = st.columns(min(3, len(missed)))
        for idx, cat in enumerate(missed[:3]):
            with miss_cols[idx]:
                sample = get_escape_sample(cat)

                st.markdown(f"""
                <div class="missed-card">
                  <div class="ttl">📂 안 본 카테고리</div>
                  <div class="name">{CAT_ICONS[cat]} {cat}</div>
                  <div class="desc">{CAT_DESC[cat]}</div>
                  <hr style="border:none; border-top:1px solid #F0E6F7; margin:10px 0;">
                  <div style="font-size:13px; font-weight:600; color:#5B4B7C; line-height:1.4;">{html.escape(sample['title'])}</div>
                  <div style="font-size:11px; color:#B5A8C9; margin-top:4px;">📡 {html.escape(sample['source'])}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"이 시각 탐색하기",
                             key=f"escape_{cat}_{len(st.session_state.escape_clicks)}",
                             use_container_width=True):
                    escape_click(cat)
                    st.rerun()

                st.markdown(
                    f'<a class="news-link-btn" href="{html.escape(sample.get("link","#"))}" '
                    f'target="_blank" rel="noopener noreferrer">🔗 원문 읽기 (새 탭)</a>',
                    unsafe_allow_html=True
                )

        if escape_diversity == 0:
            st.info("👆 위 카드 중 하나를 클릭해 첫 발걸음을 시작하세요!")
        elif escape_diversity < GOAL:
            remain = GOAL - escape_diversity
            st.success(f"💪 잘하고 있어요! {remain}가지 카테고리만 더 탐색하면 탈출 성공입니다.")

        if st.button("✖️ 챌린지 중단", use_container_width=False):
            st.session_state.escape_mode = False
            st.session_state.escape_clicks = []
            st.session_state.escape_samples = {}
            st.rerun()

# =========================================================
# 일상 속 탈출 팁
# =========================================================
st.divider()
st.markdown('<div class="section-title">🛡️ 일상 속 필터 버블 탈출 습관</div>', unsafe_allow_html=True)

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

b1, b2 = st.columns([3, 1])
with b1:
    st.markdown("#### 🎓 오늘의 수업 핵심 키워드")
    st.success("✅ 필터 버블 (Filter Bubble) · ✅ 확증 편향 (Confirmation Bias) · ✅ 추천 알고리즘 윤리 · ✅ 디지털 리터러시")
with b2:
    st.write("")
    if st.button("🔄 모든 기록 초기화", type="primary", use_container_width=True, key="final_reset"):
        reset_all()
        st.rerun()
