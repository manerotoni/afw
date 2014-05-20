"""
contrast.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from PyQt4 import QtGui
from PyQt4 import QtCore

class ContrastManager(object):

    def __init__(self, default_minimum, default_maximum,
                 disp_minimum=0, disp_maximum=255):
        self.default_minimum = default_minimum
        self.default_maximum = default_maximum
        self.minimum = default_minimum
        self.maximum = default_maximum
        self.setBitdepth(disp_maximum, disp_minimum)

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

    def setImageMinMax(self, image):
        self.image_minimum = numpy.min(image)
        self.image_maximum = numpy.max(image)

    def setImageToMinMax(self, image=None):
        if not image is None:
            self.setImageMinMax(image)
        self.minimum = self.image_minimum
        self.maximum = self.image_maximum
        self.update()

    def setContrast(self, contrast):
        self.contrast = contrast
        center = self.minimum + (self.maximum - self.minimum) / 2.0
        mid = self.slider_range / 2.0
        if contrast <= mid:
            slope = contrast / mid
        else:
            slope = mid / (self.slider_range - contrast)
        if slope > 0.0:
            range = self.default_maximum - self.default_minimum
            self.minimum = center - (0.5 * range) / slope
            self.maximum = center + (0.5 * range) / slope

    def setBrightness(self, brightness):
        self.brightness = brightness
        center = self.default_minimum + \
                 (self.default_maximum - self.default_minimum) * \
                 (self.slider_range - brightness) / self.slider_range
        width = self.maximum - self.minimum
        self.minimum = center - width / 2.0
        self.maximum = center + width / 2.0

    def setMinimum(self, minimum):
        self.minimum = minimum
        if self.minimum > self.maximum:
            self.maximum = self.minimum
        self.update()

    def setMaximum(self, maximum):
        self.maximum = maximum
        if self.minimum > self.maximum:
            self.minimum = self.maximum
        self.update()

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


class ContrastWidget(QtGui.QWidget):

    SLIDER_NAMES = ['minimum', 'maximum', 'brightness', 'contrast']

    valuesChanged = QtCore.pyqtSignal(str)

    def __init__(self, channel_names, parent, bitdepth=8):
        super(ContrastWidget, self).__init__(parent)

        self.setMaximumWidth(220)

        layout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom, self)
        layout.setContentsMargins(0, 0, 0, 0)

        frame0 = QtGui.QFrame(self)
        layout0 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight, frame0)
        layout0.setContentsMargins(0, 0, 0, 0)
        layout0.addStretch(1)
        grp = QtGui.QButtonGroup(frame0)
        grp.setExclusive(True)

        self._display_settings = {}
        self._current = None

        fct = lambda x: lambda y: self.onChannelChanged(x, y)
        for idx, name in enumerate(channel_names):
            btn = QtGui.QPushButton(name, frame0)
            btn.toggled.connect(fct(name))
            btn.setCheckable(True)
            grp.addButton(btn)
            layout0.addWidget(btn)
            self._display_settings[name] = ContrastManager(0, 2**bitdepth)

        layout0.addStretch(1)
        layout.addWidget(frame0)

        frame1 = QtGui.QFrame(self)
        layout1 = QtGui.QGridLayout(frame1)
        layout1.setContentsMargins(2, 0, 2, 0)

        self._newSlider(frame1, "minimum", (0, 2**bitdepth), 0)
        self._newSlider(frame1, "maximum", (0, 2**bitdepth), 1)
        self._newSlider(frame1, "brightness", (0, 2**bitdepth), 2)
        self._newSlider(frame1, "contrast", (0, 2**bitdepth), 3)

        layout.addWidget(frame1)

        frame2 = QtGui.QFrame(self)
        layout2 = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight, frame2)
        layout2.setContentsMargins(5, 5, 5, 5)
        btn = QtGui.QPushButton('Min/Max', self)
        btn.clicked.connect(self.onMinMax)
        layout2.addWidget(btn)
        btn = QtGui.QPushButton('Reset', self)
        btn.clicked.connect(self.onReset)
        layout2.addWidget(btn)
        layout.addWidget(frame2)

        if len(grp.buttons()) > 0:
            grp.buttons()[0].setChecked(True)

    def _newSlider(self, parent, name, range_, row):
        layout = parent.layout()
        fct = lambda x: lambda : self.onSliderChanged(x)

        label = QtGui.QLabel(name.capitalize(), parent)
        label.setAlignment(QtCore.Qt.AlignRight)
        slider = QtGui.QSlider(QtCore.Qt.Horizontal, parent)
        slider.setRange(*range_)
        slider.setTickPosition(QtGui.QSlider.TicksBelow)
        slider.valueChanged.connect(fct(name))
        slider.setObjectName(name)
        layout.addWidget(label, row, 0)
        layout.addWidget(slider, row, 1)

        setattr(self, name, slider)


    def setSliders(self, ignore=None):
        s = self._display_settings[self._current]
        for slider in (self.minimum, self.maximum,
                       self.brightness, self.contrast):
            if slider.objectName() != ignore:
                slider.blockSignals(True)
                slider.setValue(getattr(s, slider.objectName()))
                slider.blockSignals(False)

    def onSliderChanged(self, name):
        s = self._display_settings[self._current]
        sld = getattr(self, name)
        getattr(s, "set%s" %name.title())(sld.value())
        self.setSliders(ignore=name)
        self.valuesChanged.emit(self._current)

    def onReset(self):
        s = self._display_settings[self._current]
        s.reset()
        self.setSliders()
        self.valuesChanged.emit(self._current)

    def onMinMax(self):
        s = self._display_settings[self._current]
        s.setImageToMinMax()
        self.setSliders()
        self.valuesChanged.emit(self._current)

    def onChannelChanged(self, name, state):
        if state:
            self._current = name
            self.setSliders()

    def transformImage(self, name, image):

        s = self._display_settings[name]
        s.setImageMinMax(image)

        # FIXME: Just a workaround, the image comes with wrong strides
        #        fixed in master
        image2 = numpy.zeros(image.shape, dtype=numpy.float32, order='F')
        image2[:] = image

        # add a small value in case max == min
        image2 *= 255.0 / (s.maximum - s.minimum + 0.1)
        image2 -= s.minimum

        image2 = image2.clip(0, 255)

        image2 = numpy.require(image2, numpy.uint8)
        return image2
