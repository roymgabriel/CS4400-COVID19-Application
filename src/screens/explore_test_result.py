###########################################################################################################################################
########################################################## @screen5 #######################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QPushButton, QTableWidget, QVBoxLayout, QScrollArea, QHeaderView, QTableWidgetItem

import src.home_screens.student_home as student_home


class Explore_Test_Result(QDialog):
    def __init__(self, connection, table_ID, username):
        super(Explore_Test_Result, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.student_username = username
        self.table_ID = table_ID

        self.setWindowTitle('Explore Test Result')

        self.back = QPushButton("Back (Home)", self)
        self.back.clicked.connect(self.backHome)

        vbox = QVBoxLayout(self)
        scroll = QScrollArea(self)
        vbox.addWidget(scroll)
        vbox.addWidget(self.back)

        # Tests Results table
        self.tests_results_tbl = QTableWidget(self)
        self.tests_results_tbl.setRowCount(8)
        self.tests_results_tbl.setVerticalHeaderLabels(['Test ID#', 'Date Tested', 'Timeslot', 'Testing Location',
                                                             'Date Processed', 'Pooled Result', 'Individual Result', 'Processed By'])
        self.tests_results_tbl.horizontalHeader().hide()
        fnt = self.tests_results_tbl.font()
        fnt.setPointSize(14)
        self.tests_results_tbl.setFont(fnt)
        fnt.setBold(True)
        self.tests_results_tbl.verticalHeader().setFont(fnt)
        scroll.setWidget(self.tests_results_tbl)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(275)
        scroll.setFixedWidth(225)

        self.tests_results_tbl.verticalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tests_results_tbl.verticalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tests_results_tbl.verticalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tests_results_tbl.verticalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tests_results_tbl.verticalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tests_results_tbl.verticalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tests_results_tbl.verticalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.tests_results_tbl.verticalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)

        self.cursor.execute("CALL  explore_results(%s);", (self.table_ID,))
        self.connection.commit()
        self.cursor.execute("SELECT * FROM covidtest_fall2020.explore_results_result;")

        results = self.cursor.fetchall()

        self.tests_results_tbl.setColumnCount(len(results))
        row_num = 0
        for result in results:
            self.tests_results_tbl.setItem(0, row_num, QTableWidgetItem(str(result['test_id'])))
            self.tests_results_tbl.setItem(1, row_num, QTableWidgetItem(str(result['test_date'])))
            self.tests_results_tbl.setItem(2, row_num, QTableWidgetItem(str(result['timeslot'])))
            self.tests_results_tbl.setItem(3, row_num, QTableWidgetItem(str(result['testing_location'])))
            self.tests_results_tbl.setItem(4, row_num, QTableWidgetItem(str(result['date_processed'])))
            self.tests_results_tbl.setItem(5, row_num, QTableWidgetItem(str(result['pooled_result'])))
            self.tests_results_tbl.setItem(6, row_num, QTableWidgetItem(str(result['individual_result'])))
            self.tests_results_tbl.setItem(7, row_num, QTableWidgetItem(str(result['processed_by'])))
            row_num += 1



    def backHome(self):
        self.close()
        student_home.StudentHome(self.connection, self.student_username).exec()
