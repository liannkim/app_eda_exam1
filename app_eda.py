import streamlit as st
import pyrebase
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc # 한글 폰트 설정을 위함

# --- 한글 폰트 설정 (Mac, Windows, Linux 환경에 따라 선택) ---
# 시스템에 'Malgun Gothic'이 있다면 Windows에서 가장 잘 작동합니다.
# Mac 사용자는 'AppleGothic' 또는 'Apple SD Gothic Neo'를 시도해보세요.
# Streamlit Cloud나 리눅스 환경에서는 'NanumGothic' 계열 폰트가 설치되어 있어야 합니다.
# 설치되어 있지 않다면, Dockerfile 등을 통해 폰트를 먼저 설치해야 합니다.
try:
    # 맑은 고딕 (Windows)
    plt.rcParams['font.family'] = 'Malgun Gothic'
    font_manager.fontManager.findfont('Malgun Gothic')
except:
    try:
        # 애플 고딕 (Mac)
        plt.rcParams['font.family'] = 'AppleGothic'
        font_manager.fontManager.findfont('AppleGothic')
    except:
        # 나눔 고딕 (리눅스/기타)
        plt.rcParams['font.family'] = 'NanumGothic'
        font_manager.fontManager.findfont('NanumGothic')

plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
# -------------------------------------------------------------


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
        st.title("🏠 환영합니다!")

        if st.session_state.get("logged_in") and st.session_state.get("user_name"):
            st.success(f"**{st.session_state.get('user_name')}**님, 다시 오신 것을 환영합니다!")
        elif st.session_state.get("logged_in"):
            st.success(f"**{st.session_state.get('user_email')}**님, 환영합니다!")

        st.markdown("""
        ---
        ### 📈 연도별 지역 인구 추이 분석 대시보드 소개

        이 웹 애플리케이션은 **대한민국의 연도별 지역 인구 변화**를 심층적으로 탐색하고 시각화하는 대시보드입니다. `population_trends.csv` 파일을 기반으로 다양한 통계 분석과 차트를 제공하여 인구 변화의 트렌드와 패턴을 쉽게 이해할 수 있도록 돕습니다.

        #### 💡 주요 분석 기능:
        * **데이터 개요**: 업로드된 데이터의 기본 통계 및 구조 확인
        * **결측치 및 중복 데이터 검사**: 데이터 품질 확인
        * **연도별 인구 변화 추이**: 전체 인구의 흐름 시각화
        * **지역별 변화량 분석**: 인구 증감 순위 및 상세 추이 파악
        * **증감률 심층 분석**: 인구 변화가 가장 급격했던 지역/연도 식별
        * **다양한 시각화**: 누적 영역 그래프, 개별 지역 추이, 증감률 분포 등

        ---
        📁 **사용 가이드**:
        1.  `EDA` 페이지로 이동합니다.
        2.  `population_trends.csv` 파일을 업로드합니다.
            * **필수 컬럼**: `연도`, `지역`, `인구`
            * **선택 컬럼**: `출생아수(명)`, `사망자수(명)` (추가 분석에 활용될 수 있습니다)
        3.  각 탭을 클릭하며 인구 데이터에 대한 분석 결과를 확인합니다.
        """)

