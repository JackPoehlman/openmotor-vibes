"""Grain preset picker dialog for selecting and editing standard grain configurations."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QLabel, QHeaderView, QGroupBox, QApplication,
                              QFormLayout, QDoubleSpinBox, QLineEdit,
                              QMessageBox)
from PyQt6.QtCore import Qt

from motorlib.grainPresets import GrainPresetLibrary, GrainPreset


class GrainPresetEditorDialog(QDialog):
    """Dialog for adding or editing a single grain preset."""

    def __init__(self, parent=None, preset=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Grain Preset" if preset else "New Grain Preset")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.nameEdit = QLineEdit()
        form.addRow("Name:", self.nameEdit)

        self.propTypeEdit = QLineEdit()
        form.addRow("Propellant Type:", self.propTypeEdit)

        self.motorDiameterSpin = QDoubleSpinBox()
        self.motorDiameterSpin.setRange(1, 200)
        self.motorDiameterSpin.setDecimals(0)
        self.motorDiameterSpin.setSuffix(" mm")
        form.addRow("Motor Diameter:", self.motorDiameterSpin)

        self.outerDiameterSpin = QDoubleSpinBox()
        self.outerDiameterSpin.setRange(0.001, 10)
        self.outerDiameterSpin.setDecimals(4)
        self.outerDiameterSpin.setSuffix(" in")
        form.addRow("Outer Diameter:", self.outerDiameterSpin)

        self.coreDiameterSpin = QDoubleSpinBox()
        self.coreDiameterSpin.setRange(0, 10)
        self.coreDiameterSpin.setDecimals(4)
        self.coreDiameterSpin.setSuffix(" in")
        form.addRow("Core Diameter:", self.coreDiameterSpin)

        self.lengthSpin = QDoubleSpinBox()
        self.lengthSpin.setRange(0.001, 100)
        self.lengthSpin.setDecimals(3)
        self.lengthSpin.setSuffix(" in")
        form.addRow("Length:", self.lengthSpin)

        self.massSpin = QDoubleSpinBox()
        self.massSpin.setRange(0, 50000)
        self.massSpin.setDecimals(1)
        self.massSpin.setSuffix(" g")
        form.addRow("Propellant Mass:", self.massSpin)

        self.grainTypeEdit = QLineEdit()
        self.grainTypeEdit.setText("BATES")
        form.addRow("Grain Type:", self.grainTypeEdit)

        self.systemEdit = QLineEdit()
        self.systemEdit.setText("RMS")
        form.addRow("System:", self.systemEdit)

        self.castingTubePNEdit = QLineEdit()
        form.addRow("Casting Tube P/N:", self.castingTubePNEdit)

        layout.addLayout(form)

        # Buttons
        btnLayout = QHBoxLayout()
        btnLayout.addStretch()
        saveBtn = QPushButton("Save")
        saveBtn.pressed.connect(self.accept)
        btnLayout.addWidget(saveBtn)
        cancelBtn = QPushButton("Cancel")
        cancelBtn.pressed.connect(self.reject)
        btnLayout.addWidget(cancelBtn)
        layout.addLayout(btnLayout)

        self.setLayout(layout)

        if preset:
            self._loadPreset(preset)

    def _loadPreset(self, p):
        self.nameEdit.setText(p.name)
        self.propTypeEdit.setText(p.propellantType)
        self.motorDiameterSpin.setValue(p.motorDiameter)
        self.outerDiameterSpin.setValue(p.outerDiameter / 0.0254)
        self.coreDiameterSpin.setValue((p.coreDiameter or 0) / 0.0254)
        self.lengthSpin.setValue(p.length / 0.0254)
        self.massSpin.setValue(p.propellantMass * 1000)
        self.grainTypeEdit.setText(p.grainType)
        self.systemEdit.setText(p.system)
        self.castingTubePNEdit.setText(p.castingTubePN or "")

    def getPresetDict(self):
        return {
            "name": self.nameEdit.text(),
            "propellantType": self.propTypeEdit.text(),
            "motorDiameter": int(self.motorDiameterSpin.value()),
            "outerDiameter": self.outerDiameterSpin.value() * 0.0254,
            "innerDiameter": 0,
            "coreDiameter": self.coreDiameterSpin.value() * 0.0254 if self.coreDiameterSpin.value() > 0 else None,
            "length": self.lengthSpin.value() * 0.0254,
            "propellantMass": self.massSpin.value() / 1000,
            "castingTubePN": self.castingTubePNEdit.text(),
            "linerPN": None,
            "compatibleCases": [],
            "grainType": self.grainTypeEdit.text(),
            "system": self.systemEdit.text(),
            "source": "user",
        }


class GrainPresetPicker(QDialog):
    """Dialog for browsing and selecting grain presets to apply to a grain."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grain Presets — AeroTech RMS/DMS")
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QApplication.instance().icon)

        self.library = GrainPresetLibrary()
        self.library.loadPresets()
        self.selectedPreset = None

        self._buildUI()
        self._populateFilters()
        self._updateTable()

    def _buildUI(self):
        layout = QVBoxLayout()

        # Filter bar
        filterGroup = QGroupBox("Filters")
        filterLayout = QHBoxLayout()

        filterLayout.addWidget(QLabel("Diameter:"))
        self.comboDiameter = QComboBox()
        self.comboDiameter.currentIndexChanged.connect(self._updateTable)
        filterLayout.addWidget(self.comboDiameter)

        filterLayout.addWidget(QLabel("Propellant:"))
        self.comboPropellant = QComboBox()
        self.comboPropellant.currentIndexChanged.connect(self._updateTable)
        filterLayout.addWidget(self.comboPropellant)

        filterLayout.addWidget(QLabel("System:"))
        self.comboSystem = QComboBox()
        self.comboSystem.currentIndexChanged.connect(self._updateTable)
        filterLayout.addWidget(self.comboSystem)

        filterGroup.setLayout(filterLayout)
        layout.addWidget(filterGroup)

        # Preset table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Propellant", "Diameter\n(mm)", "OD\n(in)", "Length\n(in)",
            "Mass\n(g)", "Grain Type"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self._onSelectionChanged)
        self.table.doubleClicked.connect(self.accept)
        layout.addWidget(self.table)

        # Detail label
        self.detailLabel = QLabel("Select a preset to see details")
        layout.addWidget(self.detailLabel)

        # Buttons
        buttonLayout = QHBoxLayout()

        self.addButton = QPushButton("Add New...")
        self.addButton.pressed.connect(self._addPreset)
        buttonLayout.addWidget(self.addButton)

        self.editButton = QPushButton("Edit...")
        self.editButton.setEnabled(False)
        self.editButton.pressed.connect(self._editPreset)
        buttonLayout.addWidget(self.editButton)

        self.deleteButton = QPushButton("Delete")
        self.deleteButton.setEnabled(False)
        self.deleteButton.pressed.connect(self._deletePreset)
        buttonLayout.addWidget(self.deleteButton)

        buttonLayout.addStretch()
        self.applyButton = QPushButton("Apply")
        self.applyButton.setEnabled(False)
        self.applyButton.pressed.connect(self.accept)
        buttonLayout.addWidget(self.applyButton)
        cancelButton = QPushButton("Cancel")
        cancelButton.pressed.connect(self.reject)
        buttonLayout.addWidget(cancelButton)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def _updateTable(self):
        diameter = self.comboDiameter.currentData()
        propellant = self.comboPropellant.currentData()
        system = self.comboSystem.currentData()

        presets = self.library.getPresets(
            diameter=diameter,
            propellantType=propellant,
            system=system
        )

        self.table.setRowCount(len(presets))
        self._currentPresets = presets

        for row, preset in enumerate(presets):
            self.table.setItem(row, 0, QTableWidgetItem(preset.name))
            self.table.setItem(row, 1, QTableWidgetItem(preset.propellantType))
            self.table.setItem(row, 2, QTableWidgetItem(str(preset.motorDiameter)))

            od_in = preset.outerDiameter / 0.0254
            self.table.setItem(row, 3, QTableWidgetItem(f"{od_in:.3f}"))

            len_in = preset.length / 0.0254
            self.table.setItem(row, 4, QTableWidgetItem(f"{len_in:.2f}"))

            mass_g = preset.propellantMass * 1000
            self.table.setItem(row, 5, QTableWidgetItem(f"{mass_g:.0f}"))

            self.table.setItem(row, 6, QTableWidgetItem(preset.grainType))

        self.selectedPreset = None
        self.applyButton.setEnabled(False)

    def _onSelectionChanged(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            idx = rows[0].row()
            self.selectedPreset = self._currentPresets[idx]
            self.applyButton.setEnabled(True)
            self.editButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
            p = self.selectedPreset
            cases = ", ".join(p.compatibleCases[:3])
            if len(p.compatibleCases) > 3:
                cases += f" (+{len(p.compatibleCases) - 3} more)"
            detail = (f"Casting tube: {p.castingTubePN}"
                      f" | Compatible cases: {cases}"
                      f" | System: {p.system}")
            if p.linerPN:
                detail += f" | Liner: {p.linerPN}"
            self.detailLabel.setText(detail)
        else:
            self.selectedPreset = None
            self.applyButton.setEnabled(False)
            self.editButton.setEnabled(False)
            self.deleteButton.setEnabled(False)
            self.detailLabel.setText("Select a preset to see details")

    def _addPreset(self):
        dlg = GrainPresetEditorDialog(self)
        if dlg.exec():
            newPreset = GrainPreset(dlg.getPresetDict())
            self.library.addPreset(newPreset)
            self.library.savePresets()
            self._populateFilters()
            self._updateTable()

    def _editPreset(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        tableIdx = rows[0].row()
        preset = self._currentPresets[tableIdx]
        # Find the index in the full library
        libIdx = self.library.presets.index(preset)
        dlg = GrainPresetEditorDialog(self, preset)
        if dlg.exec():
            updated = GrainPreset(dlg.getPresetDict())
            # Preserve fields the editor doesn't expose
            updated.compatibleCases = preset.compatibleCases
            updated.linerPN = preset.linerPN
            updated.innerDiameter = preset.innerDiameter
            self.library.updatePreset(libIdx, updated)
            self.library.savePresets()
            self._updateTable()

    def _deletePreset(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        tableIdx = rows[0].row()
        preset = self._currentPresets[tableIdx]
        reply = QMessageBox.question(self, "Delete Preset",
            f"Delete grain preset '{preset.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            libIdx = self.library.presets.index(preset)
            self.library.deletePreset(libIdx)
            self.library.savePresets()
            self._updateTable()

    def _populateFilters(self):
        """Repopulate filter combos from current library state."""
        self.comboDiameter.blockSignals(True)
        self.comboPropellant.blockSignals(True)
        self.comboSystem.blockSignals(True)

        prevDiam = self.comboDiameter.currentData()
        prevProp = self.comboPropellant.currentData()
        prevSys = self.comboSystem.currentData()

        self.comboDiameter.clear()
        self.comboDiameter.addItem("All")
        for d in self.library.getDiameters():
            self.comboDiameter.addItem(f"{d}mm", d)
        if prevDiam is not None:
            idx = self.comboDiameter.findData(prevDiam)
            if idx >= 0:
                self.comboDiameter.setCurrentIndex(idx)

        self.comboPropellant.clear()
        self.comboPropellant.addItem("All")
        for p in self.library.getPropellantTypes():
            self.comboPropellant.addItem(p, p)
        if prevProp is not None:
            idx = self.comboPropellant.findData(prevProp)
            if idx >= 0:
                self.comboPropellant.setCurrentIndex(idx)

        self.comboSystem.clear()
        self.comboSystem.addItem("All")
        for s in self.library.getSystems():
            self.comboSystem.addItem(s, s)
        if prevSys is not None:
            idx = self.comboSystem.findData(prevSys)
            if idx >= 0:
                self.comboSystem.setCurrentIndex(idx)

        self.comboDiameter.blockSignals(False)
        self.comboPropellant.blockSignals(False)
        self.comboSystem.blockSignals(False)

    def getSelectedPreset(self):
        """Return the selected GrainPreset, or None."""
        return self.selectedPreset
