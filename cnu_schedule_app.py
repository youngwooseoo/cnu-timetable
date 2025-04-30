import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="충남대 시간표 추천 앱", layout="wide")

st.title("📘 충남대 시간표 추천 앱")
st.write("CSV 파일을 업로드하고 조건을 선택하면 시간표를 추천합니다.")

# ✅ 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")
if uploaded_file is None:
    st.warning("먼저 CSV 파일을 업로드해주세요.")
    st.stop()

# ✅ CSV 로딩
df = pd.read_csv(uploaded_file)

# ✅ 전공 선택
majors = df["운영학과"].dropna().unique().tolist()
selected_major = st.selectbox("전공 선택", sorted(majors))

# ✅ 공강 요일 선택
off_day = st.selectbox("공강 원하는 요일", ["없음", "월", "화", "수", "목", "금"])

# ✅ 수업 형태 설정
form_type = st.radio("수업 형태", ["전체", "대면강의", "화상강의"])

# ✅ 교양 미수강 여부
skip_general_ed = st.checkbox("교양 수업 미수강")

# ✅ 원하는 총 학점
credit_range = st.slider("총 이수 학점", min_value=2, max_value=21, value=15)

# ✅ 강의 필터링
filtered = df[df["운영학과"] == selected_major]

if form_type != "전체":
    filtered = filtered[filtered["수업형태"].str.contains(form_type)]

if skip_general_ed:
    filtered = filtered[~filtered["과목구분"].str.contains("교양")]

# 공강 요일 필터링
if off_day != "없음":
    filtered = filtered[~filtered["강의시간"].str.contains(off_day, na=False)]

# ✅ 추천 강의 테이블 출력
st.success(f"🔍 총 {len(filtered)}개의 강의가 조건에 맞습니다.")
st.dataframe(filtered[["과목명", "과목구분", "운영학과", "강의시간", "교수명", "성적평가방식", "수업형태"]])

# ✅ 시각화
def draw_schedule(df):
    days = ["월", "화", "수", "목", "금"]
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, row in df.iterrows():
        times = str(row["강의시간"])
        for day in days:
            if day in times:
                try:
                    time_part = times.split(day)[1].split("(")[0]
                    start, end = time_part.split("~")
                    start_hour = int(start.split(":")[0])
                    end_hour = int(end.split(":")[0])
                    ax.barh(day, end_hour - start_hour, left=start_hour, height=0.5, color="skyblue")
                    ax.text(start_hour + 0.2, days.index(day), row["과목명"], va='center', fontsize=8)
                except:
                    continue

    ax.set_xlim(8, 20)
    ax.set_xlabel("시간")
    ax.set_title("시간표 미리보기")
    st.pyplot(fig)

if not filtered.empty:
    draw_schedule(filtered)
