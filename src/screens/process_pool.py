# Screen 11

from datetime import datetime

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QLineEdit, QTabWidget, QLabel, \
    QPushButton, \
    QScrollArea, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox

import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.labtech_home as labtech_home
import src.utils.popups as popup


class ProcessPool(QDialog):
    """
    Testing:
        1. Per Piazza @873_f1, this screen can only be accessed from the view pool screen.
           The button Process Pool on the home page should take user to the view pool screen.
           Clicking on the pool id of un unprocessed test will be linked to this screen.
        2. Check if initial table is populated correctly
        3. Verify that the tables in positive and negative tabs are populated correctly.
        4. Verify that a proper processed date should be after the latest test date on the list
        5. Check if back button goes to the right home screen
    """
    def __init__(self, connection, user_type, username, pool_id):
        super(ProcessPool, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.user_type = user_type
        self.username = username
        self.pool_id = pool_id

        self.setWindowTitle('Process Pool')
        self.setFixedHeight(500)
        self.setMinimumWidth(700)

        vbox = QVBoxLayout(self)
        grid = QGridLayout(self)
        vbox.addLayout(grid)
        bottom_buttons = QHBoxLayout(self)
        vbox.addLayout(bottom_buttons)

        # ensure processed date is AFTER this date
        self.latest_test_date = datetime.strptime('0001-01-01', '%Y-%m-%d').date()
        self.date_processed = QLineEdit(self)
        self.date_processed.setPlaceholderText("YYYY-MM-DD")
        self.tab = QTabWidget(self)

        grid.addWidget(QLabel("Pool ID:"), 0, 0)
        grid.addWidget(QLabel(self.pool_id), 0, 1)
        grid.addWidget(QLabel("Date Processed:"), 1, 0)
        grid.addWidget(self.date_processed, 1, 1)
        grid.addWidget(QLabel("Pool Status:"), 2, 0)
        grid.addWidget(self.tab, 2, 1)

        scroll_p = QScrollArea(self)
        scroll_n = QScrollArea(self)
        table_p, self.tests_p = self.get_tests('positive')
        table_n, self.tests_n = self.get_tests('negative')
        scroll_p.setWidget(table_p)
        scroll_n.setWidget(table_n)
        self.tab.addTab(scroll_p, 'positive')
        self.tab.addTab(scroll_n, 'negative')

        scroll_p.setWidgetResizable(True)
        scroll_p.setMinimumHeight(350)
        scroll_n.setWidgetResizable(True)
        scroll_n.setMinimumHeight(350)

        # Bottom buttons
        self.back_home = QPushButton("Back (Home)")
        self.process_btn = QPushButton("Process Pool")

        bottom_buttons.addWidget(self.back_home)
        bottom_buttons.addWidget(self.process_btn)

        self.process_btn.clicked.connect(self.handle_process_pool)
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

    def handle_process_pool(self):
        # process pool
        if self.date_processed.text() != '':
            try:
                processed_date = datetime.strptime(self.date_processed.text(), '%Y-%m-%d')
                if processed_date.date() <= self.latest_test_date:
                    popup.Error('The processed date must be after the latest test date in the pool.').exec()
                    return
                pool_status = self.tab.tabText(self.tab.currentIndex())
                self.cursor.callproc('process_pool', [self.pool_id, pool_status, processed_date, self.username])
                self.connection.commit()
                # process tests
                if pool_status == 'positive':
                    status_entries = []  # positive pool
                    for id, selection in self.tests_p.items():
                        status_entries.append(selection)
                    if 'positive' not in status_entries:
                        res = QMessageBox.question(self, 'Warning!', "All test results are negative. Are you "
                                                                             "sure that the pool status should be "
                                                                             "positive?", QMessageBox.Yes |
                                                           QMessageBox.No)
                        if res == QMessageBox.No:
                            return
                    for id, selection in self.tests_p.items():
                        self.cursor.callproc('process_test', [id, selection.currentText()])
                        self.connection.commit()
                else:
                    for id, status in self.tests_n.items():
                        self.cursor.callproc('process_test', [id, 'negative'])
                        self.connection.commit()
                popup.Message('Successful!').exec()
                if self.user_type == "labtech":
                    self.labtech_back()
                elif self.user_type == "labtester":
                    self.labtester_back()
            except ValueError:
                popup.Error('The processed date must be valid and in the format YYYY-MM-DD.').exec()
        else:
            popup.Error('Please enter the processed date.').exec()

    def get_tests(self, tab): # result: True=pos ; False=neg
        """
        Populate tests in this pool
        """
        table = QTableWidget(self)
        table.verticalHeader().hide()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(['Test ID', 'Date Tested', 'Test Result'])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.cursor.execute('SELECT test_id, appt_date, test_status FROM test WHERE pool_id = %s;', [self.pool_id])
        results = self.cursor.fetchall()
        table.setRowCount(len(results))
        tests = {}
        row_num = 0
        for result in results:
            table.setItem(row_num, 0, QTableWidgetItem(result['test_id']))
            test_date = result['appt_date']
            if test_date > self.latest_test_date:
                self.latest_test_date = test_date
            table.setItem(row_num, 1, QTableWidgetItem(test_date.strftime("%Y-%m-%d")))
            if tab == 'positive':
                status = QComboBox(self)
                tests[result['test_id']] = status
                status.addItems(['positive', 'negative'])
                table.setCellWidget(row_num, 2, status)
            else:
                table.setItem(row_num, 2, QTableWidgetItem('negative'))
                tests[result['test_id']] = 'negative'
            row_num += 1
        return table, tests
