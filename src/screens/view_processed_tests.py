# screen 8

from datetime import datetime
import time as t

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QScrollArea, QHBoxLayout, QLineEdit, QLabel, QComboBox, \
    QTableWidget, QTableWidgetItem, QPushButton

import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.labtech_home as labtech_home
import src.screens.explore_pool_result as explore_pool
import src.utils.popups as popup


class ViewProcessedTests(QDialog):
    """
    Testing:
        1. Check if all tests shown were processed by the user--labtech
        2. Verify that only columns Date Tested and Date Processed should be sortable
        3. Verify correctness when applying different filters
        4. Verify that all pool ids are linked to the explore pool result screen
        5. Check if back button goes to the right home screen
    """
    def __init__(self, connection, user_type, username):
        super(ViewProcessedTests, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username
        self.user_type = user_type

        self.setWindowTitle('Lab Tech Tests Processed')
        self.setFixedHeight(500)
        self.setMinimumWidth(700)

        vbox = QVBoxLayout(self)
        filters = QGridLayout(self)
        vbox.addLayout(filters)
        self.scroll = QScrollArea(self)
        vbox.addWidget(self.scroll)
        bottom_btns = QHBoxLayout(self)
        vbox.addLayout(bottom_btns)

        # Date Tested
        date_filter = QHBoxLayout(self)
        self.from_date_tested = QLineEdit(self)
        self.from_date_tested.setPlaceholderText("YYYY-MM-DD")
        self.to_date_tested = QLineEdit(self)
        self.to_date_tested.setPlaceholderText("YYYY-MM-DD")
        date_filter.addWidget(self.from_date_tested)
        date_filter.addWidget(QLabel("-"))
        date_filter.addWidget(self.to_date_tested)

        # Test result
        self.test_result = QComboBox()
        self.test_result.addItems(['ALL', 'negative', 'positive'])

        filters.addWidget(QLabel("Date Tested:"), 0, 0)
        filters.addLayout(date_filter, 0, 1)
        filters.addWidget(QLabel("Test Result:"), 1, 0)
        filters.addWidget(self.test_result, 1, 1)

        # Processed tests
        self.table = QTableWidget(self)
        self.table.verticalHeader().hide()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Test ID', 'Pool ID', 'Date Tested', 'Date Processed', 'Result'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.get_processed_tests([None, None, None, self.username])
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(300)

        # Bottom buttons
        self.back_home = QPushButton("Back (Home)")
        self.reset_btn = QPushButton("Reset")
        self.filter_btn = QPushButton("Filter")

        bottom_btns.addWidget(self.back_home)
        bottom_btns.addWidget(self.reset_btn)
        bottom_btns.addWidget(self.filter_btn)

        self.reset_btn.clicked.connect(self.handle_reset_btn)
        self.filter_btn.clicked.connect(self.handle_filter_btn)

        if user_type == "labtech":
            self.back_home.clicked.connect(self.labtech_back)
        elif user_type == "labtester":
            self.back_home.clicked.connect(self.labtester_back)

    def labtech_back(self):
        self.close()
        labtech_home.LabTechHome(self.connection, self.username).exec()

    def labtester_back(self):
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.username).exec()

    def handle_reset_btn(self):
        # clear result
        self.get_processed_tests([None, None, None, self.username])
        # clear filters
        self.from_date_tested.clear()
        self.to_date_tested.clear()
        self.test_result.setCurrentText('ALL')

    def handle_filter_btn(self):
        params = []
        try:
            # from date
            if self.from_date_tested.text() == '':
                params.append(None)
            else:
                params.append(datetime.strptime(self.from_date_tested.text(), '%Y-%m-%d'))
            # to date
            if self.to_date_tested.text() == '':
                params.append(None)
            else:
                params.append(datetime.strptime(self.to_date_tested.text(), '%Y-%m-%d'))
        except ValueError:
            popup.Error('Date must be valid and in the format YYYY-MM-DD.').exec()
            return
        # test result
        if self.test_result.currentText() == 'ALL':
            params.append(None)
        else:
            params.append(self.test_result.currentText())
        params.append(self.username)
        self.get_processed_tests(params)

    def get_processed_tests(self, params):
        self.cursor.callproc('tests_processed', params)
        self.cursor.execute('SELECT * FROM tests_processed_result;')
        results = self.cursor.fetchall()
        self.table.setRowCount(len(results))
        self.table.setSortingEnabled(False)  # important: this line must be executed before populating table contents
        row_num = 0
        for result in results:
            self.table.setItem(row_num, 0, QTableWidgetItem(result['test_id']))
            # id.setStyleSheet("color: blue; text-decoration: underline;")
            self.table.setItem(row_num, 1, QTableWidgetItem(result['pool_id']))
            test_date = result['test_date'].strftime("%Y-%m-%d")
            self.table.setItem(row_num, 2, QTableWidgetItem(test_date))
            process_date = result['process_date'].strftime("%Y-%m-%d")
            self.table.setItem(row_num, 3, QTableWidgetItem(process_date))
            self.table.setItem(row_num, 4, QTableWidgetItem(result['test_status']))
            row_num += 1
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.table.cellClicked.connect(self.tbl_clicked)
        self.scroll.setWidget(self.table)

    def tbl_clicked(self, row, col):
        if col == 1:
            pool_id = self.table.item(row, col).text()
            self.close()
            explore_pool.ExplorePoolResult(self.connection, self.user_type, self.username, pool_id).exec()

    def sort_table(self, logicalIndex):
        if logicalIndex == 2 or logicalIndex == 3 or logicalIndex == 4:
            self.table.setSortingEnabled(True)
            t.sleep(0.1)
            self.table.setSortingEnabled(False)

