import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="추천 알고리즘 버블 체험", layout="wide")

categories = ["스포츠", "정치", "게임", "연예", "자극", "교육"]

# -----------------------
# 세션 상태
# -----------------------
if "weights" not in st.session_state:
    st.session_state.weights = {cat: 1 for cat in categories}

if "click_history" not in st.session_state:
    st.session_state.click_history = []

# -----------------------
# AI 기사 생성
# -----------------------
def generate_title(category, bubble_level):
    normal_titles = {
        "스포츠": [
            "⚽ 손흥민, 경기 MVP 선정",
            "🏀 NBA 플레이오프 명승부",
            "⚾ 프로야구 순위 경쟁 치열"
        ],
        "정치": [
            "🗳️ 정책 토론 주요 쟁점",
            "📢 사회 현안 논의 확대",
            "🏛️ 정부 정책 발표"
        ],
        "게임": [
            "🎮 신작 게임 출시",
            "🔥 인기 게임 대회 개최",
            "🕹️ 게이밍 트렌드 변화"
        ],
        "연예": [
            "🎤 인기 아이돌 컴백",
            "🎬 화제의 드라마 공개",
            "📺 예능 프로그램 인기 상승"
        ],
        "교육": [
            "📚 AI가 바꾸는 교육",
            "🧠 효과적인 공부법 연구",
            "💡 미래 직업 변화 전망"
        ],
        "자극": [
            "😱 충격적인 사건 발생",
            "🚨 지금 안 보면 손해",
            "🔥 모두가 놀란 소식"
        ]
    }

    extreme_titles = {
        "스포츠": [
            "⚽ 충격! 대표팀 대참사",
            "🏀 역대급 논란 발생"
        ],
        "정치": [
            "🚨 정치권 초비상",
            "🔥 여론 폭발"
        ],
        "게임": [
            "🎮 역대급 게임 중독 논란",
            "🔥 유저들 분노 폭발"
        ],
        "연예": [
            "😱 연예계 충격 소식",
            "🔥 팬들 충격"
        ],
        "교육": [
            "🚨 AI가 교사를 대체한다?",
            "😱 10년 후 사라질 직업"
        ],
        "자극": [
            "🚨 충격! 모두가 속고 있었다",
            "😱 지금 클릭 안 하면 후회"
        ]
    }

    if bubble_level >= 3:
        return random.choice(extreme_titles[category])
    return random.choice(normal_titles[category])

# -----------------------
# 추천 피드
# -----------------------
def get_bubble_level():
    clicks = len(st.session_state.click_history)

    if clicks <= 2:
        return 1
    elif clicks <= 5:
        return 2
    elif clicks <= 9:
        return 3
    return 4

def get_feed():
    bubble_level = get_bubble_level()

    weighted_categories = []
    for cat in categories:
        weighted_categories.extend([cat] * st.session_state.weights[cat])

    feed = []
    for _ in range(6):
        cat = random.choice(weighted_categories)
        feed.append({
            "title": generate_title(cat, bubble_level),
            "category": cat
        })

    return feed

def click_content(item):
    cat = item["category"]
    st.session_state.click_history.append(cat)
    st.session_state.weights[cat] += 3

# -----------------------
# 성향 분석
# -----------------------
def analyze_personality():
    history = st.session_state.click_history

    if len(history) == 0:
        return "분석 불가", "아직 데이터가 부족합니다."

    counts = {cat: history.count(cat) for cat in categories}
    dominant = max(counts, key=counts.get)

    if len(set(history)) >= 4:
        return "균형 탐색형 🌍", "다양한 관점을 탐색하는 성향입니다."

    labels = {
        "스포츠": "스포츠 몰입형 ⚽",
        "정치": "이슈 집중형 🗳️",
        "게임": "몰입형 게이머 🎮",
        "연예": "트렌드 민감형 🎤",
        "자극": "자극 추구형 🚨",
        "교육": "지식 탐구형 📚"
    }

    return labels[dominant], f"{dominant} 콘텐츠를 주로 소비합니다."

# -----------------------
# UI
# -----------------------
st.title("📱 추천 알고리즘 버블 체험")

st.markdown("""
관심 있는 콘텐츠를 클릭해보세요.  
AI가 당신의 취향을 학습합니다.
""")

feed = get_feed()

st.subheader("📰 추천 피드")

for i, item in enumerate(feed):
    st.markdown(f"### {item['title']}")
    st.caption(f"카테고리: {item['category']}")

    if st.button("보기", key=f"btn_{i}"):
        click_content(item)
        st.rerun()

total_clicks = len(st.session_state.click_history)
bubble_level = get_bubble_level()

st.divider()
st.subheader("🫧 버블 심화 단계")

if bubble_level == 1:
    st.success("1단계: 균형 상태 🌍")
elif bubble_level == 2:
    st.warning("2단계: 버블 형성 시작 🫧")
elif bubble_level == 3:
    st.error("3단계: 버블 심화 ⚠️")
else:
    st.error("4단계: 필터 버블 고착화 🚨")

st.divider()
st.subheader("📊 추천 알고리즘 분석")

df = pd.DataFrame({
    "카테고리": list(st.session_state.weights.keys()),
    "추천 강도": list(st.session_state.weights.values())
})

st.bar_chart(df.set_index("카테고리"))

st.divider()
st.subheader("📋 디지털 성향 분석 리포트")

ptype, desc = analyze_personality()
st.markdown(f"## {ptype}")
st.write(desc)

if total_clicks >= 5:
    dominant = max(st.session_state.weights, key=st.session_state.weights.get)

    st.warning(f"""
현재 알고리즘은 **{dominant}** 콘텐츠 위주로 추천하고 있습니다.

당신의 정보 환경이 점점 좁아지고 있습니다.
""")

st.divider()
st.subheader("🎓 교육 포인트")

st.markdown("""
- 필터 버블 (Filter Bubble)
- 확증 편향 (Confirmation Bias)
- 추천 알고리즘 윤리
- 디지털 리터러시
""")

if st.button("🔄 초기화"):
    st.session_state.weights = {cat: 1 for cat in categories}
    st.session_state.click_history = []
    st.rerun()
