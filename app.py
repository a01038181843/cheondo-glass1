import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 설정
st.set_page_config(page_title="천도 실리콘 관리", layout="wide")
st.title("🏗️ 천도글라스 실리콘 마스터 (최종)")

# 연결 (파일 직접 읽기)
@st.cache_resource
def init_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('secrets.json', scope)
    client = gspread.authorize(creds)
    return client.open_by_key("193becb8J4mpt1ruYvoZobtJ3I9KCVRjXh8OxzlgYzco").sheet1

sheet = init_sheet()
df = pd.DataFrame(sheet.get_all_records())

# (이하 입출고 및 등록 로직은 동일)
st.write("연결 성공! 이제 데이터를 입력해 보세요.")
st.dataframe(df)
