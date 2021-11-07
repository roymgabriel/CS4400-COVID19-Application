###########################################################################################################################################
########################################################## @screen6 #######################################################################
###########################################################################################################################################

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QTableView, QVBoxLayout, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView

import src.home_screens.admin_home as admin_home
import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.labtech_home as labtech_home
import src.home_screens.student_home as student_home
import src.home_screens.tester_home as tester_home


class AggregateResult(QDialog):
    def __init__(self, connection, user_type, username):
        super(AggregateResult, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username
        self.user_type = user_type
        self.setWindowTitle("View Aggregate Results")

        self.agg_location = QLabel("Location:")
        self.agg_housing = QLabel("Housing:")
        self.agg_site = QLabel("Testing Site:")
        self.agg_date_processed = QLabel("Date Processed:")
        self.agg_dash = QLabel(" - ")
        self.agg_begin_date = QLineEdit(self)
        self.agg_begin_date.setPlaceholderText("YYYY-MM-DD")
        self.agg_end_date = QLineEdit(self)
        self.agg_end_date.setPlaceholderText("YYYY-MM-DD")

        # \d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])
        date_reg_text = QRegExp("\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])")
        date_validator = QRegExpValidator(date_reg_text)
        self.agg_begin_date.setValidator(date_validator)
        self.agg_end_date.setValidator(date_validator)

        self.agg_location_dropdown = QComboBox(self)
        self.agg_location_dropdown.addItem("ALL")
        self.agg_location_dropdown.addItem("West")
        self.agg_location_dropdown.addItem("East")

        self.agg_housing_dropdown = QComboBox(self)
        self.agg_housing_dropdown.addItem("ALL")
        self.agg_housing_dropdown.addItem("Student Housing")
        self.agg_housing_dropdown.addItem("Greek Housing")
        self.agg_housing_dropdown.addItem("Off-Campus House")
        self.agg_housing_dropdown.addItem("Off-Campus Apartments")

        self.cursor.execute("select * from site;")
        site_fetch = self.cursor.fetchall()
        site_list = ["ALL"]
        for i in site_fetch:
            site_list.append(i["site_name"])
        self.agg_site_dropdown = QComboBox(self)
        self.agg_site_dropdown.addItems(site_list)

        self.back_home = QPushButton("Back(Home)")
        self.filter = QPushButton("Filter")
        self.reset = QPushButton("Reset")

        self.missing_positive = {'test_status': 'positive', 'num_of_test': 0, 'percentage': '0.00'}
        self.missing_negative = {'test_status': 'negative', 'num_of_test': 0, 'percentage': '0.00'}
        self.missing_pending = {'test_status': 'pending', 'num_of_test': 0, 'percentage': '0.00'}

        self.cursor.execute("CALL aggregate_results(NULL, NULL, NULL, NULL, NULL);")
        self.cursor.execute("select * from aggregate_results_result;")
        agg_fetch = self.cursor.fetchall()

        if len(agg_fetch) == 0:
            agg_fetch = []

        if len(agg_fetch) < 3:
            check_missing = []
            for i in agg_fetch:
                check_missing.append(i['test_status'])

            if len(agg_fetch) == 2:
                if "positive" not in check_missing:
                    agg_fetch.append(self.missing_positive)
                elif "negative" not in check_missing:
                    agg_fetch.insert(0, self.missing_negative)
                elif "pending" not in check_missing:
                    agg_fetch.insert(1, self.missing_pending)
            elif len(agg_fetch) == 1:
                if "pending" in check_missing:
                    agg_fetch.append(self.missing_positive)
                    agg_fetch.insert(0, self.missing_negative)
                elif "positive" in check_missing:
                    agg_fetch.insert(0, self.missing_pending)
                    agg_fetch.insert(0, self.missing_negative)
                elif "negative" in check_missing:
                    agg_fetch.append(self.missing_pending)
                    agg_fetch.append(self.missing_positive)
            elif len(agg_fetch) == 0:
                agg_fetch.append(self.missing_negative)
                agg_fetch.append(self.missing_pending)
                agg_fetch.append(self.missing_positive)

        self.agg_fetch_table = QTableWidget()
        self.agg_fetch_table.setRowCount(3)
        self.agg_fetch_table.setColumnCount(3)
        percent0 = str(agg_fetch[0]["percentage"]) + "%"
        percent1 = str(agg_fetch[1]["percentage"]) + "%"
        percent2 = str(agg_fetch[2]["percentage"]) + "%"
        self.agg_fetch_table.setItem(0, 0, QTableWidgetItem(agg_fetch[2]["test_status"]))
        self.agg_fetch_table.setItem(1, 0, QTableWidgetItem(agg_fetch[0]["test_status"]))
        self.agg_fetch_table.setItem(2, 0, QTableWidgetItem(agg_fetch[1]["test_status"]))
        self.agg_fetch_table.setItem(0, 1, QTableWidgetItem(str(agg_fetch[2]["num_of_test"])))
        self.agg_fetch_table.setItem(1, 1, QTableWidgetItem(str(agg_fetch[0]["num_of_test"])))
        self.agg_fetch_table.setItem(2, 1, QTableWidgetItem(str(agg_fetch[1]["num_of_test"])))
        self.agg_fetch_table.setItem(0, 2, QTableWidgetItem(percent2))
        self.agg_fetch_table.setItem(1, 2, QTableWidgetItem(percent0))
        self.agg_fetch_table.setItem(2, 2, QTableWidgetItem(percent1))
        self.agg_fetch_table.setHorizontalHeaderLabels(
            ["Total", str(agg_fetch[0]["num_of_test"] + agg_fetch[1]["num_of_test"] + agg_fetch[2]["num_of_test"]),
             "100%"])
        self.agg_fetch_table.verticalHeader().hide()
        self.agg_fetch_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.agg_fetch_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if agg_fetch[0]["num_of_test"] + agg_fetch[1]["num_of_test"] + agg_fetch[2]["num_of_test"] > 0:
            self.agg_fetch_table.setHorizontalHeaderLabels(
                ["Total", str(agg_fetch[0]["num_of_test"] + agg_fetch[1]["num_of_test"] + agg_fetch[2]["num_of_test"]),
                 "100%"])
        else:
            self.agg_fetch_table.setHorizontalHeaderLabels(
                ["Total", str(agg_fetch[0]["num_of_test"] + agg_fetch[1]["num_of_test"] + agg_fetch[2]["num_of_test"]),
                 "0%"])

        agg_vbox = QVBoxLayout(self)

        agg_hbox1 = QHBoxLayout(self)
        agg_hbox1.addWidget(self.agg_location)
        agg_hbox1.addWidget(self.agg_location_dropdown)
        agg_hbox1.addWidget(self.agg_housing)
        agg_hbox1.addWidget(self.agg_housing_dropdown)
        agg_hbox1.addWidget(self.agg_site)
        agg_hbox1.addWidget(self.agg_site_dropdown)

        agg_hbox2 = QHBoxLayout(self)
        agg_hbox2.addWidget(self.agg_date_processed)
        agg_hbox2.addWidget(self.agg_begin_date)
        agg_hbox2.addWidget(self.agg_dash)
        agg_hbox2.addWidget(self.agg_end_date)

        agg_hbox3 = QHBoxLayout(self)
        agg_hbox3.addWidget(self.back_home)
        agg_hbox3.addWidget(self.filter)
        agg_hbox3.addWidget(self.reset)

        agg_vbox.addLayout(agg_hbox1)
        agg_vbox.addLayout(agg_hbox2)
        agg_vbox.addWidget(self.agg_fetch_table)
        agg_vbox.addLayout(agg_hbox3)

        self.filter.clicked.connect(self.agg_filter)
        self.reset.clicked.connect(self.agg_reset)

        if user_type == "student":
            self.back_home.clicked.connect(self.student_back)
        elif user_type == "labtech":
            self.back_home.clicked.connect(self.labtech_back)
        elif user_type == "tester":
            self.back_home.clicked.connect(self.tester_back)
        elif user_type == "admin":
            self.back_home.clicked.connect(self.admin_back)
        elif user_type == "labtester":
            self.back_home.clicked.connect(self.labtester_back)

    def agg_filter(self):
        selected_location = self.agg_location_dropdown.currentText()
        selected_housing = self.agg_housing_dropdown.currentText()
        selected_site = self.agg_site_dropdown.currentText()
        input_begine_date = self.agg_begin_date.text()
        input_end_date = self.agg_end_date.text()
        if len(input_begine_date) != 10:
            input_begine_date = ""
        if len(input_end_date) != 10:
            input_end_date = ""
        end_date_condition = input_end_date >= input_begine_date

        query = "CALL aggregate_results("
        if selected_location != "ALL":
            query = query + "'" + selected_location + "'" + ", "
        else:
            query = query + "NULL, "
        if selected_housing != "ALL":
            query = query + "'" + selected_housing + "'" + ", "
        else:
            query = query + "NULL, "
        if selected_site != "ALL":
            query = query + "'" + selected_site + "'" + ", "
        else:
            query = query + "NULL, "
        if input_begine_date != "":
            query = query + "'" + input_begine_date + "'" + ", "
        else:
            query = query + "NULL, "
        if input_end_date != "" and end_date_condition:
            query = query + "'" + input_end_date + "'" + ");"
        else:
            query = query + "NULL);"
        print(query)

        self.cursor.execute(query)
        self.cursor.execute("select * from aggregate_results_result;")
        update_agg_fetch = self.cursor.fetchall()
        if len(update_agg_fetch) == 0:
            update_agg_fetch = []

        if len(update_agg_fetch) < 3:
            check_missing = []
            for i in update_agg_fetch:
                check_missing.append(i['test_status'])

            if len(update_agg_fetch) == 2:
                if "positive" not in check_missing:
                    update_agg_fetch.append(self.missing_positive)
                elif "negative" not in check_missing:
                    update_agg_fetch.insert(0, self.missing_negative)
                elif "pending" not in check_missing:
                    update_agg_fetch.insert(1, self.missing_pending)
            elif len(update_agg_fetch) == 1:
                if "pending" in check_missing:
                    update_agg_fetch.append(self.missing_positive)
                    update_agg_fetch.insert(0, self.missing_negative)
                elif "positive" in check_missing:
                    update_agg_fetch.insert(0, self.missing_pending)
                    update_agg_fetch.insert(0, self.missing_negative)
                elif "negative" in check_missing:
                    update_agg_fetch.append(self.missing_pending)
                    update_agg_fetch.append(self.missing_positive)
            elif len(update_agg_fetch) == 0:
                update_agg_fetch.append(self.missing_negative)
                update_agg_fetch.append(self.missing_pending)
                update_agg_fetch.append(self.missing_positive)
        print(update_agg_fetch)

        percent0 = str(update_agg_fetch[0]["percentage"]) + "%"
        percent1 = str(update_agg_fetch[1]["percentage"]) + "%"
        percent2 = str(update_agg_fetch[2]["percentage"]) + "%"
        self.agg_fetch_table.setItem(0, 1, QTableWidgetItem(str(update_agg_fetch[2]["num_of_test"])))
        self.agg_fetch_table.setItem(1, 1, QTableWidgetItem(str(update_agg_fetch[0]["num_of_test"])))
        self.agg_fetch_table.setItem(2, 1, QTableWidgetItem(str(update_agg_fetch[1]["num_of_test"])))
        self.agg_fetch_table.setItem(0, 2, QTableWidgetItem(percent2))
        self.agg_fetch_table.setItem(1, 2, QTableWidgetItem(percent0))
        self.agg_fetch_table.setItem(2, 2, QTableWidgetItem(percent1))

        if update_agg_fetch[0]["num_of_test"] + update_agg_fetch[1]["num_of_test"] + update_agg_fetch[2][
            "num_of_test"] > 0:
            self.agg_fetch_table.setHorizontalHeaderLabels(["Total", str(
                update_agg_fetch[0]["num_of_test"] + update_agg_fetch[1]["num_of_test"] + update_agg_fetch[2][
                    "num_of_test"]), "100%"])
        else:
            self.agg_fetch_table.setHorizontalHeaderLabels(["Total", str(
                update_agg_fetch[0]["num_of_test"] + update_agg_fetch[1]["num_of_test"] + update_agg_fetch[2][
                    "num_of_test"]), "0%"])

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

    def agg_reset(self):
        self.close()
        AggregateResult(self.connection, self.user_type, self.username).exec()