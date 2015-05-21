"""
contrast.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtEnhancerWidget', 'AtContrasSliderWidget')


from os.path import splitext
import numpy as np

from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets


class BaCCalculator(QtCore.QObject):
    """Brightness and Contrast calculator. By using the proper setter methods.
    all the other properties get updated automatically. Each call of those
    methods emit the signal 'valuesUpdated'."""

    valuesUpdated = QtCore.pyqtSignal()

    def __init__(self, default_minimum, default_maximum,
                 disp_minimum=0, disp_maximum=255, *args, **kw):
        super(BaCCalculator, self).__init__(*args, **kw)
        self.default_minimum = default_minimum
        self.default_maximum = default_maximum
        self.minimum = default_minimum
        self.maximum = default_maximum
        self.setBitdepth(disp_maximum, disp_minimum)
        self._image_properties = None

    @property
    def image_properties(self):
        return self._image_properties

    @image_properties.setter
    def image_properties(self, prop):
        self._image_properties = prop
        self.image_minimum = prop.min
        self.image_maximum = prop.max

    @image_properties.deleter
    def image_properties(self):
        del self._image_properties

    def setBitdepth(self, disp_maximum, disp_minimum=0):
        self.slider_range = disp_maximum - disp_minimum + 1
        self.brightness = self.slider_range / 2.0
        self.contrast = self.slider_range / 2.0
        self.image_minimum = disp_minimum
        self.image_maximum = disp_maximum

    def reset(self):
        self.minimum = self.default_minimum
        self.maximum = self.default_maximum
        self.brightness = self.slider_range / 2.0
        self.contrast = self.slider_range / 2.0
        self.valuesUpdated.emit()

    def setImageToMinMax(self):
        self.minimum = self.image_minimum
        self.maximum = self.image_maximum
        self.update()
        self.valuesUpdated.emit()

    def setContrast(self, contrast):
        self.contrast = contrast
        center = self.minimum + (self.maximum - self.minimum) / 2.0
        mid = self.slider_range / 2.0
        if contrast <= mid:
            slope = contrast / mid
        else:
            try:
                slope = mid / (self.slider_range - contrast)
            except ZeroDivisionError:
                slope = mid / self.slider_range

        if slope > 0.0:
            range = self.default_maximum - self.default_minimum
            self.minimum = center - (0.5 * range) / slope
            self.maximum = center + (0.5 * range) / slope
        self.valuesUpdated.emit()

    def setBrightness(self, brightness):
        self.brightness = brightness
        center = self.default_minimum + \
                 (self.default_maximum - self.default_minimum) * \
                 (self.slider_range - brightness) / self.slider_range
        width = self.maximum - self.minimum
        self.minimum = center - width / 2.0
        self.maximum = center + width / 2.0
        self.valuesUpdated.emit()

    def setMinimum(self, minimum):
        self.minimum = minimum
        if self.minimum > self.maximum:
            self.maximum = self.minimum
        self.update()
        self.valuesUpdated.emit()

    def setMaximum(self, maximum):
        self.maximum = maximum
        if self.minimum > self.maximum:
            self.minimum = self.maximum
        self.update()
        self.valuesUpdated.emit()

    def setAuto(self):
        self.minimum, self.maximum = self.image_properties.autoRange()
        self.update()
        self.valuesUpdated.emit()

    def update(self):
        range = float(self.default_maximum - self.default_minimum + 1)
        range2 = float(self.maximum - self.minimum + 1)
        mid = self.slider_range / 2.0
        self.contrast = (range / range2) * mid
        if self.contrast > mid:
            self.contrast = self.slider_range - (range2 / range) * mid
        level = self.minimum + range2 / 2.0
        normalized = 1.0 - (level - self.default_minimum) / range
        self.brightness = normalized * self.slider_range


class AtContrastSliderWidget(QtWidgets.QWidget):
    """Slider widget contains the 4 sliders for contrast enhancement of
    one slinge grey level image."""

    valuesUpdated = QtCore.pyqtSignal()
    sliderReleased = QtCore.pyqtSignal()
    buttonClicked = QtCore.pyqtSignal()

    def __init__(self, parent, range_=(0, 256)):
        super(AtContrastSliderWidget, self).__init__(parent)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.settings = BaCCalculator(*range_)

        self.minimum.setRange(*range_)
        self.maximum.setRange(*range_)
        self.brightness.setRange(*range_)
        self.contrast.setRange(*range_)

        self.settings.valuesUpdated.connect(self.updateSliders)
        self.minMaxBtn.clicked.connect(self.settings.setImageToMinMax)
        self.resetBtn.clicked.connect(self.settings.reset)
        self.autoBtn.clicked.connect(self.settings.setAuto)
        self.autoBtn.setToolTip("Cuts of 1% of the histogram")

        self.minimum.valueChanged.connect(self.settings.setMinimum)
        self.maximum.valueChanged.connect(self.settings.setMaximum)
        self.contrast.valueChanged.connect(self.settings.setContrast)
        self.brightness.valueChanged.connect(self.settings.setBrightness)

        self.minimum.valueChanged.connect(self.valuesToolTip)
        self.maximum.valueChanged.connect(self.valuesToolTip)
        self.contrast.valueChanged.connect(self.valuesToolTip)
        self.brightness.valueChanged.connect(self.valuesToolTip)

        self.minimum.sliderReleased.connect(self.sliderReleased.emit)
        self.maximum.sliderReleased.connect(self.sliderReleased.emit)
        self.contrast.sliderReleased.connect(self.sliderReleased.emit)
        self.brightness.sliderReleased.connect(self.sliderReleased.emit)

        self.minMaxBtn.clicked.connect(self.buttonClicked.emit)
        self.resetBtn.clicked.connect(self.buttonClicked.emit)
        self.autoBtn.clicked.connect(self.buttonClicked.emit)

        self.updateSliders()

    @property
    def image_properties(self):
        return self.settings.image_properties

    @image_properties.setter
    def image_properties(self, prop):
        self.settings.image_properties = prop

    def _slidersBlockSignals(self, state):
        for slider in (self.minimum, self.maximum,
                       self.contrast, self.brightness):
            slider.blockSignals(state)

    def updateSliders(self):
        self._slidersBlockSignals(True)
        self.minimum.setValue(self.settings.minimum)
        self.maximum.setValue(self.settings.maximum)
        self.contrast.setValue(self.settings.contrast)
        self.brightness.setValue(self.settings.brightness)
        self._slidersBlockSignals(False)

        self.valuesUpdated.emit()

    def valuesToolTip(self, dummy=None):
        # is connected to slider.valueChanged which emits an integer value
        msg = ("Min: %d\nMax: %d\nContrast: %d\nBrightness: %d"
               %(self.settings.minimum, self.settings.maximum,
                 self.settings.contrast, self.settings.brightness))

        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), msg, self)

    def onMinMax(self):
        self.settings.setImageToMinMax()

    def transformImage(self, image):

        # self.settings.setImageMinMax(image)
        # FIXME: Just a workaround, the image comes with wrong strides
        #        fixed in master
        image2 = np.zeros(image.shape, dtype=np.float32, order='F')
        image2[:] = image

        # add a small value in case max == min
        image2 *= 255.0 / (self.settings.maximum - self.settings.minimum + 0.1)
        image2 -= self.settings.minimum

        image2 = image2.clip(0, 255)

        image2 = np.require(image2, np.uint8)
        return image2


class AtEnhancerWidget(QtWidgets.QWidget):
    """Contrast enhancer widget manages multiple slider widgets for
    multiple channels."""

    valuesUpdated = QtCore.pyqtSignal()
    sliderReleased = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(AtEnhancerWidget, self).__init__(*args, **kw)

        vbox = QtWidgets.QVBoxLayout(self)
        self.channelBox = QtWidgets.QComboBox(self)
        self.stack = QtWidgets.QStackedWidget(self)

        vbox.addWidget(self.channelBox)
        vbox.addWidget(self.stack)

        self.channelBox.currentIndexChanged.connect(self.changeChannel)
        vbox.setContentsMargins(0, 0, 0, 0)

    def currentChannelIndex(self):
        return self.channelBox.currentIndex()

    def currentChannel(self):
        return self.channelBox.currentText()

    def clear(self):
        self.channelBox.clear()
        for i in range(self.stack.count()):
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.close()

    def toggleAutoButtons(self, state):
        for i in range(self.stack.count()):
            if state:
                self.stack.widget(i).autoBtn.show()
            else:
                self.stack.widget(i).autoBtn.hide()

    def setImageProps(self, props):

        if len(props) != self.stack.count():
            raise RuntimeError(("Lenght of list does not match the "
                                "number of enhancer widgets"))

        for i, prop in enumerate(props):
            self.stack.widget(i).image_properties = prop

    def addChannel(self, name, no_auto_button=False):
        sliderwidget = AtContrastSliderWidget(self, range_=(0, 255))
        if no_auto_button:
            sliderwidget.autoBtn.hide()
        sliderwidget.valuesUpdated.connect(self.valuesUpdated.emit)
        sliderwidget.sliderReleased.connect(self.sliderReleased.emit)
        sliderwidget.buttonClicked.connect(self.sliderReleased.emit)

        idx = self.stack.addWidget(sliderwidget)
        self.channelBox.addItem(name)

    def changeChannel(self, index):
        self.stack.setCurrentIndex(index)

    def enhanceImage(self, index, image):
        sliderwidget = self.stack.widget(index)
        return sliderwidget.transformImage(image)

    def lut_from_color(self, index, color, ncolors):
        """Create a colormap from a single color e.g. red and return
        a list of qRgb instances.
        """
        lut = np.zeros((ncolors, 3), dtype=int)
        for i, col in enumerate((color.red(), color.green(), color.blue())):
            lut[: , i] = np.array(range(ncolors)) / (ncolors - 1.0) * col

        lut2 = self.enhanceImage(index, lut)

        return [QtGui.qRgb(r, g, b) for r, g, b in lut2]
