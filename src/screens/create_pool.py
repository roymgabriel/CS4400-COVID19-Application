# screen 10

import time as t

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QHBoxLayout, QLineEdit, QLabel, QTableWidget, \
    QTableWidgetItem, QCheckBox, QPushButton

import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.labtech_home as labtech_home
import src.utils.popups as popup


class CreatePool(QDialog):
    """
    Testing:
        1. Check if initial table is populated correctly
        2. Verify that only column Date Tested should be sortable
        3. Verify that empty pool_id or pool_id of length more than 10 or pool_id consisted of letters or existing
        pool_id will trigger error message
        4. Verify that no selected tests or more than 7 tests selected will trigger error message
        5. Confirm that valid pool_id + 7 or less tests selected will properly update the database
    """
    def __init__(self, connection, user_type, username):
        super(CreatePool, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Create A Pool')
        self.setFixedHeight(500)
        self.setMinimumWidth(700)

        self.tests = {}

        vbox = QVBoxLayout(self)
        pool_id_hbox = QHBoxLayout(self)
        vbox.addLayout(pool_id_hbox)
        self.scroll = QScrollArea(self)
        vbox.addWidget(self.scroll)
        bottom_btn_hbox = QHBoxLayout(self)
        vbox.addLayout(bottom_btn_hbox)

        # New Pool ID
        self.pool_id = QLineEdit(self)
        pool_id_hbox.addWidget(QLabel('Pool ID:'))
        pool_id_hbox.addWidget(self.pool_id)

        # Test List
        self.table = QTableWidget(self)
        self.table.verticalHeader().hide()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Test ID', 'Date Tested', 'Include in Pool'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.get_tests()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(350)

        # Bottom buttons
        self.back_btn = QPushButton("Back (Home)")
        self.create_pool_btn = QPushButton("Create Pool")
        bottom_btn_hbox.addWidget(self.back_btn)
        bottom_btn_hbox.addWidget(self.create_pool_btn)

        self.create_pool_btn.clicked.connect(lambda : self.handle_create_pool(self.pool_id))
        if user_type == "labtech":
            self.back_btn.clicked.connect(self.labtech_back)
        elif user_type == "labtester":
            self.back_btn.clicked.connect(self.labtester_back)

    def labtech_back(self):
        self.close()
        labtech_home.LabTechHome(self.connection, self.username).exec()

    def labtester_back(self):
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.username).exec()

    def handle_create_pool(self, pool_id):
        """
        Create a new pool while handling edge cases.
        """
        if self.pool_id.text() == '':
            popup.Error("Please enter pool ID.").exec()
        elif not self.is_pool_id_available(pool_id):
            popup.Error("This pool ID already exists.").exec()
        elif not self.pool_id.text().isdigit() or len(self.pool_id.text()) > 10:
            popup.Error("Pool ID must be 1 to 10 digits only.").exec()
        else:
            selected_tests = []
            for testid, checkbox in self.tests.items():
                if checkbox.isChecked():
                    selected_tests.append(testid)
                    if len(selected_tests) > 7:
                        popup.Error("You are trying to add too many tests. A pool can only hold up to 7 tests.").exec()
                        return
            if len(selected_tests) != 0:
                self.cursor.callproc('create_pool', (pool_id.text(), selected_tests.pop()))
                self.connection.commit()
            else:
                popup.Error("A pool must have at least 1 test.").exec()
                return
            while len(selected_tests) > 0:
                self.cursor.callproc('assign_test_to_pool', (pool_id.text(), selected_tests.pop()))
                self.connection.commit()
            popup.Message("Successful!").exec()
            # update table
            self.pool_id.clear()
            self.get_tests()

    def is_pool_id_available(self, pool_id):
        """
        Check if the new pool id already exists in the database.
        """
        self.cursor.execute('SELECT pool_id FROm pool WHERE pool_id = %s;', (pool_id.text(),))
        result = self.cursor.fetchall()
        if len(result) == 0:
            return True
        else:
            return False

    def get_tests(self):
        self.cursor.execute('SELECT test_id, appt_date FROM test WHERE pool_id IS NULL;')
        results = self.cursor.fetchall()
        self.table.setRowCount(len(results))
        self.table.setSortingEnabled(False)  # important: this line must be executed before populating table contents
        row_num = 0
        self.tests.clear()
        for result in results:
            self.table.setItem(row_num, 0, QTableWidgetItem(result['test_id']))
            self.table.setItem(row_num, 1, QTableWidgetItem(result['appt_date'].strftime("%Y-%m-%d")))
            checkbox = QCheckBox(self)
            self.tests[result['test_id']] = checkbox
            self.table.setCellWidget(row_num, 2, checkbox)
            row_num += 1
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.scroll.setWidget(self.table)

    def sort_table(self, logicalIndex):
        if logicalIndex == 1:
            self.table.setSortingEnabled(True)
            t.sleep(0.1)
            self.table.setSortingEnabled(False)
