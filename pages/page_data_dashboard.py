import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def generate_sample_data() -> pd.DataFrame:
    """
    Generates a realistic geological rock core dataset for testing.
    Porosity and permeability correlate logarithmically.
    """
    np.random.seed(42)
    n_samples = 150
    
    # 1. Sample IDs
    sample_ids = [f"CORE-{i:03d}" for i in range(101, 101 + n_samples)]
    
    # 2. Depth in meters
    depths = np.linspace(1820.5, 1875.0, n_samples) + np.random.normal(0, 0.2, n_samples)
    depths = np.round(depths, 2)
    
    # 3. Porosity (%)
    # Base porosity around 15% with some fluctuations
    porosity = np.random.uniform(4.0, 28.0, n_samples)
    porosity = np.round(porosity, 2)
    
    # 4. Permeability (mD)
    # Permeability correlates log-linearly with porosity: log10(k) = a*phi + b + noise
    log_k = 0.16 * porosity - 1.2 + np.random.normal(0, 0.4, n_samples)
    permeability = 10 ** log_k
    # Cap permeability values to realistic range [0.01, 1500] mD
    permeability = np.clip(permeability, 0.01, 1500.0)
    permeability = np.round(permeability, 3)
    
    # 5. Lithology based on porosity and permeability thresholds
    lithology = []
    for phi, k in zip(porosity, permeability):
        if phi < 8.5:
            lithology.append("Shale")
        elif phi > 18.0 and k > 50.0:
            lithology.append("Sandstone")
        else:
            lithology.append("Limestone")
            
    df = pd.DataFrame({
        "Sample ID": sample_ids,
        "Depth (m)": depths,
        "Porosity (%)": porosity,
        "Permeability (mD)": permeability,
        "Lithology": lithology
    })
    return df

