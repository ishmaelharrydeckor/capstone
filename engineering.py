import math
from typing import Dict, Tuple, List, Optional

class Fluid:
    """
    Represents a fluid and its thermodynamic properties.
    """
    
    # Pre-defined database of standard fluids at 20°C
    STANDARD_FLUIDS = {
        "Water": {
            "density": 998.2,      # kg/m^3
            "viscosity": 0.001002  # Pa*s (kg/(m*s))
        },
        "Air": {
            "density": 1.204,      # kg/m^3
            "viscosity": 0.00001825 # Pa*s
        },
        "Crude Oil": {
            "density": 850.0,      # kg/m^3
            "viscosity": 0.020     # Pa*s (20 cP)
        }
    }

    def __init__(self, name: str, density: float, viscosity: float):
        """
        Initializes a Fluid.
        
        Args:
            name: The name of the fluid.
            density: The density in kg/m^3. Must be greater than 0.
            viscosity: The dynamic viscosity in Pa*s. Must be greater than 0.
        """
        if density <= 0:
            raise ValueError("Density must be positive and greater than zero.")
        if viscosity <= 0:
            raise ValueError("Viscosity must be positive and greater than zero.")
            
        self.name = name
        self.density = density
        self.viscosity = viscosity

    @classmethod
    def get_standard_fluid(cls, name: str) -> 'Fluid':
        """
        Returns a Fluid instance representing a standard fluid.
        
        Args:
            name: The name of the standard fluid ('Water', 'Air', 'Crude Oil').
        """
        if name not in cls.STANDARD_FLUIDS:
            raise ValueError(f"Unknown standard fluid '{name}'. Choose from {list(cls.STANDARD_FLUIDS.keys())}")
        properties = cls.STANDARD_FLUIDS[name]
        return cls(name, properties["density"], properties["viscosity"])

    def __repr__(self) -> str:
        return f"Fluid(name='{self.name}', density={self.density} kg/m³, viscosity={self.viscosity} Pa·s)"


