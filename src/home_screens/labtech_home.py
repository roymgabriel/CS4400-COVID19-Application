###########################################################################################################################################
################################################### @labtechhome ##########################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout

import src.screens.aggregate_result as aggregate_result
import src.screens.create_pool as create_pool
import src.screens.view_daily_result as view_daily_result
import src.screens.view_pool as view_pool
import src.screens.view_processed_tests as view_processed_tests


class LabTechHome(QDialog):
    def __init__(self, connection, username):
        super(LabTechHome, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Lab Technician Home')
        self.process_pool = QPushButton("Process Pool")
        self.view_my_pro_test = QPushButton("View My Processed Tests")
        self.create_pool = QPushButton("Create Pool")
        self.view_agg_result = QPushButton("View Aggregate Results")
        self.view_pool = QPushButton("View Pool")
        self.view_daily_result = QPushButton("View Daily Results")
        quit_btn = QPushButton("Quit")

        labtech_vbox = QVBoxLayout(self)

        labtech_hbox1 = QHBoxLayout(self)
        labtech_hbox1.addWidget(self.process_pool)
        labtech_hbox1.addWidget(self.view_my_pro_test)

        labtech_hbox2 = QHBoxLayout(self)
        labtech_hbox2.addWidget(self.create_pool)
        labtech_hbox2.addWidget(self.view_agg_result)

        labtech_hbox3 = QHBoxLayout(self)
        labtech_hbox3.addWidget(self.view_pool)
        labtech_hbox3.addWidget(self.view_daily_result)

        labtech_vbox.addLayout(labtech_hbox1)
        labtech_vbox.addLayout(labtech_hbox2)
        labtech_vbox.addLayout(labtech_hbox3)
        labtech_vbox.addWidget(quit_btn)

        self.view_agg_result.clicked.connect(self.link_aggregate_result)
        self.process_pool.clicked.connect(self.link_view_pool)  # Q: per Piazza @873_f1, this btn should take user to
        # view pool
        self.view_my_pro_test.clicked.connect(self.link_view_my_pro_test)  ############################################
        self.create_pool.clicked.connect(self.link_create_pool)  ############################################
        self.view_pool.clicked.connect(self.link_view_pool)  ############################################
        self.view_daily_result.clicked.connect(self.link_daily_result)  ############################################
        quit_btn.clicked.connect(self.quit_app)

    def link_view_my_pro_test(self):
        self.close()
        view_processed_tests.ViewProcessedTests(self.connection, "labtech", self.username).exec()

    def link_create_pool(self):
        self.close()
        create_pool.CreatePool(self.connection, "labtech", self.username).exec()

    def link_view_pool(self):
        self.close()
        view_pool.ViewPool(self.connection, "labtech", self.username).exec()

    def link_daily_result(self):
        self.close()
        view_daily_result.ViewDailyResults(self.connection, "labtech", self.username).exec()

    def link_aggregate_result(self):
        self.close()
        aggregate_result.AggregateResult(self.connection, "labtech", self.username).exec()

    def quit_app(self):
        self.close()


