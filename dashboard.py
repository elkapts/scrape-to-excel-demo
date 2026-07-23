"""
Streamlit dashboard for the European Job Vacancy Monitor.
 
Reads output/vacancies_result.csv (produced by main.py) and displays it as an
interactive, filterable dashboard: search by keyword, filter by location and
contract type, filter by salary range, and view summary charts.
 
Run with:
    streamlit run dashboard.py
 
This is a read-only viewer - it does not call the Adzuna API or modify any
files. Run main.py separately (or via run.sh/run.bat) to (re)generate the
data this dashboard displays.
"""

import os

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = os.environ.get(
    "VACANCY_DATA_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "vacancies_result.csv"),
)
 
st.set_page_config(
    page_title="European Job Vacancy Monitor",
    page_icon="\U0001f4ca",
    layout="wide",
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Loads the CSV produced by main.py and does light type cleanup for display."""
    df = pd.read_csv(path)
    for col in ("Salary From", "Salary Up"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Publish Date" in df.columns:
        df["Publish Date"] = pd.to_datetime(df["Publish Date"], errors="coerce", utc=True)
    return df

def main() -> None:
    st.title("\U0001f4ca European Job Vacancy Monitor")
    st.caption("Data collected via the official Adzuna API - see main.py")
 
    if not os.path.exists(DATA_PATH):
        st.warning(
            "No data found yet. Run the collector first:\n\n"
            "`./run.sh` (macOS/Linux) or `run.bat` (Windows)\n\n"
            "This will create `output/vacancies_result.csv`, which this "
            "dashboard reads automatically."
        )
        st.stop()
 
    df = load_data(DATA_PATH)
 
    # ---------- Sidebar filters ----------
    st.sidebar.header("Filters")
 
    keyword = st.sidebar.text_input("Search title or company", "")
 
    locations = sorted(df["Location"].dropna().unique().tolist())
    selected_locations = st.sidebar.multiselect("Location", locations)
 
    contract_types = sorted(df["Employment Type"].dropna().unique().tolist())
    selected_contracts = st.sidebar.multiselect("Employment Type", contract_types)
 
    min_salary_raw = df["Salary From"].min(skipna=True)
    min_salary = int(min_salary_raw) if pd.notna(min_salary_raw) else 0

    max_salary_raw = df["Salary Up"].max(skipna=True)
    max_salary = int(max_salary_raw) if pd.notna(max_salary_raw) else 0
    
    if max_salary > min_salary:
        salary_range = st.sidebar.slider(
            "Salary range",
            min_value=min_salary,
            max_value=max_salary,
            value=(min_salary, max_salary),
            step=1000,
        )
    else:
        salary_range = (min_salary, max_salary)
 
    # ---------- Apply filters ----------
    filtered = df.copy()
 
    if keyword:
        mask = filtered["Title"].str.contains(keyword, case=False, na=False) | filtered[
            "Company"
        ].str.contains(keyword, case=False, na=False)
        filtered = filtered[mask]
 
    if selected_locations:
        filtered = filtered[filtered["Location"].isin(selected_locations)]
 
    if selected_contracts:
        filtered = filtered[filtered["Employment Type"].isin(selected_contracts)]
 
    filtered = filtered[
        (filtered["Salary From"].fillna(0) >= salary_range[0])
        & (filtered["Salary Up"].fillna(salary_range[1]) <= salary_range[1])
    ]
 
    # ---------- Summary metrics ----------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Vacancies shown", len(filtered))
    col2.metric("Unique companies", filtered["Company"].nunique())
    col3.metric("Unique locations", filtered["Location"].nunique())
    avg_salary = filtered["Salary From"].mean()
    col4.metric("Avg. salary from", f"{avg_salary:,.0f}" if pd.notna(avg_salary) else "N/A")
 
    st.divider()
 
    # ---------- Charts ----------
    chart_col1, chart_col2 = st.columns(2)
 
    with chart_col1:
        st.subheader("Vacancies by location")
        by_location = filtered["Location"].value_counts().head(10).reset_index()
        by_location.columns = ["Location", "Count"]
        fig_location = px.bar(by_location, x="Count", y="Location", orientation="h")
        fig_location.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
        st.plotly_chart(fig_location, width="stretch")
 
    with chart_col2:
        st.subheader("Salary distribution (from)")
        fig_salary = px.histogram(filtered, x="Salary From", nbins=20)
        fig_salary.update_layout(height=400)
        st.plotly_chart(fig_salary, width="stretch")
 
    st.divider()
 
    # ---------- Data table ----------
    st.subheader(f"Listings ({len(filtered)})")
    display_cols = [
        c
        for c in [
            "Title",
            "Company",
            "Location",
            "Salary From",
            "Salary Up",
            "Employment Type",
            "Publish Date",
            "Link",
        ]
        if c in filtered.columns
    ]
    st.dataframe(
        filtered[display_cols],
        width="stretch",
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Open listing"),
        },
        hide_index=True,
    )
 
    st.download_button(
        "Download filtered results as CSV",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="vacancies_filtered.csv",
        mime="text/csv",
    )
 
 
if __name__ == "__main__":
    main()
 