class Pipe:
    """
    Represents a circular pipe and handles fluid flow calculations.
    """

    def __init__(self, diameter: float, length: float, roughness: float, fluid: Fluid):
        """
        Initializes a Pipe.
        
        Args:
            diameter: Inner diameter of the pipe in meters (D). Must be greater than 0.
            length: Length of the pipe in meters (L). Must be greater than 0.
            roughness: Pipe wall roughness in meters (epsilon). Must be non-negative.
            fluid: A Fluid instance.
        """
        if diameter <= 0:
            raise ValueError("Pipe diameter must be positive and greater than zero.")
        if length <= 0:
            raise ValueError("Pipe length must be positive and greater than zero.")
        if roughness < 0:
            raise ValueError("Pipe roughness cannot be negative.")
            
        self.diameter = diameter
        self.length = length
        self.roughness = roughness
        self.fluid = fluid

    def calculate_velocity(self, flow_rate: float) -> float:
        """
        Calculates fluid velocity inside the pipe.
        
        Args:
            flow_rate: Volumetric flow rate in m^3/s.
        """
        if flow_rate < 0:
            raise ValueError("Flow rate cannot be negative.")
        area = (math.pi * (self.diameter ** 2)) / 4.0
        return flow_rate / area

    def calculate_reynolds_number(self, flow_rate: float) -> float:
        """
        Calculates the Reynolds number of the pipe flow.
        
        Args:
            flow_rate: Volumetric flow rate in m^3/s.
        """
        if flow_rate == 0:
            return 0.0
        velocity = self.calculate_velocity(flow_rate)
        return (self.fluid.density * velocity * self.diameter) / self.fluid.viscosity

    def calculate_friction_factor(self, flow_rate: float) -> float:
        """
        Calculates the Darcy-Weisbach friction factor (f).
        Uses Colebrook-White solved via Newton-Raphson for turbulent flow.
        Uses 64/Re for laminar flow.
        
        Args:
            flow_rate: Volumetric flow rate in m^3/s.
        """
        re = self.calculate_reynolds_number(flow_rate)
        
        # Safe handling for no flow
        if re == 0:
            return 0.0
            
        # Laminar flow region (Re < 2300)
        if re < 2300:
            return 64.0 / re
            
        # Turbulent / Transitional flow (Re >= 2300)
        # Solve the implicit Colebrook-White equation:
        # 1 / sqrt(f) = -2.0 * log10( (eps/D)/3.7 + 2.51/(Re * sqrt(f)) )
        # Let x = 1 / sqrt(f)
        # We need to find the root of:
        # F(x) = x + 2.0 * log10( (eps/D)/3.7 + 2.51/Re * x ) = 0
        
        eps_d_ratio = self.roughness / self.diameter
        term1 = eps_d_ratio / 3.7
        term2_factor = 2.51 / re
        
        # Initial guess using Haaland equation (explicit and very close to Colebrook-White)
        # 1 / sqrt(f) = -1.8 * log10( ((eps/D)/3.7)^1.11 + 6.9/Re )
        haaland_inside = (eps_d_ratio / 3.7) ** 1.11 + 6.9 / re
        if haaland_inside <= 0:
            # Fallback starting guess
            x = 7.0
        else:
            x = -1.8 * math.log10(haaland_inside)
            
        # Newton-Raphson iteration
        max_iterations = 100
        tolerance = 1e-7
        
        for _ in range(max_iterations):
            arg = term1 + term2_factor * x
            if arg <= 0:
                # Keep inside math bounds
                arg = 1e-15
            
            val_log = math.log10(arg)
            f_val = x + 2.0 * val_log
            
            # Derivative: dF/dx = 1 + (2.0 / ln(10)) * (term2_factor / arg)
            df_val = 1.0 + (2.0 / math.log(10.0)) * (term2_factor / arg)
            
            dx = f_val / df_val
            x_new = x - dx
            
            if abs(x_new - x) < tolerance:
                # Converged!
                f = 1.0 / (x_new ** 2)
                return f
            x = x_new
            
        # Return what we have if it doesn't fully converge (should not happen for physical inputs)
        return 1.0 / (x ** 2)

    def calculate_pressure_drop(self, flow_rate: float) -> float:
        """
        Calculates the pressure drop across the pipe length using the Darcy-Weisbach equation.
        
        Args:
            flow_rate: Volumetric flow rate in m^3/s.
            
        Returns:
            Pressure drop in Pascals (Pa).
        """
        if flow_rate == 0:
            return 0.0
            
        velocity = self.calculate_velocity(flow_rate)
        f = self.calculate_friction_factor(flow_rate)
        
        # Darcy-Weisbach equation: Delta P = f * (L/D) * (rho * v^2 / 2)
        pressure_drop = f * (self.length / self.diameter) * (self.fluid.density * (velocity ** 2) / 2.0)
        return pressure_drop


class Conduction:
    """
    Represents steady-state 1D heat conduction through a flat wall (Fourier's Law).
    """

    def __init__(self, thermal_conductivity: float, thickness: float, area: float):
        """
        Initializes a Conduction model.
        
        Args:
            thermal_conductivity: Thermal conductivity of the material (k) in W/(m*K). Must be greater than 0.
            thickness: Wall thickness (L) in meters. Must be greater than 0.
            area: Heat transfer surface area (A) in m^2. Must be greater than 0.
        """
        if thermal_conductivity <= 0:
            raise ValueError("Thermal conductivity must be positive and greater than zero.")
        if thickness <= 0:
            raise ValueError("Thickness must be positive and greater than zero.")
        if area <= 0:
            raise ValueError("Area must be positive and greater than zero.")
            
        self.thermal_conductivity = thermal_conductivity
        self.thickness = thickness
        self.area = area

    def calculate_heat_flux(self, T1: float, T2: float) -> float:
        """
        Calculates the heat flux (q) in W/m^2 through the wall.
        Fourier's Law: q = k * (T1 - T2) / L
        
        Args:
            T1: Outer/hot surface temperature in °C or K.
            T2: Inner/cold surface temperature in °C or K.
        """
        return self.thermal_conductivity * (T1 - T2) / self.thickness

    def calculate_heat_flow_rate(self, T1: float, T2: float) -> float:
        """
        Calculates the total heat flow rate (Q) in Watts (W) through the wall.
        Q = q * A
        
        Args:
            T1: Outer/hot surface temperature in °C or K.
            T2: Inner/cold surface temperature in °C or K.
        """
        return self.calculate_heat_flux(T1, T2) * self.area


