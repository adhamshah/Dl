import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data Explorer", page_icon="📊", layout="wide")

st.title("📊 Data Explorer")
st.caption("Upload a CSV or Excel file to explore, filter and chart your data.")


@st.cache_data
def load_data(file) -> pd.DataFrame:
    if file.name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    return pd.read_csv(file)


# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    uploaded = st.file_uploader("Upload data", type=["csv", "xlsx", "xls"])
    st.markdown("---")
    st.write("Built with [Streamlit](https://streamlit.io)")

if uploaded is None:
    st.info("👈 Upload a file in the sidebar to get started.")
    st.stop()

try:
    df = load_data(uploaded)
except Exception as e:
    st.error(f"Could not read the file: {e}")
    st.stop()

# ---------- Filters ----------
with st.sidebar:
    st.subheader("Filters")
    filtered = df.copy()
    cat_cols = [c for c in df.columns if df[c].dtype == "object" and df[c].nunique() <= 50]
    for col in cat_cols[:3]:
        options = sorted(df[col].dropna().unique().tolist())
        chosen = st.multiselect(col, options)
        if chosen:
            filtered = filtered[filtered[col].isin(chosen)]

num_cols = filtered.select_dtypes("number").columns.tolist()

# ---------- Metrics ----------
c1, c2, c3 = st.columns(3)
c1.metric("Rows", f"{len(filtered):,}")
c2.metric("Columns", filtered.shape[1])
c3.metric("Missing values", f"{int(filtered.isna().sum().sum()):,}")

# ---------- Tabs ----------
tab_data, tab_stats, tab_chart = st.tabs(["Data", "Summary", "Charts"])

with tab_data:
    st.dataframe(filtered, use_container_width=True)
    st.download_button(
        "Download filtered data (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_data.csv",
        mime="text/csv",
    )

with tab_stats:
    if num_cols:
        st.dataframe(filtered[num_cols].describe().T, use_container_width=True)
    else:
        st.write("No numeric columns found.")

with tab_chart:
    if not num_cols:
        st.write("No numeric columns to chart.")
    else:
        chart_type = st.radio("Chart type", ["Line", "Bar", "Scatter"], horizontal=True)
        if chart_type == "Scatter" and len(num_cols) >= 2:
            x = st.selectbox("X axis", num_cols, index=0)
            y = st.selectbox("Y axis", num_cols, index=1)
            st.scatter_chart(filtered, x=x, y=y)
        else:
            cols = st.multiselect("Columns to plot", num_cols, default=num_cols[:1])
            if cols:
                if chart_type == "Bar":
                    st.bar_chart(filtered[cols])
                else:
                    st.line_chart(filtered[cols])
