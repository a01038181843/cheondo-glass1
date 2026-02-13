import streamlit as st
import pandas as pd
import os

# =============================================================================
# [천도글라스 마스터 V50.0] : 모바일 & 태블릿 전용 (WEB)
# =============================================================================

# 1. 페이지 설정 (넓게 보기, 제목 설정)
st.set_page_config(page_title="천도글라스 마스터", layout="wide")

# 2. 스타일 꾸미기 (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드 함수
@st.cache_data # 속도 향상을 위해 데이터 기억하기
def load_data():
    file_path = 'glass_data.xlsx'
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_excel(file_path, engine='openpyxl')
    df.fillna('', inplace=True)
    
    # 숫자 변환
    cols_to_fix = ['열관류율', '투과율', '반사율', 'SC', 'SHGC']
    for col in cols_to_fix:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
    return df

# 4. 메인 화면 시작
st.title("🏙️ 천도글라스 마스터 (Mobile)")
st.caption("Cheondo Glass High-Performance Search System")

df = load_data()

if df is None:
    st.error("❌ 'glass_data.xlsx' 파일이 서버에 없습니다.")
    st.stop()

# --- 사이드바 (검색 필터) ---
with st.sidebar:
    st.header("🔍 검색 조건")
    
    # 브랜드 선택
    brand_list = ["전체"] + sorted(df['브랜드'].unique().tolist())
    f_brand = st.selectbox("브랜드", brand_list)
    
    # 두께 선택
    thick_list = ["전체"] + sorted(df['두께'].unique().tolist())
    f_thick = st.selectbox("두께", thick_list)
    
    # 수치 입력
    f_u_max = st.number_input("열관류율 (Max)", value=9.9, step=0.1)
    f_t_min = st.number_input("투과율 (Min)", value=0.0, step=1.0)
    
    st.info(f"총 데이터: {len(df)}건")

# --- 데이터 필터링 ---
filtered_df = df.copy()

if f_brand != "전체":
    filtered_df = filtered_df[filtered_df['브랜드'] == f_brand]
    
if f_thick != "전체":
    filtered_df = filtered_df[filtered_df['두께'] == f_thick]

# 수치 필터 (0.0 포함 or 이하)
filtered_df = filtered_df[
    ((filtered_df['열관류율'] <= f_u_max) | (filtered_df['열관류율'] == 0)) &
    (filtered_df['투과율'] >= f_t_min)
]

# --- 결과 표시 ---
st.subheader(f"📊 검색 결과: {len(filtered_df)}건")

if not filtered_df.empty:
    # 보기 좋게 컬럼 정리
    display_cols = ['브랜드', '두께', '공식', '모델명', '가스', '열관류율', '투과율', '반사율', 'SC', 'SHGC']
    final_df = filtered_df[display_cols].copy()

    # ★ 색상 입히기 (스타일링)
    def highlight_rows(row):
        styles = [''] * len(row)
        
        # 브랜드 컬러
        if row['브랜드'] == 'LX':
            styles[0] = 'color: red; font-weight: bold;'
        elif row['브랜드'] == 'KCC':
            styles[0] = 'color: blue; font-weight: bold;'
            
        # 프리미엄 (1.0 이하) - 전체 행 초록 배경
        if 0 < row['열관류율'] <= 1.0:
            return ['background-color: #d5f5e3; color: black'] * len(row)
            
        return styles

    # 열관류율 0.0은 '-'로 표시하기 위해 문자열로 변환 (화면 표시용)
    # (주의: 스타일링 적용을 위해 숫자 유지하고 포맷팅으로 처리)
    
    st.dataframe(
        final_df.style.apply(highlight_rows, axis=1)
        .format({"열관류율": "{:.2f}", "투과율": "{:.1f}", "반사율": "{:.1f}", "SC": "{:.2f}", "SHGC": "{:.2f}"}),
        use_container_width=True,
        height=600
    )
else:
    st.warning("검색 결과가 없습니다.")