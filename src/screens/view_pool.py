# screen 9

import datetime
import time as t

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QScrollArea, QHBoxLayout, QLineEdit, QLabel, QComboBox, \
    QTableWidget, QPushButton, QTableWidgetItem

import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.labtech_home as labtech_home
import src.screens.explore_pool_result as explore_pool_result
import src.screens.process_pool as process_pool
import src.utils.popups as popup


class ViewPool(QDialog):
    """
    Testing:
        1. Check if initial table is populated correctly
        2. Verify that only columns Date Processed, Processed By, and Pool Status should be sortable
        3. Verify correctness when applying different filters
        4. Verify error messages when entering invalid username
        5. Verify that pool ids of processed pools are linked to the explore pool result screens, and
           and pool ids of unprocessed pools are linked to process pool screen
        6. Check if back button goes to the right home screen
    """
    def __init__(self, connection, user_type, username):
        super(ViewPool, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username
        self.user_type = user_type

        self.setWindowTitle('View Pools')
        self.setFixedHeight(500)
        self.setMinimumWidth(700)

        # get a list of lab techs
        self.labtechs = []
        self.cursor.execute('SELECT * FROM labtech;')
        results = self.cursor.fetchall()
        for result in results:
            self.labtechs.append(result['labtech_username'])

        vbox = QVBoxLayout(self)
        filters = QGridLayout(self)
        self.scroll = QScrollArea(self)
        bottom_buttons = QHBoxLayout(self)
        vbox.addLayout(filters)
        vbox.addWidget(self.scroll)
        vbox.addLayout(bottom_buttons)

        # Date Processed
        date_filter = QHBoxLayout(self)
        self.from_date_processed = QLineEdit(self)
        self.from_date_processed.setPlaceholderText("YYYY-MM-DD")
        self.to_date_processed = QLineEdit(self)
        self.to_date_processed.setPlaceholderText("YYYY-MM-DD")
        date_filter.addWidget(self.from_date_processed)
        date_filter.addWidget(QLabel("-"))
        date_filter.addWidget(self.to_date_processed)

        # Pool Status
        self.pool_status = QComboBox()
        self.pool_status.addItems(['ALL', 'negative', 'positive', 'pending'])

        # Processed By
        self.processed_by = QLineEdit(self)

        filters.addWidget(QLabel("Date Processed:"), 0, 0)
        filters.addLayout(date_filter, 0, 1)
        filters.addWidget(QLabel("Pool Status:"), 0, 2)
        filters.addWidget(self.pool_status, 0, 3)
        filters.addWidget(QLabel("Processed By:"), 1, 0)
        filters.addWidget(self.processed_by, 1, 1)

        # Pool List
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels(['Pool ID', 'Test IDs', 'Date Processed',
                                              'Processed By', 'Pool Status'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.get_pools([None, None, None, None])
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(300)

        # Bottom buttons
        self.back_home = QPushButton("Back (Home)")
        self.reset_btn = QPushButton("Reset")
        self.filter_btn = QPushButton("Filter")

        bottom_buttons.addWidget(self.back_home)
        bottom_buttons.addWidget(self.reset_btn)
        bottom_buttons.addWidget(self.filter_btn)

        self.reset_btn.clicked.connect(self.handle_reset_btn)
        self.filter_btn.clicked.connect(self.handle_filter_btn)
        self.table.clicked.connect(self.pool_id_clicked)

        if self.user_type == "labtech":
            self.back_home.clicked.connect(self.labtech_back)
        elif self.user_type == "labtester":
            self.back_home.clicked.connect(self.labtester_back)

    def labtech_back(self):
        self.close()
        labtech_home.LabTechHome(self.connection, self.username).exec()

    def labtester_back(self):
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.username).exec()

    def handle_reset_btn(self):
        # clear results
        self.get_pools([None, None, None, None])
        # clear filters
        self.from_date_processed.clear()
        self.to_date_processed.clear()
        self.processed_by.clear()
        self.pool_status.setCurrentText('ALL')

    def pool_id_clicked(self, item):
        if item.column() == 0:
            pool_ID = item.data()
            if self.table.item(item.row(), 3).text() != 'NULL':
                pool_tests_cell = self.table.item(0, 1)
                pool_tests = pool_tests_cell.text()
                self.close()
                explore_pool_result.ExplorePoolResult(
                    self.connection, self.user_type, self.username, pool_ID).exec()
            else:
                self.close()
                process_pool.ProcessPool(self.connection, self.user_type, self.username, pool_ID).exec()

    def handle_filter_btn(self):
        params = []
        try:
            if self.from_date_processed.text() != "":
                params.append(datetime.datetime.strptime(self.from_date_processed.text(), '%Y-%m-%d'))
            else:
                params.append(None)
            if self.to_date_processed.text() != "":
                params.append(datetime.datetime.strptime(self.to_date_processed.text(), '%Y-%m-%d'))
            else:
                params.append(None)
        except ValueError:
            popup.Error('Date must be valid and in the format YYYY-MM-DD.').exec()
            return
        params.append(self.pool_status.currentText())
        if self.processed_by.text() != "":
            entry = self.processed_by.text()
            techs = []
            invalid = True
            for tech in self.labtechs:
                if entry in tech:
                    invalid = False
                    techs.append(tech)
            if invalid:
                popup.Error('No labtechs whose usernames contain "' + entry + '" are found.').exec()
                return
            params.append(techs)
        else:
            params.append(None)
        self.get_pools(params)

    def get_pools(self, args):
        # last element of args could be a list of labtechs
        args1 = args[0:3]
        args2 = args[-1]
        params_list = [] # each element is a complete list of params to be passed into procedure view_pools
        if args2 is None or len(args2) == 1:
            params_list.append(args)
        else:
            for labtech in args2:
                params_list.append(args1 + [labtech])
        row_num = 0
        results = [] # hold queried data from for labtechs
        for params in params_list:
            self.cursor.callproc('view_pools', params)
            self.cursor.execute('SELECT * FROM view_pools_result;')
            results += self.cursor.fetchall()
        self.table.setRowCount(len(results))
        for result in results:
            self.table.setItem(row_num, 0, QTableWidgetItem(result['pool_id']))
            self.table.setItem(row_num, 1, QTableWidgetItem(result['test_ids']))
            if result['date_processed'] is None:
                self.table.setItem(row_num, 2, QTableWidgetItem('NULL'))
            else:
                self.table.setItem(row_num, 2, QTableWidgetItem(result['date_processed'].strftime("%Y-%m-%d")))
            if result['processed_by'] is None:
                self.table.setItem(row_num, 3, QTableWidgetItem('NULL'))
            else:
                self.table.setItem(row_num, 3, QTableWidgetItem(result['processed_by']))
            self.table.setItem(row_num, 4, QTableWidgetItem(result['pool_status']))
            row_num += 1
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.scroll.setWidget(self.table)

    def sort_table(self, logicalIndex):
        if logicalIndex == 2 or logicalIndex == 3 or logicalIndex == 4:
            self.table.setSortingEnabled(True)
            t.sleep(0.1)
            self.table.setSortingEnabled(False)
