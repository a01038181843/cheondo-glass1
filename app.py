import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. 화면 설정
st.set_page_config(page_title="천도 실리콘 관리", layout="wide")
st.title("🏗️ 천도글라스 실리콘 마스터 (최종본)")

# 2. 구글 시트 연결 (가장 확실한 secrets.json 직접 읽기 방식)
@st.cache_resource
def get_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # 깃허브에 올려둔 secrets.json 파일을 바로 사용합니다.
        creds = ServiceAccountCredentials.from_json_keyfile_name('secrets.json', scope)
        client = gspread.authorize(creds)
        # 대표님 시트 ID를 직접 입력해두었습니다.
        return client.open_by_key("193becb8J4mpt1ruYvoZobtJ3I9KCVRjXh8OxzlgYzco").sheet1
    except Exception as e:
        st.error(f"연결 실패: {e}")
        return None

sheet = get_sheet()

if sheet:
    # 데이터 읽기
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    tab1, tab2, tab3 = st.tabs(["📊 재고 현황", "⚡ 입출고 입력", "⚙️ 제품 등록/관리"])

    with tab1:
        st.subheader("창고 재고 목록")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("실시간 입출고")
        if not df.empty:
            with st.form("inout"):
                df['display'] = df['제품명'] + " (" + df['색상'] + ")"
                selected = st.selectbox("품목 선택", df['display'])
                mode = st.radio("구분", ["📦 입고", "📤 출고"], horizontal=True)
                qty = st.number_input("수량", min_value=1, step=1)
                if st.form_submit_button("저장"):
                    idx = df[df['display'] == selected].index[0]
                    # 구글 시트 업데이트 (엑셀은 1부터 시작, 제목줄 제외 +2)
                    row_idx = int(idx) + 2
                    current_val = int(df.at[idx, '현재고'])
                    new_val = current_val + qty if mode == "📦 입고" else current_val - qty
                    sheet.update_cell(row_idx, 4, new_val) # 4번째 열이 '현재고'
                    st.success("반영 완료!"); st.rerun()

    with tab3:
        st.subheader("⚙️ 신규 제품 등록")
        with st.form("add"):
            c1, c2 = st.columns(2)
            name = c1.text_input("제품명"); color = c1.text_input("색상")
            stock = c2.number_input("초기재고", min_value=0); price = c2.number_input("단가", min_value=0)
            if st.form_submit_button("신규 등록"):
                # 구글 시트에 줄 추가 (제품명, 색상, 용도, 현재고, 단가, 안전재고)
                sheet.append_row([name, color, "기타", stock, price, 10])
                st.success("등록 완료!"); st.rerun()
