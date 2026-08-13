import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from engineering import Conduction, Cooling

def run():
    st.title("🔥 Heat Transfer Calculator")
    st.markdown("Perform steady-state conduction analyses and transient convective cooling simulations.")

    # Create tabs for the two different calculations
    tab1, tab2 = st.tabs(["🧱 Steady-State Conduction", "❄️ Newton's Law of Cooling"])

    # ==========================================
    # TAB 1: STEADY-STATE CONDUCTION
    # ==========================================
    with tab1:
        st.subheader("1D Conduction Through a Flat Wall")
        st.markdown(
            "Fourier's Law of Thermal Conduction describes heat transfer through solid materials. "
            "It states that the rate of heat flow is proportional to the temperature gradient "
            "and the cross-sectional area perpendicular to that flow."
        )
        
        # Display Fourier's Law LaTeX
        st.latex(r"q = \frac{Q}{A} = -k \frac{dT}{dx} \quad \xrightarrow{\text{1D Steady State}} \quad Q = k A \frac{T_1 - T_2}{L}")

        col_left, col_right = st.columns([1, 1.5])

        with col_left:
            st.markdown("### Inputs")
            
            # Guidelines on typical conductivities
            st.info(
                "**Typical Thermal Conductivities (k, W/(m·K)):**\n"
                "- Copper: `401` | Steel: `50` | Concrete: `1.5`\n"
                "- Glass: `0.8` | Wood: `0.15` | Fiberglass: `0.04`"
            )
            
            k_cond = st.number_input(
                "Thermal Conductivity, k (W/(m·K))",
                min_value=0.001,
                max_value=5000.0,
                value=1.5,
                step=0.1,
                help="Material property representing its ability to conduct heat (W per meter-Kelvin)."
            )
            
            thickness_cm = st.number_input(
                "Wall Thickness, L (cm)",
                min_value=0.1,
                max_value=5000.0,
                value=20.0,
                step=1.0,
                help="Thickness of the solid barrier through which heat conducts. Measured in centimeters."
            )
            
            area_cond = st.number_input(
                "Surface Area, A (m²)",
                min_value=0.01,
                max_value=100000.0,
                value=10.0,
                step=1.0,
                help="Total cross-sectional surface area perpendicular to the direction of heat flow."
            )
            
            t1_temp = st.number_input(
                "Hot Side Temperature, T₁ (°C)",
                value=25.0,
                step=1.0,
                help="Temperature of the hotter surface of the wall."
            )
            
            t2_temp = st.number_input(
                "Cold Side Temperature, T₂ (°C)",
                value=15.0,
                step=1.0,
                help="Temperature of the cooler surface of the wall."
            )

        with col_right:
            st.markdown("### Conduction Results")
            
            try:
                # Convert thickness to meters
                thickness_m = thickness_cm / 100.0
                
                # Instanstiate conduction model
                conduction = Conduction(
                    thermal_conductivity=k_cond,
                    thickness=thickness_m,
                    area=area_cond
                )
                
                # Perform calculations
                heat_flux = conduction.calculate_heat_flux(t1_temp, t2_temp)
                heat_flow = conduction.calculate_heat_flow_rate(t1_temp, t2_temp)
                
                # Display metrics
                mcol1, mcol2 = st.columns(2)
                with mcol1:
                    st.markdown(
                        f'<div class="metric-container">'
                        f'  <div class="metric-label">Heat Flux (q)</div>'
                        f'  <div class="metric-value">{heat_flux:.1f}<span class="metric-unit">W/m²</span></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with mcol2:
                    st.markdown(
                        f'<div class="metric-container">'
                        f'  <div class="metric-label">Total Heat Flow Rate (Q)</div>'
                        f'  <div class="metric-value">{heat_flow:.1f}<span class="metric-unit">W</span></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                # Display physical explanation
                st.markdown("#### Thermodynamic Interpretation")
                direction = "from Hot Side ($T_1$) to Cold Side ($T_2$)" if t1_temp > t2_temp else "from Cold Side ($T_2$) to Hot Side ($T_1$)"
                
                st.write(
                    f"At steady state, **{abs(heat_flow):,.1f} Watts** of thermal energy is continuously "
                    f"transferred through the **{thickness_cm} cm** thick wall {direction}. "
                    f"This corresponds to a heat flow density of **{abs(heat_flux):,.1f} W/m²** "
                    f"over the **{area_cond} m²** surface area."
                )

                # Visual illustration of temperatures
                fig_cond = go.Figure()
                fig_cond.add_trace(go.Scatter(
                    x=[0, thickness_cm],
                    y=[t1_temp, t2_temp],
                    mode='lines+markers',
                    line=dict(color='#FF4B4B', width=4),
                    marker=dict(size=12, color=['#FF4B4B', '#0072F5']),
                    hovertemplate='Position: %{x} cm<br>Temperature: %{y:.1f} °C<extra></extra>'
                ))
                fig_cond.update_layout(
                    title="Linear Temperature Profile Through the Wall",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='#18181B',
                    margin=dict(l=40, r=40, t=40, b=40),
                    xaxis=dict(
                        title='Position (cm)',
                        gridcolor='rgba(255,255,255,0.06)',
                        zerolinecolor='rgba(255,255,255,0.1)',
                        tickfont=dict(color='#A1A1AA')
                    ),
                    yaxis=dict(
                        title='Temperature (°C)',
                        gridcolor='rgba(255,255,255,0.06)',
                        zerolinecolor='rgba(255,255,255,0.1)',
                        tickfont=dict(color='#A1A1AA')
                    )
                )
                st.plotly_chart(fig_cond, use_container_width=True)

            except Exception as e:
                st.error(f"Calculation Error: {str(e)}")

    # ==========================================
    # TAB 2: NEWTON'S LAW OF COOLING
    # ==========================================
    with tab2:
        st.subheader("Transient Cooling / Heating Simulation")
        st.markdown(
            "Newton's Law of Cooling states that the rate of temperature change of an object "
            "is proportional to the difference between its own temperature ($T$) and the ambient temperature ($T_{\infty}$)."
        )
        st.latex(r"\frac{dT}{dt} = -C(T - T_{\infty}) \quad \xrightarrow{\text{Analytical Solution}} \quad T(t) = T_{\infty} + (T_0 - T_{\infty})e^{-C t}")
        st.latex(r"\text{where } C = \frac{h A}{m C_p}")

        col_sliders, col_plot = st.columns([1, 1.5])

        with col_sliders:
            st.markdown("### Interactive Simulation Inputs")

            # Temperature inputs using sliders for real-time responsiveness
            t0_cooling = st.slider(
                "Initial Object Temperature, T₀ (°C)",
                min_value=-50.0,
                max_value=500.0,
                value=80.0,
                step=5.0,
                help="Initial temperature of the object when cooling begins."
            )
            
            t_inf_cooling = st.slider(
                "Ambient/Surrounding Temperature, T_inf (°C)",
                min_value=-50.0,
                max_value=200.0,
                value=20.0,
                step=2.0,
                help="Temperature of the surrounding fluid (air, water, oil, etc.)."
            )
            
            # Dynamically adjust min/max targets based on cooling vs heating direction
            is_cooling_direction = t0_cooling > t_inf_cooling
            
            if is_cooling_direction:
                min_t_target = t_inf_cooling + 0.1
                max_t_target = t0_cooling
                default_target = (t0_cooling + t_inf_cooling) / 2.0
            else:
                min_t_target = t0_cooling
                max_t_target = t_inf_cooling - 0.1
                default_target = (t0_cooling + t_inf_cooling) / 2.0

            t_target_cooling = st.slider(
                "Target Object Temperature, T_target (°C)",
                min_value=float(min_t_target),
                max_value=float(max_t_target),
                value=float(default_target),
                step=1.0,
                help="The desired temperature to reach. Must lie strictly between T0 and Ambient."
            )

            # Input parameters choice: Physical vs Direct
            input_mode = st.radio(
                "Cooling Characterization Method",
                options=["Use Physical Parameters (Calculate C)", "Enter Cooling Constant (C) Directly"],
                help="Choose to build the cooling rate from physical properties, or supply the coefficient directly."
            )

            if input_mode == "Use Physical Parameters (Calculate C)":
                st.info(
                    "**Typical Heat Transfer Coefficients (h, W/(m²·K)):**\n"
                    "- Still Air: `5 - 25` | Flowing Air: `10 - 200`\n"
                    "- Flowing Water: `50 - 10,000`"
                )
                h_coeff = st.number_input(
                    "Convective Coefficient, h (W/(m²·K))",
                    min_value=0.1,
                    max_value=20000.0,
                    value=25.0,
                    step=5.0,
                    help="Heat transfer rate per unit area per unit temperature difference."
                )
                area_cooling = st.number_input(
                    "Exposed Surface Area, A (m²)",
                    min_value=0.0001,
                    max_value=100.0,
                    value=0.1,
                    format="%.4f",
                    step=0.01,
                    help="Surface area of the object in contact with the ambient fluid."
                )
                mass_cooling = st.number_input(
                    "Object Mass, m (kg)",
                    min_value=0.001,
                    max_value=10000.0,
                    value=5.0,
                    step=0.5,
                    help="Mass of the object being cooled."
                )
                # Specific Heat J/kgK
                st.info(
                    "**Specific Heat (Cp, J/(kg·K)):**\n"
                    "- Water: `4184` | Air: `1005` | Aluminum: `900` | Steel: `450`"
                )
                cp_cooling = st.number_input(
                    "Specific Heat Capacity, Cp (J/(kg·K))",
                    min_value=1.0,
                    max_value=20000.0,
                    value=450.0,
                    step=50.0,
                    help="Specific heat capacity of the object material."
                )
                
                try:
                    cooling_model = Cooling(
                        h=h_coeff,
                        area=area_cooling,
                        mass=mass_cooling,
                        specific_heat=cp_cooling
                    )
                except Exception as e:
                    st.error(str(e))
                    cooling_model = None
            else:
                c_constant = st.number_input(
                    "Cooling Constant, C (s⁻¹)",
                    min_value=1e-6,
                    max_value=1.0,
                    value=0.001111,
                    format="%.6f",
                    step=1e-4,
                    help="Overall lumped capacitance heat transfer coefficient. A higher value means faster cooling."
                )
                try:
                    cooling_model = Cooling(cooling_constant=c_constant)
                except Exception as e:
                    st.error(str(e))
                    cooling_model = None

        with col_plot:
            st.markdown("### Dynamic Cooling Curve")
            
            if cooling_model is not None:
                try:
                    # Calculate time to reach target temperature
                    time_sec = cooling_model.time_to_cool(t_target_cooling, t0_cooling, t_inf_cooling)
                    time_min = time_sec / 60.0
                    
                    # Display metrics
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.markdown(
                            f'<div class="metric-container">'
                            f'  <div class="metric-label">Cooling Constant (C)</div>'
                            f'  <div class="metric-value">{cooling_model.cooling_constant:.6f}<span class="metric-unit">s⁻¹</span></div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with mcol2:
                        st.markdown(
                            f'<div class="metric-container">'
                            f'  <div class="metric-label">Time to Target Temp</div>'
                            f'  <div class="metric-value">{time_min:.2f}<span class="metric-unit">min</span></div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    # Plotting temperature decay
                    # Generate curve data up to 2x the target time for context, or at least 10 minutes
                    max_plot_time = max(time_sec * 1.5, 600.0)
                    curve_points = cooling_model.generate_cooling_curve(t0_cooling, t_inf_cooling, max_plot_time, 200)
                    
                    df_cooling = pd.DataFrame(curve_points, columns=["Time (s)", "Temperature (°C)"])
                    df_cooling["Time (min)"] = df_cooling["Time (s)"] / 60.0

                    fig_cool = go.Figure()
                    
                    # Ambient temperature asymptote
                    fig_cool.add_hline(
                        y=t_inf_cooling,
                        line_dash="dash",
                        line_color="rgba(250,250,250,0.5)",
                        annotation_text="Ambient Temp (T_inf)",
                        annotation_position="bottom right",
                        annotation_font=dict(color="#A1A1AA")
                    )

                    # Cooling curve
                    fig_cool.add_trace(go.Scatter(
                        x=df_cooling["Time (min)"],
                        y=df_cooling["Temperature (°C)"],
                        mode='lines',
                        name='Object Temp',
                        line=dict(color='#0072F5', width=3),
                        hovertemplate='Time: %{x:.2f} min<br>Temperature: %{y:.1f} °C<extra></extra>'
                    ))

                    # Mark Target temperature point
                    fig_cool.add_trace(go.Scatter(
                        x=[time_min],
                        y=[t_target_cooling],
                        mode='markers+text',
                        name='Target Temp',
                        marker=dict(color='#F59E0B', size=12, symbol='circle', line=dict(color='#ECEDEE', width=1.5)),
                        text=[f"Target: {t_target_cooling:.1f}°C<br>({time_min:.1f} min)"],
                        textposition="top right",
                        textfont=dict(color='#ECEDEE'),
                        hovertemplate='Target Point<br>Time: %{x:.2f} min<br>Temperature: %{y:.1f} °C<extra></extra>'
                    ))

                    fig_cool.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='#18181B',
                        margin=dict(l=40, r=40, t=30, b=40),
                        xaxis=dict(
                            title='Time (minutes)',
                            gridcolor='rgba(255,255,255,0.06)',
                            zerolinecolor='rgba(255,255,255,0.1)',
                            tickfont=dict(color='#A1A1AA')
                        ),
                        yaxis=dict(
                            title='Temperature (°C)',
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
                    
                    st.plotly_chart(fig_cool, use_container_width=True)

                except Exception as e:
                    st.error(f"Error executing cooling simulation: {str(e)}")
                    st.info("Check that initial and target temperatures are physical and consistent with heat flow direction.")
            else:
                st.warning("Please resolve validation errors in inputs to view the simulation.")

# Execute page runner
run()
