import streamlit as st

def run():
    st.title("📚 AI Usage & Technical Documentation")
    st.markdown("Detailed breakdown of governing engineering physics, mathematical models, and AI development logs.")

    tab1, tab2 = st.tabs(["📐 Physics & Formulation Reference", "🤖 AI Co-Pilot Development Log"])

    # ==========================================
    # TAB 1: MATHEMATICAL FORMULATIONS
    # ==========================================
    with tab1:
        st.subheader("Governing Engineering Equations")
        
        st.markdown("### 1. Fluid Dynamics & Friction Loss")
        st.write(
            "The pipe flow analyser calculates pressure drop using the **Darcy-Weisbach Equation**:"
        )
        st.latex(r"\Delta P = f \cdot \frac{L}{D} \cdot \frac{\rho v^2}{2}")
        st.write(
            "Where velocity is calculated from the volumetric flow rate:"
        )
        st.latex(r"v = \frac{Q}{A} = \frac{4Q}{\pi D^2}")
        st.write(
            "The flow regime is classified by the **Reynolds Number** ($Re$):"
        )
        st.latex(r"Re = \frac{\rho v D}{\mu}")
        st.write(
            "For laminar flow ($Re < 2300$), the friction factor ($f$) is solved analytically as:"
        )
        st.latex(r"f = \frac{64}{Re}")
        st.write(
            "For turbulent flow ($Re \ge 2300$), the friction factor is calculated by solving the implicit **Colebrook-White Equation**:"
        )
        st.latex(r"\frac{1}{\sqrt{f}} = -2.0 \log_{10}\left(\frac{\epsilon/D}{3.7} + \frac{2.51}{Re\sqrt{f}}\right)")
        st.write(
            "Since the equation is implicit, the application implements a numerical **Newton-Raphson iteration**, "
            "seeded with the explicit **Haaland Approximation** for high speed and precision:"
        )
        st.latex(r"\frac{1}{\sqrt{f}} \approx -1.8 \log_{10}\left(\left(\frac{\epsilon/D}{3.7}\right)^{1.11} + \frac{6.9}{Re}\right)")

        st.write("---")
        
        st.markdown("### 2. Thermal Conduction")
        st.write(
            "Steady-state conduction through a single layer, flat wall follows **Fourier's Law**:"
        )
        st.latex(r"q = \frac{Q}{A} = k \frac{T_1 - T_2}{L}")
        st.write(
            "Where:"
            "\n- $Q$ is heat transfer rate ($\text{W}$)"
            "\n- $q$ is heat flux ($\text{W/m}^2$)"
            "\n- $k$ is thermal conductivity ($\text{W/(m}\cdot\text{K)}$)"
            "\n- $L$ is wall thickness ($\text{m}$)"
            "\n- $A$ is perpendicular surface area ($\text{m}^2$)"
        )

        st.write("---")
        
        st.markdown("### 3. Transient Cooling (Newton's Law of Cooling)")
        st.write(
            "Newton's law of cooling governs the heat loss of a body to its surrounding environment. The analytical temperature solution is:"
        )
        st.latex(r"T(t) = T_{\infty} + (T_0 - T_{\infty})e^{-C t}")
        st.write(
            "Where the lumped capacitance cooling constant $C$ is computed from physical properties:"
        )
        st.latex(r"C = \frac{h A}{m C_p}")
        st.write(
            "By inverting the cooling equation, the time to cool to a target temperature ($T_{\text{target}}$) is calculated as:"
        )
        st.latex(r"t = -\frac{1}{C} \ln\left(\frac{T_{\text{target}} - T_{\infty}}{T_0 - T_{\infty}}\right)")

    # ==========================================
    # TAB 2: AI CO-PILOT DEVELOPMENT LOG
    # ==========================================
    with tab2:
        st.subheader("AI Assistance Documentation")
        st.markdown(
            "In accordance with **Module D** requirements, this section details the prompts used to assist "
            "development, what calculations/functionality were verified, and what code blocks were corrected."
        )

        st.markdown("---")
        
        # PROMPT 1
        st.markdown("### 🤖 Prompt 1: Colebrook-White Friction Factor Solver")
        st.markdown(
            "**Submitted Prompt:**\n"
            "> *\"Write a Python solver for the Darcy-Weisbach friction factor in circular pipes. "
            "Implement Colebrook-White solved using the Newton-Raphson method for turbulent flow, and use "
            "64/Re for laminar flow. Use the Haaland equation as a starting guess for the Newton loop. "
            "Provide comments on units and handle edge cases like zero flow or dynamic viscosity.\"*"
        )
        st.success(
            "**What was verified:**\n"
            "- Verified that the friction factor returned for turbulent flow matches the hand-calculated Colebrook solution of $f \approx 0.0275$ for Water flow ($D=50$ mm, roughness $=0.15$ mm, $Q=4$ L/s).\n"
            "- Verified convergence rate: Newton-Raphson converged in 2-3 iterations from the Haaland starting seed."
        )
        st.warning(
            "**What was corrected:**\n"
            "- Added an early exit check for $Re == 0$ to return a friction factor of $0.0$ instead of causing division by zero.\n"
            "- Standardized input types so that roughness ($\epsilon$) and diameter ($D$) are converted to the same unit (meters) prior to calculation to avoid unit-mismatch errors."
        )

        st.markdown("---")

        # PROMPT 2
        st.markdown("### 🤖 Prompt 2: Newton's Law of Cooling Calculation & Validation")
        st.markdown(
            "**Submitted Prompt:**\n"
            "> *\"Implement a Cooling class representing Newton's Law of Cooling. The constructor should accept "
            "either a direct cooling constant or individual physical parameters (h, area, mass, Cp). "
            "Write functions to compute temperature at time t and time to reach a target temperature. "
            "Add safety constraints to verify inputs represent a physical cooling process.\"*"
        )
        st.success(
            "**What was verified:**\n"
            "- Verified the analytical math output for time to cool a steel block ($5$ kg, surface area $0.1$ m², $Cp=450$ J/kgK, $h=25$ W/m²K) from $80$°C to $40$°C in a $20$°C environment. The result matches the analytical solution of $988.75$ seconds."
        )
        st.warning(
            "**What was corrected:**\n"
            "- The initial AI script allowed the target temperature ($T_{\\text{target}}$) to cross the ambient temperature ($T_{\\infty}$). Mathematically, this evaluates a negative logarithm argument (log of a negative value), raising a Python `ValueError` and crashing the page. Added validation constraints to verify that the target temperature is bounded strictly between the initial temperature ($T_0$) and the ambient temperature ($T_{\\infty}$), providing descriptive error feedback to the user."
        )

        st.markdown("---")

        # PROMPT 3
        st.markdown("### 🤖 Prompt 3: Streamlit Modern Layout & Routing")
        st.markdown(
            "**Submitted Prompt:**\n"
            "> *\"Design a multi-page routing framework for a Streamlit app using modern Streamlit 1.35+ features "
            "(st.navigation and st.Page). Incorporate a custom CSS template to override the default light/dark colors "
            "to show a premium dark mode, utilizing Google Fonts (Outfit for headers, Inter for body) and Vercel-like card styles.\"*"
        )
        st.success(
            "**What was verified:**\n"
            "- Verified that Streamlit loads the pages and sidebar correctly and that the CSS overrides the default font styling and border layouts successfully."
        )
        st.warning(
            "**What was corrected:**\n"
            "- The initial template called `st.set_page_config` in every page file. Streamlit raises a runtime error if page config is defined multiple times or after other elements. Consolidated the `st.set_page_config` call to the very first line of the main `app.py` wrapper, letting the subpages focus entirely on layout and computations without configuration collisions."
        )

# Execute page runner
run()
