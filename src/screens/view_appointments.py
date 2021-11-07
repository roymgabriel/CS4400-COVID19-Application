###########################################################################################################################################
########################################################## @screen13
# ######################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QRadioButton, QLineEdit, QPushButton, QVBoxLayout, \
    QHBoxLayout, QTableWidgetItem, QGridLayout, QScrollArea, QMessageBox, QTableWidget, QHeaderView


import time as t
from datetime import datetime
import src.utils.popups as popup


import src.home_screens.admin_home as admin_home
import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.tester_home as tester_home


class View_Appointments(QDialog):
    def __init__(self, connection, user_type, username):
        super(View_Appointments, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username
        self.user_type = user_type

        self.setWindowTitle('View Appointments')

        vbox = QVBoxLayout(self)
        filters = QGridLayout(self)
        self.scroll = QScrollArea(self)
        bottom_buttons = QHBoxLayout(self)
        vbox.addLayout(filters)
        vbox.addWidget(self.scroll)
        vbox.addLayout(bottom_buttons)

        self.site_name = QLabel("Testing Site:")
        self.cursor.execute("SELECT DISTINCT site FROM covidtest_fall2020.WORKING_AT;")
        self.list_of_sites = []
        sites = self.cursor.fetchall()
        for i in sites:
            self.list_of_sites.append(i["site"])

        self.comboBox = QComboBox(self) # need to find way to make it dynamic when adding a testing site...
        self.comboBox.addItem("ALL")
        self.comboBox.addItems(self.list_of_sites)


        self.availability = QLabel("Availability:")
        self.booked_only = QRadioButton("Show Booked Only")
        self.available_only = QRadioButton("Show Available Only")
        self.show_all = QRadioButton("Show All")
        self.show_all.setChecked(True)

        self.date_label = QLabel("Date:")
        self.date_from = QLineEdit()
        self.date_from.setPlaceholderText("YYYY-MM-DD")
        self.dash_label = QLabel("-")
        self.date_to = QLineEdit()
        self.date_to.setPlaceholderText("YYYY-MM-DD")

        self.time_label = QLabel("Time:")
        self.time_from = QLineEdit()
        self.time_from.setPlaceholderText("HH:MM")
        self.dash_label1 = QLabel("-")
        self.time_to = QLineEdit()
        self.time_to.setPlaceholderText("HH:MM")

        self.filter = QPushButton("Filter")
        self.filter.clicked.connect(self.handle_filter_btn)
        self.reset = QPushButton("Reset")
        self.reset.clicked.connect(self.reset_func)
        self.back_home = QPushButton("Back (Home)", self)


        View_Appointments_hbox1 = QHBoxLayout(self)
        View_Appointments_hbox1.addWidget(self.site_name)
        View_Appointments_hbox1.addWidget(self.comboBox)

        View_Appointments_hbox2 = QHBoxLayout(self)
        View_Appointments_hbox2.addWidget(self.date_label)
        View_Appointments_hbox2.addWidget(self.date_from)
        View_Appointments_hbox2.addWidget(self.dash_label)
        View_Appointments_hbox2.addWidget(self.date_to)

        View_Appointments_hbox3 = QHBoxLayout(self)
        View_Appointments_hbox3.addWidget(self.time_label)
        View_Appointments_hbox3.addWidget(self.time_from)
        View_Appointments_hbox3.addWidget(self.dash_label1)
        View_Appointments_hbox3.addWidget(self.time_to)

        View_Appointments_vbox1 = QVBoxLayout(self)
        View_Appointments_vbox1.addLayout(View_Appointments_hbox2)
        View_Appointments_vbox1.addLayout(View_Appointments_hbox3)

        View_Appointments_vbox2 = QVBoxLayout(self)
        View_Appointments_vbox2.addWidget(self.booked_only)
        View_Appointments_vbox2.addWidget(self.available_only)
        View_Appointments_vbox2.addWidget(self.show_all)

        View_Appointments_hbox4 = QHBoxLayout(self)
        View_Appointments_hbox4.addWidget(self.availability)
        View_Appointments_hbox4.addLayout(View_Appointments_vbox2)

        View_Appointments_vbox4 = QVBoxLayout(self)
        View_Appointments_vbox4.addLayout(View_Appointments_hbox1)
        View_Appointments_vbox4.addLayout(View_Appointments_hbox4)

        # add filters
        filters.addLayout(View_Appointments_vbox4, 0, 0)
        filters.addLayout(View_Appointments_vbox1, 0, 1)

        # Appt table
        self.appt_tbl = QTableWidget(self)
        self.appt_tbl.setColumnCount(5)
        self.appt_tbl.setHorizontalHeaderLabels(['Date', 'Time', 'Test Site',
                                                 'Location', 'User'])
        self.appt_tbl.verticalHeader().hide()
        fnt = self.appt_tbl.font()
        fnt.setPointSize(14)
        self.appt_tbl.setFont(fnt)
        fnt.setBold(True)
        self.appt_tbl.horizontalHeader().setFont(fnt)
        self.scroll.setWidget(self.appt_tbl)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(250)
        self.scroll.setFixedWidth(750)

        self.appt_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.appt_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.appt_tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.appt_tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.appt_tbl.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # update table to include all appointments
        self.cursor.callproc("view_appointments", [None, None, None, None, None, None ])
        self.cursor.execute('SELECT * FROM covidtest_fall2020.view_appointments_result;')
        results = self.cursor.fetchall()

        self.appt_tbl.setRowCount(len(results))
        self.appt_tbl.setSortingEnabled(False)

        row_num = 0
        for result in results:
            date = result['appt_date'].strftime("%Y-%m-%d")
            # for the sorting to work correctly, the hour must have 2 digits
            time = str(result['appt_time'])
            if time[1] == ':':
                time = '0' + time
            time = time[:5] # truncate the seconds
            self.appt_tbl.setItem(row_num, 0, QTableWidgetItem(date))
            self.appt_tbl.setItem(row_num, 1, QTableWidgetItem(time))
            self.appt_tbl.setItem(row_num, 2, QTableWidgetItem(str(result['site_name'])))
            self.appt_tbl.setItem(row_num, 3, QTableWidgetItem(str(result['location'])))
            self.appt_tbl.setItem(row_num, 4, QTableWidgetItem(str(result['username'])))
            row_num += 1

        self.appt_tbl.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.scroll.setWidget(self.appt_tbl)

        bottom_buttons.addWidget(self.back_home)
        bottom_buttons.addWidget(self.reset)
        bottom_buttons.addWidget(self.filter)


        if self.user_type == "tester":
            self.back_home.clicked.connect(self.tester_back)
        elif self.user_type == "admin":
            self.back_home.clicked.connect(self.admin_back)
        elif self.user_type == "labtester":
            self.back_home.clicked.connect(self.labtester_back)

    def tester_back(self):
        self.close()
        tester_home.TesterHome(self.connection, self.username).exec()
    def admin_back(self):
        self.close()
        admin_home.AdminHome(self.connection, self.username).exec()
    def labtester_back(self):
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.username).exec()


    def reset_func(self):
        self.comboBox.setCurrentText("ALL")
        self.show_all.setChecked(True)
        self.date_from.clear()
        self.date_to.clear()
        self.time_from.clear()
        self.time_to.clear()

        self.date_from.setPlaceholderText("YYYY-MM-DD")
        self.date_to.setPlaceholderText("YYYY-MM-DD")
        self.time_from.setPlaceholderText("HH:MM:SS")
        self.time_to.setPlaceholderText("HH:MM:SS")

        self.appt_tbl.verticalHeader().hide()
        self.appt_tbl.setColumnCount(5)
        self.appt_tbl.setHorizontalHeaderLabels(['Appt Date', 'Appt Time', 'Site Name',
                                                 'Location', 'username'])

        self.cursor.callproc("view_appointments", [None, None, None, None, None, None ])
        self.cursor.execute('SELECT * FROM covidtest_fall2020.view_appointments_result;')
        results = self.cursor.fetchall()

        self.appt_tbl.setRowCount(len(results))
        self.appt_tbl.setSortingEnabled(False)

        row_num = 0
        for result in results:
            date = result['appt_date'].strftime("%Y-%m-%d")
            # for the sorting to work correctly, the hour must have 2 digits
            time = str(result['appt_time'])
            if time[1] == ':':
                time = '0' + time
            time = time[:5] # truncate the seconds
            self.appt_tbl.setItem(row_num, 0, QTableWidgetItem(date))
            self.appt_tbl.setItem(row_num, 1, QTableWidgetItem(time))
            self.appt_tbl.setItem(row_num, 2, QTableWidgetItem(str(result['site_name'])))
            self.appt_tbl.setItem(row_num, 3, QTableWidgetItem(str(result['location'])))
            self.appt_tbl.setItem(row_num, 4, QTableWidgetItem(str(result['username'])))
            row_num += 1

        self.appt_tbl.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.scroll.setWidget(self.appt_tbl)

    def sort_table(self, logicalIndex):
        if logicalIndex in [0, 1, 2, 3, 4]:
            self.appt_tbl.setSortingEnabled(True)
            t.sleep(0.1)
            self.appt_tbl.setSortingEnabled(False)

    def handle_filter_btn(self):
        query = 'CALL view_appointments('
        if self.comboBox.currentText() != "" and self.comboBox.currentText() != "ALL":
            query += '"' + self.comboBox.currentText() + '",'
        else:
            query += 'NULL,'

        if self.date_from.text() != "":
            try:
                date_from = datetime.strptime(self.date_from.text(), '%Y-%m-%d')
                query += '"' + str(date_from) + '",'
            except ValueError:
                popup.Error('Date must be valid and in the format YYYY-MM-DD.').exec()
                return
        else:
            query += 'NULL,'

        if self.date_to.text() != "":
            try:
                date_to = datetime.strptime(self.date_to.text(), '%Y-%m-%d')
                query += '"' + str(date_to) + '",'
            except ValueError:
                popup.Error('Date must be valid and in the format YYYY-MM-DD.').exec()
                return
        else:
            query += 'NULL,'

        if self.time_from.text() != "":
            try:
                time_from = datetime.strptime(self.time_from.text(), '%H:%M')
                query += '"' + str(time_from) + '",'
            except ValueError:
                popup.Error('Time must be valid and in the format HH:MM.').exec()
                return
        else:
            query += 'NULL,'

        if self.time_to.text() != "":
            try:
                time_to = datetime.strptime(self.time_to.text(), '%H:%M')
                query += '"' + str(time_to) + '",'
            except ValueError:
                popup.Error('Time must be valid and in the format HH:MM.').exec()
                return
        else:
            query += 'NULL,'

        if self.booked_only.isChecked():
            query += '0);'
        elif self.available_only.isChecked():
            query += '1);'
        else: # showing all
            query += 'NULL);'


        # print(query)
        try:
            self.cursor.execute(query)
        except:
            QMessageBox.about(self, "Error!", "Please enter dates in valid date format and time in valid time format!")
        self.cursor.execute('SELECT * FROM covidtest_fall2020.view_appointments_result;')
        results = self.cursor.fetchall()

        self.appt_tbl.setRowCount(len(results))
        row_num = 0
        for result in results:
            date = result['appt_date'].strftime("%Y-%m-%d")
            # for the sorting to work correctly, the hour must have 2 digits
            time = str(result['appt_time'])
            if time[1] == ':':
                time = '0' + time
            time = time[:5] # truncate the seconds
            self.appt_tbl.setItem(row_num, 0, QTableWidgetItem(str(result['appt_date'])))
            self.appt_tbl.setItem(row_num, 1, QTableWidgetItem(time))
            self.appt_tbl.setItem(row_num, 2, QTableWidgetItem(str(result['site_name'])))
            self.appt_tbl.setItem(row_num, 3, QTableWidgetItem(str(result['location'])))
            self.appt_tbl.setItem(row_num, 4, QTableWidgetItem(str(result['username'])))
            row_num += 1
