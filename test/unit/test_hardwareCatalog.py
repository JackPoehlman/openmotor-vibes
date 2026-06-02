import unittest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from motorlib.hardwareCatalog import MotorCase, NozzleHardware, HardwareCatalog


class TestMotorCase(unittest.TestCase):

    def test_case_creation(self):
        data = {
            "designation": "RMS-54/1706",
            "type": "RMS",
            "diameter": 54,
            "maxTotalImpulse": 1706,
            "maxGrains": 4,
            "hardwareWeightG": 598.0,
            "compatibleNozzles": ["54mm-313", "54mm-455"],
        }
        case = MotorCase(data)
        self.assertEqual(case.designation, "RMS-54/1706")
        self.assertEqual(case.diameter, 54)
        self.assertEqual(case.maxGrains, 4)
        self.assertAlmostEqual(case.hardwareWeightG, 598.0)

    def test_case_weight_kg(self):
        case = MotorCase({"hardwareWeightG": 598.0})
        self.assertAlmostEqual(case.getHardwareWeightKg(), 0.598)

    def test_case_weight_kg_none(self):
        case = MotorCase({"hardwareWeightG": None})
        self.assertEqual(case.getHardwareWeightKg(), 0)

    def test_case_display_string(self):
        data = {
            "designation": "RMS-54/1706",
            "diameter": 54,
            "maxGrains": 4,
            "hardwareWeightG": 598.0,
        }
        case = MotorCase(data)
        display = case.getDisplayString()
        self.assertIn("RMS-54/1706", display)
        self.assertIn("598g", display)


class TestNozzleHardware(unittest.TestCase):

    def test_nozzle_creation(self):
        data = {
            "partNumber": "54mm-313",
            "description": "54mm Nozzle, 0.313\" throat",
            "motorDiameter": 54,
            "throatDiameter": 0.007950,
            "exitDiameter": 0.020625,
            "weight": 0.055,
            "material": "glass/phenolic",
        }
        nozzle = NozzleHardware(data)
        self.assertEqual(nozzle.partNumber, "54mm-313")
        self.assertEqual(nozzle.motorDiameter, 54)
        self.assertAlmostEqual(nozzle.throatDiameter, 0.007950)

    def test_nozzle_weight_kg(self):
        nozzle = NozzleHardware({"weight": 0.055})
        self.assertAlmostEqual(nozzle.getWeightKg(), 0.055)

    def test_nozzle_weight_none(self):
        nozzle = NozzleHardware({"weight": None})
        self.assertEqual(nozzle.getWeightKg(), 0)


class TestHardwareCatalog(unittest.TestCase):

    def setUp(self):
        self.catalog = HardwareCatalog()
        self.catalog.loadCatalog()

    def test_load_catalog(self):
        self.assertGreater(len(self.catalog.cases), 0)
        self.assertGreater(len(self.catalog.nozzles), 0)

    def test_get_cases_all(self):
        cases = self.catalog.getCases()
        self.assertGreater(len(cases), 0)

    def test_get_cases_by_diameter(self):
        cases_54 = self.catalog.getCases(diameter=54)
        self.assertGreater(len(cases_54), 0)
        for c in cases_54:
            self.assertEqual(c.diameter, 54)

    def test_get_case_by_designation(self):
        case = self.catalog.getCase("RMS-54/1706")
        self.assertIsNotNone(case)
        self.assertEqual(case.designation, "RMS-54/1706")
        self.assertEqual(case.diameter, 54)
        self.assertEqual(case.maxGrains, 4)

    def test_get_nozzles_by_diameter(self):
        nozzles_54 = self.catalog.getNozzles(diameter=54)
        self.assertGreater(len(nozzles_54), 0)
        for n in nozzles_54:
            self.assertEqual(n.motorDiameter, 54)

    def test_get_nozzle_by_part_number(self):
        nozzle = self.catalog.getNozzle("54mm-313")
        self.assertIsNotNone(nozzle)
        self.assertEqual(nozzle.partNumber, "54mm-313")

    def test_get_case_diameters(self):
        diameters = self.catalog.getCaseDiameters()
        self.assertIn(29, diameters)
        self.assertIn(38, diameters)
        self.assertIn(54, diameters)
        self.assertIn(75, diameters)
        self.assertIn(98, diameters)

    def test_nonexistent_case(self):
        case = self.catalog.getCase("NONEXISTENT")
        self.assertIsNone(case)

    def test_nonexistent_nozzle(self):
        nozzle = self.catalog.getNozzle("NONEXISTENT")
        self.assertIsNone(nozzle)


class TestMotorHardwareIntegration(unittest.TestCase):
    """Test that Motor class hardware fields work correctly."""

    def test_motor_hardware_default_none(self):
        import motorlib.motor
        m = motorlib.motor.Motor()
        self.assertIsNone(m.hardwareCase)
        self.assertIsNone(m.hardwareNozzle)
        self.assertEqual(m.getHardwareWeight(), 0)

    def test_motor_hardware_weight(self):
        import motorlib.motor
        m = motorlib.motor.Motor()
        m.hardwareCase = {"designation": "RMS-54/1706", "hardwareWeightKg": 0.598}
        m.hardwareNozzle = {"partNumber": "54mm-313", "weightKg": 0.055}
        self.assertAlmostEqual(m.getHardwareWeight(), 0.653)

    def test_motor_hardware_serialization(self):
        import motorlib.motor
        m = motorlib.motor.Motor()
        m.hardwareCase = {"designation": "RMS-54/1706", "hardwareWeightKg": 0.598}

        d = m.getDict()
        self.assertIn("hardwareCase", d)
        self.assertEqual(d["hardwareCase"]["designation"], "RMS-54/1706")

        m2 = motorlib.motor.Motor()
        m2.applyDict(d)
        self.assertEqual(m2.hardwareCase["designation"], "RMS-54/1706")
        self.assertAlmostEqual(m2.getHardwareWeight(), 0.598)

    def test_motor_backward_compat(self):
        """Old motor dicts without hardware fields should load fine."""
        import motorlib.motor
        old_dict = {
            "nozzle": {"throat": 0.01, "exit": 0.02, "efficiency": 0.9,
                       "divAngle": 15, "convAngle": 45, "throatLength": 0.005,
                       "slagCoeff": 0, "erosionCoeff": 0},
            "propellant": None,
            "grains": [],
            "config": {"maxPressure": 1e7, "maxMassFlux": 1500, "maxMachNumber": 0.7,
                       "minPortThroat": 2, "burnoutWebThres": 0.001,
                       "burnoutThrustThres": 0.1, "timestep": 0.03,
                       "ambPressure": 101325, "mapDim": 750, "sepPressureRatio": 0.4,
                       "flowSeparationWarnPercent": 0.05}
        }
        m = motorlib.motor.Motor(old_dict)
        self.assertIsNone(m.hardwareCase)
        self.assertIsNone(m.hardwareNozzle)
        self.assertEqual(m.getHardwareWeight(), 0)


if __name__ == "__main__":
    unittest.main()
