from PyQt6.QtWidgets import QDialog, QApplication

from motorlib.properties import PropertyCollection, FloatProperty, StringProperty, EnumProperty
from ..converter import Exporter

from ..views.EngExporter_ui import Ui_EngExporterDialog
from motorlib.constants import maximumRefDiameter, maximumRefLength

class EngSettings(PropertyCollection):
    def __init__(self):
        super().__init__()
        self.props['diameter'] = FloatProperty('Motor Diameter', 'm', 0, maximumRefDiameter)
        self.props['length'] = FloatProperty('Motor Length', 'm', 0, maximumRefLength)
        self.props['hardwareMass'] = FloatProperty('Hardware Mass', 'kg', 0, 10000)
        self.props['designation'] = StringProperty('Motor Designation')
        self.props['manufacturer'] = StringProperty('Motor Manufacturer')
        self.props['append'] = EnumProperty('Existing File', ['Append', 'Overwrite'])


class EngExportMenu(QDialog):
    def __init__(self, exporter):
        QDialog.__init__(self)
        self.ui = Ui_EngExporterDialog()
        self.ui.setupUi(self)

        self.setWindowIcon(QApplication.instance().icon)

        self.exporter = exporter

    def exec(self):
        newSettings = EngSettings()
        designation = self.exporter.manager.simRes.getDesignation()
        newSettings.setProperties({'designation': designation})
        motor = self.exporter.manager.simRes.motor
        # Pre-populate hardware mass from motor's assigned hardware if available
        hwWeight = motor.getHardwareWeight()
        if hwWeight > 0:
            newSettings.setProperties({'hardwareMass': hwWeight})
        # Pre-populate motor diameter and length from hardware case catalog data
        if motor.hardwareCase is not None:
            caseDia = motor.hardwareCase.get('motorDiameter', 0)
            if caseDia > 0:
                newSettings.setProperties({'diameter': caseDia / 1000.0})
            caseLen = motor.hardwareCase.get('motorLength', 0)
            if caseLen > 0:
                newSettings.setProperties({'length': caseLen / 1000.0})
        else:
            # Fallback to grain dimensions if no hardware case assigned
            if motor.grains:
                grainDiameter = max(g.getProperty('diameter') for g in motor.grains)
                if grainDiameter > 0:
                    newSettings.setProperties({'diameter': grainDiameter})
                totalLength = sum(g.getProperty('length') for g in motor.grains)
                if totalLength > 0:
                    newSettings.setProperties({'length': totalLength})
        self.ui.motorStats.setPreferences(self.exporter.manager.preferences)
        self.ui.motorStats.loadProperties(newSettings)
        if super().exec():
            return self.ui.motorStats.getProperties()
        return None


class EngExporter(Exporter):
    def __init__(self, manager):
        super().__init__(manager, 'ENG File',
            'Exports the results of a simulation in the RASP ENG format', {'.eng': 'RASP Files'}, False)
        self.menu = EngExportMenu(self)
        self.reqNotMet = "Must have run a simulation to export a .ENG file."

    def doConversion(self, path, config):
        mode = 'a' if config['append'] == 'Append' else 'w'
        with open(path, mode) as outFile:
            propMass = self.manager.simRes.getPropellantMass()
            contents = ' '.join([config['designation'],
                                 str(round(config['diameter'] * 1000, 6)),
                                 str(round(config['length'] * 1000, 6)),
                                 'P',
                                 str(round(propMass, 6)),
                                 str(round(propMass + config['hardwareMass'], 6)),
                                 config['manufacturer']
                                 ]) + '\n'

            timeData = self.manager.simRes.channels['time'].getData()
            forceData = self.manager.simRes.channels['force'].getData()
            # Add on a 0-thrust datapoint right after the burn to satisfy RAS Aero
            if forceData[-1] != 0:
                timeData.append(self.manager.simRes.getBurnTime() + 0.01)
                forceData.append(0)
            for time, force in zip(timeData, forceData):
                if time == 0: # Increase the first point so it isn't 0 thrust
                    force += 0.01
                contents += str(round(time, 4)) + ' ' + str(round(force, 4)) + '\n'

            contents += ';\n;\n'

            outFile.write(contents)

    def checkRequirements(self):
        return self.manager.simRes is not None
