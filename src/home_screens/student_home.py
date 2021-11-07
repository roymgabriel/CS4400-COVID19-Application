###########################################################################################################################################
################################################### @studenthome ##########################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout

import src.screens.aggregate_result as aggregate_result
import src.screens.sign_up_for_a_test as sign_up_for_a_test
import src.screens.student_view_test_result as student_view_test_result
import src.screens.view_daily_result as view_daily_result


class StudentHome(QDialog):
    def __init__(self, connection, username):
        super(StudentHome, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Student Home')
        self.view_my_result = QPushButton("View My Result")
        self.sign_up_for_a_test = QPushButton("Sign Up for a Test")
        self.view_agg_result = QPushButton("View Aggregate Results")
        self.view_daily_result = QPushButton("View Daily Results")
        quit_btn = QPushButton("Quit")

        ##Following are resize the button size, but it look more ugly
        # geowidth = 200
        # geoheight = 50
        # self.view_my_result.setFixedSize(geowidth,geoheight)
        # self.sign_up_for_a_test.setFixedSize(geowidth,geoheight)
        # self.view_agg_result.setFixedSize(geowidth,geoheight)
        # self.view_daily_result.setFixedSize(geowidth,geoheight)

        student_vbox = QVBoxLayout(self)

        student_hbox1 = QHBoxLayout(self)
        student_hbox1.addWidget(self.view_my_result)
        student_hbox1.addWidget(self.view_agg_result)

        student_hbox2 = QHBoxLayout(self)
        student_hbox2.addWidget(self.sign_up_for_a_test)
        student_hbox2.addWidget(self.view_daily_result)

        student_vbox.addLayout(student_hbox1)
        student_vbox.addLayout(student_hbox2)
        student_vbox.addWidget(quit_btn)

        self.view_agg_result.clicked.connect(self.link_aggregate_result)
        self.view_my_result.clicked.connect(self.link_view_result)
        self.sign_up_for_a_test.clicked.connect(self.link_sign_up)  ################################################
        self.view_daily_result.clicked.connect(self.link_daily_result)  ############################################
        quit_btn.clicked.connect(self.quit_app)

    def link_view_result(self):
        self.close()
        student_view_test_result.Student_View_Test_Result(self.connection, self.username).exec()

    def link_sign_up(self):
        self.close()
        sign_up_for_a_test.SignUpForATest(self.connection, self.username).exec()

    def link_daily_result(self):
        self.close()
        view_daily_result.ViewDailyResults(self.connection, "student", self.username).exec()

    def link_aggregate_result(self):
        self.close()
        aggregate_result.AggregateResult(self.connection, "student", self.username).exec()

    def quit_app(self):
        self.close()
