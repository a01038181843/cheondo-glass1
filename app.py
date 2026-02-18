import streamlit as st
import pandas as pd

# 설정
st.set_page_config(page_title="천도 실리콘 관리", layout="wide")
st.title("🏗️ 천도글라스 실리콘 마스터 (v4.1)")

# 대표님 구글 시트 정보 (주소에서 ID만 추출)
SHEET_ID = "193becb8J4mpt1ruYvoZobtJ3I9KCVRjXh8OxzlgYzco"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=0)
def load_data():
    try:
        # 보안 파일 없이 링크 권한으로 데이터를 읽어옵니다.
        return pd.read_csv(CSV_URL)
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = load_data()

# 화면 구성 (조회와 입출고 가이드)
tab1, tab2 = st.tabs(["📊 재고 현황", "⚡ 입출고 관리"])

with tab1:
    st.subheader("현재 창고 재고 현황")
    if not df.empty:
        # 검색 기능 추가
        search = st.text_input("🔍 제품명 또는 색상 검색")
        if search:
            df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("시트에 데이터가 없거나 접근 권한이 없습니다.")

with tab2:
    st.subheader("⚡ 실시간 입출고 및 제품 관리")
    st.info("💡 보안 에러를 원천 차단하기 위해, 아래 '장부 열기' 버튼을 눌러 숫자를 수정해 주세요.")
    st.write("1. 아래 버튼을 눌러 **구글 시트(장부)**를 엽니다.")
    st.write("2. '현재고' 칸의 숫자를 바꾸거나 맨 아래 줄에 새 제품을 적습니다.")
    st.write("3. 앱으로 돌아와서 **새로고침(F5)**을 누르면 즉시 반영됩니다.")
    
    # 구글 시트로 바로가는 큰 버튼
    st.link_button("📂 천도글라스 실리콘 장부 열기", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    
    st.divider()
    st.warning("⚠️ 주의: 장부에서 '제목 줄(1행)'은 절대 건드리지 마세요!")
