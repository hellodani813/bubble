import streamlit as st
import random
import pandas as pd
import feedparser
import urllib.parse
import re

# -----------------------
# 페이지 설정 
# -----------------------
st.set_page_config(page_title="추천 알고리즘 버블 체험", page_icon="🫧", layout="wide")

# -----------------------
# 세션 상태 초기화 및 관리
# -----------------------
default_categories = ["스포츠", "정치", "게임", "연예", "사건사고", "교육"]

if "categories" not in st.session_state:
    st.session_state.categories = default_categories.copy()

if "weights" not in st.session_state:
    st.session_state.weights = {cat: 1 for cat in st.session_state.categories}

if "click_history" not in st.session_state:
    st.session_state.click_history = []

if "selected_article" not in st.session_state:
    st.session_state.selected_article = None

# --- 버튼 클릭 시 즉시 실행되는 콜백(Callback) 함수들 ---
def click_content(item):
    cat = item["category"]
    st.session_state.click_history.append(cat)
    st.session_state.weights[cat] += 3
    st.session_state.selected_article = item 

def close_article():
    st.session_state.selected_article = None

def reset_all():
    st.session_state.categories = default_categories.copy()
    st.session_state.weights = {cat: 1 for cat in st.session_state.categories}
    st.session_state.click_history = []
    st.session_state.selected_article = None

def break_bubble():
    kw = st.session_state.get("new_keyword", "").strip()
    sel = st.session_state.get("new_select", "선택안함")
    target = kw if kw else (sel if sel != "선택안함" else "")
    
    if target:
        if target not in st.session_state.categories:
            st.session_state.categories.append(target)
        
        st.session_state.weights = {cat: 1 for cat in st.session_state.categories}
        st.session_state.weights[target] = 5
        st.session_state.click_history = []
        st.session_state.selected_article = None
# --------------------------------------------------------

