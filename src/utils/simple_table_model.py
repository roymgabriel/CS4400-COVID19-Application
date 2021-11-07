###########################################################################################################################################
###################################################### Simple Table Setup #################################################################
###########################################################################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *


class SimpleTableModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self, None)
        self.data = data
        self.headers = [str(k) for k, v in data[0].items()]
        self.rows = [[str(v) for k, v in record.items()] for record in data]

    def rowCount(self, parent):
        return len(self.rows)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()
        else:
            return QVariant(self.rows[index.row()][index.column()])

    def row(self, index):
        return self.data[index]

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        elif orientation == Qt.Vertical:
            return section + 1
        else:
            return self.headers[section]