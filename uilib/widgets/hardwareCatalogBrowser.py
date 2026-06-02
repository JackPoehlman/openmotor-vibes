"""Hardware catalog browser dialog for motor cases and nozzles."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QLabel, QHeaderView, QGroupBox, QTabWidget,
                              QWidget, QApplication)
from PyQt6.QtCore import Qt

from motorlib.hardwareCatalog import HardwareCatalog


class HardwareCatalogBrowser(QDialog):
    """Dialog for browsing motor case hardware and nozzles, and assigning them to a motor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hardware Catalog — AeroTech RMS")
        self.setMinimumSize(800, 550)
        self.setWindowIcon(QApplication.instance().icon)

        self.catalog = HardwareCatalog()
        self.catalog.loadCatalog()
        self.catalog.updateFromThrustCurveData()

        self.selectedCase = None
        self.selectedNozzle = None

        self._buildUI()
        self._populateFilters()
        self._updateCaseTable()
        self._updateNozzleTable()

    def _buildUI(self):
        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        # Cases tab
        casesWidget = QWidget()
        casesLayout = QVBoxLayout()

        caseFilterLayout = QHBoxLayout()
        caseFilterLayout.addWidget(QLabel("Diameter:"))
        self.comboCaseDiameter = QComboBox()
        self.comboCaseDiameter.currentIndexChanged.connect(self._updateCaseTable)
        caseFilterLayout.addWidget(self.comboCaseDiameter)
        caseFilterLayout.addStretch()
        casesLayout.addLayout(caseFilterLayout)

        self.caseTable = QTableWidget()
        self.caseTable.setColumnCount(5)
        self.caseTable.setHorizontalHeaderLabels([
            "Designation", "Diameter\n(mm)", "Max Impulse\n(Ns)", "Max\nGrains",
            "Hardware\nWeight (g)"
        ])
        self.caseTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.caseTable.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.caseTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.caseTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.caseTable.itemSelectionChanged.connect(self._onCaseSelectionChanged)
        casesLayout.addWidget(self.caseTable)

        self.caseDetailLabel = QLabel("Select a case to see details")
        casesLayout.addWidget(self.caseDetailLabel)

        casesWidget.setLayout(casesLayout)
        self.tabs.addTab(casesWidget, "Motor Cases")

        # Nozzles tab
        nozzlesWidget = QWidget()
        nozzlesLayout = QVBoxLayout()

        nozzleFilterLayout = QHBoxLayout()
        nozzleFilterLayout.addWidget(QLabel("Diameter:"))
        self.comboNozzleDiameter = QComboBox()
        self.comboNozzleDiameter.currentIndexChanged.connect(self._updateNozzleTable)
        nozzleFilterLayout.addWidget(self.comboNozzleDiameter)
        nozzleFilterLayout.addStretch()
        nozzlesLayout.addLayout(nozzleFilterLayout)

        self.nozzleTable = QTableWidget()
        self.nozzleTable.setColumnCount(5)
        self.nozzleTable.setHorizontalHeaderLabels([
            "Part Number", "Description", "Throat\n(in)", "Exit\n(in)", "Weight\n(g)"
        ])
        self.nozzleTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.nozzleTable.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.nozzleTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        nHeader = self.nozzleTable.horizontalHeader()
        nHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        nHeader.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in range(2, 5):
            nHeader.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.nozzleTable.itemSelectionChanged.connect(self._onNozzleSelectionChanged)
        nozzlesLayout.addWidget(self.nozzleTable)

        self.nozzleDetailLabel = QLabel("Select a nozzle to see details")
        nozzlesLayout.addWidget(self.nozzleDetailLabel)

        nozzlesWidget.setLayout(nozzlesLayout)
        self.tabs.addTab(nozzlesWidget, "Nozzles")

        layout.addWidget(self.tabs)

        # Bottom buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        self.assignButton = QPushButton("Assign to Motor")
        self.assignButton.setEnabled(False)
        self.assignButton.pressed.connect(self.accept)
        buttonLayout.addWidget(self.assignButton)
        cancelButton = QPushButton("Cancel")
        cancelButton.pressed.connect(self.reject)
        buttonLayout.addWidget(cancelButton)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def _populateFilters(self):
        self.comboCaseDiameter.addItem("All")
        self.comboNozzleDiameter.addItem("All")
        for d in self.catalog.getCaseDiameters():
            self.comboCaseDiameter.addItem(f"{d}mm", d)
            self.comboNozzleDiameter.addItem(f"{d}mm", d)

    def _updateCaseTable(self):
        diameter = self.comboCaseDiameter.currentData()
        cases = self.catalog.getCases(diameter=diameter)

        self.caseTable.setRowCount(len(cases))
        self._currentCases = cases

        for row, case in enumerate(cases):
            self.caseTable.setItem(row, 0, QTableWidgetItem(case.designation))
            self.caseTable.setItem(row, 1, QTableWidgetItem(str(case.diameter)))
            self.caseTable.setItem(row, 2, QTableWidgetItem(str(case.maxTotalImpulse)))
            self.caseTable.setItem(row, 3, QTableWidgetItem(str(case.maxGrains)))
            weight_str = f"{case.hardwareWeightG:.0f}" if case.hardwareWeightG else "—"
            self.caseTable.setItem(row, 4, QTableWidgetItem(weight_str))

        self.selectedCase = None
        self._updateAssignButton()

    def _updateNozzleTable(self):
        diameter = self.comboNozzleDiameter.currentData()
        nozzles = self.catalog.getNozzles(diameter=diameter)

        self.nozzleTable.setRowCount(len(nozzles))
        self._currentNozzles = nozzles

        for row, nozzle in enumerate(nozzles):
            self.nozzleTable.setItem(row, 0, QTableWidgetItem(nozzle.partNumber))
            self.nozzleTable.setItem(row, 1, QTableWidgetItem(nozzle.description))
            throat_in = nozzle.throatDiameter / 0.0254
            self.nozzleTable.setItem(row, 2, QTableWidgetItem(f"{throat_in:.3f}"))
            if nozzle.exitDiameter:
                exit_in = nozzle.exitDiameter / 0.0254
                self.nozzleTable.setItem(row, 3, QTableWidgetItem(f"{exit_in:.3f}"))
            else:
                self.nozzleTable.setItem(row, 3, QTableWidgetItem("—"))
            if nozzle.weight:
                self.nozzleTable.setItem(row, 4, QTableWidgetItem(f"{nozzle.weight * 1000:.0f}"))
            else:
                self.nozzleTable.setItem(row, 4, QTableWidgetItem("—"))

        self.selectedNozzle = None
        self._updateAssignButton()

    def _onCaseSelectionChanged(self):
        rows = self.caseTable.selectionModel().selectedRows()
        if rows:
            idx = rows[0].row()
            self.selectedCase = self._currentCases[idx]
            nozzles = ", ".join(self.selectedCase.compatibleNozzles[:4])
            if len(self.selectedCase.compatibleNozzles) > 4:
                nozzles += "..."
            self.caseDetailLabel.setText(
                f"Compatible nozzles: {nozzles} | Type: {self.selectedCase.type}")
        else:
            self.selectedCase = None
            self.caseDetailLabel.setText("Select a case to see details")
        self._updateAssignButton()

    def _onNozzleSelectionChanged(self):
        rows = self.nozzleTable.selectionModel().selectedRows()
        if rows:
            idx = rows[0].row()
            self.selectedNozzle = self._currentNozzles[idx]
            self.nozzleDetailLabel.setText(
                f"Material: {self.selectedNozzle.material} | "
                f"Motor diameter: {self.selectedNozzle.motorDiameter}mm")
        else:
            self.selectedNozzle = None
            self.nozzleDetailLabel.setText("Select a nozzle to see details")
        self._updateAssignButton()

    def _updateAssignButton(self):
        self.assignButton.setEnabled(self.selectedCase is not None or self.selectedNozzle is not None)

    def getSelectedCase(self):
        """Return the selected MotorCase, or None."""
        return self.selectedCase

    def getSelectedNozzle(self):
        """Return the selected NozzleHardware, or None."""
        return self.selectedNozzle
