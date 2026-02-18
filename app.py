import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. 화면 설정 및 제목
st.set_page_config(page_title="천도 실리콘 자재관리", layout="wide")
st.title("🏗️ 천도글라스 실리콘 마스터 (통합본)")

# 2. 구글 시트 연결 (가장 안전한 최신 방식)
try:
    # 이 방식은 secrets.json 파일 없이 Streamlit 설정창의 주소만 사용합니다.
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
except Exception as e:
    st.error("시트 연결에 문제가 있습니다. [설정-Secrets]의 주소를 확인해주세요.")
    st.stop()

# 3. 화면 구성 (탭)
tab1, tab2, tab3 = st.tabs(["📊 재고 현황", "⚡ 입출고 입력", "⚙️ 제품 등록/관리"])

# --- 탭1: 재고 현황 ---
with tab1:
    st.subheader("현재 창고 재고")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("데이터가 없습니다. 제품을 먼저 등록하세요.")

# --- 탭2: 입출고 입력 ---
with tab2:
    st.subheader("실시간 입출고 기록")
    if not df.empty:
        with st.form("inout_form"):
            # 제품명과 색상을 합쳐서 선택하기 쉽게 만듦
            df['display'] = df['제품명'] + " (" + df['색상'] + ")"
            selected = st.selectbox("품목 선택", df['display'])
            mode = st.radio("작업 구분", ["📦 입고", "📤 출고"], horizontal=True)
            qty = st.number_input("박스 수량", min_value=1, step=1)
            
            if st.form_submit_button("장부 기록하기"):
                idx = df[df['display'] == selected].index[0]
                # 숫자 계산
                if mode == "📦 입고":
                    df.at[idx, '현재고'] = int(df.at[idx, '현재고']) + qty
                else:
                    df.at[idx, '현재고'] = int(df.at[idx, '현재고']) - qty
                
                # 시트에 즉시 반영 (임시 열 제거 후 업데이트)
                final_df = df.drop(columns=['display'])
                conn.update(data=final_df)
                st.success(f"{selected} 변경 완료!")
                st.rerun()

# --- 탭3: 제품 등록 및 삭제 ---
with tab3:
    st.subheader("🆕 신규 제품 등록")
    with st.form("add_product"):
        col1, col2 = st.columns(2)
        p_name = col1.text_input("제품명 (예: KCC SL1000)")
        p_color = col1.text_input("색상 (예: 백색)")
        p_usage = col1.selectbox("용도", ["내부용", "외부용", "구조용", "기타"])
        
        p_stock = col2.number_input("현재 재고(Box)", min_value=0)
        p_price = col2.number_input("단가(원)", min_value=0)
        p_safe = col2.number_input("안전재고 레벨", min_value=0)
        
        if st.form_submit_button("제품 추가"):
            if p_name and p_color:
                new_row = pd.DataFrame([{"제품명": p_name, "색상": p_color, "용도": p_usage, "현재고": p_stock, "단가": p_price, "안전재고": p_safe}])
                # 기존 데이터에 합치기
                updated_df = pd.concat([df.drop(columns=['display'], errors='ignore'), new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("새 제품이 등록되었습니다!")
                st.rerun()
