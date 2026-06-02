import unittest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from motorlib.grainPresets import GrainPreset, GrainPresetLibrary


class TestGrainPreset(unittest.TestCase):

    def test_preset_creation(self):
        data = {
            "name": "Test Grain",
            "propellantType": "White Lightning",
            "motorDiameter": 54,
            "outerDiameter": 0.04763,
            "innerDiameter": 0.04572,
            "coreDiameter": None,
            "length": 0.41275,
            "propellantMass": 1.230,
            "castingTubePN": "03178L",
            "linerPN": None,
            "compatibleCases": ["RMS-54/1706"],
            "grainType": "BATES",
            "system": "RMS",
            "source": "test"
        }
        preset = GrainPreset(data)
        self.assertEqual(preset.name, "Test Grain")
        self.assertEqual(preset.motorDiameter, 54)
        self.assertAlmostEqual(preset.outerDiameter, 0.04763)
        self.assertAlmostEqual(preset.propellantMass, 1.230)
        self.assertEqual(preset.grainType, "BATES")

    def test_preset_getDict_roundtrip(self):
        data = {
            "name": "54mm WL",
            "propellantType": "White Lightning",
            "motorDiameter": 54,
            "outerDiameter": 0.04763,
            "innerDiameter": 0.04572,
            "coreDiameter": None,
            "length": 0.41275,
            "propellantMass": 1.230,
            "castingTubePN": "03178L",
            "linerPN": None,
            "compatibleCases": ["RMS-54/1706"],
            "grainType": "BATES",
            "system": "RMS",
            "source": "test"
        }
        preset = GrainPreset(data)
        result = preset.getDict()
        self.assertEqual(result["name"], "54mm WL")
        self.assertEqual(result["motorDiameter"], 54)

    def test_preset_display_string(self):
        data = {
            "name": "54mm White Lightning",
            "propellantType": "White Lightning",
            "motorDiameter": 54,
            "outerDiameter": 0.04763,
            "innerDiameter": 0.04572,
            "length": 0.41275,
            "propellantMass": 1.230,
        }
        preset = GrainPreset(data)
        display = preset.getDisplayString()
        self.assertIn("54mm White Lightning", display)
        self.assertIn("1230g", display)


class TestGrainPresetLibrary(unittest.TestCase):

    def setUp(self):
        self.library = GrainPresetLibrary()
        self.library.loadPresets()

    def test_load_presets(self):
        self.assertGreater(len(self.library.presets), 0)

    def test_filter_by_diameter(self):
        presets_54 = self.library.getPresets(diameter=54)
        self.assertGreater(len(presets_54), 0)
        for p in presets_54:
            self.assertEqual(p.motorDiameter, 54)

    def test_filter_by_propellant(self):
        presets_wl = self.library.getPresets(propellantType="White Lightning")
        self.assertGreater(len(presets_wl), 0)
        for p in presets_wl:
            self.assertEqual(p.propellantType, "White Lightning")

    def test_filter_combined(self):
        presets = self.library.getPresets(diameter=38, propellantType="Blue Thunder")
        self.assertGreater(len(presets), 0)
        for p in presets:
            self.assertEqual(p.motorDiameter, 38)
            self.assertEqual(p.propellantType, "Blue Thunder")

    def test_get_diameters(self):
        diameters = self.library.getDiameters()
        self.assertIn(29, diameters)
        self.assertIn(38, diameters)
        self.assertIn(54, diameters)
        self.assertIn(75, diameters)
        self.assertIn(98, diameters)

    def test_get_propellant_types(self):
        types = self.library.getPropellantTypes()
        self.assertIn("White Lightning", types)
        self.assertIn("Blue Thunder", types)

    def test_no_presets_for_nonexistent_diameter(self):
        presets = self.library.getPresets(diameter=999)
        self.assertEqual(len(presets), 0)


if __name__ == "__main__":
    unittest.main()
