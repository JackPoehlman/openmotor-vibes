"""Hardware catalog for motor cases and nozzles.

Provides a catalog of AeroTech RMS motor case hardware and nozzle specifications.
Hardware weights can be populated from ThrustCurve.org API data or entered manually.
"""

import json
import os


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class MotorCase:
    """A motor case hardware entry with weight and compatibility info."""

    def __init__(self, data):
        self.designation = data.get("designation", "")
        self.type = data.get("type", "RMS")
        self.diameter = data.get("diameter", 0)
        self.motorDiameter = data.get("motorDiameter", 0)
        self.motorLength = data.get("motorLength", 0)
        self.maxTotalImpulse = data.get("maxTotalImpulse", 0)
        self.maxGrains = data.get("maxGrains", 0)
        self.hardwareWeightG = data.get("hardwareWeightG")
        self.compatibleNozzles = data.get("compatibleNozzles", [])
        self.assemblyDrawingRef = data.get("assemblyDrawingRef", "")

    def getDict(self):
        return {
            "designation": self.designation,
            "type": self.type,
            "diameter": self.diameter,
            "motorDiameter": self.motorDiameter,
            "motorLength": self.motorLength,
            "maxTotalImpulse": self.maxTotalImpulse,
            "maxGrains": self.maxGrains,
            "hardwareWeightG": self.hardwareWeightG,
            "compatibleNozzles": self.compatibleNozzles,
            "assemblyDrawingRef": self.assemblyDrawingRef,
        }

    def getHardwareWeightKg(self):
        """Return hardware weight in kg, or 0 if unknown."""
        if self.hardwareWeightG is not None:
            return self.hardwareWeightG / 1000.0
        return 0

    def getDisplayString(self):
        weight_str = f"{self.hardwareWeightG:.0f}g" if self.hardwareWeightG else "unknown"
        return f"{self.designation} ({self.diameter}mm, max {self.maxGrains} grains, {weight_str})"


class NozzleHardware:
    """A nozzle hardware entry with dimensions and weight."""

    def __init__(self, data):
        self.partNumber = data.get("partNumber", "")
        self.description = data.get("description", "")
        self.motorDiameter = data.get("motorDiameter", 0)
        self.outerDiameter = data.get("outerDiameter", 0)
        self.throatDiameter = data.get("throatDiameter", 0)
        self.exitDiameter = data.get("exitDiameter")
        self.weight = data.get("weight")
        self.material = data.get("material", "")

    def getDict(self):
        return {
            "partNumber": self.partNumber,
            "description": self.description,
            "motorDiameter": self.motorDiameter,
            "outerDiameter": self.outerDiameter,
            "throatDiameter": self.throatDiameter,
            "exitDiameter": self.exitDiameter,
            "weight": self.weight,
            "material": self.material,
        }

    def getWeightKg(self):
        """Return weight in kg, or 0 if unknown."""
        if self.weight is not None:
            return self.weight
        return 0

    def getDisplayString(self):
        throat_in = self.throatDiameter / 0.0254
        weight_str = f"{self.weight * 1000:.0f}g" if self.weight else "unknown"
        return f"{self.description} — throat:{throat_in:.3f}\" {weight_str}"


class HardwareCatalog:
    """Manages loading and querying of motor case and nozzle hardware data."""

    def __init__(self):
        self.cases = {}
        self.nozzles = []

    def loadCatalog(self, casePath=None, nozzlePath=None):
        """Load hardware catalog from JSON files. Uses bundled data files by default."""
        if casePath is None:
            casePath = os.path.join(DATA_DIR, "hardware_catalog.json")
        if nozzlePath is None:
            nozzlePath = os.path.join(DATA_DIR, "nozzle_presets.json")

        if os.path.exists(casePath):
            with open(casePath, "r") as f:
                data = json.load(f)
            self.cases = {k: MotorCase(v) for k, v in data.items()}

        if os.path.exists(nozzlePath):
            with open(nozzlePath, "r") as f:
                data = json.load(f)
            self.nozzles = [NozzleHardware(entry) for entry in data]

    def updateFromThrustCurveData(self, hwWeightsPath=None):
        """Update case hardware weights from ThrustCurve-derived data."""
        if hwWeightsPath is None:
            hwWeightsPath = os.path.join(DATA_DIR, "hardware_weights.json")
        if not os.path.exists(hwWeightsPath):
            return

        with open(hwWeightsPath, "r") as f:
            tc_data = json.load(f)

        for case_key, tc_info in tc_data.items():
            if case_key in self.cases and self.cases[case_key].hardwareWeightG is None:
                self.cases[case_key].hardwareWeightG = tc_info.get("avgHardwareWeightG")

    def getCases(self, diameter=None, caseType=None):
        """Return cases matching filters."""
        results = list(self.cases.values())
        if diameter is not None:
            results = [c for c in results if c.diameter == diameter]
        if caseType is not None:
            results = [c for c in results if c.type == caseType]
        return sorted(results, key=lambda c: (c.diameter, c.maxTotalImpulse))

    def getCase(self, designation):
        """Look up a case by designation string."""
        return self.cases.get(designation)

    def getNozzles(self, diameter=None):
        """Return nozzles matching filters."""
        results = self.nozzles
        if diameter is not None:
            results = [n for n in results if n.motorDiameter == diameter]
        return results

    def getNozzle(self, partNumber):
        """Look up a nozzle by part number."""
        for n in self.nozzles:
            if n.partNumber == partNumber:
                return n
        return None

    def getCaseDiameters(self):
        """Return sorted list of unique case diameters."""
        return sorted(set(c.diameter for c in self.cases.values()))

    def getCaseWeight(self, designation):
        """Return hardware weight in kg for a case designation, or 0 if unknown."""
        case = self.getCase(designation)
        if case:
            return case.getHardwareWeightKg()
        return 0

    def getFullHardwareWeight(self, caseDesignation, nozzlePartNumber=None):
        """Return total inert mass (case + nozzle) in kg."""
        weight = self.getCaseWeight(caseDesignation)
        if nozzlePartNumber:
            nozzle = self.getNozzle(nozzlePartNumber)
            if nozzle:
                weight += nozzle.getWeightKg()
        return weight
