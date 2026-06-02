from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView

import motorlib

from ..views.PropellantPreview_ui import Ui_PropellantPreview

class PropellantPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_PropellantPreview()
        self.ui.setupUi(self)

        # Add an Ingredients tab to the preview tab widget
        self.ingredientTable = QTableWidget()
        self.ingredientTable.setColumnCount(2)
        self.ingredientTable.setHorizontalHeaderLabels(["Ingredient", "%"])
        self.ingredientTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ingredientTable.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        header = self.ingredientTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.ingredientTable.verticalHeader().setVisible(False)
        self.ui.tabWidget.addTab(self.ingredientTable, "Ingredients")

    def setPreferences(self, pref):
        self.ui.tabBurnRate.setPreferences(pref)
        self.ui.tabPressure.setPreferences(pref)

    def loadPropellant(self, propellant):
        self.ui.tabAlerts.clear()
        self.ui.tabBurnRate.cleanup()
        self.ui.tabPressure.cleanup()
        self._loadIngredients(propellant)
        alerts = propellant.getErrors()
        for err in alerts:
            self.ui.tabAlerts.addItem(err.description)

        for alert in alerts:
            if alert.level == motorlib.simResult.SimAlertLevel.ERROR:
                return

        burnrateData = [[], []]
        minPres = int(propellant.getMinimumValidPressure()) + 1 # Add 1 Pa to avoid crashing on burnrate for 0 Pa
        maxPres = int(propellant.getMaximumValidPressure())
        for pres in range(minPres, maxPres, 2000):
            burnrateData[0].append(pres)
            burnrateData[1].append(propellant.getBurnRate(pres))
        self.ui.tabBurnRate.showGraph(burnrateData)

        pressureData = [[], []]
        for kn in range(1, 750, 10):
            pressureData[0].append(kn)
            pressureData[1].append(propellant.getPressureFromKn(kn))
        self.ui.tabPressure.showGraph(pressureData)

    def _loadIngredients(self, propellant):
        """Populate the ingredients table from the propellant's data or the library."""
        self.ingredientTable.setRowCount(0)
        ingredients = getattr(propellant, 'ingredients', [])

        # If no ingredients on the propellant object, try looking up by name in the library
        if not ingredients:
            ingredients = self._lookupLibraryIngredients(propellant.getProperty('name'))

        if not ingredients:
            self.ingredientTable.setRowCount(1)
            self.ingredientTable.setItem(0, 0, QTableWidgetItem("No ingredient data available"))
            self.ingredientTable.setItem(0, 1, QTableWidgetItem(""))
            return

        self.ingredientTable.setRowCount(len(ingredients))
        for row, ing in enumerate(ingredients):
            self.ingredientTable.setItem(row, 0, QTableWidgetItem(ing.get("name", "")))
            pct = ing.get("percentage", 0)
            self.ingredientTable.setItem(row, 1, QTableWidgetItem(f"{pct:g}%"))

    def _lookupLibraryIngredients(self, propName):
        """Look up ingredient data from the bundled propellant library by name."""
        if not hasattr(self, '_libraryCache'):
            import json, os
            libPath = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "data", "propellant_library.json")
            try:
                with open(libPath, "r") as f:
                    self._libraryCache = {entry["name"]: entry.get("ingredients", []) for entry in json.load(f)}
            except Exception:
                self._libraryCache = {}
        return self._libraryCache.get(propName, [])

    def cleanup(self):
        self.ui.tabAlerts.clear()
        self.ui.tabBurnRate.cleanup()
        self.ui.tabPressure.cleanup()
        self.ingredientTable.setRowCount(0)
