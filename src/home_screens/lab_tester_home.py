###########################################################################################################################################
################################################# @labtesterhome ##########################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QPushButton, QHBoxLayout, QVBoxLayout

import src.screens.aggregate_result as aggregate_result
import src.screens.change_site as change_site
import src.screens.create_appointment as create_appointment
import src.screens.create_pool as create_pool
import src.screens.view_appointments as view_appointments
import src.screens.view_daily_result as view_daily_result
import src.screens.view_pool as view_pool
import src.screens.view_processed_tests as view_processed_tests


class LabTesterHome(QDialog):
    def __init__(self, connection, username):
        super(LabTesterHome, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Lab Technician / Tester Home')
        self.process_pool = QPushButton("Process Pool")
        self.create_pool = QPushButton("Create Pool")
        self.view_pool = QPushButton("View Pool")
        self.view_my_pro_test = QPushButton("View My Processed Tests")
        self.view_agg_result = QPushButton("View Aggregate Results")
        self.change_test_site = QPushButton("Change Testing Site")
        self.view_appt = QPushButton("View Appointments")
        self.create_appt = QPushButton("Create Appointments")
        self.view_daily_result = QPushButton("View Daily Results")
        quit_btn = QPushButton("Quit")

        labtester_hbox = QHBoxLayout(self)

        labtester_vbox1 = QVBoxLayout(self)
        labtester_vbox1.addWidget(self.process_pool)
        labtester_vbox1.addWidget(self.create_pool)
        labtester_vbox1.addWidget(self.view_pool)
        labtester_vbox1.addWidget(self.view_my_pro_test)
        labtester_vbox1.addWidget(self.view_agg_result)

        labtester_vbox2 = QVBoxLayout(self)
        labtester_vbox2.addWidget(self.change_test_site)
        labtester_vbox2.addWidget(self.view_appt)
        labtester_vbox2.addWidget(self.create_appt)
        labtester_vbox2.addWidget(self.view_daily_result)
        labtester_vbox2.addWidget(quit_btn)

        labtester_hbox.addLayout(labtester_vbox1)
        labtester_hbox.addLayout(labtester_vbox2)

        self.process_pool.clicked.connect(self.link_process_pool)
        self.create_pool.clicked.connect(self.link_create_pool)
        self.view_pool.clicked.connect(self.link_view_pool)
        self.view_my_pro_test.clicked.connect(self.link_view_my_pro_test)
        self.view_agg_result.clicked.connect(self.link_aggregate_result)
        self.change_test_site.clicked.connect(self.link_change_test_site)
        self.view_appt.clicked.connect(self.link_view_appt)
        self.create_appt.clicked.connect(self.link_create_appt)
        self.view_daily_result.clicked.connect(self.link_view_daily_result)
        quit_btn.clicked.connect(self.quit_app)

    def link_process_pool(self):
        self.close()
        view_pool.ViewPool(self.connection, "labtester", self.username).exec()

    def link_create_pool(self):
        self.close()
        create_pool.CreatePool(self.connection, "labtester", self.username).exec()

    def link_view_pool(self):
        self.close()
        view_pool.ViewPool(self.connection, "labtester", self.username).exec()

    def link_view_my_pro_test(self):
        self.close()
        view_processed_tests.ViewProcessedTests(self.connection, "labtester", self.username).exec()

    def link_aggregate_result(self):
        self.close()
        aggregate_result.AggregateResult(self.connection, "labtester", self.username).exec()

    def link_change_test_site(self):
        self.close()
        change_site.ChangeSite(self.connection, "labtester", self.username).exec()

    def link_view_appt(self):
        self.close()
        view_appointments.View_Appointments(self.connection, "labtester", self.username).exec()

    def link_create_appt(self):
        self.close()
        create_appointment.Create_Appointment(self.connection, "labtester", self.username).exec()

    def link_view_daily_result(self):
        self.close()
        view_daily_result.ViewDailyResults(self.connection, "labtester", self.username).exec()

    def quit_app(self):
        self.close()

