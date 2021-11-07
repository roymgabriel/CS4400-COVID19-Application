# Screen 7

import time as t
from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QScrollArea, QHBoxLayout, QComboBox, QLineEdit, QLabel, \
    QTableWidget, QTableWidgetItem, QPushButton

import src.home_screens.student_home as student_home
import src.utils.popups as popup


class SignUpForATest(QDialog):
    """
    Testing:
        1. Check if the tests shown are in the student's location
        2. Verify that only columns Date, Time, Test Site should be sortable
        3. Verify that if a student currently has a pending test, the sign up button should be disable
            - initial DB state: aallman302 has a pending test, rgreen97 does not
        4. Verify correctness when applying different filters
        5. Verify that after signing up, the sign up button is grayed out and the test shows up in DB as pending
        6. Check if back button goes to the right home screen
    """
    def __init__(self, connection, username):
        super(SignUpForATest, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username
        self.selected_appt = []
        self.appts = {}
        self.hasPendingTest = False

        self.setWindowTitle('Sign Up for A Test')
        self.setFixedHeight(500)
        self.setMinimumWidth(700)

        vbox = QVBoxLayout(self)
        filters = QGridLayout(self)
        self.scroll = QScrollArea(self)
        bottom_btns = QHBoxLayout(self)
        vbox.addLayout(filters)
        vbox.addWidget(self.scroll)
        vbox.addLayout(bottom_btns)

        # Site
        self.sites = QComboBox(self)
        self.cursor.execute('SELECT location FROM student WHERE student_username = %s', [self.username])
        location = self.cursor.fetchall()[0]['location']
        self.cursor.execute('SELECT site_name FROM site WHERE location = %s', [location])
        site_names = self.cursor.fetchall()
        site_list = ['ALL',]
        for site_name in site_names:
            site_list.append(site_name['site_name'])
        self.sites.addItems(site_list)

        # Date
        self.from_date = QLineEdit(self)
        self.from_date.setPlaceholderText("YYYY-MM-DD")
        self.to_date = QLineEdit(self)
        self.to_date.setPlaceholderText("YYYY-MM-DD")

        # Time
        self.from_time = QLineEdit(self)
        self.from_time.setPlaceholderText("HH:MM")
        self.to_time = QLineEdit(self)
        self.to_time.setPlaceholderText("HH:MM")

        filters.addWidget(QLabel("Testing Site:"), 0, 0)
        filters.addWidget(self.sites, 0, 1)
        filters.addWidget(QLabel("Date:"), 0, 2)
        filters.addWidget(self.from_date, 0, 3)
        filters.addWidget(self.to_date, 1, 3)
        filters.addWidget(QLabel("-"), 0, 4)
        filters.addWidget(QLabel("Time"), 0, 5)
        filters.addWidget(self.from_time, 0, 6)
        filters.addWidget(self.to_time, 1, 6)
        filters.addWidget(QLabel("-"), 0, 7)

        # Available appointment table
        self.table = QTableWidget(self)
        self.table.verticalHeader().hide()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Date', 'Time', 'Site Address', 'Test Site', 'Sign Up'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.get_appts([self.username, None, None, None, None, None])
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(300)

        # Bottom buttons
        self.back_btn = QPushButton("Back (Home)")
        self.reset_btn = QPushButton("Reset")
        self.filter_btn = QPushButton("Filter")
        self.signup_btn = QPushButton("Sign Up")

        bottom_btns.addWidget(self.back_btn)
        bottom_btns.addWidget(self.reset_btn)
        bottom_btns.addWidget(self.filter_btn)
        bottom_btns.addWidget(self.signup_btn)

        # disable sign up button if student has a pending test
        self.update_signup_btn()

        self.back_btn.clicked.connect(self.handle_back)
        self.reset_btn.clicked.connect(self.handle_reset)
        self.filter_btn.clicked.connect(self.handle_filter)
        self.signup_btn.clicked.connect(self.handle_signup)

    def handle_back(self):
        self.close()
        student_home.StudentHome(self.connection, self.username).exec()

    def handle_filter(self):
        params = [self.username,]
        # site
        if self.sites.currentText() == 'ALL':
            params.append(None)
        else:
            params.append(self.sites.currentText())
        try:
            # from date
            if self.from_date.text() == '':
                params.append(None)
            else:
                params.append(datetime.strptime(self.from_date.text(), '%Y-%m-%d'))
            # to date
            if self.to_date.text() == '':
                params.append(None)
            else:
                params.append(datetime.strptime(self.to_date.text(), '%Y-%m-%d'))
        except ValueError:
            popup.Error('Date must be valid and in the format YYYY-MM-DD.').exec()
            return
        try:
            # from time
            if self.from_time.text() == '':
                params.append(None)
            else:
                params.append(datetime.strptime(self.from_time.text(), '%H:%M'))
            # to time
            if self.to_time.text() == '':
                params.append(None)
            else:
                params.append(datetime.strptime(self.to_time.text(), '%H:%M'))
        except ValueError:
            popup.Error('Time must be valid and in the format HH:MM.').exec()
            return
        self.get_appts(params)

    def handle_signup(self):
        self.update_signup_btn()
        self.selected_appt = [self.username] + self.selected_appt + [str(self.get_new_id())]
        self.cursor.callproc('test_sign_up', self.selected_appt)
        self.connection.commit()
        self.update_signup_btn()
        popup.Message("Successful!").exec()

    def get_new_id(self):
        self.cursor.execute('SELECT test_id FROM test;')
        results = self.cursor.fetchall()
        ids = []
        for result in results:
            ids.append(int(result['test_id']))
        return max(ids) + 1

    def handle_reset(self):
        # clear results
        self.get_appts([self.username, None, None, None, None, None])
        # clear the filters
        self.sites.setCurrentText('ALL')
        self.from_date.clear()
        self.to_date.clear()
        self.from_time.clear()
        self.to_time.clear()

    def get_appts(self, params):
        self.cursor.callproc('test_sign_up_filter', params)
        self.cursor.execute('SELECT * FROM test_sign_up_filter_result;')
        results = self.cursor.fetchall()

        self.table.setRowCount(len(results))
        self.table.setSortingEnabled(False) # important: this line must be executed before populating table contents
        row_num = 0
        self.appts.clear()
        for result in results:
            date = result['appt_date'].strftime("%Y-%m-%d")
            self.table.setItem(row_num, 0, QTableWidgetItem(date))

            ##### Q: please don't delete these lines; I might need them for other screens
            # hours, remainder = divmod(result['appt_time'].seconds, 3600)
            # minutes, seconds = divmod(remainder, 60)
            # if minutes < 10:
            #     minutes = '0' + str(minutes)
            # else:
            #     minutes = str(minutes)
            # time = str(hours) + ':' + minutes
            # self.table.setItem(row_num, 1, QTableWidgetItem(time))

            # for the sorting to work correctly, the hour must have 2 digits
            time = str(result['appt_time'])
            if time[1] == ':':
                time = '0' + time
            time = time[:5] # truncate the seconds
            self.table.setItem(row_num, 1, QTableWidgetItem(time))
            self.table.setItem(row_num, 2, QTableWidgetItem(result['street']))
            site = result['site_name']
            self.table.setItem(row_num, 3, QTableWidgetItem(site))
            radio = QtWidgets.QRadioButton(self)
            radio.toggled.connect(self.on_clicked)
            self.appts[(site, date, time)] = radio
            self.table.setCellWidget(row_num, 4, radio)
            row_num += 1
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.scroll.setWidget(self.table)

    def on_clicked(self):
        if not self.hasPendingTest:
            for appt, radioBtn in self.appts.items():
                print((appt, radioBtn))
                if radioBtn.isChecked():
                    self.selected_appt = list(appt)
                    return

    def sort_table(self, logicalIndex):
        if logicalIndex == 0 or logicalIndex == 3 or logicalIndex == 1:
            self.table.setSortingEnabled(True)
            t.sleep(0.1)
            self.table.setSortingEnabled(False)

    def update_signup_btn(self):
        self.cursor.callproc('has_pending_test', [self.username])
        self.cursor.execute('SELECT * FROM has_pending_test_result')
        result = self.cursor.fetchall()
        if len(result) == 0:
            self.signup_btn.setDisabled(False)
        else:
            self.signup_btn.setDisabled(True)
            self.hasPendingTest = True
