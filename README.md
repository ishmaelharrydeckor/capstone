# Fluid Flow & Heat Transfer Engineering Suite

A professional-quality, multi-page web application developed in Python using Streamlit, Plotly, and Object-Oriented Programming (OOP) principles. 

This platform serves as a complete computational engineering suite for fluid mechanics, thermal conduction, transient cooling, and reservoir data analytics.

## 🚀 Live Demo
**App URL:** *[Insert Live Streamlit Community Cloud URL here]*

---

## 🛠️ Modules & Features

### 1. Pipe Flow Analyser (Module A)
- **Fluid Selection:** Automatically populates density and dynamic viscosity properties for water, air, crude oil, or custom user-defined fluids.
- **Pipe Geometry & Friction Calculations:** Computes velocity, Reynolds number ($Re$), Darcy friction factor ($f$), and total pressure drop ($\Delta P$).
- **Friction Solver:** Uses a numerical **Newton-Raphson solver** to resolve the implicit **Colebrook-White equation** for turbulent flow ($Re \ge 2300$), seeded with the **Haaland equation** for quick convergence. Falls back to $64/Re$ for laminar flow.
- **Visual Analytics:** Generates an interactive Plotly sweep curve plotting pressure drop vs. volumetric flow rate with a highlighted diamond marker at the operating point.
- **Export:** Exposes a download button to export the sweep data to a CSV file.

### 2. Heat Transfer Calculator (Module B)
- **Steady-State Conduction:** Applies **Fourier's Law** through a flat wall layer to calculate temperature gradients, heat flux ($q$), and heat flow rate ($Q$). Includes an interactive Plotly temperature profile plot.
- **Newton's Law of Cooling:** Simulates transient cooling (or heating) decay over time. Supports calculations derived from convective heat transfer coefficients ($h$) or direct cooling constants ($C$).
- **Interactive Cooling Decay Curve:** Renders a real-time Plotly graph showing temperature decay over time against the ambient temperature limit, updating instantaneously via slider controls.

### 3. Rock & Fluid Data Dashboard (Module C)
- **Core Analysis Loader:** Accepts user-uploaded reservoir CSV datasets.
- **Demo Mode:** Embeds a button to dynamically generate and load a synthetic core dataset featuring realistic porosity, depth, and logarithmically correlated permeability.
- **Data Filtering:** Dynamic sidebar ranges (porosity, permeability, lithology type) instantly filter the core data.
- **Visual Plots:** Renders two charts: a porosity distribution histogram and a porosity-permeability scatter plot color-coded by lithology.
- **Export:** Exposes a button to download the filtered sub-dataset as a CSV file.

### 4. Technical Documentation (Module D)
- Governed by class objects (`Fluid`, `Pipe`, `Conduction`, `Cooling`) stored inside `engineering.py`.
- Features an **AI Co-Pilot Development Log** highlighting 3 distinct prompt interactions, verified calculations, and corrected edge cases.

---

## 💻 Installation & Local Execution

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ishmaelharrydeckor/capstone.git
   cd capstone
   ```

2. **Install Required Libraries:**
   ```bash
   pip install streamlit pandas plotly numpy
   ```

3. **Run Verification Tests:**
   Ensure all computational equations and analytical solutions verify successfully:
   ```bash
   python -m unittest test_calculations.py
   ```

4. **Launch the Application:**
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Deployment to Streamlit Community Cloud

To deploy this application:
1. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click **New app**.
3. Select this GitHub repository (`ishmaelharrydeckor/capstone`), branch `main`, and main file path `app.py`.
4. Click **Deploy!**
