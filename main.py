import pathlib
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NHS Workforce Reality Check", layout="wide")

st.title("NHS Workforce & Vacancy Reality Check")
st.markdown("Comparing overseas staff contributions directly against local NHS vacancy rates.")
st.caption(
    "Sources: NHS England (NHS Workforce Statistics, Mar 2026; NHS Vacancy Statistics, to Mar 2025). "
    "Per-trust figures for all 205 English NHS trusts; UK/overseas split and vacancies are official "
    "national shares applied proportionally to each trust's real staff-in-post figure."
)


@st.cache_data
def load_data():
    data_path = pathlib.Path(__file__).resolve().parent / "nhs_workforce_data.csv"
    if not data_path.exists():
        st.error(
            f"Could not find nhs_workforce_data.csv at {data_path}. "
            "Run prepare_data.py first to generate the dataset."
        )
        st.stop()
    return pd.read_csv(data_path)


df = load_data()

selected_trust = st.selectbox("Select your Local NHS Trust:", df["Trust_Name"].unique())
trust_data = df[df["Trust_Name"] == selected_trust]

total_fte = trust_data["UK_Staff_FTE"].sum() + trust_data["Overseas_Staff_FTE"].sum()
overseas_pct = trust_data["Overseas_Staff_FTE"].sum() / total_fte * 100
total_vacancies = int(trust_data["Vacancies_FTE"].sum())

col1, col2, col3 = st.columns(3)
col1.metric(label="Overseas Staff", value=f"{overseas_pct:.1f}% of total FTE")
col2.metric(label="Current Unfilled Vacancies", value=f"{total_vacancies} FTE")
col3.metric(label="Est. Domestic Training Gap", value="7–10 Years")

fig = px.bar(
    trust_data,
    x="Staff_Group",
    y=["UK_Staff_FTE", "Overseas_Staff_FTE"],
    title=f"Staffing Breakdown by Staff Group for {selected_trust}",
    barmode="stack",
)
fig.update_layout(yaxis_title="FTE", xaxis_title="Staff Group")
st.plotly_chart(fig, use_container_width=True)

overseas_total = int(trust_data["Overseas_Staff_FTE"].sum())
combined_gap = overseas_total + total_vacancies
st.warning(
    f"Operational impact: {selected_trust} currently has {total_vacancies} unfilled FTE vacancies. "
    f"Removing {overseas_total} FTE of overseas staff would leave roughly {combined_gap} FTE in total "
    f"understaffing, more than doubling the structural shortfall overnight."
)