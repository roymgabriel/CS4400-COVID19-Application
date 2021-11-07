###########################################################################################################################################
##################################################### @adminhome ##########################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout

import src.screens.aggregate_result as aggregate_result
import src.screens.create_appointment as create_appointment
import src.screens.create_testing_site as create_testing_site
import src.screens.reassign_tester as reassign_tester
import src.screens.view_appointments as view_appointments
import src.screens.view_daily_result as view_daily_result


class AdminHome(QDialog):
    def __init__(self, connection, username):
        super(AdminHome, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Admin Home')
        self.reassign_tester = QPushButton("Reassign Testers")
        self.create_testing_site = QPushButton("Create Testing Site")
        self.create_appt = QPushButton("Create Appointments")
        self.view_agg_result = QPushButton("View Aggregate Results")
        self.view_appt = QPushButton("View Appointments")
        self.view_daily_result = QPushButton("View Daily Results")
        quit_btn = QPushButton("Quit")

        admin_vbox = QVBoxLayout(self)

        admin_hbox1 = QHBoxLayout(self)
        admin_hbox1.addWidget(self.reassign_tester)
        admin_hbox1.addWidget(self.create_testing_site)

        admin_hbox2 = QHBoxLayout(self)
        admin_hbox2.addWidget(self.create_appt)
        admin_hbox2.addWidget(self.view_agg_result)

        admin_hbox3 = QHBoxLayout(self)
        admin_hbox3.addWidget(self.view_appt)
        admin_hbox3.addWidget(self.view_daily_result)

        admin_vbox.addLayout(admin_hbox1)
        admin_vbox.addLayout(admin_hbox2)
        admin_vbox.addLayout(admin_hbox3)
        admin_vbox.addWidget(quit_btn)

        self.create_testing_site.clicked.connect(self.link_create_testing_site)
        self.view_agg_result.clicked.connect(self.link_aggregate_result)
        self.reassign_tester.clicked.connect(self.link_reassign_tester)  #########################################
        self.create_appt.clicked.connect(self.link_create_appt)  #########################################
        self.view_appt.clicked.connect(self.link_view_appt)  #########################################
        self.view_daily_result.clicked.connect(self.link_view_daily_result)  #########################################
        quit_btn.clicked.connect(self.quit_app)

    def link_create_testing_site(self):
        self.close()
        create_testing_site.Create_Testing_Site(self.connection, self.username).exec()

    def link_aggregate_result(self):
        self.close()
        aggregate_result.AggregateResult(self.connection, "admin", self.username).exec()

    def link_reassign_tester(self):
        self.close()
        reassign_tester.ReassignTester(self.connection, self.username).exec()

    def link_create_appt(self):
        self.close()
        create_appointment.Create_Appointment(self.connection, "admin", self.username).exec()

    def link_view_appt(self):
        self.close()
        view_appointments.View_Appointments(self.connection, "admin", self.username).exec()

    def link_view_daily_result(self):
        self.close()
        view_daily_result.ViewDailyResults(self.connection, "admin", self.username).exec()

    def quit_app(self):
        self.close()
