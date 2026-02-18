import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="천도글라스 실리콘 마스터", layout="wide")

st.title("🏗️ 천도글라스 실리콘 마스터 (v2.0)")
st.caption("실시간 재고 관리 및 제품 관리 시스템")

# 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 불러오기 함수
def load_data():
    return conn.read(ttl=0)

df = load_data()

# 상단 메뉴 (탭 구성)
tab1, tab2, tab3 = st.tabs(["📊 재고 현황", "⚡ 입출고 입력", "⚙️ 제품 등록/관리"])

# --- TAB 1: 재고 현황 ---
with tab1:
    st.subheader("실시간 재고 목록")
    if not df.empty:
        # 검색 및 필터
        search = st.text_input("🔍 제품명 또는 색상 검색")
        filtered_df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info("등록된 제품이 없습니다. '제품 등록' 탭에서 새 제품을 추가하세요.")

# --- TAB 2: 입출고 입력 ---
with tab2:
    st.subheader("빠른 입출고 기록")
    if not df.empty:
        with st.form("log_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                item = st.selectbox("품목 선택", df['제품명'] + " (" + df['색상'] + ")")
            with col2:
                mode = st.radio("구분", ["📦 입고", "📤 출고"], horizontal=True)
            with col3:
                qty = st.number_input("수량(Box)", min_value=1, step=1)
            
            submit = st.form_submit_button("기록하기")
            
            if submit:
                # 데이터 업데이트 로직
                idx = df[df['제품명'] + " (" + df['색상'] + ")" == item].index[0]
                if mode == "📦 입고":
                    df.at[idx, '현재고'] += qty
                else:
                    df.at[idx, '현재고'] -= qty
                
                conn.update(data=df)
                st.success(f"{item} {qty}박스 {mode} 완료!")
                st.rerun()
    else:
        st.warning("먼저 제품을 등록해야 입출고가 가능합니다.")

# --- TAB 3: 제품 등록/관리 (대표님이 원하신 기능!) ---
with tab3:
    st.subheader("🆕 새 제품 등록")
    with st.form("new_item_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_name = st.text_input("제품명 (예: 다우 1001)")
            new_color = st.text_input("색상 (예: 백색)")
        with c2:
            new_type = st.selectbox("용도", ["내부용", "외부용", "구조용", "기타"])
            new_stock = st.number_input("초기 재고(Box)", min_value=0, step=1)
        with c3:
            new_price = st.number_input("단가(원)", min_value=0, step=100)
            new_safe = st.number_input("안전 재고(Box)", min_value=0, step=1)
            
        add_btn = st.form_submit_button("제품 추가하기")
        
        if add_btn:
            if new_name and new_color:
                new_data = pd.DataFrame([{
                    "제품명": new_name,
                    "색상": new_color,
                    "용도": new_type,
                    "현재고": new_stock,
                    "단가": new_price,
                    "안전재고": new_safe
                }])
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(data=updated_df)
                st.success(f"'{new_name}({new_color})' 제품이 등록되었습니다!")
                st.rerun()
            else:
                st.error("제품명과 색상은 필수 입력 사항입니다.")

    st.divider()
    st.subheader("🗑️ 제품 삭제")
    if not df.empty:
        del_item = st.selectbox("삭제할 제품 선택", df['제품명'] + " (" + df['색상'] + ")", key="del")
        if st.button("선택한 제품 영구 삭제", type="primary"):
            df = df[df['제품명'] + " (" + df['색상'] + ")" != del_item]
            conn.update(data=df)
            st.success("삭제되었습니다.")
            st.rerun()
