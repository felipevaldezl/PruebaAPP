import os
import pandas as pd
import streamlit as st


DATA_FILE = os.path.join(os.path.dirname(__file__), "monthly_sales.csv")


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m", errors="coerce")
        df["year"] = df["date"].dt.year
    return df


def main() -> None:
    st.set_page_config(page_title="Customer Lookup App", page_icon="🔎", layout="wide")
    st.title("Customer Records Lookup")
    st.caption("Search, filter, and inspect records through a clean Streamlit interface.")

    df = load_data(DATA_FILE)

    if df.empty:
        st.warning("No data available to display.")
        return

    st.sidebar.header("Filters")
    search_query = st.sidebar.text_input("Search", placeholder="Type to filter records")

    year_values = ["All"] + sorted([int(y) for y in df["year"].dropna().astype(int).unique()])
    selected_year = st.sidebar.selectbox("Year", year_values)

    if search_query:
        mask = df.astype(str).apply(lambda col: col.str.contains(search_query, case=False, na=False)).any(axis=1)
        filtered_df = df.loc[mask]
    else:
        filtered_df = df

    if selected_year != "All":
        filtered_df = filtered_df[filtered_df["year"] == selected_year]

    st.sidebar.text(f"Showing {len(filtered_df)} of {len(df)} records")

    st.dataframe(
        filtered_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()


