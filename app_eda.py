import streamlit as st
import pyrebase
import time
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------
# Firebase 설정
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.firebasestorage.app",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
firestore = firebase.database()
storage = firebase.storage()

# ---------------------
# 세션 상태 초기화
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.user_name = ""
    st.session_state.user_gender = "선택 안함"
    st.session_state.user_phone = ""
    st.session_state.profile_image_url = ""

# ---------------------
# 홈 페이지 클래스
# ---------------------
class Home:
    def __init__(self, login_page, register_page, findpw_page):
        st.title("🏠 Home")

        if st.session_state.get("logged_in"):
            st.success(f"{st.session_state.get('user_email')}님 환영합니다.")

        st.markdown("""
        ---
        ### 📈 연도별 지역 인구 추이 분석 소개

        이 웹 애플리케이션은 **연도별 지역 인구 변화**를 다양한 시각화와 통계 기법으로 탐색하고 분석합니다.
        사용자 업로드 기반의 `population_trends.csv` 파일을 활용하여 다음과 같은 분석을 수행합니다:

        #### 🔍 주요 변수:
        - `연도`: 연도 정보 (예: 2010, 2011, 2012 등)
        - `지역`: 행정구역 단위 (예: 서울특별시, 부산광역시 등)
        - `인구`: 해당 연도·지역의 총 인구수
        - `출생아수(명)`, `사망자수(명)`: 부가적인 인구 변화 요인

        #### 📊 제공되는 분석 기능:
        1. 결측치 및 중복값 확인
        2. 연도별 전체 인구 변화 시각화
        3. 지역별 인구 변화량 순위
        4. 증감률 기준 상위 지역/연도 추출
        5. 누적 영역 그래프 등 다양한 시각화

        ---
        📁 분석에 사용할 CSV 파일 예시는 `population_trends.csv` 형식을 따라야 하며,
        기본적으로 `연도`, `지역`, `인구` 세 컬럼이 반드시 포함되어야 합니다.
        """)

# ---------------------
# 로그인 페이지 클래스
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user['idToken']

                user_info = firestore.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.user_name = user_info.get("name", "")
                    st.session_state.user_gender = user_info.get("gender", "선택 안함")
                    st.session_state.user_phone = user_info.get("phone", "")
                    st.session_state.profile_image_url = user_info.get("profile_image_url", "")

                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            except Exception:
                st.error("로그인 실패")

# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("성명")
        gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone = st.text_input("휴대전화번호")

        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                firestore.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "name": name,
                    "gender": gender,
                    "phone": phone,
                    "role": "user",
                    "profile_image_url": ""
                })
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except Exception:
                st.error("회원가입 실패")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 메일 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("이메일 전송 실패")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 사용자 정보")

        email = st.session_state.get("user_email", "")
        new_email = st.text_input("이메일", value=email)
        name = st.text_input("성명", value=st.session_state.get("user_name", ""))
        gender = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(st.session_state.get("user_gender", "선택 안함"))
        )
        phone = st.text_input("휴대전화번호", value=st.session_state.get("user_phone", ""))

        uploaded_file = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_path = f"profiles/{email.replace('.', '_')}.jpg"
            storage.child(file_path).put(uploaded_file, st.session_state.id_token)
            image_url = storage.child(file_path).get_url(st.session_state.id_token)
            st.session_state.profile_image_url = image_url
            st.image(image_url, width=150)
        elif st.session_state.get("profile_image_url"):
            st.image(st.session_state.profile_image_url, width=150)

        if st.button("수정"):
            st.session_state.user_email = new_email
            st.session_state.user_name = name
            st.session_state.user_gender = gender
            st.session_state.user_phone = phone

            firestore.child("users").child(new_email.replace(".", "_")).update({
                "email": new_email,
                "name": name,
                "gender": gender,
                "phone": phone,
                "profile_image_url": st.session_state.get("profile_image_url", "")
            })

            st.success("사용자 정보가 저장되었습니다.")
            time.sleep(1)
            st.rerun()

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = ""
        st.session_state.user_name = ""
        st.session_state.user_gender = "선택 안함"
        st.session_state.user_phone = ""
        st.session_state.profile_image_url = ""
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()