# -----------------------
# 구글 뉴스 RSS 연동 함수 (캐싱 적용)
# -----------------------
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_google_news(category, is_extreme):
    search_query = category
    if is_extreme:
        search_query += " (논란 OR 충격 OR 분노 OR 단독 OR 의혹)"
    
    encoded_query = urllib.parse.quote(search_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        feed = feedparser.parse(rss_url)
        news_data = []
        for entry in feed.entries[:20]:
            clean_title = re.sub(r' - .+$', '', entry.title)
            news_data.append({
                "title": clean_title,
                "link": entry.link
            })
        return news_data if news_data else None
    except Exception as e:
        return None

# -----------------------
# 기사 제목 데이터베이스 (안전장치용 더미 데이터)
# -----------------------
normal_titles = {
    "스포츠": ["⚽ 손흥민, 경기 MVP 선정", "🏀 NBA 플레이오프 명승부", "⚾ 프로야구 순위 경쟁 치열"],
    "정치": ["🗳️ 정책 토론 주요 쟁점", "📢 사회 현안 논의 확대", "🏛️ 정부 정책 발표"],
    "게임": ["🎮 신작 게임 출시 기대감", "🔥 인기 게임 e스포츠 대회 개최", "🕹️ 게이밍 트렌드 변화 분석"],
    "연예": ["🎤 인기 아이돌 성공적인 컴백", "🎬 화제의 웹드라마 전편 공개", "📺 주말 예능 프로그램 시청률 1위"],
    "교육": ["📚 AI 시대가 바꾸는 교실 풍경", "🧠 뇌과학 기반 효과적인 공부법 연구", "💡 10년 뒤 미래 직업 변화 전망"],
    "사건사고": ["경찰, 대규모 보이스피싱 일당 검거", "주말 고속도로 다중 추돌 사고", "전국적인 집중 호우 대비 태세"]
}

extreme_titles = {
    "스포츠": ["⚽ 충격! 대표팀 대참사", "🏀 역대급 오심 논란, 팬들 분노"],
    "정치": ["🚨 정치권 초비상 사태", "🔥 국민 여론 폭발, 대규모 시위 예고"],
    "게임": ["🎮 역대급 게임 중독 논란 확산", "🔥 서버 터짐! 유저들 분노 폭발"],
    "연예": ["😱 연예계 발칵 뒤집힌 충격 소식", "🔥 팬들 멘붕, 단독 열애설 포착"],
    "교육": ["🚨 AI가 모든 교사를 완전히 대체한다?", "😱 10년 후 완전히 멸종할 직업 리스트"],
    "사건사고": ["🚨 충격 단독! 전 국민이 속고 있었다", "😱 충격적인 흉악 범죄 발생, 시민들 불안"]
}

# -----------------------
# 추천 알고리즘 로직
# -----------------------
def get_bubble_level():
    clicks = len(st.session_state.click_history)
    if clicks <= 2: return 1
    elif clicks <= 5: return 2
    elif clicks <= 9: return 3
    return 4

def get_feed():
    bubble_level = get_bubble_level()
    is_extreme = bubble_level >= 3
    
    weighted_categories = []
    for cat in st.session_state.categories:
        weighted_categories.extend([cat] * st.session_state.weights[cat])
    
    if not weighted_categories:
        return []

    chosen_categories = random.choices(weighted_categories, k=6)
    cat_counts = {cat: chosen_categories.count(cat) for cat in set(chosen_categories)}
    
    feed = []
    for cat, count in cat_counts.items():
        news_pool = fetch_google_news(cat, is_extreme)
        
        if not news_pool or len(news_pool) < count:
            if cat in normal_titles:
                titles_pool = extreme_titles[cat] if is_extreme else normal_titles[cat]
            else:
                titles_pool = [f"📰 [{cat}] 관련 최신 뉴스", f"🔍 [{cat}]에 대한 심층 분석", f"💡 [{cat}] 전문가 의견", f"📈 [{cat}] 관련 이슈 트렌드"]

            sampled_titles = random.sample(titles_pool, count) if count <= len(titles_pool) else random.choices(titles_pool, k=count)
            sampled_news = [{"title": t, "link": "https://news.google.com"} for t in sampled_titles]
        else:
            sampled_news = random.sample(news_pool, count) if count <= len(news_pool) else random.choices(news_pool, k=count)
            
        for news in sampled_news:
            display_title = news['title'] if (" " in news['title'] and news['title'].startswith("🚨")) else f"🗞️ {news['title']}"
            feed.append({
                "title": display_title, 
                "link": news['link'], 
                "category": cat
            })
            
    random.shuffle(feed)
    return feed

def analyze_personality():
    history = st.session_state.click_history
    if len(history) == 0:
        return "분석 대기 중 ⏳", "콘텐츠를 클릭하면 분석이 시작됩니다."

    counts = {cat: history.count(cat) for cat in st.session_state.categories}
    dominant = max(counts, key=counts.get)

    if len(set(history)) >= 4:
        return "균형 탐색형 🌍", "다양한 분야의 관점을 고르게 탐색하는 건강한 성향입니다."

    labels = {
        "스포츠": "스포츠 몰입형 ⚽", "정치": "이슈 집중형 🗳️", "게임": "몰입형 게이머 🎮",
        "연예": "트렌드 민감형 🎤", "사건사고": "도파민 추구형 🚨", "교육": "지식 탐구형 📚"
    }
    ptype = labels.get(dominant, f"{dominant} 탐구형 🔍")
    return ptype, f"현재 **{dominant}** 콘텐츠를 집중적으로 소비하고 있습니다."

# -----------------------
# 메인 UI 구성
# -----------------------
st.title("📱 추천 알고리즘과 필터 버블 체험")
st.markdown("**마음에 드는 기사를 계속 클릭해 보세요. AI가 여러분의 취향을 학습하여 화면을 바꿉니다!**")
st.write("") 

left_col, right_col = st.columns([1.2, 1])

# --- 좌측: 맞춤형 추천 피드 ---
with left_col:
    st.subheader("📰 맞춤형 실시간 추천 피드")
    
    # 선택된 기사가 있을 때 원문 링크를 보여주는 영역
    if st.session_state.selected_article:
        with st.container(border=True):
            st.markdown("### 👀 방금 클릭한 기사")
            st.markdown(f"**{st.session_state.selected_article['title']}**")
            st.link_button("🌐 구글 뉴스 원문 보러가기", st.session_state.selected_article['link'])
            
            # 닫기 버튼에도 on_click 콜백 적용
            st.button("❌ 닫기", on_click=close_article)
        st.divider()

    feed = get_feed()
    
    if feed:
        feed_col1, feed_col2 = st.columns(2)
        for i, item in enumerate(feed):
            target_col = feed_col1 if i % 2 == 0 else feed_col2
            with target_col:
                with st.container(border=True):
                    st.markdown(f"**{item['title']}**")
                    st.caption(f"📂 카테고리: {item['category']}")
                    
                    # 핵심 수정 사항: on_click 파라미터와 안정적인 key 값 사용
                    st.button(
                        "클릭하여 보기", 
                        key=f"feed_btn_{i}", 
                        on_click=click_content, 
                        args=(item,), 
                        use_container_width=True
                    )

# --- 우측: 실시간 분석 대시보드 ---
with right_col:
    st.subheader("🤖 실시간 AI 분석")
    total_clicks = len(st.session_state.click_history)
    bubble_level = get_bubble_level()

    if bubble_level == 1:
        st.success("🟢 **1단계: 균형 상태**\n\n다양한 정보가 고르게 추천되고 있습니다.")
    elif bubble_level == 2:
        st.warning("🟡 **2단계: 버블 형성 시작**\n\n특정 분야의 추천 비율이 슬슬 늘어나고 있습니다.")
    elif bubble_level == 3:
        st.error("🟠 **3단계: 버블 심화 (주의!)**\n\n자극적인 기사가 늘고, 다른 분야의 정보가 사라지고 있습니다.")
    else:
        st.error("🔴 **4단계: 필터 버블 고착화 (확증 편향)**\n\n완전히 갇혔습니다! 내가 좋아하는 정보만 보입니다.")

    ptype, desc = analyze_personality()
    with st.expander("📋 나의 디지털 성향 분석 결과", expanded=True):
        st.markdown(f"### {ptype}")
        st.write(desc)
        
        if total_clicks >= 5:
            dominant = max(st.session_state.weights, key=st.session_state.weights.get)
            st.warning(f"🚨 경고: 정보 환경이 **{dominant}** 위주로 좁아지고 있습니다.")

    st.markdown(f"**📊 카테고리별 AI 추천 가중치 (총 클릭: {total_clicks}회)**")
    df = pd.DataFrame({
        "카테고리": list(st.session_state.weights.keys()),
        "추천 강도": list(st.session_state.weights.values())
    })
    st.bar_chart(df.set_index("카테고리"), height=250)

# -----------------------
# 하단: 버블 해제(탈출) 및 새로운 관심사 검색
# -----------------------
st.divider()
st.subheader("🛡️ 필터 버블 해제하기: 능동적 탐색")
st.markdown("수동적으로 AI가 주는 정보만 받지 말고, **내가 직접 새로운 분야를 검색**하면 갇혀있던 버블을 깰 수 있습니다.")

search_col1, search_col2 = st.columns(2)

with search_col1:
    # 세션 상태에 저장되도록 key 지정
    st.text_input("🔍 1. 새로운 관심사 직접 검색", placeholder="예: 우주 과학, 환경 보호, 인공지능 등", key="new_keyword")

with search_col2:
    # 세션 상태에 저장되도록 key 지정
    st.selectbox("📌 2. 또는 추천 키워드 선택", ["선택안함", "환경/기후변화", "우주 탐사", "세계 역사", "클래식 음악", "미술/전시", "경제/재테크", "심리학"], key="new_select")

# 콜백 함수 방식 적용
st.button("🚀 이 키워드로 알고리즘 버블 깨기!", type="primary", on_click=break_bubble, use_container_width=True)

st.write("") 

bottom_col1, bottom_col2 = st.columns([3, 1])
with bottom_col1:
    st.markdown("#### 🎓 수업 핵심 키워드")
    st.info("✅ **필터 버블 (Filter Bubble)** | ✅ **확증 편향 (Confirmation Bias)** | ✅ **추천 알고리즘 윤리** | ✅ **디지털 능동성**")

with bottom_col2:
    st.write("") 
    # 콜백 함수 방식 적용
    st.button("🔄 전체 초기화 (처음부터 다시)", on_click=reset_all, use_container_width=True)
