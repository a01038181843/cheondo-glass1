import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- 화면 설정 ---
st.set_page_config(page_title="천도 실리콘 자재관리", layout="wide", page_icon="🏗️")

# --- 스타일(디자인) 설정 ---
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #ddd; border-radius: 10px; padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 구글 시트 연결 (열쇠 사용) ---
@st.cache_resource
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    try:
        # secrets.json 파일을 찾아서 열쇠로 씁니다
        creds = ServiceAccountCredentials.from_json_keyfile_name('secrets.json', scope)
        client = gspread.authorize(creds)
        return client
    except:
        return None

# --- 데이터 읽어오기 ---
def load_data():
    client = init_connection()
    if client is None: return None
    try:
        # 구글 시트 이름이 'silicon_db'여야 합니다
        sheet = client.open("silicon_db").sheet1
        return pd.DataFrame(sheet.get_all_records())
    except: return None

# --- 재고 수정하기 (입고/출고) ---
def update_stock(product, qty, type='in'):
    client = init_connection()
    sheet = client.open("silicon_db").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # 엑셀에서 제품 찾기
    idx = df[df['제품명'] == product].index
    if len(idx) > 0:
        row = idx[0] + 2 # 엑셀 행 번호 계산
        current = df.loc[idx[0], '현재고']
        
        # 더하기 빼기 계산
        if type == 'in':
            new_val = current + qty
        else:
            new_val = current - qty
            
        # 엑셀 파일 업데이트 (4번째 칸 = D열)
        sheet.update_cell(row, 4, int(new_val))
        return True
    return False

# --- 메인 화면 시작 ---
st.title("🏗️ 천도글라스 실리콘 마스터")
st.caption("구글 시트 실시간 연동 시스템")

df = load_data()

# 연결 실패시 에러 메시지
if df is None:
    st.error("🚨 연결 실패!")
    st.write("1. 깃허브에 secrets.json 파일이 있는지 확인하세요.")
    st.write("2. 구글 시트 이름이 'silicon_db' 인지 확인하세요.")
    st.write("3. 구글 시트 [공유] 버튼을 눌러 로봇 이메일을 초대했는지 확인하세요.")
    st.stop()

# --- 대시보드 (카드) ---
c1, c2, c3 = st.columns(3)
c1.metric("총 재고", f"{df['현재고'].sum()} Box")
# 단가와 현재고를 곱해서 자산가치 계산
total_asset = (pd.to_numeric(df['단가']) * pd.to_numeric(df['현재고'])).sum()
c2.metric("총 자산 가치", f"{total_asset:,.0f} 원")
c3.metric("부족 품목", f"{len(df[df['현재고'] <= df['안전재고']])} 건")

st.divider()

# --- 탭 화면 (조회 / 입력) ---
t1, t2 = st.tabs(["📊 재고 현황", "⚡ 입출고 입력"])

with t1:
    col1, col2 = st.columns([2,1])
    col1.dataframe(df, use_container_width=True)
    if not df.empty:
        fig = px.pie(df, values='현재고', names='색상', title="색상별 재고")
        col2.plotly_chart(fig, use_container_width=True)

with t2:
    cc1, cc2 = st.columns(2)
    
    # [입고 화면]
    with cc1:
        st.info("📦 입고 (자재 구매)")
        in_name = st.selectbox("어떤 제품인가요?", df['제품명'], key='in_sb')
        in_qty = st.number_input("몇 박스 들어왔나요?", min_value=1, key='in_qty')
        if st.button("입고 등록"):
            if update_stock(in_name, in_qty, 'in'):
                st.success("처리 완료! (새로고침 됩니다)")
                st.rerun()

    # [출고 화면]
    with cc2:
        st.error("🚀 출고 (현장 사용)")
        out_name = st.selectbox("어떤 제품인가요?", df['제품명'], key='out_sb')
        out_qty = st.number_input("몇 박스 썼나요?", min_value=1, key='out_qty')
        if st.button("출고 등록"):
            if update_stock(out_name, out_qty, 'out'):
                st.success("처리 완료! (새로고침 됩니다)")
                st.rerun()
