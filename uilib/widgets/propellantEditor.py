from motorlib.propellant import Propellant
from .collectionEditor import CollectionEditor
from .propellantPreviewWidget import PropellantPreviewWidget

class PropellantEditor(CollectionEditor):
    def __init__(self, parent):
        super().__init__(parent, False)

        self.propellantPreview = PropellantPreviewWidget()
        self.propellantPreview.hide()
        self.stats.addWidget(self.propellantPreview)
        self._currentIngredients = []

    def cleanup(self):
        self.propellantPreview.hide()
        self._currentIngredients = []
        super().cleanup()

    def setPreferences(self, pref):
        super().setPreferences(pref)
        self.propellantPreview.setPreferences(self.preferences)

    def propertyUpdate(self):
        props = self.getProperties()
        if self._currentIngredients:
            props['ingredients'] = self._currentIngredients
        previewProp = Propellant(props)
        self.propellantPreview.loadPropellant(previewProp)

    def loadProperties(self, obj):
        self._currentIngredients = getattr(obj, 'ingredients', [])
        super().loadProperties(obj)
        self.propellantPreview.show()
