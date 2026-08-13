import unittest
import math
from engineering import Fluid, Pipe, Conduction, Cooling

class TestEngineeringCalculations(unittest.TestCase):
    """
    Unit tests to verify physical and thermodynamic calculations
    against hand-calculated/analytical solutions.
    """

    def setUp(self):
        # Set up a standard water fluid
        self.water = Fluid.get_standard_fluid("Water")

    def test_fluid_properties(self):
        """Verify fluid property retrieval and validation."""
        self.assertEqual(self.water.name, "Water")
        self.assertAlmostEqual(self.water.density, 998.2)
        self.assertAlmostEqual(self.water.viscosity, 0.001002)

        # Verify invalid input raises errors
        with self.assertRaises(ValueError):
            Fluid("BadFluid", -10, 0.001)
        with self.assertRaises(ValueError):
            Fluid("BadFluid", 1000, -0.001)

    def test_pipe_flow_turbulent(self):
        """
        Verify pipe flow calculations in the turbulent regime.
        Hand-calculation validation:
        - Fluid: Water (density=998.2, viscosity=0.001002)
        - D = 0.05 m, L = 100 m, roughness = 0.00015 m
        - Flow Rate Q = 0.004 m^3/s (4.0 L/s)
        Calculated outputs:
        - Area = 0.0019635 m^2
        - Velocity = 2.03718 m/s
        - Re = (998.2 * 2.03718 * 0.05) / 0.001002 = 101469.7
        - Haaland f = 0.02715
        - Colebrook-White converged f = 0.0275
        - Pressure Drop = f * (L/D) * (rho * v^2 / 2) = 113941.7 Pa
        """
        pipe = Pipe(diameter=0.05, length=100.0, roughness=0.00015, fluid=self.water)
        flow_rate = 0.004
        
        velocity = pipe.calculate_velocity(flow_rate)
        re = pipe.calculate_reynolds_number(flow_rate)
        f = pipe.calculate_friction_factor(flow_rate)
        dp = pipe.calculate_pressure_drop(flow_rate)

        expected_area = (math.pi * 0.05**2) / 4.0
        self.assertAlmostEqual(velocity, flow_rate / expected_area, places=4)
        self.assertAlmostEqual(re, (998.2 * velocity * 0.05) / 0.001002, places=1)
        
        # Friction factor should be around 0.0275 (turbulent Colebrook solution)
        self.assertAlmostEqual(f, 0.02747, places=4)
        
        # Pressure drop
        expected_dp = f * (100.0 / 0.05) * (998.2 * velocity**2 / 2.0)
        self.assertAlmostEqual(dp, expected_dp, places=1)

    def test_pipe_flow_laminar(self):
        """
        Verify pipe flow calculations in the laminar regime.
        Hand-calculation validation:
        - Fluid: Water
        - D = 0.05 m, L = 100 m, roughness = 0.0000015 m
        - Flow Rate Q = 0.00004 m^3/s (0.04 L/s)
        Calculated outputs:
        - Velocity = 0.02037 m/s
        - Re = 1014.7 (Laminar, since < 2300)
        - f = 64 / Re = 0.06307
        - Pressure Drop = 26.11 Pa
        """
        pipe = Pipe(diameter=0.05, length=100.0, roughness=0.0000015, fluid=self.water)
        flow_rate = 0.00004
        
        velocity = pipe.calculate_velocity(flow_rate)
        re = pipe.calculate_reynolds_number(flow_rate)
        f = pipe.calculate_friction_factor(flow_rate)
        dp = pipe.calculate_pressure_drop(flow_rate)

        self.assertTrue(re < 2300)
        self.assertAlmostEqual(re, 1014.7, places=1)
        self.assertAlmostEqual(f, 64.0 / re, places=5)
        self.assertAlmostEqual(dp, 26.11, places=1)

    def test_conduction_steady_state(self):
        """
        Verify steady-state 1D heat conduction calculations.
        Hand-calculation validation:
        - Conductivity k = 1.5 W/(m*K) (concrete)
        - Thickness L = 0.2 m (200 mm)
        - Area A = 10 m^2
        - T1 = 25°C, T2 = 15°C
        Calculated outputs:
        - heat flux q = 1.5 * (25 - 15) / 0.2 = 75 W/m^2
        - heat flow rate Q = 75 * 10 = 750 W
        """
        cond = Conduction(thermal_conductivity=1.5, thickness=0.2, area=10.0)
        q = cond.calculate_heat_flux(25.0, 15.0)
        Q = cond.calculate_heat_flow_rate(25.0, 15.0)

        self.assertEqual(q, 75.0)
        self.assertEqual(Q, 750.0)

        # Verification of negative heat flux (reverse temperature gradient)
        q_rev = cond.calculate_heat_flux(15.0, 25.0)
        self.assertEqual(q_rev, -75.0)

    def test_newtons_cooling_law(self):
        """
        Verify transient heat transfer (Newton's Law of Cooling).
        Hand-calculation validation:
        - h = 25 W/(m^2*K)
        - Area = 0.1 m^2
        - mass = 5.0 kg
        - Cp = 450 J/(kg*K)
        - T0 = 80°C, T_inf = 20°C, T_target = 40°C
        Calculated outputs:
        - cooling constant C = (25 * 0.1) / (5 * 450) = 0.001111 s^-1
        - Time to cool t = -1/C * ln( (40-20)/(80-20) ) = -900 * ln(1/3) = 988.75 seconds
        """
        cooling = Cooling(h=25.0, area=0.1, mass=5.0, specific_heat=450.0)
        
        c = cooling.cooling_constant
        self.assertAlmostEqual(c, 0.001111, places=6)

        t_target = 40.0
        t_cool = cooling.time_to_cool(t_target, T0=80.0, T_inf=20.0)
        self.assertAlmostEqual(t_cool, 988.75, places=2)

        # Temperature at target time should be very close to T_target
        temp_at_t = cooling.temperature_at_time(t_cool, T0=80.0, T_inf=20.0)
        self.assertAlmostEqual(temp_at_t, t_target, places=4)

        # Test boundary and validation exceptions
        with self.assertRaises(ValueError):
            # Target temperature cannot cross ambient
            cooling.time_to_cool(15.0, T0=80.0, T_inf=20.0)
        with self.assertRaises(ValueError):
            # Target temperature in wrong direction (object cannot cool to a higher temp)
            cooling.time_to_cool(90.0, T0=80.0, T_inf=20.0)

    def test_cooling_constant_direct(self):
        """Verify that direct cooling constant initialization works as expected."""
        cooling = Cooling(cooling_constant=0.002)
        self.assertEqual(cooling.cooling_constant, 0.002)
        
        # Verify it computes temperature correctly
        # T(100) = 20 + (80 - 20) * e^(-0.002 * 100) = 20 + 60 * e^(-0.2) = 20 + 60 * 0.81873 = 69.12°C
        temp = cooling.temperature_at_time(100.0, T0=80.0, T_inf=20.0)
        self.assertAlmostEqual(temp, 69.1238, places=4)

if __name__ == "__main__":
    unittest.main()