class Cooling:
    """
    Represents transient heat cooling of an object via Newton's Law of Cooling.
    """

    def __init__(self, 
                 h: Optional[float] = None, 
                 area: Optional[float] = None, 
                 mass: Optional[float] = None, 
                 specific_heat: Optional[float] = None,
                 cooling_constant: Optional[float] = None):
        """
        Initializes a Cooling model. Either specify the individual physical properties
        (h, area, mass, specific_heat) to compute the cooling constant, or input
        cooling_constant directly.
        
        Args:
            h: Convective heat transfer coefficient in W/(m^2*K).
            area: Heat transfer surface area in m^2.
            mass: Mass of the object in kg.
            specific_heat: Specific heat capacity of the object in J/(kg*K).
            cooling_constant: Explicit cooling constant (C) in s^-1.
        """
        # If cooling constant is directly provided
        if cooling_constant is not None:
            if cooling_constant <= 0:
                raise ValueError("Cooling constant must be positive and greater than zero.")
            self._cooling_constant = cooling_constant
            self.h = None
            self.area = None
            self.mass = None
            self.specific_heat = None
        else:
            # Verify all physical parameters are provided and valid
            if h is None or area is None or mass is None or specific_heat is None:
                raise ValueError("Must provide either a direct 'cooling_constant' or all physical parameters "
                                 "('h', 'area', 'mass', 'specific_heat').")
            if h <= 0:
                raise ValueError("Convective heat transfer coefficient (h) must be positive.")
            if area <= 0:
                raise ValueError("Surface area must be positive.")
            if mass <= 0:
                raise ValueError("Mass must be positive.")
            if specific_heat <= 0:
                raise ValueError("Specific heat must be positive.")
                
            self.h = h
            self.area = area
            self.mass = mass
            self.specific_heat = specific_heat
            # C = (h * A) / (m * Cp)
            self._cooling_constant = (h * area) / (mass * specific_heat)

    @property
    def cooling_constant(self) -> float:
        """
        Returns the cooling constant in s^-1.
        """
        return self._cooling_constant

    def temperature_at_time(self, t: float, T0: float, T_inf: float) -> float:
        """
        Calculates temperature of the object at time t (seconds).
        T(t) = T_inf + (T0 - T_inf) * e^(-C * t)
        
        Args:
            t: Time in seconds. Must be non-negative.
            T0: Initial temperature of the object in °C or K.
            T_inf: Ambient/fluid temperature in °C or K.
        """
        if t < 0:
            raise ValueError("Time cannot be negative.")
        return T_inf + (T0 - T_inf) * math.exp(-self.cooling_constant * t)

    def time_to_cool(self, T_target: float, T0: float, T_inf: float) -> float:
        """
        Calculates time in seconds to cool (or warm) from T0 to T_target.
        t = - (1 / C) * ln( (T_target - T_inf) / (T0 - T_inf) )
        
        Args:
            T_target: Target temperature of the object in °C or K.
            T0: Initial temperature of the object in °C or K.
            T_inf: Ambient/fluid temperature in °C or K.
        """
        if T0 == T_inf:
            if T_target == T0:
                return 0.0
            raise ValueError("Object is already at ambient temperature; it cannot reach a different target temperature without external heat input.")
            
        ratio = (T_target - T_inf) / (T0 - T_inf)
        
        # Physical boundary checks:
        # 1. Target cannot overshoot ambient (it approaches asymptotically)
        # 2. Temperature change must be in the correct physical direction
        if ratio <= 0:
            raise ValueError("Target temperature cannot be reached. It cannot cross or overshoot ambient temperature.")
        if ratio > 1:
            raise ValueError("Target temperature lies in the wrong direction (object would need to heat up if cooling, or cool down if heating).")
            
        return -(1.0 / self.cooling_constant) * math.log(ratio)

    def generate_cooling_curve(self, T0: float, T_inf: float, duration_sec: float, num_points: int = 100) -> List[Tuple[float, float]]:
        """
        Generates temperature vs time data points for the cooling process.
        
        Args:
            T0: Initial temperature.
            T_inf: Ambient temperature.
            duration_sec: Total duration to simulate in seconds. Must be positive.
            num_points: Number of data points to generate.
            
        Returns:
            A list of (time_seconds, temperature) tuples.
        """
        if duration_sec <= 0:
            raise ValueError("Duration must be positive.")
        if num_points < 2:
            raise ValueError("Number of points must be at least 2.")
            
        curve = []
        dt = duration_sec / (num_points - 1)
        for i in range(num_points):
            t = i * dt
            temp = self.temperature_at_time(t, T0, T_inf)
            curve.append((t, temp))
        return curve
