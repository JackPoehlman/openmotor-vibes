import math

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox
from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox, QComboBox, QSlider
from PyQt6.QtCore import pyqtSignal, Qt

import motorlib

from .polygonEditor import PolygonEditor
from .tabularEditor import TabularEditor

class PropertyEditor(QWidget):

    valueChanged = pyqtSignal()

    def __init__(self, parent, prop, preferences):
        super(PropertyEditor, self).__init__(QWidget(parent))
        self.preferences = preferences
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.prop = prop

        if self.preferences is not None:
            self.dispUnit = self.preferences.getUnit(self.prop.unit)
        else:
            self.dispUnit = self.prop.unit

        if isinstance(prop, motorlib.properties.FloatProperty):
            self.editor = QDoubleSpinBox()

            self.editor.setSuffix(' {}'.format(self.dispUnit))

            convMin = motorlib.units.convert(self.prop.min, self.prop.unit, self.dispUnit)
            convMax = motorlib.units.convert(self.prop.max, self.prop.unit, self.dispUnit)
            self.editor.setRange(convMin, convMax)

            self.editor.setDecimals(8) # Large number of decimals for now while I pick a better method
            self.editor.setSingleStep(10 ** (int(math.log(convMax, 10) - 4)))

            self.editor.setValue(motorlib.units.convert(self.prop.getValue(), prop.unit, self.dispUnit))

            # Add slider for float properties — uses a local window centered on
            # the current value so the slider provides fine-grained control even
            # when the property's full min/max range is very large.
            self.slider = QSlider(Qt.Orientation.Horizontal)
            self._sliderResolution = 10000
            self._fullMin = convMin
            self._fullMax = convMax
            # Window = 10% of full range, at least 1 display-unit wide
            self._windowHalf = max((convMax - convMin) * 0.05, 0.5)
            self.slider.setRange(0, self._sliderResolution)
            self._recentreSlider(self.editor.value())

            self._updatingFromSlider = False
            self._updatingFromSpinbox = False
            self.slider.valueChanged.connect(self._sliderChanged)
            self.editor.valueChanged.connect(self._spinboxChanged)

            row = QHBoxLayout()
            row.setSpacing(6)
            row.addWidget(self.editor, 1)
            row.addWidget(self.slider, 1)
            self.layout().addLayout(row)

        elif isinstance(prop, motorlib.properties.IntProperty):
            self.editor = QSpinBox()

            convMin = motorlib.units.convert(self.prop.min, self.prop.unit, self.dispUnit)
            convMax = motorlib.units.convert(self.prop.max, self.prop.unit, self.dispUnit)
            self.editor.setRange(convMin, convMax)

            self.editor.setValue(self.prop.getValue())
            self.editor.valueChanged.connect(self.valueChanged.emit)
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.StringProperty):
            self.editor = QLineEdit()
            self.editor.setText(self.prop.getValue())
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.BooleanProperty):
            self.editor = QCheckBox()
            self.editor.setCheckState(Qt.CheckState.Checked if self.prop.getValue() else Qt.CheckState.Unchecked)
            self.editor.stateChanged.connect(self.valueChanged.emit)
            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.EnumProperty):
            self.editor = QComboBox()

            self.editor.addItems(self.prop.values)
            self.editor.setCurrentText(self.prop.value)
            self.editor.currentTextChanged.connect(self.valueChanged.emit)

            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.PolygonProperty):
            self.editor = PolygonEditor(self)

            self.editor.pointsChanged.connect(self.valueChanged.emit)
            self.editor.points = self.prop.getValue()
            self.editor.preferences = self.preferences

            self.layout().addWidget(self.editor)

        elif isinstance(prop, motorlib.properties.TabularProperty):
            self.editor = TabularEditor()

            self.editor.setPreferences(self.preferences)
            for tab in prop.tabs:
                self.editor.addTab(tab)
            self.editor.updated.connect(self.valueChanged.emit)

            self.layout().addWidget(self.editor)

    def getValue(self):
        if isinstance(self.prop, motorlib.properties.FloatProperty):
            return motorlib.units.convert(self.editor.value(), self.dispUnit, self.prop.unit)

        if isinstance(self.prop, motorlib.properties.IntProperty):
            return motorlib.units.convert(self.editor.value(), self.dispUnit, self.prop.unit)

        if isinstance(self.prop, motorlib.properties.StringProperty):
            return self.editor.text()

        if isinstance(self.prop, motorlib.properties.BooleanProperty):
            return self.editor.isChecked()

        if isinstance(self.prop, motorlib.properties.EnumProperty):
            return self.editor.currentText()

        if isinstance(self.prop, motorlib.properties.PolygonProperty):
            return self.editor.points

        if isinstance(self.prop, motorlib.properties.TabularProperty):
            return self.editor.getTabs()

        return None

    def _recentreSlider(self, centre):
        """Set the slider window to centre ± windowHalf, clamped to property bounds."""
        self._sliderMin = max(self._fullMin, centre - self._windowHalf)
        self._sliderMax = min(self._fullMax, centre + self._windowHalf)
        # Avoid degenerate zero-width window
        if self._sliderMax <= self._sliderMin:
            self._sliderMax = self._sliderMin + self._windowHalf
        self.slider.blockSignals(True)
        self.slider.setValue(self._valueToSlider(centre))
        self.slider.blockSignals(False)

    def _valueToSlider(self, value):
        """Convert a spinbox value to a slider position."""
        if self._sliderMax == self._sliderMin:
            return 0
        fraction = (value - self._sliderMin) / (self._sliderMax - self._sliderMin)
        return int(round(max(0.0, min(1.0, fraction)) * self._sliderResolution))

    def _sliderToValue(self, pos):
        """Convert a slider position to a spinbox value."""
        fraction = pos / self._sliderResolution
        return self._sliderMin + fraction * (self._sliderMax - self._sliderMin)

    def _sliderChanged(self, pos):
        """Handle slider movement — update spinbox."""
        if self._updatingFromSpinbox:
            return
        self._updatingFromSlider = True
        self.editor.setValue(self._sliderToValue(pos))
        self._updatingFromSlider = False
        self.valueChanged.emit()

    def _spinboxChanged(self, value):
        """Handle spinbox value change — update slider and re-centre window."""
        if self._updatingFromSlider:
            return
        self._updatingFromSpinbox = True
        # Re-centre the window on the new value typed into the spinbox
        self._recentreSlider(value)
        self._updatingFromSpinbox = False
        self.valueChanged.emit()
