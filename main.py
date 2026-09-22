import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # 장르 열: '세로막대(|)' 기호로 여러 장르가 적혀 있으면 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # 개봉일(openDt)은 8자리 숫자(YYYYMMDD) -> 날짜형으로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
        )

    return df


def insight_box(key: str):
    """그래프 아래에 학생이 직접 해석을 적어보는 입력창"""
    st.text_area(
        "✏️ 이 그래프로 알 수 있는 것",
        key=key,
        placeholder="그래프를 보고 알 수 있는 점을 한 문장으로 적어보세요.",
        height=80,
    )


# ------------------------------------------------------------
# 데이터 로드
# ------------------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 가운데, 이 기간 안에 개봉한 216편의 데이터를 살펴봅니다."
)

with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data(DATA_URL)

with st.expander("📋 원본 데이터 살펴보기"):
    st.dataframe(df, use_container_width=True)
    st.caption(f"전체 {len(df)}편의 영화 데이터")

st.divider()

# ------------------------------------------------------------
# 1. 장르별 영화 편수 - 도넛 그래프
# ------------------------------------------------------------
st.header("1️⃣ 장르별 영화 편수")

genre_counts = (
    df["genre"].value_counts().reset_index()
)
genre_counts.columns = ["genre", "count"]

fig_donut = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
    title="장르별 영화 편수",
)
fig_donut.update_traces(
    textinfo="label+percent",
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_donut.update_layout(legend_title_text="장르")

st.plotly_chart(fig_donut, use_container_width=True)
insight_box("insight_1_genre_donut")

st.divider()

# ------------------------------------------------------------
# 2. 장르 안의 영화들 - 트리맵 (칸 크기 = 총 관객수)
# ------------------------------------------------------------
st.header("2️⃣ 장르 안의 영화들 (칸 크기 = 총 관객수)")

fig_treemap = px.treemap(
    df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르 안의 영화들 - 칸 크기는 총 관객수",
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객수: %{value:,}명<extra></extra>",
)

st.plotly_chart(fig_treemap, use_container_width=True)
insight_box("insight_2_genre_treemap")

st.divider()

# ------------------------------------------------------------
# 3. 총 관객수 분포 - 히스토그램
# ------------------------------------------------------------
st.header("3️⃣ 총 관객수 분포")

fig_hist_audi = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객수 분포",
    labels={"total_audi": "총 관객수(명)"},
)
fig_hist_audi.update_traces(
    hovertemplate="총 관객수 구간: %{x}<br>영화 편수: %{y}편<extra></extra>"
)
fig_hist_audi.update_layout(yaxis_title="영화 편수")

st.plotly_chart(fig_hist_audi, use_container_width=True)

# 대부분의 영화가 몰려 있는 구간과, 가장 관객이 많은 영화를 자동으로 계산
counts, bin_edges = np.histogram(df["total_audi"].dropna(), bins=30)
mode_idx = counts.argmax()
mode_low, mode_high = bin_edges[mode_idx], bin_edges[mode_idx + 1]

top_row = df.loc[df["total_audi"].idxmax()]
top_movie = top_row["movieNm"]
top_audi = top_row["total_audi"]

st.info(
    f"📌 전체 216편 중 **{int(counts[mode_idx])}편**이 총 관객수 "
    f"**{mode_low:,.0f}명 ~ {mode_high:,.0f}명** 구간에 몰려 있습니다.  \n"
    f"📌 가장 많은 관객을 동원한 영화는 **'{top_movie}'**이며, "
    f"총 **{top_audi:,.0f}명**을 기록했습니다."
)

insight_box("insight_2_audi_hist")

st.divider()

# ------------------------------------------------------------
# 4. 제작 국가별 영화 편수 - 막대 그래프
# ------------------------------------------------------------
st.header("4️⃣ 제작 국가별 영화 편수")

nation_counts = df["nation"].value_counts().reset_index()
nation_counts.columns = ["nation", "count"]

fig_bar_nation = px.bar(
    nation_counts,
    x="nation",
    y="count",
    title="제작 국가별 영화 편수",
    labels={"nation": "제작 국가", "count": "영화 편수"},
)
fig_bar_nation.update_traces(
    hovertemplate="국가: %{x}<br>편수: %{y}편<extra></extra>"
)

st.plotly_chart(fig_bar_nation, use_container_width=True)
insight_box("insight_4_nation_bar")

st.divider()

# ------------------------------------------------------------
# 5. 개봉일 스크린수 vs 총 관객수 - 산점도
# ------------------------------------------------------------
st.header("5️⃣ 개봉일 스크린수와 총 관객수의 관계")

fig_scatter_scrn = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객수의 관계",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객수(명)"},
)
fig_scatter_scrn.update_traces(
    hovertemplate="영화명: %{hovertext}<br>스크린수: %{x}<br>총 관객수: %{y}<extra></extra>"
)

st.plotly_chart(fig_scatter_scrn, use_container_width=True)
insight_box("insight_5_scrn_scatter")

st.divider()

# ------------------------------------------------------------
# 6. 개봉 첫 주 관객수 vs 총 관객수 - 산점도
# ------------------------------------------------------------
st.header("6️⃣ 개봉 첫 주 관객수와 총 관객수의 관계")

fig_scatter_week = px.scatter(
    df,
    x="first_week_audi",
    y="total_audi",
    hover_name="movieNm",
    title="개봉 첫 주 관객수와 총 관객수의 관계",
    labels={"first_week_audi": "개봉 첫 주 관객수", "total_audi": "총 관객수(명)"},
)
fig_scatter_week.update_traces(
    hovertemplate="영화명: %{hovertext}<br>첫 주 관객수: %{x}<br>총 관객수: %{y}<extra></extra>"
)

st.plotly_chart(fig_scatter_week, use_container_width=True)
insight_box("insight_6_week_scatter")

st.divider()

# ------------------------------------------------------------
# 7. 박스오피스 10위권 유지 일수 분포 - 히스토그램
# ------------------------------------------------------------
st.header("7️⃣ 박스오피스 10위권 유지 일수 분포")

fig_hist_days = px.histogram(
    df,
    x="days_in_top10",
    nbins=20,
    title="박스오피스 10위권 유지 일수 분포",
    labels={"days_in_top10": "10위권 유지 일수"},
)
fig_hist_days.update_traces(
    hovertemplate="유지 일수 구간: %{x}<br>영화 편수: %{y}편<extra></extra>"
)
fig_hist_days.update_layout(yaxis_title="영화 편수")

st.plotly_chart(fig_hist_days, use_container_width=True)
insight_box("insight_7_days_hist")
