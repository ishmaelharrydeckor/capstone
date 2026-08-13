import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from engineering import Fluid, Pipe

def run():
    st.title("🚰 Pipe Flow Analyser")
    st.markdown("Calculate fluid velocity, Reynolds number, friction factor, and pressure drop in a circular pipe.")

    # 1. Sidebar Inputs
    st.sidebar.header("Fluid Properties")
    
    fluid_type = st.sidebar.selectbox(
        "Select Fluid",
        options=["Water", "Air", "Crude Oil", "User-Defined"],
        help="Choose a standard fluid to auto-populate properties, or define custom density and viscosity."
    )

    if fluid_type == "User-Defined":
        density = st.sidebar.number_input(
            "Density (kg/m³)",
            min_value=0.01,
            max_value=20000.0,
            value=1000.0,
            step=10.0,
            help="Mass per unit volume of the fluid."
        )
        viscosity = st.sidebar.number_input(
            "Dynamic Viscosity (Pa·s)",
            min_value=1e-6,
            max_value=10.0,
            value=0.001,
            format="%.6f",
            step=1e-4,
            help="Dynamic viscosity of the fluid. Water at 20°C is ~0.001 Pa·s."
        )
        fluid = Fluid(name="Custom Fluid", density=density, viscosity=viscosity)
    else:
        fluid = Fluid.get_standard_fluid(fluid_type)
        st.sidebar.info(
            f"**{fluid.name} Properties (20°C):**\n\n"
            f"- Density: `{fluid.density}` kg/m³\n"
            f"- Viscosity: `{fluid.viscosity}` Pa·s"
        )

    st.sidebar.header("Pipe Geometry")
    
    # Input in millimeters for user convenience, converted to meters
    diameter_mm = st.sidebar.number_input(
        "Inner Diameter (mm)",
        min_value=1.0,
        max_value=10000.0,
        value=50.0,
        step=5.0,
        help="Inner diameter of the pipe. Standard residential water supply is ~15-25 mm."
    )
    
    length = st.sidebar.number_input(
        "Pipe Length (m)",
        min_value=0.1,
        max_value=100000.0,
        value=100.0,
        step=10.0,
        help="Total length of the pipe section."
    )
    
    # Roughness in millimeters, converted to meters
    roughness_mm = st.sidebar.number_input(
        "Wall Roughness (mm)",
        min_value=0.0,
        max_value=100.0,
        value=0.15,
        format="%.5f",
        step=0.01,
        help="Absolute pipe wall roughness (epsilon). E.g., PVC = 0.0015 mm, Steel = 0.045 mm, Galvanized Iron = 0.15 mm."
    )

    st.sidebar.header("Operating Conditions")
    
    # Volumetric flow rate in liters per second, converted to m^3/s
    flow_rate_lps = st.sidebar.number_input(
        "Volumetric Flow Rate (L/s)",
        min_value=0.0,
        max_value=100000.0,
        value=4.0,
        step=0.5,
        help="Volume of fluid passing through the pipe per second."
    )

    # 2. Computations and Error Handling
    try:
        # Convert inputs to SI base units
        diameter_m = diameter_mm / 1000.0
        roughness_m = roughness_mm / 1000.0
        flow_rate_m3s = flow_rate_lps / 1000.0

        # Construct Pipe instance
        pipe = Pipe(
            diameter=diameter_m,
            length=length,
            roughness=roughness_m,
            fluid=fluid
        )

        # Calculate values
        velocity = pipe.calculate_velocity(flow_rate_m3s)
        re = pipe.calculate_reynolds_number(flow_rate_m3s)
        f = pipe.calculate_friction_factor(flow_rate_m3s)
        dp = pipe.calculate_pressure_drop(flow_rate_m3s)
        
        # Determine flow regime
        if re == 0:
            regime = "Static"
            regime_color = "#71717A"
        elif re < 2300:
            regime = "Laminar"
            regime_color = "#10B981" # Green
        elif re <= 4000:
            regime = "Transitional"
            regime_color = "#F59E0B" # Orange
        else:
            regime = "Turbulent"
            regime_color = "#3B82F6" # Blue

        # 3. UI Display Layout
        # Display Key Metrics using premium styled cards
        st.subheader("Calculation Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f'<div class="metric-container">'
                f'  <div class="metric-label">Flow Velocity</div>'
                f'  <div class="metric-value">{velocity:.3f}<span class="metric-unit">m/s</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown(
                f'<div class="metric-container">'
                f'  <div class="metric-label">Reynolds Number</div>'
                f'  <div class="metric-value">{re:,.1f}<span class="metric-unit" style="color:{regime_color};">({regime})</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                f'<div class="metric-container">'
                f'  <div class="metric-label">Friction Factor (f)</div>'
                f'  <div class="metric-value">{f:.5f}<span class="metric-unit">Darcy</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )
            
        with col4:
            st.markdown(
                f'<div class="metric-container">'
                f'  <div class="metric-label">Pressure Drop (ΔP)</div>'
                f'  <div class="metric-value">{dp/1000.0:.3f}<span class="metric-unit">kPa</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.write("---")

        # 4. Range Sweeping and Plotting
        st.subheader("Pressure Drop Sweep Analysis")
        st.markdown("Visualizes how pressure drop scales with volumetric flow rate for the selected pipe and fluid configuration.")

        # Generate flow rate sweep range (excluding 0, up to 2x the user input, min 10 points)
        max_sweep_lps = max(flow_rate_lps * 2.0, 10.0)
        sweep_lps = np.linspace(0.1, max_sweep_lps, 50)
        
        sweep_data = []
        for q_lps in sweep_lps:
            q_m3s = q_lps / 1000.0
            try:
                v_s = pipe.calculate_velocity(q_m3s)
                re_s = pipe.calculate_reynolds_number(q_m3s)
                f_s = pipe.calculate_friction_factor(q_m3s)
                dp_s = pipe.calculate_pressure_drop(q_m3s)
                sweep_data.append({
                    "Flow Rate (L/s)": q_lps,
                    "Velocity (m/s)": v_s,
                    "Reynolds Number": re_s,
                    "Friction Factor": f_s,
                    "Pressure Drop (kPa)": dp_s / 1000.0
                })
            except Exception:
                pass
                
        df_sweep = pd.DataFrame(sweep_data)

        # Plotly plot configuration matching sleek dark mode
        fig = go.Figure()
        
        # Add sweep line
        fig.add_trace(go.Scatter(
            x=df_sweep["Flow Rate (L/s)"],
            y=df_sweep["Pressure Drop (kPa)"],
            mode='lines',
            name='Pressure Drop Curve',
            line=dict(color='#0072F5', width=3),
            hovertemplate='Flow Rate: %{x:.2f} L/s<br>Pressure Drop: %{y:.3f} kPa<extra></extra>'
        ))
        
        # Highlight operating point if greater than 0
        if flow_rate_lps > 0:
            fig.add_trace(go.Scatter(
                x=[flow_rate_lps],
                y=[dp / 1000.0],
                mode='markers',
                name='Operating Point',
                marker=dict(color='#F59E0B', size=12, symbol='diamond', line=dict(color='#ECEDEE', width=1.5)),
                hovertemplate='Operating Point<br>Flow Rate: %{x:.2f} L/s<br>Pressure Drop: %{y:.3f} kPa<extra></extra>'
            ))
            
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#18181B',
            margin=dict(l=40, r=40, t=20, b=40),
            xaxis=dict(
                title='Volumetric Flow Rate (L/s)',
                gridcolor='rgba(255,255,255,0.06)',
                zerolinecolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#A1A1AA')
            ),
            yaxis=dict(
                title='Pressure Drop (kPa)',
                gridcolor='rgba(255,255,255,0.06)',
                zerolinecolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#A1A1AA')
            ),
            legend=dict(
                font=dict(color='#ECEDEE'),
                bgcolor='rgba(24,24,27,0.8)',
                bordercolor='rgba(255,255,255,0.08)',
                borderwidth=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # 5. CSV Export Functionality
        # Generate export CSV string
        csv_data = df_sweep.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Export Sweep Data to CSV",
            data=csv_data,
            file_name=f"pipe_flow_sweep_{fluid.name.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            help="Download the entire flow rate sweep analysis data as a CSV file."
        )

    except Exception as e:
        st.error(f"An error occurred during calculations: {str(e)}")
        st.info("Please verify that all geometry and fluid values are physically reasonable.")

# Execute page runner
run()
