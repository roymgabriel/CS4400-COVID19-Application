###########################################################################################################################################
################################################ Below is Functionality Screen ############################################################
###########################################################################################################################################
###########################################################################################################################################
########################################################## @screen4 #######################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget, QHeaderView,\
                                 QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QTableWidgetItem, QMessageBox

import time as t
from datetime import datetime
import src.utils.popups as popup

import src.home_screens.student_home as student_home
import src.screens.explore_test_result as explore_test_result

class Student_View_Test_Result(QDialog):
    def __init__(self, connection, username):
        super(Student_View_Test_Result, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.student_username = username

        self.setWindowTitle('Student View Test Results')

        vbox = QVBoxLayout(self)
        filters = QGridLayout(self)
        self.scroll = QScrollArea(self)
        bottom_buttons = QHBoxLayout(self)
        vbox.addLayout(filters)
        vbox.addWidget(self.scroll)
        vbox.addLayout(bottom_buttons)


        self.tempLine = QLabel()

        self.filter = QPushButton("Filter")
        self.reset = QPushButton("Reset")
        self.timeslot_date_label = QLabel("Timeslot Date:")
        self.date_from = QLineEdit()
        self.date_from.setPlaceholderText("YYYY-MM-DD")
        self.dash_label = QLabel("-")
        self.date_to = QLineEdit()
        self.date_to.setPlaceholderText("YYYY-MM-DD")
        self.status = QLabel("Status:")
        self.comboBox = QComboBox(self)
        self.comboBox.addItem("All")
        self.comboBox.addItem("Pending")
        self.comboBox.addItem("Positive")
        self.comboBox.addItem("Negative")

        self.back = QPushButton("Back (Home)", self)
        self.back.clicked.connect(self.backHome)

        Student_View_Test_Result_hbox = QHBoxLayout(self)
        Student_View_Test_Result_hbox.addWidget(self.status)
        Student_View_Test_Result_hbox.addWidget(self.comboBox)
        Student_View_Test_Result_hbox.addWidget(self.timeslot_date_label)
        Student_View_Test_Result_hbox.addWidget(self.date_from)
        Student_View_Test_Result_hbox.addWidget(self.dash_label)
        Student_View_Test_Result_hbox.addWidget(self.date_to)


        filters.addLayout(Student_View_Test_Result_hbox, 0, 0)

        # Tests Results table
        self.tests_results_tbl = QTableWidget(self)
        self.tests_results_tbl.setColumnCount(5)
        self.tests_results_tbl.setHorizontalHeaderLabels(['Test ID#', 'Timeslot Date', 'Date Processed', 'Pool Status', 'Status'])
        self.tests_results_tbl.verticalHeader().hide()
        fnt = self.tests_results_tbl.font()
        fnt.setPointSize(14)
        self.tests_results_tbl.setFont(fnt)
        fnt.setBold(True)
        self.tests_results_tbl.horizontalHeader().setFont(fnt)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(250)
        self.scroll.setFixedWidth(750)

        self.tests_results_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tests_results_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tests_results_tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tests_results_tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tests_results_tbl.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.cursor.callproc("student_view_results", [self.student_username, None, None, None])
        self.connection.commit()
        self.cursor.execute("SELECT * FROM covidtest_fall2020.student_view_results_result;")
        results = self.cursor.fetchall()


        self.tests_results_tbl.setRowCount(len(results))
        self.tests_results_tbl.setSortingEnabled(False)
        row_num = 0
        for result in results:
            timeslot_date = result['timeslot_date'].strftime("%Y-%m-%d")
            if str(result['date_processed']) not in ['NULL', 'None']:
                date_processed = result['date_processed'].strftime("%Y-%m-%d")
            else:
                date_processed = str(result['date_processed'])
            self.tests_results_tbl.setItem(row_num, 0, QTableWidgetItem(str(result['test_id'])))
            self.tests_results_tbl.setItem(row_num, 1, QTableWidgetItem(timeslot_date))
            self.tests_results_tbl.setItem(row_num, 2, QTableWidgetItem(date_processed))
            self.tests_results_tbl.setItem(row_num, 3, QTableWidgetItem(str(result['pool_status'])))
            self.tests_results_tbl.setItem(row_num, 4, QTableWidgetItem(str(result['test_status'])))
            row_num += 1

        self.tests_results_tbl.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.scroll.setWidget(self.tests_results_tbl)


        bottom_buttons.addWidget(self.back)
        bottom_buttons.addWidget(self.reset)
        bottom_buttons.addWidget(self.filter)

        # Add clicking function
        self.tests_results_tbl.clicked.connect(self.explore_test_result)
        self.filter.clicked.connect(self.handle_filter_btn)
        self.reset.clicked.connect(self.reset_func)


    def backHome(self):
        self.close()
        student_home.StudentHome(self.connection, self.student_username).exec()

    def sort_table(self, logicalIndex):
        if logicalIndex == 1 or logicalIndex == 2 or logicalIndex == 3 or logicalIndex == 4:
            self.tests_results_tbl.setSortingEnabled(True)
            t.sleep(0.1)
            self.tests_results_tbl.setSortingEnabled(False)

    def reset_func(self):
        self.comboBox.setCurrentText("All")
        self.date_from.clear()
        self.date_to.clear()

        self.tests_results_tbl.verticalHeader().hide()
        self.tests_results_tbl.setColumnCount(5)
        self.tests_results_tbl.setHorizontalHeaderLabels(['Test ID#', 'Timeslot Date', 'Date Processed', 'Pool Status', 'Status'])
        fnt = self.tests_results_tbl.font()
        fnt.setPointSize(14)
        self.tests_results_tbl.setFont(fnt)
        fnt.setBold(True)
        self.tests_results_tbl.horizontalHeader().setFont(fnt)

        self.cursor.callproc("student_view_results", [self.student_username, None, None, None])
        self.connection.commit()
        self.cursor.execute("SELECT * FROM covidtest_fall2020.student_view_results_result;")
        results = self.cursor.fetchall()

        self.tests_results_tbl.setRowCount(len(results))
        row_num = 0
        for result in results:
            timeslot_date = result['timeslot_date'].strftime("%Y-%m-%d")
            if str(result['date_processed']) not in ['NULL', 'None']:
                date_processed = result['date_processed'].strftime("%Y-%m-%d")
            else:
                date_processed = str(result['date_processed'])
            self.tests_results_tbl.setItem(row_num, 0, QTableWidgetItem(str(result['test_id'])))
            self.tests_results_tbl.setItem(row_num, 1, QTableWidgetItem(timeslot_date))
            self.tests_results_tbl.setItem(row_num, 2, QTableWidgetItem(date_processed))
            self.tests_results_tbl.setItem(row_num, 3, QTableWidgetItem(str(result['pool_status'])))
            self.tests_results_tbl.setItem(row_num, 4, QTableWidgetItem(str(result['test_status'])))
            row_num += 1


        self.tests_results_tbl.clicked.connect(self.explore_test_result)
        self.scroll.setWidget(self.tests_results_tbl)


    def explore_test_result(self, item):
        if item.column() == 0:
            if self.tests_results_tbl.item(item.row(), 2).text() not in  ['NULL', 'None']:
                self.table_ID = item.data()
                self.close()
                explore_test_result.Explore_Test_Result(self.connection, self.table_ID, self.student_username).exec()
            else:
                QMessageBox.about(self, "ERROR!", "Can only Explore Test Results if it has been processed!")

    def handle_filter_btn(self):
        query = 'CALL student_view_results("' + self.student_username + '",'
        if self.comboBox.currentText() == "Pending":
            query += '"' + self.comboBox.currentText() + '",'
        elif self.comboBox.currentText() == "Positive":
            query += '"' + self.comboBox.currentText() + '",'
        elif self.comboBox.currentText() == "Negative":
            query += '"' + self.comboBox.currentText() + '",'
        else: # if it was "ALL" (Default)
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
                query += '"' + str(date_to) + '");'
            except ValueError:
                popup.Error('Date must be valid and in the format YYYY-MM-DD.').exec()
                return
        else:
            query += 'NULL);'


        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            QMessageBox.about(self, "Error!", "Please enter dates in valid date format!")

        self.cursor.execute('SELECT * FROM covidtest_fall2020.student_view_results_result;')
        results = self.cursor.fetchall()

        self.tests_results_tbl.setRowCount(len(results))
        row_num = 0
        for result in results:
            timeslot_date = result['timeslot_date'].strftime("%Y-%m-%d")
            if str(result['date_processed']) not in ['NULL', 'None']:
                date_processed = result['date_processed'].strftime("%Y-%m-%d")
            else:
                date_processed = str(result['date_processed'])
            self.tests_results_tbl.setItem(row_num, 0, QTableWidgetItem(str(result['test_id'])))
            self.tests_results_tbl.setItem(row_num, 1, QTableWidgetItem(timeslot_date))
            self.tests_results_tbl.setItem(row_num, 2, QTableWidgetItem(date_processed))
            self.tests_results_tbl.setItem(row_num, 3, QTableWidgetItem(str(result['pool_status'])))
            self.tests_results_tbl.setItem(row_num, 4, QTableWidgetItem(str(result['test_status'])))
            row_num += 1