# ---------------------
# EDA 페이지 클래스
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 연도별 지역 인구 추이 분석")

        uploaded = st.file_uploader("인구 데이터 업로드 (population_trends.csv)", type="csv")
        if not uploaded:
            st.info("population_trends.csv 파일을 업로드 해주세요.")
            return

        df = pd.read_csv(uploaded)
        df.rename(columns={'인구': '인구수'}, inplace=True)
        df['연도'] = df['연도'].astype(int)

        # 문제의 라인: 'if' 문이 정확히 8칸 들여쓰기 되어야 합니다.
        if '연도' not in df.columns or '지역' not in df.columns or '인구수' not in df.columns:
            st.error("'연도', '지역', '인구수' 컬럼이 존재해야 합니다.")
            return

        # 미리 정렬 및 변화량/증감률 계산
        df_sorted = df.sort_values(by=['지역', '연도'])
        df_sorted['변화량'] = df_sorted.groupby('지역')['인구수'].diff()
        df_sorted['증감률(%)'] = df_sorted.groupby('지역')['인구수'].pct_change() * 100

        tabs = st.tabs([
            "1. 결측치 및 중복 확인",
            "2. 연도별 전체 인구 추이",
            "3. 지역별 인구 변화량 순위",
            "4. 증감률 상위 지역 및 연도",
            "5. 시각화"
        ])

        with tabs[0]:
            st.header("1. 결측치 및 중복 확인")
            st.subheader("결측치 확인")
            st.dataframe(df.isnull().sum().rename("결측치 개수"))
            st.subheader("중복 확인")
            st.write("중복 행 수:", df.duplicated().sum())

        with tabs[1]:
            st.header("2. 연도별 전체 인구 추이")
            yearly = df.groupby('연도')['인구수'].sum().reset_index()
            st.line_chart(yearly.set_index('연도'))

        with tabs[2]:
            st.header("3. 지역별 인구 변화량 순위")
            latest_change = df_sorted.dropna().groupby('지역').agg({'변화량': 'last'}).sort_values(by='변화량', ascending=False)
            st.dataframe(latest_change)

        with tabs[3]:
            st.header("4. 증감률 상위 지역 및 연도")
            top_increase = df_sorted.sort_values(by='증감률(%)', ascending=False).dropna().head(10)
            st.subheader("증감률 상위 10개 지역/연도")
            st.dataframe(top_increase[['연도', '지역', '인구수', '증감률(%)']])

        with tabs[4]:
            st.header("5. 시각화")
            st.subheader("누적 영역 그래프 (연도별 지역 인구)")
            pivot_df = df.pivot(index='연도', columns='지역', values='인구수')
            pivot_df.fillna(0, inplace=True)
            fig, ax = plt.subplots(figsize=(12, 6))
            pivot_df.plot.area(ax=ax)
            ax.set_title("연도별 지역 인구 누적 추이")
            ax.set_ylabel("인구수")
            ax.set_xlabel("연도")
            st.pyplot(fig)

            st.subheader("📌 지역별 개별 추이 확인")
            region = st.selectbox("지역을 선택하세요", sorted(df['지역'].unique()))
            region_df = df[df['지역'] == region]
            fig2, ax2 = plt.subplots()
            ax2.plot(region_df['연도'], region_df['인구수'], marker='o')
            ax2.set_title(f"{region} 인구 추이")
            ax2.set_xlabel("연도")
            ax2.set_ylabel("인구수")
            st.pyplot(fig2)

# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login = st.Page(Login, title="Login", icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="Register", icon="📝", url_path="register")
Page_FindPW = st.Page(FindPassword, title="Find PW", icon="🔎", url_path="find-password")
Page_Home = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="Home", icon="🏠", url_path="home", default=True)
Page_User = st.Page(UserInfo, title="My Info", icon="👤", url_path="user-info")
Page_Logout = st.Page(Logout, title="Logout", icon="🔓", url_path="logout")
Page_EDA = st.Page(EDA, title="EDA", icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
if st.session_state.logged_in:
    pages = [Page_Home, Page_User, Page_Logout, Page_EDA]
else:
    pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

selected_page = st.navigation(pages)
selected_page.run()
