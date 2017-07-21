from PyQt4.QtGui import QApplication, QWidget, QGridLayout
from PyQt4.QtCore import SIGNAL, QObject, QTimer
from DMCircularGauge import DMCircularGauge


class PyDMWindowSim(QWidget):
    def __init__(self, parent=None):
        super(PyDMWindowSim, self).__init__(parent)

        self.pv1 = PV(self, 'FirstPV')
        self.pv2 = PV(self, 'SecondPV')
        self.pv3 = PV(self, 'ThirdPV')
        self.pv4 = PV(self, 'ForthPV')

        self.setupUI()

    def setupUI(self):
        layout = QGridLayout(self)
        layout.addWidget(DMCircularGauge(self.pv1, None, None, self), 0, 0)
        layout.addWidget(DMCircularGauge(self.pv1, None, None, self), 0, 1)
        layout.addWidget(DMCircularGauge(self.pv3, None, None, self), 1, 0)
        layout.addWidget(DMCircularGauge(self.pv4, None, None, self), 1, 1)


class PV(QObject):
    invalid = False

    def __init__(self, parent=None, name='MyFakePV'):
        super(PV, self).__init__(parent)

        self._name = name
        self._egu = 'Torr'
        self._value = 50.0
        self._hopr = 100.0
        self._lopr = 0.0
        self._hihi = 75.0
        self._high = 60.0
        self._low = 40.0
        self._lolo = 25.0

        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL("timeout()"), self.update_value)
        self.timer.start(100)
        # print 'Timer started'

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = float(value)
        self.emit(SIGNAL("new_value(float)"), self.value)

    @property
    def name(self):
        # This property only set at initialization, no setter
        return str(self._name)

    @property
    def egu(self):
        return self._egu

    @egu.setter
    def egu(self, units):
        self._egu = str(units)

    @property
    def hopr(self):
        return self._hopr

    @hopr.setter
    def hopr(self, limit):
        self._hopr = float(limit)
        self.emit(SIGNAL("new_range(list)"), self.range)

    @property
    def lopr(self):
        return self._lopr

    @lopr.setter
    def lopr(self, limit):
        self._lopr = float(limit)
        self.emit(SIGNAL("new_range(list)"), self.range)

    def range(self):
        return [self.lopr, self.hopr]

    @property
    def hihi(self):
        return self._hihi

    @hihi.setter
    def hihi(self, limit):
        self._hihi = float(limit)
        self.emit(SIGNAL("new_limits(list)"), self.limits)

    @property
    def high(self):
        return self._high

    @high.setter
    def high(self, limit):
        self._high = float(limit)
        self.emit(SIGNAL("new_limits(list)"), self.limits)

    @property
    def low(self):
        return self._low

    @low.setter
    def low(self, limit):
        self._low = float(limit)
        self.emit(SIGNAL("new_limits(list)"), self.limits)

    @property
    def lolo(self):
        return self._lolo

    @lolo.setter
    def lolo(self, limit):
        self._lolo = float(limit)
        self.emit(SIGNAL("new_limits(list)"), self.limits)

    def limits(self):
        return self.lolo, self.low, self.high, self.hihi

    @property
    def sevr(self):
        if self.value <= self.lolo or self.value >= self.hihi:
            severity = 'major'
        elif self.value <= self.low or self.value >= self.high:
            severity = 'minor'
        elif self.invalid:
            severity = 'invalid'
        else:
            severity = 'no_alarm'
        return severity

    def update_value(self):
        from random import uniform, randint

        direction = randint(0, 1)
        if direction == 0:
            delta = self.value * uniform(0, 0.01)
        else:
            delta = self.value * uniform(-0.01, 0)
        self.value = max(min(self.value + delta, self.hopr), self.lopr)
        # print self.value


if __name__ == "__main__":
    from sys import argv

    app = QApplication(argv)
    window = PyDMWindowSim()
    window.show()
    window.raise_()

    exit(app.exec_())
