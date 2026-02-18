import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 화면 설정
st.set_page_config(page_title="천도 실리콘 자재관리", layout="wide")

# 구글 시트 연결 함수 (열쇠 사용 방식)
@st.cache_resource
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name('secrets.json', scope)
        client = gspread.authorize(creds)
        # 시트 이름 'silicon_db'를 엽니다
        return client.open("silicon_db").sheet1
    except Exception as e:
        st.error(f"연결 오류: {e}")
        return None

sheet = init_connection()

# 데이터 불러오기
def get_data():
    if sheet:
        return pd.DataFrame(sheet.get_all_records())
    return pd.DataFrame()

df = get_data()

st.title("🏗️ 천도글라스 실리콘 마스터 (v2.1)")

tab1, tab2, tab3 = st.tabs(["📊 재고 현황", "⚡ 입출고 입력", "⚙️ 제품 등록/관리"])

with tab1:
    st.subheader("현재고 목록")
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("입출고 기록")
    if not df.empty:
        with st.form("inout_form"):
            item_list = df['제품명'] + " (" + df['색상'] + ")"
            selected_item = st.selectbox("품목 선택", item_list)
            mode = st.radio("구분", ["📦 입고", "📤 출고"], horizontal=True)
            qty = st.number_input("수량(Box)", min_value=1)
            if st.form_submit_button("확인"):
                idx = df[df['제품명'] + " (" + df['색상'] + ")" == selected_item].index[0]
                current = int(df.at[idx, '현재고'])
                new_val = current + qty if mode == "📦 입고" else current - qty
                sheet.update_cell(idx + 2, 4, new_val) # 4번째 열(현재고) 업데이트
                st.success("반영되었습니다!")
                st.rerun()

with tab3:
    st.subheader("🆕 새 제품 추가")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("제품명")
        color = c1.text_input("색상")
        usage = c1.selectbox("용도", ["내부용", "외부용", "구조용"])
        stock = c2.number_input("현재고", min_value=0)
        price = c2.number_input("단가", min_value=0)
        safe = c2.number_input("안전재고", min_value=0)
        
        if st.form_submit_button("제품 등록"):
            sheet.append_row([name, color, usage, stock, price, safe])
            st.success("새 제품이 등록되었습니다!")
            st.rerun()
