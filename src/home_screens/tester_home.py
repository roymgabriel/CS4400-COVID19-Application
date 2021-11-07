###########################################################################################################################################
#################################################### @testerhome ##########################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QPushButton, QHBoxLayout, QVBoxLayout

import src.screens.aggregate_result as aggregate_result
import src.screens.change_site as change_site
import src.screens.create_appointment as create_appointment
import src.screens.view_appointments as view_appointments
import src.screens.view_daily_result as view_daily_result


class TesterHome(QDialog):
    def __init__(self, connection, username):
        super(TesterHome, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Tester Home')
        self.change_test_site = QPushButton("Change Testing Site")
        self.view_appt = QPushButton("View Appointments")
        self.create_appt = QPushButton("Create Appointments")
        self.view_agg_result = QPushButton("View Aggregate Results")
        self.view_daily_result = QPushButton("View Daily Results")
        quit_btn = QPushButton("Quit")

        tester_hbox = QHBoxLayout(self)

        tester_vbox1 = QVBoxLayout(self)
        tester_vbox1.addWidget(self.change_test_site)
        tester_vbox1.addWidget(self.view_appt)
        tester_vbox1.addWidget(self.create_appt)

        tester_vbox2 = QVBoxLayout(self)
        tester_vbox2.addWidget(self.view_agg_result)
        tester_vbox2.addWidget(self.view_daily_result)
        tester_vbox2.addWidget(quit_btn)

        tester_hbox.addLayout(tester_vbox1)
        tester_hbox.addLayout(tester_vbox2)


        self.change_test_site.clicked.connect(self.link_change_test_site)  ################################
        self.create_appt.clicked.connect(self.link_create_appointment)
        self.view_appt.clicked.connect(self.link_view_appointment)
        self.view_agg_result.clicked.connect(self.link_aggregate_result)
        self.view_daily_result.clicked.connect(self.link_daily_result)  ############################################
        quit_btn.clicked.connect(self.quit_app)

    def link_change_test_site(self):
        self.close()
        change_site.ChangeSite(self.connection, "tester", self.username).exec()

    def link_create_appointment(self):
        self.close()
        create_appointment.Create_Appointment(self.connection, "tester", self.username).exec()

    def link_view_appointment(self):
        self.close()
        view_appointments.View_Appointments(self.connection, "tester", self.username).exec()

    def link_aggregate_result(self):
        self.close()
        aggregate_result.AggregateResult(self.connection, "tester", self.username).exec()

    def link_daily_result(self):
        self.close()
        view_daily_result.ViewDailyResults(self.connection, "tester", self.username).exec()

    def quit_app(self):
        self.close()
