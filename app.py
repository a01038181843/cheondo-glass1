import streamlit as st
import pandas as pd

# 설정
st.set_page_config(page_title="천도 실리콘 관리", layout="wide")
st.title("🏗️ 천도글라스 실리콘 마스터 (v4.0 - 무결점 버전)")

# [중요] 비밀 파일(json) 없이 주소로만 직접 접근합니다.
# 대표님의 시트 주소에서 ID 부분만 추출했습니다.
SHEET_ID = "193becb8J4mpt1ruYvoZobtJ3I9KCVRjXh8OxzlgYzco"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=0)
def load_data():
    try:
        # 이 방식은 보안 파일 에러(JWT)가 원천적으로 발생하지 않습니다.
        return pd.read_csv(CSV_URL)
    except Exception as e:
        st.error(f"데이터를 가져올 수 없습니다: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    tab1, tab2 = st.tabs(["📊 재고 현황", "⚡ 입출고 관리(안내)"])

    with tab1:
        st.subheader("현재 창고 재고")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.info("💡 보안 오류를 피하기 위해, 현재 버전은 '조회' 전용으로 먼저 복구했습니다.")
        st.write("재고 수정이나 제품 등록은 아래 구글 시트에서 직접 하시면 앱에 즉시 반영됩니다.")
        st.markdown(f"[👉 실리콘 장부(구글 시트) 바로가기](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)")
else:
    st.warning("구글 시트의 공유 설정을 '링크가 있는 모든 사용자 - 뷰어(또는 편집자)'로 바꿔주세요.")
