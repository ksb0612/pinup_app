import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()  # 로컬 개발용 .env 파일 지원

st.set_page_config(page_title="PinUp GBP Manager", page_icon="🍔", layout="wide")

# API Key 우선순위: Streamlit Secrets (클라우드) → .env (로컬) → 사이드바 입력
try:
    env_api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
except Exception:
    env_api_key = os.environ.get("GOOGLE_API_KEY", "")

with st.sidebar:
    st.header("📌 Navigation")
    menu = st.radio("메뉴 선택", ["📝 GBP 콘텐츠 생성기", "📊 GBP 진단 리포트"])
    
    st.divider()
    
    st.header("⚙️ Configuration")
    if env_api_key:
        api_key = st.text_input("Google API Key", value=env_api_key, type="password", help="Loaded from .env file")
    else:
        api_key = st.text_input("Google API Key", type="password")
        
    if api_key:
        genai.configure(api_key=api_key)
    st.markdown("Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/).")


if menu == "📝 GBP 콘텐츠 생성기":
    st.title("🍔 PinUp GBP 콘텐츠 생성기")
    st.markdown("한국어로 식당 정보를 입력하면 Google Business Profile(GBP)에 최적화된 영문 마케팅 콘텐츠 4종 세트(및 한글 번역)를 생성합니다.")

    st.header("📝 Restaurant Information")
    col1, col2 = st.columns(2)
    with col1:
        restaurant_name = st.text_input("식당 이름 (Restaurant Name)", placeholder="예: 맛돌이 곱창")
        location = st.text_input("위치/주소 (Location)", placeholder="예: 서울 마포구 연남동 123-4")
    with col2:
        main_menu = st.text_input("주요 메뉴 (Main Menu)", placeholder="예: 소곱창구이, 막창, 볶음밥")
        features = st.text_area("매장 특색 (Features & Vibe)", placeholder="예: 레트로 감성, 20년 전통, 현지인 맛집")

    def generate_content(name, loc, menu_text, feat):
        prompt = f"""
You are a World-class Local SEO & Restaurant Marketing Specialist.
Create compelling, native-level English content that sounds like a local hidden gem or a trendy hotspot.
Ensure the 'Business Description' stays within 750 characters while including essential keywords.
For each generated English content, provide a high-quality, natural-sounding Korean translation that captures the same tone and marketing appeal.

Translate and optimize the following Korean restaurant information into English Google Business Profile content, and then translate your English outputs back to Korean:
- Restaurant Name: {name}
- Location: {loc}
- Main Menu: {menu_text}
- Features: {feat}

You must return a JSON object with exactly the following 8 keys:
- "description_en": Business Description in English (Max 750 characters)
- "description_ko": Business Description in Korean
- "menu_en": Menu Categories & Items formatted elegantly in English
- "menu_ko": Menu Categories & Items formatted elegantly in Korean
- "qa_en": Q&A 10 Sets in English (Common customer questions & answers)
- "qa_ko": Q&A 10 Sets in Korean
- "posts_en": Google Posts 4 Samples in English (1 Update, 1 Offer, 1 Event, 1 Food focus)
- "posts_ko": Google Posts 4 Samples in Korean
"""
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        return json.loads(response.text)

    if st.button("🚀 Generate GBP Content"):
        if not api_key:
            st.error("Please enter your Google API Key in the sidebar.")
        elif not all([restaurant_name, location, main_menu, features]):
            st.error("Please fill in all the restaurant information fields.")
        else:
            with st.spinner("Generating SEO-optimized content and Korean translations..."):
                try:
                    result = generate_content(restaurant_name, location, main_menu, features)
                    st.success("Successfully generated!")
                    
                    tab1, tab2, tab3, tab4 = st.tabs(["Description", "Menu", "Q&A", "Google Posts"])
                    
                    with tab1:
                        st.subheader("🇺🇸 English")
                        st.code(result.get("description_en", ""), language="markdown")
                        st.subheader("🇰🇷 Korean")
                        st.code(result.get("description_ko", ""), language="markdown")
                        
                    with tab2:
                        st.subheader("🇺🇸 English")
                        st.code(result.get("menu_en", ""), language="markdown")
                        st.subheader("🇰🇷 Korean")
                        st.code(result.get("menu_ko", ""), language="markdown")
                        
                    with tab3:
                        st.subheader("🇺🇸 English")
                        st.code(result.get("qa_en", ""), language="markdown")
                        st.subheader("🇰🇷 Korean")
                        st.code(result.get("qa_ko", ""), language="markdown")
                        
                    with tab4:
                        st.subheader("🇺🇸 English")
                        st.code(result.get("posts_en", ""), language="markdown")
                        st.subheader("🇰🇷 Korean")
                        st.code(result.get("posts_ko", ""), language="markdown")
                except Exception as e:
                    st.error(f"Failed to generate content: {e}")
                    try:
                        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        st.info(f"Available models for this API key: {', '.join(models)}")
                        st.info("Try changing the model name in `main.py` (line 45) to one of the models listed above (e.g., 'gemini-1.5-pro-latest').")
                    except Exception as list_e:
                        st.error(f"Could not fetch model list: {list_e}")

