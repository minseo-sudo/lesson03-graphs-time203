import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)


# ---------------------------------------------------------------------------
# 데이터 불러오기
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="데이터를 불러오는 중...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")
    # 날짜: 20240101 같은 여덟 자리 숫자 -> 진짜 날짜(datetime)
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df.sort_values("날짜").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 공통 도우미
# ---------------------------------------------------------------------------
def show_insight(text: str) -> None:
    """그래프 아래에 '이 그래프로 알 수 있는 것' 한 문장을 보여 주는 자리."""
    st.markdown(f"**💡 이 그래프로 알 수 있는 것**  \n{text}")


# ---------------------------------------------------------------------------
# 구역 1: 시간에 따른 변화
# ---------------------------------------------------------------------------
def section_daily_audience(df: pd.DataFrame) -> None:
    st.header("1-1. 영화별 일관객 변화")

    # 누적관객이 많은 영화가 드롭다운 위쪽에 오도록 정렬
    movies = (
        df.groupby("영화명")["누적관객"].max().sort_values(ascending=False).index.tolist()
    )
    movie = st.selectbox("영화를 골라 보세요", movies, key="s1_movie")

    movie_df = df[df["영화명"] == movie].sort_values("날짜")

    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"{movie} - 날짜별 일관객",
    )
    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객(명)",
        yaxis_tickformat=",",
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True)

    # 👇 여기 문장을 직접 채워 넣으세요
    show_insight("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ---------------------------------------------------------------------------
# 구역 2: 영화별 합계로 보는 순위
# ---------------------------------------------------------------------------
def section_top10_total_audience(df: pd.DataFrame) -> None:
    st.header("2-1. 총 관객 TOP 10")

    summary = (
        df.groupby("영화명")
        .agg(총관객=("일관객", "sum"), 순위권_일수=("날짜", "count"))
        .reset_index()
        .sort_values("총관객", ascending=False)
        .head(10)
    )

    fig = px.bar(
        summary,
        x="총관객",
        y="영화명",
        orientation="h",
        custom_data=["순위권_일수"],
        title="총 관객 TOP 10",
    )
    fig.update_traces(
        hovertemplate=(
            "영화명: %{y}<br>"
            "총 관객: %{x:,}명<br>"
            "10위권 유지 일수: %{customdata[0]}일<extra></extra>"
        )
    )
    fig.update_layout(
        xaxis_title="총 관객(명)",
        yaxis_title="영화명",
        xaxis_tickformat=",",
        # 관객이 많은 영화가 맨 위로 오도록 순서 고정
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # 👇 여기 문장을 직접 채워 넣으세요
    show_insight("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ---------------------------------------------------------------------------
# 구역 3: 월 × 요일 패턴
# ---------------------------------------------------------------------------
def section_month_weekday_heatmap(df: pd.DataFrame) -> None:
    st.header("3-1. 월 × 요일별 일관객 합계")

    weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}

    tmp = df.copy()
    tmp["월"] = tmp["날짜"].dt.month
    tmp["요일"] = tmp["날짜"].dt.weekday.map(weekday_map)

    pivot = (
        tmp.groupby(["월", "요일"])["일관객"]
        .sum()
        .unstack("요일")
        .reindex(columns=weekday_order)
        .reindex(index=range(1, 13))
    )

    fig = px.imshow(
        pivot,
        x=pivot.columns,
        y=[f"{m}월" for m in pivot.index],
        color_continuous_scale="Reds",
        aspect="auto",
        title="월 × 요일별 일관객 합계",
    )
    fig.update_traces(
        hovertemplate="%{y} %{x}요일<br>일관객 합계: %{z:,}명<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="요일",
        yaxis_title="월",
        coloraxis_colorbar_title="일관객 합계",
    )
    st.plotly_chart(fig, use_container_width=True)

    # 👇 여기 문장을 직접 채워 넣으세요
    show_insight("여기에 이 그래프로 알 수 있는 내용을 한 문장으로 적어 주세요.")


# ---------------------------------------------------------------------------
# 구역 4 이후: 그래프를 추가할 자리
# 새 그래프는 위와 같은 형태의 함수(section_...)를 만들고
# 아래 main()에 st.divider()와 함께 호출만 추가하면 됩니다.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 앱 시작
# ---------------------------------------------------------------------------
def main() -> None:
    st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
    st.caption("KOBIS 일별 박스오피스 10위권 기록 (1년치)")

    df = load_data()

    section_daily_audience(df)
    st.divider()

    section_top10_total_audience(df)
    st.divider()

    section_month_weekday_heatmap(df)
    st.divider()

    # 다음 그래프 구역은 여기에 추가
    # section_next_graph(df)
    # st.divider()


if __name__ == "__main__":
    main()
