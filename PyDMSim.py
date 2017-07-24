from PyQt4.QtGui import QApplication, QWidget, QGridLayout
from PyQt4.QtCore import SIGNAL, QObject, QTimer
from DMCircularGauge import DMCircularGauge


class PyDMWindowSim(QWidget):
    num_widgets = 4

    def __init__(self, parent=None):
        super(PyDMWindowSim, self).__init__(parent)

        self.pv_list = []
        for i in range(0, self.num_widgets):
            self.pv_list.append(PV(self, 'FAKE:LOC0:' + str(i) + ':PVAL'))

        self.setupUI()
        self.resize(300, 200)

    def setupUI(self):
        from math import sqrt, ceil
        layout = QGridLayout(self)

        cols = int(ceil(sqrt(len(self.pv_list)))) - 1
        i = 0
        j = 0
        for pv in self.pv_list:
            layout.addWidget(DMCircularGauge(pv, None, None, self), i, j)
            if j < cols:
                j += 1
            else:
                j = 0
                i += 1


class PV(QObject):
    invalid = False

    def __init__(self, parent=None, name='MyFakePV'):
        from random import choice, uniform
        super(PV, self).__init__(parent)

        self._name = name
        self._egu = choice(['Torr', 'm', 'l/s', 'Volts', 'Amps', 'eV', 'Joules', 'nC', 'degC', 'psi', 'Watts'])
        self._hopr = uniform(-40000.0, 50000.0)
        self._lopr = uniform(-50000.0, self.hopr - abs(self.hopr * 0.1))
        self._value = self.lopr + ((self.hopr-self.lopr) / 2)
        self._hihi = self.hopr - abs((self.hopr-self.lopr) * uniform(0.0, 0.2))
        self._high = self.hopr - abs((self.hopr-self.lopr) * uniform(0.2, 0.4))
        self._low = self.lopr + abs((self.hopr-self.lopr) * uniform(0.2, 0.4))
        self._lolo = self.lopr + abs((self.hopr-self.lopr) * uniform(0.0, 0.2))

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
