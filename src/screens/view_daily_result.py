# screen 18
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QPushButton, QTableWidget, QTableWidgetItem

import src.home_screens.admin_home as admin_home
import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.labtech_home as labtech_home
import src.home_screens.student_home as student_home
import src.home_screens.tester_home as tester_home


class ViewDailyResults(QDialog):
    """
    Testing:
        1. Check if all columns' headers and contents' formats are correct
        2. Check if back button goes to the right home screen
    """
    def __init__(self, connection, user_type, username):
        super(ViewDailyResults, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('View Daily Results')
        self.setFixedHeight(500)
        self.setMinimumWidth(700)

        vbox = QVBoxLayout(self)
        scroll = QScrollArea(self)
        back_btn = QPushButton("Back (Home)")
        vbox.addWidget(scroll)
        vbox.addWidget(back_btn)

        scroll.setWidget(self.query_daily_results())
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)

        if user_type == "student":
            back_btn.clicked.connect(self.student_back)
        elif user_type == "labtech":
            back_btn.clicked.connect(self.labtech_back)
        elif user_type == "tester":
            back_btn.clicked.connect(self.tester_back)
        elif user_type == "admin":
            back_btn.clicked.connect(self.admin_back)
        elif user_type == "labtester":
            back_btn.clicked.connect(self.labtester_back)

    def student_back(self):
        self.close()
        student_home.StudentHome(self.connection, self.username).exec()

    def labtech_back(self):
        self.close()
        labtech_home.LabTechHome(self.connection, self.username).exec()

    def tester_back(self):
        self.close()
        tester_home.TesterHome(self.connection, self.username).exec()

    def admin_back(self):
        self.close()
        admin_home.AdminHome(self.connection, self.username).exec()

    def labtester_back(self):
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.username).exec()

    def query_daily_results(self):
        table = QTableWidget(self)
        table.verticalHeader().hide()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Date', 'Tests Processed', 'Positive Count', 'Positive Percent'])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        self.cursor.execute('CALL daily_results();')
        self.cursor.execute('SELECT * from daily_results_result;')
        results = self.cursor.fetchall()
        table.setRowCount(len(results))
        row_num = 0
        for result in results:
            table.setItem(row_num, 0, QTableWidgetItem(result['process_date'].strftime("%Y-%m-%d")))
            table.setItem(row_num, 1, QTableWidgetItem(str(result['num_tests'])))
            table.setItem(row_num, 2, QTableWidgetItem(str(result['pos_tests'])))
            table.setItem(row_num, 3, QTableWidgetItem(str(result['pos_percent']) + '%'))
            row_num += 1
        return table
