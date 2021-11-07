###########################################################################################################################################
############################################## Below are Import Statement #################################################################
###########################################################################################################################################
import sys
sys.path.append("/Users/Roy/Documents/PythonPrograms/Temp/cs4400-phase4")
import hashlib

import pymysql
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import src.screens.register_home as register_home
import src.home_screens.admin_home as admin_home
import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.labtech_home as labtech_home
import src.home_screens.student_home as student_home
import src.home_screens.tester_home as tester_home


###########################################################################################################################################
################################################### THIS IS A DIVIDE LINE #################################################################
###########################################################################################################################################
################################################### Below is Login Screen #################################################################
###########################################################################################################################################
class DbLoginDialog(QDialog):
    def __init__(self):
        super(DbLoginDialog, self).__init__()
        self.root_pw = "CS4400@fall2020"
        self.connection = pymysql.connect(host="localhost",
                                          user="root",
                                          password=self.root_pw,
                                          db="covidtest_fall2020",
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        self.view = QListView()
        self.model = QStandardItemModel(self.view)
        # self.view.setModel(self.model) #Quynh: I don't think we need this because line 33 already did the job
        # self.connection = db_connect.DBConnect()
        ###
        self.user = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        ###
        self.luser = QLabel("Username:")
        self.lpassword = QLabel("Password:")
        ###
        v = QVBoxLayout(self)
        group_box = QGroupBox("GT COVID-19 Testing Login Credentials")
        l = QFormLayout()
        l.addRow(self.luser, self.user)
        l.addRow(self.lpassword, self.password)
        group_box.setLayout(l)
        v.addWidget(group_box)
        ##
        self.login = QPushButton("Login", self)
        self.register = QPushButton("Register", self)
        log_reg = QHBoxLayout(self)
        log_reg.addWidget(self.login)
        log_reg.addWidget(self.register)

        v.addLayout(log_reg)
        ##
        self.cursor.execute("select student_username from student;")
        student_fetch = self.cursor.fetchall()
        self.list_of_student = []
        for i in student_fetch:
            self.list_of_student.append(i["student_username"])

        self.cursor.execute("select labtech_username from labtech;")
        labtech_fetch = self.cursor.fetchall()
        self.list_of_labtech = []
        for i in labtech_fetch:
            self.list_of_labtech.append(i["labtech_username"])

        self.cursor.execute("select sitetester_username from sitetester;")
        sitetester_fetch = self.cursor.fetchall()
        self.list_of_sitetester = []
        for i in sitetester_fetch:
            self.list_of_sitetester.append(i["sitetester_username"])

        self.cursor.execute("select admin_username from administrator;")
        admin_fetch = self.cursor.fetchall()
        self.list_of_admin = []
        for i in admin_fetch:
            self.list_of_admin.append(i["admin_username"])

        self.cursor.execute("select username, user_password from user;")
        self.password_fetech = self.cursor.fetchall()
        self.password_check = {}
        for i in self.password_fetech:
            self.password_check[i["username"]] = i["user_password"]

        ##
        self.login.clicked.connect(self.handlelogin)
        self.register.clicked.connect(self.handle_register)

    def handlelogin(self):
        len_check = len(self.password.text()) >= 8
        if (self.user.text().lower() in self.list_of_student) and (
                hashlib.md5(self.password.text().encode()).hexdigest() == self.password_check[
            self.user.text().lower()]) and len_check:
            self.student()
        elif self.user.text().lower() in self.list_of_admin and (
                hashlib.md5(self.password.text().encode()).hexdigest() == self.password_check[
            self.user.text().lower()]) and len_check:
            self.admin()
        elif (self.user.text().lower() in self.list_of_labtech and self.user.text().lower() in self.list_of_sitetester) and (
                hashlib.md5(self.password.text().encode()).hexdigest() == self.password_check[
            self.user.text().lower()]) and len_check:
            self.labtester()
        elif self.user.text().lower() in self.list_of_labtech and (
                hashlib.md5(self.password.text().encode()).hexdigest() == self.password_check[
            self.user.text().lower()]) and len_check:
            self.labtech()
        elif self.user.text().lower() in self.list_of_sitetester and (
                hashlib.md5(self.password.text().encode()).hexdigest() == self.password_check[
            self.user.text().lower()]) and len_check:
            self.tester()
        else:
            self.sign_in_error()

    def handle_register(self):
        self.close()
        register_home.RegisterHome(self.connection).exec()

    def student(self):
        self.close()
        student_home.StudentHome(self.connection, self.user.text().lower()).exec()

    def labtech(self):
        self.close()
        labtech_home.LabTechHome(self.connection, self.user.text().lower()).exec()

    def tester(self):
        self.close()
        tester_home.TesterHome(self.connection, self.user.text().lower()).exec()

    def admin(self):
        self.close()
        admin_home.AdminHome(self.connection, self.user.text().lower()).exec()

    def labtester(self):
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.user.text().lower()).exec()

    def sign_in_error(self):
        signinerror().exec()


class signinerror(QDialog):
    def __init__(self):
        super(signinerror, self).__init__()
        self.setWindowTitle('Sign In Error')

        self.error_msg = QLabel("Username or password is incorrect. Please Try again")
        self.go_back = QPushButton("Close")

        error_display = QVBoxLayout(self)
        error_display.addWidget(self.error_msg)
        error_display.addWidget(self.go_back)

        self.go_back.clicked.connect(self.close_error_msg)

    def close_error_msg(self):
        self.close()


###########################################################################################################################################
################################################### THIS IS A DIVIDE LINE #################################################################
###########################################################################################################################################
################################################### Below are Logistic Stuff ##############################################################
###########################################################################################################################################
if __name__ == '__main__':
    print("     Student  username: aallman302  password: password47")
    print("     Labtech  username: ygao10      password: password6")
    print("     Tester   username: mgrey91     password: password15")
    print("     Admin    username: mmoss7      password: password2")
    app = QApplication(sys.argv)
    main = DbLoginDialog()
    main.show()
    sys.exit(app.exec_())