def run():
    st.title("📊 Rock & Fluid Data Dashboard")
    st.markdown("Upload rock core analysis data, filter properties, inspect distributions, and export results.")

    # 1. File Upload or Sample Data Loader
    st.subheader("Data Source Selection")
    
    col_upload, col_sample = st.columns([2, 1])
    
    uploaded_file = col_upload.file_uploader(
        "Upload Rock Core Data (CSV)",
        type=["csv"],
        help="Upload a CSV file containing rock core measurements. Must include numeric columns."
    )
    
    # Use session state to persist sample data loading
    if "use_sample_data" not in st.session_state:
        st.session_state.use_sample_data = False
        
    def set_sample_data():
        st.session_state.use_sample_data = True
        
    def reset_data():
        st.session_state.use_sample_data = False

    # Download button for sample template
    sample_df = generate_sample_data()
    sample_csv = sample_df.to_csv(index=False).encode('utf-8')
    
    col_sample.markdown("<div style='margin-top: 1.6rem;'></div>", unsafe_allow_html=True)
    if col_sample.button("⚡ Load Demo Dataset", help="Load pre-generated realistic reservoir core data.", on_click=set_sample_data):
        pass

    # Read the data based on source
    df = None
    data_source = ""
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            data_source = "Uploaded File"
            # If user uploaded a file, cancel the sample data override
            st.session_state.use_sample_data = False
        except Exception as e:
            st.error(f"Error reading CSV: {str(e)}")
    elif st.session_state.use_sample_data:
        df = sample_df.copy()
        data_source = "Demo Dataset"
        
    # Download Demo Template Link
    st.download_button(
        label="📥 Download Sample CSV Template",
        data=sample_csv,
        file_name="sample_reservoir_cores.csv",
        mime="text/csv",
        help="Download the sample rock core dataset as a CSV file to inspect its structure."
    )

    if df is None:
        st.info("💡 To start, please upload a rock core CSV file or click the **Load Demo Dataset** button above.")
        return

    # Check for required columns
    # We will dynamically adapt to the uploaded columns if possible, but guide users to standard column names.
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    if len(numeric_cols) < 2:
        st.error("Uploaded CSV must contain at least 2 numerical columns (e.g. Porosity, Permeability, Depth) for analysis.")
        return

    st.success(f"Successfully loaded {len(df)} samples from **{data_source}**!")

    # 2. Sidebar Filters
    st.sidebar.header("Dashboard Filters")
    
    # Filter selection
    # Choose which numeric columns to filter on (default to Porosity/Permeability if present)
    p_col = next((c for c in numeric_cols if "porosity" in c.lower()), numeric_cols[0])
    k_col = next((c for c in numeric_cols if "permeability" in c.lower() or "perm" in c.lower()), numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])
    
    # Add filters for numeric columns
    filtered_df = df.copy()
    
    st.sidebar.markdown(f"### Numeric Range Filters")
    
    for col in [p_col, k_col]:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        
        # Avoid slider errors if min == max
        if min_val == max_val:
            st.sidebar.disabled_slider = st.sidebar.slider(f"{col}", min_value=min_val, max_value=max_val+1.0, value=(min_val, max_val+1.0))
        else:
            val_range = st.sidebar.slider(
                f"{col}",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                step=round((max_val - min_val) / 100.0, 3) or 0.1,
                help=f"Filter samples by {col} range."
            )
            filtered_df = filtered_df[(filtered_df[col] >= val_range[0]) & (filtered_df[col] <= val_range[1])]

    # Categorical filters (e.g. Lithology)
    cat_filter_col = next((c for c in categorical_cols if "lithology" in c.lower() or "type" in c.lower() or "rock" in c.lower()), None)
    if cat_filter_col is None and len(categorical_cols) > 0:
         cat_filter_col = categorical_cols[0]
         
    if cat_filter_col is not None:
        st.sidebar.markdown(f"### Categorical Filters")
        unique_vals = df[cat_filter_col].dropna().unique().tolist()
        selected_vals = st.sidebar.multiselect(
            f"Select {cat_filter_col}",
            options=unique_vals,
            default=unique_vals,
            help=f"Filter samples by {cat_filter_col} categories."
        )
        filtered_df = filtered_df[filtered_df[cat_filter_col].isin(selected_vals)]

    # 3. Main Dashboard Layout
    
    # Key Performance Metrics
    total_samples = len(df)
    matched_samples = len(filtered_df)
    pct_match = (matched_samples / total_samples) * 100.0 if total_samples > 0 else 0
    
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.markdown(
            f'<div class="metric-container">'
            f'  <div class="metric-label">Total Samples</div>'
            f'  <div class="metric-value">{total_samples}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with mcol2:
        st.markdown(
            f'<div class="metric-container">'
            f'  <div class="metric-label">Filtered Samples</div>'
            f'  <div class="metric-value">{matched_samples} <span class="metric-unit">({pct_match:.1f}%)</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with mcol3:
        avg_p = filtered_df[p_col].mean() if matched_samples > 0 else 0
        st.markdown(
            f'<div class="metric-container">'
            f'  <div class="metric-label">Mean {p_col}</div>'
            f'  <div class="metric-value">{avg_p:.2f}<span class="metric-unit">%</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with mcol4:
        avg_k = filtered_df[k_col].mean() if matched_samples > 0 else 0
        unit = "mD" if "mD" in k_col or "perm" in k_col.lower() else ""
        st.markdown(
            f'<div class="metric-container">'
            f'  <div class="metric-label">Mean {k_col}</div>'
            f'  <div class="metric-value">{avg_k:.2f}<span class="metric-unit">{unit}</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.write("---")

    # Table and Statistics side-by-side
    col_tbl, col_stats = st.columns([1.5, 1])
    
    with col_tbl:
        st.subheader("Filtered Dataset View")
        if matched_samples > 0:
            st.dataframe(filtered_df, height=300, use_container_width=True)
        else:
            st.warning("No samples match the selected filters. Please expand your filter ranges.")

    with col_stats:
        st.subheader("Summary Statistics")
        if matched_samples > 0:
            st.dataframe(filtered_df.describe().T[["mean", "std", "min", "50%", "max"]], use_container_width=True)
        else:
            st.info("No statistics available for empty selection.")

    st.write("---")

    # 4. Plots Section
    st.subheader("Analytical Visualizations")
    
    if matched_samples > 1:
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown(f"#### Distribution Histogram of {p_col}")
            
            # Interactive Histogram
            fig_hist = px.histogram(
                filtered_df,
                x=p_col,
                color=cat_filter_col if cat_filter_col in filtered_df.columns else None,
                nbins=20,
                color_discrete_sequence=px.colors.qualitative.Safe,
                labels={p_col: p_col, "count": "Sample Count"}
            )
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='#18181B',
                margin=dict(l=40, r=40, t=20, b=40),
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.06)',
                    tickfont=dict(color='#A1A1AA')
                ),
                yaxis=dict(
                    title='Sample Count',
                    gridcolor='rgba(255,255,255,0.06)',
                    tickfont=dict(color='#A1A1AA')
                ),
                legend=dict(
                    font=dict(color='#ECEDEE'),
                    bgcolor='rgba(24,24,27,0.8)',
                    bordercolor='rgba(255,255,255,0.08)'
                )
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_c2:
            st.markdown(f"#### {p_col} vs {k_col} Crossplot")
            
            # Interactive Crossplot (using Log scale for Permeability if relevant)
            log_scale_y = "perm" in k_col.lower() or "mD" in k_col
            
            fig_cross = px.scatter(
                filtered_df,
                x=p_col,
                y=k_col,
                color=cat_filter_col if cat_filter_col in filtered_df.columns else None,
                hover_data=df.columns.tolist(),
                color_discrete_sequence=px.colors.qualitative.Safe,
                log_y=log_scale_y
            )
            fig_cross.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='#18181B',
                margin=dict(l=40, r=40, t=20, b=40),
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.06)',
                    tickfont=dict(color='#A1A1AA')
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.06)',
                    tickfont=dict(color='#A1A1AA')
                ),
                legend=dict(
                    font=dict(color='#ECEDEE'),
                    bgcolor='rgba(24,24,27,0.8)',
                    bordercolor='rgba(255,255,255,0.08)'
                )
            )
            st.plotly_chart(fig_cross, use_container_width=True)
    else:
        st.info("Please select at least 2 samples to view charts.")

    st.write("---")

    # 5. Download Filtered Data as CSV
    if matched_samples > 0:
        filtered_csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Dataset (CSV)",
            data=filtered_csv,
            file_name="filtered_rock_data.csv",
            mime="text/csv",
            help="Download the filtered records matching the slider ranges as a CSV file."
        )

# Execute page runner
run()