# ---------------------
# 로그인 페이지 클래스
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 로그인")
        st.markdown("계정이 없다면 'Register' 페이지에서 회원가입을 해주세요.")
        email = st.text_input("이메일 주소")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                with st.spinner("로그인 중..."):
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

                st.success(f"로그인 성공! {st.session_state.user_name if st.session_state.user_name else st.session_state.user_email}님 환영합니다.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"로그인 실패: {e}")
                st.warning("이메일과 비밀번호를 다시 확인해주세요.")


# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        st.info("이메일과 비밀번호, 그리고 사용자 정보를 입력해주세요.")
        email = st.text_input("이메일 주소")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("성명")
        gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone = st.text_input("휴대전화번호 (선택 사항)")

        if st.button("회원가입 완료"):
            if not email or not password or not name:
                st.error("이메일, 비밀번호, 성명은 필수 입력 항목입니다.")
                return
            try:
                with st.spinner("회원가입 처리 중..."):
                    auth.create_user_with_email_and_password(email, password)
                    firestore.child("users").child(email.replace(".", "_")).set({
                        "email": email,
                        "name": name,
                        "gender": gender,
                        "phone": phone,
                        "role": "user", # 기본 역할 설정
                        "profile_image_url": ""
                    })
                st.success("회원가입 성공! 이제 로그인 페이지로 이동하여 앱을 이용할 수 있습니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except Exception as e:
                st.error(f"회원가입 실패: {e}")
                st.warning("이미 등록된 이메일이거나 비밀번호 형식이 올바르지 않을 수 있습니다 (최소 6자).")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        st.info("가입 시 사용한 이메일 주소를 입력하시면 비밀번호 재설정 링크를 보내드립니다.")
        email = st.text_input("이메일 주소")
        if st.button("비밀번호 재설정 메일 전송"):
            if not email:
                st.error("이메일 주소를 입력해주세요.")
                return
            try:
                with st.spinner("이메일 전송 중..."):
                    auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일이 성공적으로 전송되었습니다. 이메일함을 확인해주세요.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"이메일 전송 실패: {e}")
                st.warning("등록되지 않은 이메일이거나 일시적인 오류일 수 있습니다.")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 내 정보 관리")
        st.info("회원님의 개인 정보를 수정하고 프로필 이미지를 업데이트할 수 있습니다.")

        email = st.session_state.get("user_email", "")
        current_name = st.session_state.get("user_name", "")
        current_gender = st.session_state.get("user_gender", "선택 안함")
        current_phone = st.session_state.get("user_phone", "")
        current_profile_image_url = st.session_state.get("profile_image_url", "")

        # 이메일은 변경 불가능하게 Read-only로 표시
        st.text_input("이메일", value=email, disabled=True)

        new_name = st.text_input("성명", value=current_name)
        new_gender = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(current_gender)
        )
        new_phone = st.text_input("휴대전화번호", value=current_phone)

        st.markdown("---")
        st.subheader("프로필 이미지")
        # 현재 프로필 이미지 표시
        if current_profile_image_url:
            st.image(current_profile_image_url, width=150, caption="현재 프로필 이미지")
        else:
            st.info("현재 설정된 프로필 이미지가 없습니다.")

        uploaded_file = st.file_uploader("새 프로필 이미지 업로드 (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            with st.spinner("이미지 업로드 중..."):
                file_path = f"profiles/{email.replace('.', '_')}.jpg"
                try:
                    # 기존 이미지를 덮어쓰기 위해 put 메서드 사용
                    storage.child(file_path).put(uploaded_file, st.session_state.id_token)
                    image_url = storage.child(file_path).get_url(st.session_state.id_token)
                    st.session_state.profile_image_url = image_url
                    st.success("프로필 이미지가 성공적으로 업로드되었습니다.")
                    st.image(image_url, width=150, caption="새로운 프로필 이미지 미리보기")
                except Exception as e:
                    st.error(f"이미지 업로드 실패: {e}")
                    st.warning("파일 크기가 너무 크거나 네트워크 문제일 수 있습니다.")


        if st.button("정보 수정 완료"):
            if not new_name:
                st.error("성명은 필수 입력 항목입니다.")
                return

            with st.spinner("정보 저장 중..."):
                st.session_state.user_name = new_name
                st.session_state.user_gender = new_gender
                st.session_state.user_phone = new_phone

                try:
                    firestore.child("users").child(email.replace(".", "_")).update({
                        "name": new_name,
                        "gender": new_gender,
                        "phone": new_phone,
                        "profile_image_url": st.session_state.get("profile_image_url", "")
                    })
                    st.success("사용자 정보가 성공적으로 업데이트되었습니다!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"정보 업데이트 실패: {e}")
                    st.warning("데이터베이스 연결 문제일 수 있습니다.")

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        st.success("안전하게 로그아웃 되었습니다. 다음에 또 방문해주세요!")
        # 모든 세션 상태 초기화
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = ""
        st.session_state.user_name = ""
        st.session_state.user_gender = "선택 안함"
        st.session_state.user_phone = ""
        st.session_state.profile_image_url = ""
        time.sleep(1)
        st.rerun()

# ---------------------
# EDA 페이지 클래스
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 연도별 지역 인구 추이 분석 대시보드")
        st.markdown("`population_trends.csv` 파일을 업로드하여 인구 데이터를 분석하고 다양한 시각화를 경험해보세요.")

        uploaded = st.file_uploader("인구 데이터 업로드 (CSV 파일)", type="csv", help="필수 컬럼: '연도', '지역', '인구'")
        if not uploaded:
            st.info("데이터 분석을 시작하려면 `population_trends.csv` 파일을 업로드 해주세요.")
            st.stop() # 파일이 없으면 여기서 실행 중단

        df = self._load_and_preprocess_data(uploaded)

        if df is None: # 데이터 로드 실패 시
            return

        st.success("데이터 로드 및 전처리 완료!")

        # 탭 구성
        tabs = st.tabs([
            "🔍 데이터 개요",
            "📊 전체 인구 추이",
            "📈 지역별 변화 분석",
            "🚀 증감률 심층 분석",
            "✨ 추가 시각화"
        ])

        with tabs[0]:
            self._display_data_overview(df)
        with tabs[1]:
            self._plot_yearly_population(df)
        with tabs[2]:
            self._analyze_regional_changes(df)
        with tabs[3]:
            self._analyze_growth_rate(df)
        with tabs[4]:
            self._additional_visualizations(df)

    def _load_and_preprocess_data(self, uploaded_file):
        try:
            df = pd.read_csv(uploaded_file)
            df.rename(columns={'인구': '인구수'}, inplace=True)

            # 필수 컬럼 검사
            required_columns = ['연도', '지역', '인구수']
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                st.error(f"필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")
                st.warning("업로드된 파일에 '연도', '지역', '인구' 컬럼이 반드시 포함되어야 합니다.")
                return None

            df['연도'] = df['연도'].astype(int)
            # 데이터 정렬 및 변화량/증감률 미리 계산
            df_sorted = df.sort_values(by=['지역', '연도']).copy() # SettingWithCopyWarning 방지
            df_sorted['변화량'] = df_sorted.groupby('지역')['인구수'].diff()
            # 첫 해의 증감률은 NaN이므로 0으로 처리하거나 제외 (여기서는 제외)
            df_sorted['증감률(%)'] = df_sorted.groupby('지역')['인구수'].pct_change() * 100
            # 초기값이 NaN이므로, 보기 좋게 0으로 채우거나 필터링 가능
            # df_sorted['증감률(%)'] = df_sorted['증감률(%)'].fillna(0)
            return df_sorted
        except Exception as e:
            st.error(f"데이터 로드 또는 전처리 중 오류가 발생했습니다: {e}")
            st.warning("CSV 파일 형식이 올바른지 확인해주세요.")
            return None

    def _display_data_overview(self, df):
        st.header("🔍 데이터 개요")
        st.subheader("원본 데이터 미리보기")
        st.dataframe(df.head())

        st.subheader("데이터 정보")
        buffer = io.StringIO()
        df.info(buf=buffer)
        st.text(buffer.getvalue())

        st.subheader("수치형 데이터 통계 요약")
        st.dataframe(df.describe())

        st.subheader("결측치 및 중복 데이터 확인")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**결측치 개수**")
            st.dataframe(df.isnull().sum().rename("결측치 개수"))
        with col2:
            st.info("**중복 행 개수**")
            st.write(f"총 중복 행 수: **{df.duplicated().sum()}** 개")
            if df.duplicated().sum() > 0:
                st.warning("중복된 행이 발견되었습니다. 데이터 클리닝이 필요할 수 있습니다.")

    def _plot_yearly_population(self, df):
        st.header("📊 연도별 전체 인구 추이")
        st.markdown("각 연도별 대한민국 총 인구수의 변화를 보여줍니다.")
        yearly_total = df.groupby('연도')['인구수'].sum().reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=yearly_total, x='연도', y='인구수', marker='o', ax=ax)
        ax.set_title("연도별 대한민국 총 인구수 추이")
        ax.set_xlabel("연도")
        ax.set_ylabel("총 인구수")
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)

        st.subheader("데이터 테이블")
        st.dataframe(yearly_total)


    def _analyze_regional_changes(self, df):
        st.header("📈 지역별 인구 변화 분석")
        st.markdown("각 지역의 인구 변화량 및 최종 인구수 순위를 확인하고, 특정 지역의 상세 추이를 볼 수 있습니다.")

        # 최신 연도 기준으로 인구 변화량 계산 (마지막 연도 - 첫 연도)
        min_year = df['연도'].min()
        max_year = df['연도'].max()

        st.subheader(f"인구 변화량 순위 ({min_year}년 ~ {max_year}년)")
        first_year_pop = df[df['연도'] == min_year].set_index('지역')['인구수']
        last_year_pop = df[df['연도'] == max_year].set_index('지역')['인구수']

        # 두 기간 모두 데이터가 있는 지역만 선택
        common_regions = list(set(first_year_pop.index) & set(last_year_pop.index))

        if not common_regions:
            st.warning("첫 해와 마지막 해 모두 데이터가 있는 지역이 없습니다. 인구 변화량 계산이 어렵습니다.")
        else:
            first_year_pop = first_year_pop.loc[common_regions]
            last_year_pop = last_year_pop.loc[common_regions]

            total_change = last_year_pop - first_year_pop
            change_df = pd.DataFrame({
                '시작 인구수': first_year_pop,
                '최종 인구수': last_year_pop,
                '총 변화량': total_change
            }).sort_values(by='총 변화량', ascending=False)
            st.dataframe(change_df)

            st.subheader("인구 변화량 (상위/하위 N개 지역)")
            num_regions = st.slider("표시할 지역 수 (N)", min_value=5, max_value=20, value=10)

            # 상위 N개 지역
            top_n_regions = change_df.head(num_regions).index.tolist()
            bottom_n_regions = change_df.tail(num_regions).index.tolist()

            col_top, col_bottom = st.columns(2)
            with col_top:
                st.info(f"**총 변화량 상위 {num_regions}개 지역**")
                st.dataframe(change_df.head(num_regions))
            with col_bottom:
                st.info(f"**총 변화량 하위 {num_regions}개 지역**")
                st.dataframe(change_df.tail(num_regions))

            # 상위 N개 지역 인구 추이 그래프
            st.subheader(f"상위 {num_regions}개 지역 연도별 인구 추이")
            fig_top, ax_top = plt.subplots(figsize=(12, 6))
            sns.lineplot(data=df[df['지역'].isin(top_n_regions)],
                         x='연도', y='인구수', hue='지역', marker='o', ax=ax_top)
            ax_top.set_title(f"인구 변화량 상위 {num_regions}개 지역 추이")
            ax_top.set_xlabel("연도")
            ax_top.set_ylabel("인구수")
            ax_top.grid(True, linestyle='--', alpha=0.6)
            ax_top.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            st.pyplot(fig_top)

    def _analyze_growth_rate(self, df):
        st.header("🚀 증감률 심층 분석")
        st.markdown("연도별/지역별 인구 증감률을 분석하여 변화가 가장 활발했던 시기와 지역을 식별합니다.")

        # 증감률이 NaN이 아닌 값만 사용
        df_growth = df.dropna(subset=['증감률(%)'])

        if df_growth.empty:
            st.warning("증감률을 계산할 수 있는 데이터가 부족합니다 (최소 2개 연도 데이터 필요).")
            return

        st.subheader("증감률 분포 (히스토그램)")
        fig_hist, ax_hist = plt.subplots(figsize=(10, 5))
        sns.histplot(df_growth['증감률(%)'], kde=True, ax=ax_hist)
        ax_hist.set_title("인구 증감률 분포")
        ax_hist.set_xlabel("증감률 (%)")
        ax_hist.set_ylabel("빈도")
        st.pyplot(fig_hist)

        st.subheader("증감률 상위/하위 N개 지역 및 연도")
        col_top_rate, col_bottom_rate = st.columns(2)

        # 증감률 상위 10개
        top_growth = df_growth.sort_values(by='증감률(%)', ascending=False).head(10)
        with col_top_rate:
            st.info("📈 **가장 높은 증감률 (상위 10)**")
            st.dataframe(top_growth[['연도', '지역', '인구수', '증감률(%)']])

        # 증감률 하위 10개 (감소율이 높은)
        bottom_growth = df_growth.sort_values(by='증감률(%)', ascending=True).head(10)
        with col_bottom_rate:
            st.error("📉 **가장 낮은 증감률 (하위 10)**")
            st.dataframe(bottom_growth[['연도', '지역', '인구수', '증감률(%)']])

    def _additional_visualizations(self, df):
        st.header("✨ 추가 시각화")
        st.markdown("다양한 형태로 인구 추이를 시각화하여 더 깊은 인사이트를 얻어보세요.")

        st.subheader("1. 누적 영역 그래프: 연도별 지역 인구 구성")
        st.info("전체 인구에서 각 지역이 차지하는 비중 변화를 한눈에 볼 수 있습니다.")
        pivot_df = df.pivot(index='연도', columns='지역', values='인구수')
        pivot_df.fillna(0, inplace=True) # 누락된 데이터는 0으로 채움 (시각화를 위함)

        fig_area, ax_area = plt.subplots(figsize=(15, 8))
        pivot_df.plot.area(ax=ax_area, stacked=True, alpha=0.7)
        ax_area.set_title("연도별 지역 인구 누적 추이", fontsize=16)
        ax_area.set_ylabel("총 인구수", fontsize=12)
        ax_area.set_xlabel("연도", fontsize=12)
        ax_area.legend(title="지역", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        st.pyplot(fig_area)


        st.subheader("2. 개별 지역 인구 추이")
        st.info("원하는 지역을 선택하여 해당 지역의 인구 변화 추이를 상세히 확인합니다.")
        unique_regions = sorted(df['지역'].unique())
        selected_region = st.selectbox("분석할 지역을 선택하세요:", unique_regions)

        region_df = df[df['지역'] == selected_region].sort_values(by='연도')
        if not region_df.empty:
            fig_region, ax_region = plt.subplots(figsize=(10, 5))
            sns.lineplot(data=region_df, x='연도', y='인구수', marker='o', ax=ax_region)
            ax_region.set_title(f"'{selected_region}' 인구 추이", fontsize=16)
            ax_region.set_xlabel("연도", fontsize=12)
            ax_region.set_ylabel("인구수", fontsize=12)
            ax_region.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig_region)

            st.markdown(f"#### '{selected_region}'의 인구 데이터")
            st.dataframe(region_df[['연도', '인구수', '변화량', '증감률(%)']].round(2))
        else:
            st.warning(f"선택한 '{selected_region}' 지역에 대한 데이터가 없습니다.")


        st.subheader("3. 선택 연도별 지역 인구 막대 그래프")
        st.info("특정 연도의 지역별 인구수를 비교합니다.")
        unique_years = sorted(df['연도'].unique(), reverse=True)
        selected_year = st.selectbox("확인할 연도를 선택하세요:", unique_years)

        year_df = df[df['연도'] == selected_year].sort_values(by='인구수', ascending=False)
        if not year_df.empty:
            fig_bar, ax_bar = plt.subplots(figsize=(12, 7))
            sns.barplot(data=year_df, x='인구수', y='지역', ax=ax_bar, palette='viridis')
            ax_bar.set_title(f"{selected_year}년 지역별 인구수", fontsize=16)
            ax_bar.set_xlabel("인구수", fontsize=12)
            ax_bar.set_ylabel("지역", fontsize=12)
            st.pyplot(fig_bar)

            st.markdown(f"#### '{selected_year}'년 지역별 인구 데이터")
            st.dataframe(year_df[['지역', '인구수']].reset_index(drop=True))
        else:
            st.warning(f"선택한 '{selected_year}' 연도에 대한 데이터가 없습니다.")


# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login = st.Page(Login, title="로그인", icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="회원가입", icon="📝", url_path="register")
Page_FindPW = st.Page(FindPassword, title="비밀번호 찾기", icon="🔎", url_path="find-password")
Page_Home = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="홈", icon="🏠", url_path="home", default=True)
Page_User = st.Page(UserInfo, title="내 정보", icon="👤", url_path="user-info")
Page_Logout = st.Page(Logout, title="로그아웃", icon="🔓", url_path="logout")
Page_EDA = st.Page(EDA, title="데이터 분석", icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
# 사이드바에 프로필 정보 표시
with st.sidebar:
    st.image("https://www.streamlit.io/images/brand/streamlit-logo-light.svg", width=150) # 로고 추가
    st.markdown("---")
    if st.session_state.logged_in:
        st.success(f"환영합니다, **{st.session_state.user_name if st.session_state.user_name else st.session_state.user_email.split('@')[0]}**님!")
        if st.session_state.profile_image_url:
            st.image(st.session_state.profile_image_url, width=100, caption="내 프로필")
        st.markdown("---")
        # 로그인 상태일 때 보여줄 페이지
        pages = [Page_Home, Page_EDA, Page_User, Page_Logout]
    else:
        st.info("로그인 또는 회원가입 후 모든 기능을 이용해 보세요.")
        st.markdown("---")
        # 로그아웃 상태일 때 보여줄 페이지
        pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

    # 사이드바 하단에 링크 추가
    st.markdown("---")
    st.markdown("##### 🔗 관련 링크")
    st.markdown("- [GitHub Repository](https://github.com/liannkim/app_eda_exam)")
    st.markdown("- [Streamlit Docs](https://docs.streamlit.io/)")

# 선택된 페이지 실행
selected_page = st.navigation(pages)
selected_page.run()
