"""Grain preset library for common commercial propellant grain configurations.

Provides a catalog of AeroTech RMS and DMS grain dimensions that can be
applied to grain objects in the motor editor, saving users from manually
entering dimensions for standard grain sizes.
"""

import json
import os


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class GrainPreset:
    """A single grain preset with dimensions and metadata."""

    def __init__(self, data):
        self.name = data.get("name", "")
        self.propellantType = data.get("propellantType", "")
        self.motorDiameter = data.get("motorDiameter", 0)
        self.outerDiameter = data.get("outerDiameter", 0)
        self.innerDiameter = data.get("innerDiameter", 0)
        self.coreDiameter = data.get("coreDiameter")
        self.length = data.get("length", 0)
        self.propellantMass = data.get("propellantMass", 0)
        self.castingTubePN = data.get("castingTubePN", "")
        self.linerPN = data.get("linerPN")
        self.compatibleCases = data.get("compatibleCases", [])
        self.grainType = data.get("grainType", "BATES")
        self.system = data.get("system", "RMS")
        self.source = data.get("source", "")

    def getDict(self):
        """Returns a serializable representation of the preset."""
        return {
            "name": self.name,
            "propellantType": self.propellantType,
            "motorDiameter": self.motorDiameter,
            "outerDiameter": self.outerDiameter,
            "innerDiameter": self.innerDiameter,
            "coreDiameter": self.coreDiameter,
            "length": self.length,
            "propellantMass": self.propellantMass,
            "castingTubePN": self.castingTubePN,
            "linerPN": self.linerPN,
            "compatibleCases": self.compatibleCases,
            "grainType": self.grainType,
            "system": self.system,
            "source": self.source,
        }

    def getDisplayString(self):
        """Returns a human-readable summary string."""
        mass_g = self.propellantMass * 1000
        od_in = self.outerDiameter / 0.0254
        length_in = self.length / 0.0254
        return f"{self.name} — OD:{od_in:.3f}\" L:{length_in:.2f}\" {mass_g:.0f}g"


class GrainPresetLibrary:
    """Manages loading and filtering of grain presets."""

    def __init__(self):
        self.presets = []

    def loadPresets(self, path=None):
        """Load grain presets from a JSON file. Uses the bundled data file by default."""
        if path is None:
            path = os.path.join(DATA_DIR, "grain_presets.json")
        if not os.path.exists(path):
            return
        with open(path, "r") as f:
            data = json.load(f)
        self.presets = [GrainPreset(entry) for entry in data]

    def getPresets(self, diameter=None, propellantType=None, system=None, grainType=None):
        """Return presets matching the given filters. None means no filter."""
        results = self.presets
        if diameter is not None:
            results = [p for p in results if p.motorDiameter == diameter]
        if propellantType is not None:
            results = [p for p in results if p.propellantType == propellantType]
        if system is not None:
            results = [p for p in results if p.system == system]
        if grainType is not None:
            results = [p for p in results if p.grainType == grainType]
        return results

    def getDiameters(self):
        """Return sorted list of unique motor diameters available."""
        return sorted(set(p.motorDiameter for p in self.presets))

    def getPropellantTypes(self):
        """Return sorted list of unique propellant types available."""
        return sorted(set(p.propellantType for p in self.presets))

    def getSystems(self):
        """Return sorted list of unique systems (RMS, DMS) available."""
        return sorted(set(p.system for p in self.presets))

    def addPreset(self, preset):
        """Add a new preset to the library."""
        self.presets.append(preset)

    def updatePreset(self, index, preset):
        """Replace the preset at the given index."""
        if 0 <= index < len(self.presets):
            self.presets[index] = preset

    def deletePreset(self, index):
        """Remove the preset at the given index."""
        if 0 <= index < len(self.presets):
            del self.presets[index]

    def savePresets(self, path=None):
        """Save the current preset library to a JSON file."""
        if path is None:
            path = os.path.join(DATA_DIR, "grain_presets.json")
        data = [p.getDict() for p in self.presets]
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def applyPreset(self, preset, grain):
        """Apply a grain preset's dimensions to a Grain instance.

        Sets the grain's diameter and length from the preset. For perforated grains,
        also sets the core diameter if the grain type supports it.
        """
        grain.setProperty("diameter", preset.outerDiameter)
        grain.setProperty("length", preset.length)

        # For BATES grains with a core, set coreDiameter
        if preset.coreDiameter is not None and hasattr(grain, 'props') and 'coreDiameter' in grain.props:
            grain.setProperty("coreDiameter", preset.coreDiameter)
