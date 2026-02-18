import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="천도 실리콘 관리", layout="wide")
st.title("🏗️ 천도글라스 실리콘 마스터 (최종본)")

# 연결 설정
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl=0).dropna(how='all')

df = load_data()

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
                val = int(df.at[idx, '현재고'])
                df.at[idx, '현재고'] = val + qty if mode == "📦 입고" else val - qty
                conn.update(data=df.drop(columns=['display']))
                st.success("반영 완료!"); st.rerun()

with tab3:
    st.subheader("⚙️ 제품 관리")
    with st.form("add"):
        c1, c2 = st.columns(2)
        name = c1.text_input("제품명"); color = c1.text_input("색상")
        stock = c2.number_input("초기재고", min_value=0); price = c2.number_input("단가", min_value=0)
        if st.form_submit_button("신규 등록"):
            new_row = pd.DataFrame([{"제품명":name, "색상":color, "용도":"기타", "현재고":stock, "단가":price, "안전재고":10}])
            conn.update(data=pd.concat([df.drop(columns=['display'], errors='ignore'), new_row], ignore_index=True))
            st.success("등록 완료!"); st.rerun()
