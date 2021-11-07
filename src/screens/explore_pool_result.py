###########################################################################################################################################
########################################################## @screen16 ######################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QScrollArea, QLabel, QTableWidget, QTableWidgetItem, \
    QPushButton, QHeaderView

import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.labtech_home as labtech_home


class ExplorePoolResult(QDialog):
    def __init__(self, connection, user_type, username, pool_ID):
        super(ExplorePoolResult, self).__init__()
        self.setWindowTitle('Explore Pool Result')
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Explore Pool Result')

        self.pool_metadata = QLabel("Pool Metadata:")
        self.tests_in_pool = QLabel("Tests In Pool:")

        self.back_home = QPushButton("Back (Home)", self)

        if user_type == "labtech":
            self.back_home.clicked.connect(self.labtech_back)
        elif user_type == "labtester":
            self.back_home.clicked.connect(self.labtester_back)

        vbox = QVBoxLayout(self)
        headers = QGridLayout(self)
        headers2 = QGridLayout(self)
        scroll = QScrollArea(self)
        scroll2 = QScrollArea(self)
        vbox.addLayout(headers)
        vbox.addWidget(scroll)
        vbox.addLayout(headers2)
        vbox.addWidget(scroll2)
        vbox.addWidget(self.back_home)

        # Pool Metadata Header
        headers.addWidget(self.pool_metadata, 0, 0)

        # Pool Metadata table
        self.pool_md_tbl = QTableWidget(self)
        self.pool_md_tbl.setColumnCount(4)
        self.pool_md_tbl.setHorizontalHeaderLabels(['Pool ID', 'Date Processed', 'Pooled Result', 'Processed By'])
        self.pool_md_tbl.verticalHeader().hide()
        fnt = self.pool_md_tbl.font()
        fnt.setPointSize(14)
        self.pool_md_tbl.setFont(fnt)
        fnt.setBold(True)
        self.pool_md_tbl.horizontalHeader().setFont(fnt)
        scroll.setWidget(self.pool_md_tbl)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(58.5)
        scroll.setFixedWidth(550)

        self.pool_md_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.pool_md_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.pool_md_tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.pool_md_tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)


        self.cursor.callproc('pool_metadata', ([pool_ID]))
        self.connection.commit()
        self.cursor.execute('SELECT * FROM covidtest_fall2020.pool_metadata_result;')
        results = self.cursor.fetchall()

        self.pool_md_tbl.setRowCount(len(results))
        row_num = 0
        for result in results:
            self.pool_md_tbl.setItem(row_num, 0, QTableWidgetItem(str(result['pool_id'])))
            self.pool_md_tbl.setItem(row_num, 1, QTableWidgetItem(str(result['date_processed'])))
            self.pool_md_tbl.setItem(row_num, 2, QTableWidgetItem(str(result['pooled_result'])))
            self.pool_md_tbl.setItem(row_num, 3, QTableWidgetItem(str(result['processed_by'])))
            row_num += 1

        # Pool Tests Header
        headers2.addWidget(self.tests_in_pool, 0, 0)

        # Pool Tests Table
        self.pool_tests_tbl = QTableWidget(self)
        self.pool_tests_tbl.setColumnCount(4)
        self.pool_tests_tbl.setHorizontalHeaderLabels(['Test ID#', 'Date Tested', 'Testing Site', 'Test Result'])
        self.pool_tests_tbl.verticalHeader().hide()
        fnt = self.pool_tests_tbl.font()
        fnt.setPointSize(14)
        self.pool_tests_tbl.setFont(fnt)
        fnt.setBold(True)
        self.pool_tests_tbl.horizontalHeader().setFont(fnt)
        scroll2.setWidget(self.pool_tests_tbl)
        scroll2.setWidgetResizable(True)
        scroll2.setFixedHeight(200)
        scroll2.setFixedWidth(550)


        self.pool_tests_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.pool_tests_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.pool_tests_tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.pool_tests_tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # update table to include all appointments

        self.cursor.callproc('tests_in_pool', ([pool_ID]))
        self.connection.commit()
        self.cursor.execute('SELECT * FROM covidtest_fall2020.tests_in_pool_result;')
        results1 = self.cursor.fetchall()

        self.pool_tests_tbl.setRowCount(len(results1))
        row_num = 0
        for result in results1:
            self.pool_tests_tbl.setItem(row_num, 0, QTableWidgetItem(str(result['test_id'])))
            self.pool_tests_tbl.setItem(row_num, 1, QTableWidgetItem(str(result['date_tested'])))
            self.pool_tests_tbl.setItem(row_num, 2, QTableWidgetItem(str(result['testing_site'])))
            self.pool_tests_tbl.setItem(row_num, 3, QTableWidgetItem(str(result['test_result'])))
            row_num += 1


    def labtech_back(self):
        self.close()
        labtech_home.LabTechHome(self.connection, self.username).exec()
    def labtester_back(self):
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.username).exec()
