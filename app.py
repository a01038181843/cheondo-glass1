import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 화면 설정
st.set_page_config(page_title="천도 실리콘 관리", layout="wide")
st.title("🏗️ 천도글라스 실리콘 마스터 (입력 기능 복구)")

# 2. 구글 시트 연결 (가장 안정적인 최신 방식)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # 데이터를 읽어옵니다.
    return conn.read(ttl=0).dropna(how='all')

df = load_data()

# 3. 화면 구성 (탭)
tab1, tab2, tab3 = st.tabs(["📊 재고 현황", "⚡ 입출고 입력", "⚙️ 제품 관리"])

# --- 탭1: 재고 현황 ---
with tab1:
    st.subheader("현재 창고 재고")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- 탭2: 입출고 입력 (대표님이 원하신 바로 그 기능!) ---
with tab2:
    st.subheader("앱에서 바로 입출고 기록")
    if not df.empty:
        with st.form("inout_form"):
            # 제품명과 색상을 합쳐서 선택창을 만듭니다.
            df['display'] = df['제품명'].astype(str) + " (" + df['색상'].astype(str) + ")"
            selected = st.selectbox("품목 선택", df['display'])
            mode = st.radio("작업 구분", ["📦 입고", "📤 출고"], horizontal=True)
            qty = st.number_input("박스 수량", min_value=1, step=1)
            
            if st.form_submit_button("장부 기록하기"):
                idx = df[df['display'] == selected].index[0]
                # 숫자 계산
                current_stock = int(df.at[idx, '현재고'])
                if mode == "📦 입고":
                    df.at[idx, '현재고'] = current_stock + qty
                else:
                    df.at[idx, '현재고'] = current_stock - qty
                
                # 시트에 즉시 반영 (임시 열 제거 후 업데이트)
                updated_df = df.drop(columns=['display'])
                conn.update(data=updated_df)
                st.success(f"✅ {selected} {qty}박스 {mode} 완료!")
                st.rerun()

# --- 탭3: 제품 등록 ---
with tab3:
    st.subheader("🆕 신규 제품 등록")
    with st.form("add_product"):
        c1, c2 = st.columns(2)
        p_name = c1.text_input("제품명")
        p_color = c1.text_input("색상")
        p_stock = c2.number_input("초기 재고", min_value=0)
        p_price = c2.number_input("단가", min_value=0)
        
        if st.form_submit_button("제품 추가"):
            if p_name and p_color:
                new_row = pd.DataFrame([{"제품명": p_name, "색상": p_color, "용도": "기타", "현재고": p_stock, "단가": p_price, "안전재고": 10}])
                final_df = pd.concat([df.drop(columns=['display'], errors='ignore'), new_row], ignore_index=True)
                conn.update(data=final_df)
                st.success("새 제품이 등록되었습니다!")
                st.rerun()
