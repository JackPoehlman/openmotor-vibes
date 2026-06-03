from threading import Thread

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QTimer

import motorlib

from ..views.GrainPreview_ui import Ui_GrainPreview

class GrainPreviewWidget(QWidget):

    FAST_FACE_MAP_DIM = 160
    FULL_FACE_MAP_DIM = 250
    FAST_REGRESSION_MAP_DIM = 140
    FULL_REGRESSION_MAP_DIM = 250
    FAST_NUM_CONTOURS = 10
    FULL_NUM_CONTOURS = 15
    IDLE_FULL_REFRESH_MS = 350

    faceReady = pyqtSignal(tuple)
    regressionReady = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.ui = Ui_GrainPreview()
        self.ui.setupUi(self)

        self.ui.tabFace.setupImagePlot()
        self.ui.tabRegression.setupImagePlot()
        self.ui.tabAreaGraph.setupGraphPlot()

        # Used to navigate back to the tab the user was on after they clear alerts
        self.lastNonAlertTab = 1

        self.ui.tabWidget.currentChanged.connect(self.onTabChanged)

        self.faceReady.connect(self.updateFace)
        self.regressionReady.connect(self.updateRegression)

        self._requestId = 0
        self._activeGrain = None
        self._regressionReadyRequest = -1
        self._regressionInFlightRequest = -1
        self._faceReadyMapDim = 0
        self._regressionReadyMapDim = 0

        self._fullRefreshTimer = QTimer(self)
        self._fullRefreshTimer.setSingleShot(True)
        self._fullRefreshTimer.timeout.connect(self._refreshFullPreview)

    def loadGrain(self, grain):
        self._activeGrain = grain
        self._requestId += 1
        requestId = self._requestId
        self._regressionReadyRequest = -1
        self._regressionInFlightRequest = -1
        self._faceReadyMapDim = 0
        self._regressionReadyMapDim = 0

        geomAlerts = grain.getGeometryErrors()

        self.ui.tabAlerts.clear()
        for err in geomAlerts:
            self.ui.tabAlerts.addItem(err.description)

        for alert in geomAlerts:
            if alert.level == motorlib.simResult.SimAlertLevel.ERROR:
                # Go to alerts tab and clear up graph/images
                self.ui.tabWidget.setCurrentIndex(0)
                self.ui.tabFace.cleanup()
                self.ui.tabRegression.cleanup()
                self.ui.tabAreaGraph.cleanup()
                return

        # If they were on the alert tab, go to their last image/graph tab. Otherwise, let them stay
        if self.ui.tabWidget.currentIndex() == 0:
            self.ui.tabWidget.setCurrentIndex(self.lastNonAlertTab)

        # Fast face preview for responsive editing.
        faceThread = Thread(
            target=self._genFaceData,
            args=[grain, requestId, self.FAST_FACE_MAP_DIM],
        )
        faceThread.start()

        # Regression/area data is expensive; generate it only when those tabs are in use.
        if self.ui.tabWidget.currentIndex() in (2, 3):
            self._startRegressionGeneration(
                grain,
                requestId,
                self.FAST_REGRESSION_MAP_DIM,
                self.FAST_NUM_CONTOURS,
            )
        else:
            self.ui.tabRegression.cleanup()
            self.ui.tabAreaGraph.cleanup()

        # When edits pause briefly, refresh at full quality.
        self._fullRefreshTimer.start(self.IDLE_FULL_REFRESH_MS)

    def _startRegressionGeneration(self, grain, requestId, mapDim, numContours):
        if self._regressionInFlightRequest == requestId and self._regressionReadyMapDim >= mapDim:
            return
        self._regressionInFlightRequest = requestId
        regressionThread = Thread(
            target=self._genRegressionData,
            args=[grain, requestId, mapDim, numContours],
        )
        regressionThread.start()

    def _refreshFullPreview(self):
        if self._activeGrain is None:
            return

        requestId = self._requestId

        if self._faceReadyMapDim < self.FULL_FACE_MAP_DIM:
            faceThread = Thread(
                target=self._genFaceData,
                args=[self._activeGrain, requestId, self.FULL_FACE_MAP_DIM],
            )
            faceThread.start()

        if (
            self.ui.tabWidget.currentIndex() in (2, 3)
            and self._regressionReadyMapDim < self.FULL_REGRESSION_MAP_DIM
        ):
            self._startRegressionGeneration(
                self._activeGrain,
                requestId,
                self.FULL_REGRESSION_MAP_DIM,
                self.FULL_NUM_CONTOURS,
            )

    def _genFaceData(self, grain, requestId, mapDim):
        try:
            faceImage = grain.getFaceImage(mapDim)
            self.faceReady.emit((requestId, mapDim, faceImage))
        except Exception:
            # Keep UI responsive even if preview generation fails for transient states.
            return

    def _genRegressionData(self, grain, requestId, mapDim, numContours):
        try:
            out = grain.getRegressionData(
                mapDim,
                numContours=numContours,
                coreBlack=False,
            )
            self.regressionReady.emit((requestId, mapDim, out))
        except Exception:
            return

    def updateFace(self, data):
        requestId, mapDim, coreIm = data
        if requestId != self._requestId:
            return
        if mapDim < self._faceReadyMapDim:
            return

        self._faceReadyMapDim = mapDim

        self.ui.tabFace.cleanup()
        self.ui.tabFace.showImage(coreIm)

    def updateRegression(self, data):
        requestId, mapDim, payload = data
        if requestId != self._requestId:
            return
        if mapDim < self._regressionReadyMapDim:
            return

        self._regressionInFlightRequest = -1
        self._regressionReadyRequest = requestId
        self._regressionReadyMapDim = mapDim

        coreIm, regImage, contours, contourLengths = payload

        if regImage is not None:
            self.ui.tabRegression.cleanup()
            self.ui.tabRegression.showImage(regImage)
            self.ui.tabRegression.showContours(contours)

            points = [[], []]

            for k in contourLengths.keys():
                points[0].append(k)
                points[1].append(contourLengths[k])

            self.ui.tabAreaGraph.cleanup()
            self.ui.tabAreaGraph.showGraph(points)

    def onTabChanged(self, tabIndex):
        if tabIndex != 0:
            self.lastNonAlertTab = tabIndex

        if tabIndex in (2, 3) and self._activeGrain is not None:
            if self._regressionReadyRequest != self._requestId:
                self._startRegressionGeneration(
                    self._activeGrain,
                    self._requestId,
                    self.FAST_REGRESSION_MAP_DIM,
                    self.FAST_NUM_CONTOURS,
                )
            self._fullRefreshTimer.start(self.IDLE_FULL_REFRESH_MS)

    def cleanup(self):
        self.lastNonAlertTab = 1
        self._requestId += 1
        self._activeGrain = None
        self._regressionReadyRequest = -1
        self._regressionInFlightRequest = -1
        self._faceReadyMapDim = 0
        self._regressionReadyMapDim = 0
        self._fullRefreshTimer.stop()
        self.ui.tabAlerts.clear()
        self.ui.tabRegression.cleanup()
        self.ui.tabFace.cleanup()
        self.ui.tabAreaGraph.cleanup()
        self.ui.tabAreaGraph.resetGraphBounds()