elif menu == "📊 GBP 진단 리포트":
    st.title("📊 PinUp GBP 진단 리포트")
    st.markdown("매장의 현재 상태와 타겟 고객층을 바탕으로 GBP 최적화 진단 및 개선 리포트를 제공합니다.")

    import datetime
    
    st.header("🏪 Section 1: 식당 기본 정보")
    col1, col2 = st.columns(2)
    with col1:
        diag_name_ko = st.text_input("식당명 (한국어) *", key="diag_name_ko", placeholder="예: 진미식당")
        diag_address = st.text_input("주소 *", key="diag_address", placeholder="예: 서울 중구 을지로 xxx")
        diag_category = st.selectbox("음식 카테고리 *", ["한식", "중식", "일식", "양식", "분식", "카페", "기타"], key="diag_category")
    with col2:
        diag_name_en = st.text_input("식당명 (영문)", key="diag_name_en", placeholder="미등록", help="영문 식당명이 없다면 비워두세요.")
        diag_menu = st.text_input("대표 메뉴", key="diag_menu", placeholder="예: 김치찌개, 된장찌개, 제육볶음")
        diag_date = st.date_input("진단 날짜", datetime.date.today(), key="diag_date")
        
    st.divider()

    st.header("📋 Section 2: GBP 현황 진단 체크리스트")
    st.markdown("항목별 질문에 답하여 현재 GBP 최적화 상태를 진단해보세요.")
    
    def get_score(val):
        import re
        match = re.search(r'\((\d+)\)', str(val))
        if match:
            return int(match.group(1))
        return 0

    cat_keys = {
        "cat1": ["c1_1", "c1_2", "c1_3", "c1_4", "c1_5"],
        "cat2": ["c2_1", "c2_2", "c2_3"],
        "cat3": ["c3_1", "c3_2", "c3_3"],
        "cat4": ["c4_1", "c4_2", "c4_3"],
        "cat5": ["c5_1", "c5_2", "c5_3"],
        "cat6": ["c6_1", "c6_2"]
    }
    
    cat_scores = {}
    total_score = 0
    for cat, keys in cat_keys.items():
        score = 0
        for k in keys:
            if k in st.session_state:
                score += get_score(st.session_state[k])
        cat_scores[cat] = score
        total_score += score
        
    # ── expander 고정 열림 상태 초기화 ──────────────────────────────────
    for _cat in ["cat1","cat2","cat3","cat4","cat5","cat6"]:
        if f"exp_{_cat}" not in st.session_state:
            st.session_state[f"exp_{_cat}"] = False

    def _open(cat):
        """라디오 버튼 변경 시 해당 카테고리를 열린 상태로 고정"""
        st.session_state[f"exp_{cat}"] = True

    with st.expander(
        f"카테고리 1: 프로필 기본 정보 ({cat_scores['cat1']} / 30점)",
        expanded=st.session_state["exp_cat1"]
    ):
        st.radio("GBP 등록 상태", ["미등록(0)", "자동생성-미클레임(3)", "클레임완료(6)"],
                 key="c1_1", horizontal=True, on_change=_open, args=("cat1",))
        st.radio("가게명 영문 표기", ["없음(0)", "있으나 부정확(3)", "정확(6)"],
                 key="c1_2", horizontal=True, on_change=_open, args=("cat1",))
        st.radio("영업시간 설정", ["없음(0)", "일부만(3)", "완전(6)"],
                 key="c1_3", horizontal=True, on_change=_open, args=("cat1",))
        st.radio("전화번호 표기", ["없음(0)", "국내형식(3)", "국제형식+82(6)"],
                 key="c1_4", horizontal=True, on_change=_open, args=("cat1",))
        st.radio("카테고리 설정", ["미설정(0)", "대분류만(3)", "Primary+Secondary(6)"],
                 key="c1_5", horizontal=True, on_change=_open, args=("cat1",))

    with st.expander(
        f"카테고리 2: 영문 콘텐츠 ({cat_scores['cat2']} / 20점)",
        expanded=st.session_state["exp_cat2"]
    ):
        st.radio("영문 비즈니스 소개글", ["없음(0)", "1~2줄(3)", "상세(7)"],
                 key="c2_1", horizontal=True, on_change=_open, args=("cat2",))
        st.radio("영문 메뉴 등록", ["없음(0)", "일부(3)", "전체+가격(7)"],
                 key="c2_2", horizontal=True, on_change=_open, args=("cat2",))
        st.radio("Q&A 섹션", ["없음(0)", "1~3개(3)", "5개+(6)"],
                 key="c2_3", horizontal=True, on_change=_open, args=("cat2",))

    with st.expander(
        f"카테고리 3: 사진/영상 ({cat_scores['cat3']} / 20점)",
        expanded=st.session_state["exp_cat3"]
    ):
        st.radio("음식 사진 수", ["0장(0)", "1~3장(3)", "4~10장(5)", "10장+(7)"],
                 key="c3_1", horizontal=True, on_change=_open, args=("cat3",))
        st.radio("사진 품질", ["없음(0)", "어둡거나 낮음(2)", "보통(4)", "밝고 전문적(7)"],
                 key="c3_2", horizontal=True, on_change=_open, args=("cat3",))
        st.radio("영상 유무", ["없음(0)", "있음(6)"],
                 key="c3_3", horizontal=True, on_change=_open, args=("cat3",))

    with st.expander(
        f"카테고리 4: 리뷰 관리 ({cat_scores['cat4']} / 15점)",
        expanded=st.session_state["exp_cat4"]
    ):
        st.radio("전체 리뷰 수", ["0건(0)", "1~10건(2)", "11~50건(4)", "50건+(5)"],
                 key="c4_1", horizontal=True, on_change=_open, args=("cat4",))
        st.radio("외국어 리뷰 수", ["0건(0)", "1~5건(2)", "6~20건(4)", "20건+(5)"],
                 key="c4_2", horizontal=True, on_change=_open, args=("cat4",))
        st.radio("리뷰 응답 여부", ["무응답(0)", "일부 응답(2)", "대부분 응답(5)"],
                 key="c4_3", horizontal=True, on_change=_open, args=("cat4",))

    with st.expander(
        f"카테고리 5: 속성(Attributes) 설정 ({cat_scores['cat5']} / 10점)",
        expanded=st.session_state["exp_cat5"]
    ):
        st.radio("결제수단 표기", ["없음(0)", "일부(2)", "완전(4)"],
                 key="c5_1", horizontal=True, on_change=_open, args=("cat5",))
        st.radio("편의시설 (Wi-Fi, 주차 등)", ["없음(0)", "일부(2)", "완전(3)"],
                 key="c5_2", horizontal=True, on_change=_open, args=("cat5",))
        st.radio("분위기/서비스 태그", ["없음(0)", "일부(1)", "완전(3)"],
                 key="c5_3", horizontal=True, on_change=_open, args=("cat5",))

    with st.expander(
        f"카테고리 6: 멀티채널 ({cat_scores['cat6']} / 5점)",
        expanded=st.session_state["exp_cat6"]
    ):
        st.radio("TripAdvisor 등록", ["없음(0)", "있음(2)"],
                 key="c6_1", horizontal=True, on_change=_open, args=("cat6",))
        st.radio("Instagram 영문 계정", ["없음(0)", "있음(3)"],
                 key="c6_2", horizontal=True, on_change=_open, args=("cat6",))

    st.info(f"**진단 체크리스트 총 점수: {total_score} / 100점**")
    
    st.divider()
    import plotly.graph_objects as go
    st.header("📊 Section 3: 진단 결과 대시보드 (실시간)")

    # 3-1. 종합 점수 게이지
    if total_score <= 20:
        grade, color = "🔴 위험", "red"
    elif total_score <= 40:
        grade, color = "🟠 미흡", "orange"
    elif total_score <= 60:
        grade, color = "🟡 보통", "yellow"
    elif total_score <= 80:
        grade, color = "🟢 양호", "green"
    else:
        grade, color = "🔵 우수", "blue"
        
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("종합 진단 점수")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"현재 등급: {grade}", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 20], 'color': 'rgba(255, 0, 0, 0.1)'},
                    {'range': [20, 40], 'color': 'rgba(255, 165, 0, 0.1)'},
                    {'range': [40, 60], 'color': 'rgba(255, 255, 0, 0.1)'},
                    {'range': [60, 80], 'color': 'rgba(0, 128, 0, 0.1)'},
                    {'range': [80, 100], 'color': 'rgba(0, 0, 255, 0.1)'}
                ]
            }
        ))
        fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.subheader("카테고리별 레이더 차트")
        categories = ['기본 정보', '영문 콘텐츠', '사진/영상', '리뷰 관리', '속성 설정', '멀티채널']
        max_scores = [30, 20, 20, 15, 10, 5]
        current_scores = [cat_scores['cat1'], cat_scores['cat2'], cat_scores['cat3'], 
                         cat_scores['cat4'], cat_scores['cat5'], cat_scores['cat6']]
                         
        fig_radar = go.Figure()
        
        # 최적화 후 (만점)
        fig_radar.add_trace(go.Scatterpolar(
            r=max_scores + [max_scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='최적화 후 (만점)',
            line_color='blue',
            opacity=0.3
        ))
        
        # 현재 상태
        fig_radar.add_trace(go.Scatterpolar(
            r=current_scores + [current_scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='현재 상태',
            line_color='red',
            opacity=0.7
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 30])
            ),
            showlegend=True,
            height=350,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # 3-3. 개선 우선순위 자동 추출
    st.subheader("개선 우선순위 자동 추출")
    
    immediate_actions = []
    suggested_actions = []
    
    def get_val(key):
        return st.session_state.get(key, "미설정(0)")
        
    def check_action(key, zero_msg, partial_msg, max_val):
        score = get_score(get_val(key))
        if score == 0:
            immediate_actions.append(zero_msg)
        elif 0 < score < max_val:
            if partial_msg:
                suggested_actions.append(partial_msg)

    check_action("c1_1", "GBP 미등록 → 🔵 PinUp: 신규 등록 및 기초 세팅", "클레임 미완료 → 🔵 PinUp: 소유권 클레임 및 등록 관리", 6)
    check_action("c1_2", "가게명 영문 표기 없음 → 🔵 PinUp: 영문 텍스트 번역", "영문 가게명 부정확 → 🔵 PinUp: 정확한 영문 텍스트 번역 및 최적화", 6)
    check_action("c1_3", "영업시간 미설정 → 🔵 PinUp: 비즈니스 정보 완전성 확보", "영업시간 일부 누락 → 🔵 PinUp: 정확한 영업시간 최신화", 6)
    check_action("c1_4", "전화번호 미표기 → 🔵 PinUp: 국제 형식 전화번호 세팅 (+82)", "국내형식 전화번호 → 🔵 PinUp: 국제 형식 전화번호 갱신", 6)
    check_action("c1_5", "카테고리 미설정 → 🔵 PinUp: 최적화 카테고리 선정", "하위 카테고리 누락 → 🔵 PinUp: Secondary 카테고리 발굴", 6)
    
    check_action("c2_1", "영문 소개글 없음 → 🔵 PinUp: 영문 비즈니스 소개글 작성", "소개글 내용 부족 → 🔵 PinUp: 키워드 반영 영문 소개글 보완", 7)
    check_action("c2_2", "영문 메뉴 등록 없음 → 🔵 PinUp: 영문 메뉴판 제작 및 등록", "메뉴 전체 미등록 → 🔵 PinUp: 글로벌 고객용 영문 메뉴 완비", 7)
    check_action("c2_3", "Q&A 섹션 없음 → 🔵 PinUp: 자주 묻는 질문(FAQ) 영문 세팅", "Q&A 항목 부족 → 🔵 PinUp: Q&A 콘텐츠 보완", 6)
    
    check_action("c3_1", "음식 사진 없음 → 🔵 PinUp: 매력적인 음식 사진 확보 가이드 제공", "사진 수량 부족 → 🔵 PinUp: 추가 음식 사진 업로드", 7)
    check_action("c3_2", "사진 품질 없음/매우 낮음 → 🔵 PinUp: 고품질 전문가 사진 촬영/보정 제안", "사진 퀄리티 향상 필요 → 🔵 PinUp: 고해상도 사진 교체", 7)
    check_action("c3_3", "영상 콘텐츠 없음 → 🔵 PinUp: 짧은 홍보 영상 제작 및 업로드", "", 6)
    
    check_action("c4_1", "전체 리뷰 0건 → 🔵 PinUp: 초기 리뷰 확보 전략 제공", "리뷰 수량 부족 → 🔵 PinUp: 리뷰 이벤트 등 유치 방안 도출", 5)
    check_action("c4_2", "외국어 리뷰 0건 → 🔵 PinUp: 외국인 타겟 맞춤형 리뷰 유도 캠페인", "외국어 리뷰 부족 → 🔵 PinUp: 인바운드 관광객 맞춤형 인센티브 설계", 5)
    check_action("c4_3", "리뷰 무응답 → 🔵 PinUp: 영문 리뷰 템플릿 제공 및 응답 관리", "리뷰 응답 누락 지점 → 🔵 PinUp: 일관성 있는 영문 리뷰 답변 관리", 5)
    
    check_action("c5_1", "결제수단 표기 없음 → 🔵 PinUp: 결제수단 추가 정보 제공 (Apple Pay 등)", "일부 결제수단만 표기 → 🔵 PinUp: 다양한 결제수단 추가", 4)
    check_action("c5_2", "편의시설 정보 없음 → 🔵 PinUp: Wi-Fi/주차 등 속성 완비", "일부 편의시설만 표기 → 🔵 PinUp: 주요 편의시설 정보 보완", 3)
    check_action("c5_3", "분위기/서비스 태그 없음 → 🔵 PinUp: 검색 노출용 태그 매핑", "일부 태그만 설정 → 🔵 PinUp: 상세 서비스 태그 매핑", 3)
    
    check_action("c6_1", "트립어드바이저 미등록 → 🔵 PinUp: 다채널 글로컬 진보 (TripAdvisor 기초 세팅)", "", 2)
    check_action("c6_2", "Instagram 영문 계정 없음 → 🔵 PinUp: 다채널 글로컬 진보 (Instagram 글로벌 계정 세팅)", "", 3)

    if not immediate_actions and not suggested_actions:
        st.success("🎉 완벽합니다! 현재 즉시 개선할 사항이 없습니다.")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if immediate_actions:
                st.error("#### 🔴 즉시 개선 필요")
                for act in immediate_actions:
                    st.markdown(f"- {act}")
            else:
                st.info("#### 🔴 즉시 개선 필요\n\n해당 사항이 없습니다.")
                
        with col_act2:
            if suggested_actions:
                st.warning("#### 🟡 추가 최적화 권장")
                for act in suggested_actions:
                    st.markdown(f"- {act}")
            else:
                st.info("#### 🟡 추가 최적화 권장\n\n해당 사항이 없습니다.")
    
    st.divider()
    st.header("✨ Section 4: AI 기반 종합 리포트 및 액션 플랜")

    def format_analysis(val):
        """analysis dict → 구조화된 마크다운 문자열"""
        if isinstance(val, str):
            return val
        if not isinstance(val, dict):
            return str(val)
        
        lines = []
        if "strengths" in val:
            lines.append("## ✅ 강점 (Strengths)")
            items = val["strengths"]
            if isinstance(items, list):
                for item in items:
                    lines.append(f"- {item}")
            else:
                lines.append(str(items))
        if "weaknesses" in val:
            lines.append("\n## ⚠️ 약점 (Weaknesses)")
            items = val["weaknesses"]
            if isinstance(items, list):
                for item in items:
                    lines.append(f"- {item}")
            else:
                lines.append(str(items))
        if "seo_opportunities" in val:
            lines.append("\n## 🚀 SEO 개선 기회")
            items = val["seo_opportunities"]
            if isinstance(items, list):
                for item in items:
                    lines.append(f"- {item}")
            else:
                lines.append(str(items))
        # 알 수 없는 키 fallback
        known = {"strengths", "weaknesses", "seo_opportunities"}
        for k, v in val.items():
            if k not in known:
                lines.append(f"\n## {k}")
                if isinstance(v, list):
                    for item in v:
                        lines.append(f"- {item}")
                else:
                    lines.append(str(v))
        return "\n".join(lines)

    def format_action_plan(val):
        """action_plan list/dict → 구조화된 마크다운 문자열"""
        if isinstance(val, str):
            return val
        if isinstance(val, dict):
            # {"step1": ..., "step2": ...} 형태
            lines = []
            for k, v in val.items():
                if isinstance(v, dict):
                    title = v.get("title", k)
                    desc  = v.get("description", "")
                    lines.append(f"### {title}")
                    if desc:
                        lines.append(f"{desc}")
                else:
                    lines.append(f"### {k}")
                    lines.append(str(v))
            return "\n\n".join(lines)
        if isinstance(val, list):
            lines = []
            for i, item in enumerate(val, 1):
                if isinstance(item, dict):
                    title = item.get("title", f"Step {i}")
                    desc  = item.get("description", "")
                    lines.append(f"### Step {i}. {title}")
                    if desc:
                        lines.append(f"{desc}")
                else:
                    lines.append(f"### Step {i}")
                    lines.append(str(item))
            return "\n\n".join(lines)
        return str(val)

    def generate_diagnostic(name_ko, name_en, loc, category, menu_text, diag_date, total_score):
        prompt = f"""
You are a World-class Local SEO Analyst & Restaurant Marketing Expert.
Provide a comprehensive Google Business Profile (GBP) diagnostic report based on the restaurant info below.
Write everything in Korean. Use the manual checklist score ({total_score}/100) to calibrate the SEO score and depth of analysis.

Restaurant Info:
- 한국어 식당명: {name_ko}
- 영문 식당명: {name_en if name_en else '미등록'}
- 주소: {loc}
- 음식 카테고리: {category}
- 대표 메뉴: {menu_text if menu_text else '미등록'}
- 진단 날짜: {diag_date}
- 체크리스트 점수: {total_score}/100

Return a JSON object with EXACTLY these 3 keys:
1. "seo_score": string — A GBP Visibility Score (0-100) with a concise 1-sentence Korean assessment.
2. "analysis": object with these 3 keys:
   - "strengths": array of Korean strings (3~5 items)
   - "weaknesses": array of Korean strings (3~5 items)
   - "seo_opportunities": array of Korean strings (3~5 items)
3. "action_plan": array of 3 objects, each with:
   - "step": number (1, 2, or 3)
   - "title": Korean string — concise step title
   - "description": Korean string — detailed 3~4 sentence description of what to do
"""
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        raw = json.loads(response.text)
        # 후처리: 구조화된 데이터를 마크다운 문자열로 변환
        raw["analysis"]     = format_analysis(raw.get("analysis", ""))
        raw["action_plan"]  = format_action_plan(raw.get("action_plan", ""))
        return raw


    def create_pdf(name_ko, name_en, category, date_str, score, analysis, plan):
        from fpdf import FPDF
        import tempfile

        # AI가 dict를 반환할 경우 안전하게 문자열로 변환
        def to_str(val):
            if isinstance(val, dict):
                return "\n".join(f"{k}: {v}" for k, v in val.items())
            return str(val) if val else ""
        score    = to_str(score)
        analysis = to_str(analysis)
        plan     = to_str(plan)
        
        class PDF(FPDF):
            def header(self):
                # PinUp Branding
                self.set_font('NanumGothic', 'B', 15)
                self.cell(0, 10, 'PinUp GBP 진단 리포트', 0, 1, 'C')
                self.ln(5)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('NanumGothic', '', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = PDF()
        # Add a Korean font (Assuming NanumGothic.ttf is in the same directory)
        font_path = os.path.join(os.path.dirname(__file__), "NanumGothic.ttf")
        if os.path.exists(font_path):
            pdf.add_font("NanumGothic", "", font_path, uni=True)
            pdf.add_font("NanumGothic", "B", font_path, uni=True)
        else:
            st.warning("Korean font not found. PDF might not render Korean properly. Please ensure 'NanumGothic.ttf' is in the project directory.")
        
        pdf.add_page()
        pdf.set_font("NanumGothic", "B", 14)
        pdf.cell(0, 10, f"식당명: {name_ko} ({name_en if name_en else '영문 미등록'})", 0, 1, 'L')
        pdf.set_font("NanumGothic", "", 11)
        pdf.cell(0, 8, f"카테고리: {category}   |   진단일: {date_str}", 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font("NanumGothic", "B", 12)
        pdf.cell(0, 10, "[예상 탐색 가시성 점수]", 0, 1, 'L')
        pdf.set_font("NanumGothic", "", 10)
        pdf.multi_cell(0, 8, score)
        pdf.ln(5)
        
        pdf.set_font("NanumGothic", "B", 12)
        pdf.cell(0, 10, "[현재 상태 분석]", 0, 1, 'L')
        pdf.set_font("NanumGothic", "", 10)
        pdf.multi_cell(0, 8, analysis)
        pdf.ln(5)
        
        pdf.set_font("NanumGothic", "B", 12)
        pdf.cell(0, 10, "[3-Step 개선 액션 플랜]", 0, 1, 'L')
        pdf.set_font("NanumGothic", "", 10)
        pdf.multi_cell(0, 8, plan)
        
        # Save to a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        pdf.output(temp_path)
        return temp_path

    if st.button("📈 Report Generation"):
        if not api_key:
            st.error("Please enter your Google API Key in the sidebar.")
        elif not all([diag_name_ko, diag_address, diag_category]):
            st.error("필수 항목(식당명, 주소, 카테고리)을 모두 입력해주세요 (Please fill in all required fields).")
        else:
            with st.spinner("Analyzing GBP and generating diagnostic report..."):
                try:
                    result = generate_diagnostic(diag_name_ko, diag_name_en, diag_address, diag_category, diag_menu, diag_date.strftime("%Y-%m-%d"), total_score)
                    st.success("✅ 진단 리포트가 성공적으로 생성되었습니다!")

                    # Store results in session state
                    st.session_state['result_name_ko'] = diag_name_ko
                    st.session_state['result_name_en'] = diag_name_en
                    st.session_state['result_category'] = diag_category
                    st.session_state['result_address'] = diag_address
                    st.session_state['result_date'] = diag_date.strftime("%Y-%m-%d")
                    st.session_state['result_total_score'] = total_score
                    st.session_state['seo_score'] = result.get("seo_score", "")
                    st.session_state['analysis'] = result.get("analysis", "")
                    st.session_state['action_plan'] = result.get("action_plan", "")

                except Exception as e:
                    st.error(f"Failed to generate report: {e}")

    # ─── 결과 대시보드 + 다운로드 ───────────────────────────────────────
    if 'seo_score' in st.session_state:
        st.divider()
        
        rname_ko   = st.session_state['result_name_ko']
        rname_en   = st.session_state.get('result_name_en', '')
        rcategory  = st.session_state['result_category']
        raddress   = st.session_state.get('result_address', '')
        rdate      = st.session_state['result_date']
        rscore_txt = st.session_state['seo_score']
        ranalysis  = st.session_state['analysis']
        rplan      = st.session_state['action_plan']
        rtotal     = st.session_state.get('result_total_score', total_score)

        # ── 1-Page 보고서 미리보기 (Streamlit 네이티브) ─────────────────
        st.subheader("📋 1-Page 진단 보고서")
        
        # 헤더 카드
        st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a1a2e,#0f3460);color:#fff;padding:20px 28px;border-radius:12px;margin-bottom:16px;">
<div style="font-size:11px;letter-spacing:2px;color:#e94560;font-weight:700;">PINUP GBP MANAGER</div>
<div style="font-size:22px;font-weight:700;margin-top:4px;">{rname_ko} <span style="font-size:14px;opacity:.7;">({rname_en if rname_en else '영문명 미등록'})</span></div>
<div style="font-size:13px;opacity:.65;margin-top:6px;">📍 {raddress}&nbsp;&nbsp;|&nbsp;&nbsp;🍽️ {rcategory}&nbsp;&nbsp;|&nbsp;&nbsp;📅 {rdate}</div>
</div>
""", unsafe_allow_html=True)

        # 점수 지표 행
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📊 체크리스트 총점", f"{rtotal} / 100")
        
        # 등급 계산
        if rtotal <= 20:   grade_lbl = "🔴 위험"
        elif rtotal <= 40: grade_lbl = "🟠 미흡"
        elif rtotal <= 60: grade_lbl = "🟡 보통"
        elif rtotal <= 80: grade_lbl = "🟢 양호"
        else:              grade_lbl = "🔵 우수"
        m2.metric("🏅 등급", grade_lbl)
        m3.metric("📁 카테고리", rcategory)
        m4.metric("📅 진단일", rdate)

        # AI 가시성 평가 배너
        st.info(f"🎯 **AI 가시성 평가:** {rscore_txt}")

        # 분석 + 액션 플랜 (탭 분리)
        tab_analysis, tab_plan = st.tabs(["🔍 현재 상태 분석", "🚀 3-Step 액션 플랜"])
        with tab_analysis:
            st.markdown(ranalysis)
        with tab_plan:
            st.markdown(rplan)

        # HTML 리포트용 마크다운 → HTML 변환 헬퍼
        def md_to_html(text):
            """마크다운 텍스트를 HTML 조각으로 변환 (## 섹션, ### 소제목, - 불릿, 빈 줄)"""
            import re
            html_parts = []
            lines = text.split("\n")
            in_ul = False
            i = 0
            while i < len(lines):
                line = lines[i]
                # ## 섹션 헤더
                if line.startswith("## "):
                    if in_ul: html_parts.append("</ul>"); in_ul = False
                    html_parts.append(f'<div class="sub-h2">{line[3:].strip()}</div>')
                # ### Step 소제목
                elif line.startswith("### "):
                    if in_ul: html_parts.append("</ul>"); in_ul = False
                    html_parts.append(f'<div class="sub-h3">{line[4:].strip()}</div>')
                # 불릿 항목
                elif line.startswith("- "):
                    if not in_ul: html_parts.append("<ul>"); in_ul = True
                    html_parts.append(f"<li>{line[2:].strip()}</li>")
                # 빈 줄
                elif line.strip() == "":
                    if in_ul: html_parts.append("</ul>"); in_ul = False
                    html_parts.append("<br>")
                # 일반 텍스트
                else:
                    if in_ul: html_parts.append("</ul>"); in_ul = False
                    html_parts.append(f"<p>{line.strip()}</p>")
                i += 1
            if in_ul: html_parts.append("</ul>")
            return "\n".join(html_parts)

        # HTML 다운로드용 리포트 (내부 생성)
        html_report = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<title>PinUp GBP 진단 리포트 - {rname_ko}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Noto Sans KR',sans-serif;background:#f0f2f8;color:#1a1a2e;line-height:1.7}}
  .page{{max-width:900px;margin:32px auto;background:#fff;border-radius:18px;box-shadow:0 6px 30px rgba(0,0,0,.12);overflow:hidden}}

  /* ── 헤더 ── */
  .header{{background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%);color:#fff;padding:32px 40px}}
  .brand{{font-size:11px;letter-spacing:3px;color:#e94560;font-weight:700;text-transform:uppercase}}
  .header h1{{font-size:22px;font-weight:700;margin:6px 0 4px}}
  .header .meta{{font-size:12px;opacity:.65;margin-top:2px}}

  /* ── 점수 밴드 ── */
  .score-band{{background:#0f3460;color:#fff;padding:16px 40px;display:flex;align-items:center;gap:24px}}
  .score-badge{{font-size:40px;font-weight:700;color:#e94560;line-height:1}}
  .score-badge span{{font-size:20px;opacity:.7}}
  .score-label{{font-size:13px;line-height:1.7}}
  .score-label b{{font-size:14px;color:#f5c518}}

  /* ── 본문 ── */
  .body{{padding:32px 40px}}
  .info-row{{display:flex;gap:14px;margin-bottom:28px}}
  .info-card{{flex:1;background:#f4f6fb;border-radius:10px;padding:14px 16px;border-top:3px solid #e94560}}
  .info-card .lbl{{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}}
  .info-card .val{{font-size:15px;font-weight:700}}

  /* ── 섹션 제목 ── */
  .sec-title{{font-size:15px;font-weight:700;color:#0f3460;border-left:4px solid #e94560;
              padding-left:12px;margin:24px 0 12px;letter-spacing:.3px}}
  .sec-body{{font-size:13.5px;line-height:1.85;background:#f9fafc;border-radius:10px;padding:18px 20px}}

  /* ── 분석 서브 헤더 / 불릿 ── */
  .sub-h2{{font-size:13px;font-weight:700;color:#0f3460;margin:14px 0 6px;padding:4px 8px;
            background:#edf1ff;border-radius:6px;display:inline-block}}
  .sub-h3{{font-size:13.5px;font-weight:700;color:#e94560;margin:16px 0 6px;
            padding-left:8px;border-left:3px solid #e94560}}
  ul{{margin:4px 0 4px 20px;padding:0}}
  li{{margin-bottom:5px;font-size:13px;color:#333}}
  p{{font-size:13px;color:#444;margin-bottom:6px}}
  br{{display:block;margin:6px 0}}

  /* ── 푸터 ── */
  .footer{{background:#1a1a2e;color:#888;font-size:11px;text-align:center;padding:14px 40px}}
  .footer b{{color:#e94560;font-weight:700}}
</style></head><body>
<div class="page">
  <div class="header">
    <div class="brand">PinUp GBP Manager</div>
    <h1>{rname_ko} <span style="font-size:15px;opacity:.7">({rname_en if rname_en else '영문명 미등록'})</span></h1>
    <div class="meta">📍 {raddress} &nbsp;|&nbsp; 🍽️ {rcategory} &nbsp;|&nbsp; 📅 {rdate}</div>
  </div>

  <div class="score-band">
    <div class="score-badge">{rtotal}<span>/100</span></div>
    <div class="score-label">
      체크리스트 기반 진단 점수<br>
      <b>AI 가시성 평가:</b> {rscore_txt}
    </div>
  </div>

  <div class="body">
    <div class="info-row">
      <div class="info-card"><div class="lbl">식당명</div><div class="val">{rname_ko}</div></div>
      <div class="info-card"><div class="lbl">주소</div><div class="val">{raddress}</div></div>
      <div class="info-card"><div class="lbl">카테고리</div><div class="val">{rcategory}</div></div>
    </div>

    <div class="sec-title">🔍 현재 상태 분석</div>
    <div class="sec-body">{md_to_html(ranalysis)}</div>

    <div class="sec-title">🚀 3-Step 개선 액션 플랜</div>
    <div class="sec-body">{md_to_html(rplan)}</div>
  </div>

  <div class="footer">Generated by <b>PinUp GBP Manager</b> &nbsp;|&nbsp; {rdate}</div>
</div>
</body></html>"""


        # ── 다운로드 버튼 3종 ─────────────────────────────────────────
        st.markdown("#### 📥 리포트 다운로드")
        dl_col1, dl_col2, dl_col3 = st.columns(3)

        # 1) HTML 다운로드
        with dl_col1:
            st.download_button(
                label="🌐 HTML 다운로드",
                data=html_report.encode("utf-8"),
                file_name=f"PinUp_GBP_Report_{rname_ko}.html",
                mime="text/html",
                use_container_width=True
            )

        # 2) CSV 다운로드
        import csv, io
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["항목", "내용"])
        writer.writerow(["식당명 (한국어)", rname_ko])
        writer.writerow(["식당명 (영문)", rname_en])
        writer.writerow(["주소", raddress])
        writer.writerow(["카테고리", rcategory])
        writer.writerow(["진단일", rdate])
        writer.writerow(["체크리스트 총점 (/100)", rtotal])
        writer.writerow(["AI 가시성 평가", rscore_txt])
        writer.writerow(["현재 상태 분석", ranalysis])
        writer.writerow(["3-Step 액션 플랜", rplan])
        csv_str = csv_buf.getvalue()

        with dl_col2:
            st.download_button(
                label="📊 CSV 다운로드",
                data=csv_str.encode("utf-8-sig"),  # BOM for Excel 한글 호환
                file_name=f"PinUp_GBP_Report_{rname_ko}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # 3) PDF 다운로드
        with dl_col3:
            with st.spinner("PDF 생성 중..."):
                pdf_path = create_pdf(
                    rname_ko, rname_en, rcategory, rdate,
                    rscore_txt, ranalysis, rplan
                )
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="📄 PDF 다운로드",
                    data=pdf_bytes,
                    file_name=f"PinUp_GBP_Report_{rname_ko}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                try:
                    os.remove(pdf_path)
                except:
                    pass

