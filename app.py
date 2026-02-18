import streamlit as st
import pandas as pd
from 메뉴얼_구글연결 import GSheetsConnection # 이 부분은 제가 내부적으로 처리해 드릴게요

st.set_page_config(page_title="천도 실리콘 관리", layout="wide")
st.title("🏗️ 천도글라스 실리콘 마스터 (v3.0)")

# [핵심] 복잡한 파일 없이 주소로만 바로 연결합니다.
try:
    conn = st.connection("gsheets", type="streamlit_gsheets.gsheets_connection.GSheetsConnection")
    df = conn.read(ttl=0).dropna(how='all')
except Exception as e:
    st.error(f"연결 오류가 발생했습니다. 아래 설정을 확인해주세요: {e}")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📊 재고 현황", "⚡ 입출고 입력", "⚙️ 제품 관리"])

with tab1:
    st.subheader("현재 창고 재고")
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("실시간 입출고")
    if not df.empty:
        with st.form("inout"):
            df['display'] = df['제품명'] + " (" + df['색상'] + ")"
            selected = st.selectbox("품목 선택", df['display'])
            mode = st.radio("구분", ["📦 입고", "📤 출고"], horizontal=True)
            qty = st.number_input("수량", min_value=1, step=1)
            if st.form_submit_button("장부 기록하기"):
                idx = df[df['display'] == selected].index[0]
                val = int(df.at[idx, '현재고'])
                df.at[idx, '현재고'] = val + qty if mode == "📦 입고" else val - qty
                conn.update(data=df.drop(columns=['display']))
                st.success("반영 완료!"); st.rerun()

with tab3:
    st.subheader("🆕 신규 제품 등록")
    with st.form("add"):
        c1, c2 = st.columns(2)
        name = c1.text_input("제품명"); color = c1.text_input("색상")
        stock = c2.number_input("초기재고", min_value=0); price = c2.number_input("단가", min_value=0)
        if st.form_submit_button("제품 추가"):
            new_row = pd.DataFrame([{"제품명":name, "색상":color, "용도":"기타", "현재고":stock, "단가":price, "안전재고":10}])
            conn.update(data=pd.concat([df.drop(columns=['display'], errors='ignore'), new_row], ignore_index=True))
            st.success("등록 성공!"); st.rerun()
