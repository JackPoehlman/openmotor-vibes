from PyQt6.QtWidgets import QDialog, QApplication

from ..converter import Exporter

from ..views.CSVExporter_ui import Ui_CSVExporter

class CsvExportMenu(QDialog):
    def __init__(self, converter):
        QDialog.__init__(self)
        self.ui = Ui_CSVExporter()
        self.ui.setupUi(self)

        self.setWindowIcon(QApplication.instance().icon)

        self.converter = converter

    def exec(self):
        self.ui.channelSelector.resetChecks()
        self.ui.channelSelector.setupChecks(True, disabled=["time"], default=["time"])
        self.ui.grainSelector.resetChecks()
        self.ui.grainSelector.setupChecks(len(self.converter.manager.simRes.motor.grains), True)
        if super().exec():
            return [self.ui.channelSelector.getUnselectedChannels(), self.ui.grainSelector.getUnselectedGrains()]
        return None


class CsvExporter(Exporter):
    def __init__(self, manager):
        super().__init__(manager, 'CSV File',
            'Exports the results of a simulation in a csv.', {'.csv': 'Comma separated value file'})
        self.menu = CsvExportMenu(self)
        self.reqNotMet = "Must have run a simulation to export a .CSV file."

    def doConversion(self, path, config):
        with open(path, 'w') as outFile:
            csvContent = self.manager.simRes.getCSV(self.manager.preferences, config[0], config[1])
            # Append hardware info as a comment block at the end
            motor = self.manager.simRes.motor
            hwWeight = motor.getHardwareWeight()
            if hwWeight > 0:
                csvContent += "\n# Hardware Information\n"
                if motor.hardwareCase is not None:
                    csvContent += "# Case: {}\n".format(motor.hardwareCase.get("designation", ""))
                    csvContent += "# Case Weight: {:.1f} g\n".format(
                        motor.hardwareCase.get("hardwareWeightKg", 0) * 1000)
                if motor.hardwareNozzle is not None:
                    csvContent += "# Nozzle: {}\n".format(motor.hardwareNozzle.get("partNumber", ""))
                    csvContent += "# Nozzle Weight: {:.1f} g\n".format(
                        motor.hardwareNozzle.get("weightKg", 0) * 1000)
                csvContent += "# Total Hardware Weight: {:.1f} g\n".format(hwWeight * 1000)
                propMass = self.manager.simRes.getPropellantMass()
                csvContent += "# Total Motor Weight: {:.1f} g\n".format((propMass + hwWeight) * 1000)
            outFile.write(csvContent)

    def checkRequirements(self):
        return self.manager.simRes is not None
