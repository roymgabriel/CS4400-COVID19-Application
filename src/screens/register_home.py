###########################################################################################################################################
################################################### Below is Register Screen ##############################################################
###########################################################################################################################################

import re

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QComboBox, \
    QCheckBox, QPushButton

import src.app


class RegisterHome(QDialog):
    def __init__(self, connection):
        super(RegisterHome, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.setWindowTitle('Register')

        self.reg_username = QLabel("Username:")
        self.reg_email = QLabel("Email:")
        self.reg_fname = QLabel("First Name:")
        self.reg_lname = QLabel("Last Name:")
        self.reg_password = QLabel("Password:")
        self.reg_confirm_password = QLabel("Confirm Password:")

        self.input_username = QLineEdit(self)
        self.input_email = QLineEdit(self)
        self.input_fname = QLineEdit(self)
        self.input_lname = QLineEdit(self)
        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_confirm_password = QLineEdit(self)
        self.input_confirm_password.setEchoMode(QLineEdit.Password)

        self.input_username.setMaxLength(40)
        self.input_email.setMaxLength(40)
        self.input_fname.setMaxLength(40)
        self.input_lname.setMaxLength(40)
        self.input_password.setMaxLength(40)
        self.input_confirm_password.setMaxLength(40)

        name_reg_text = QRegExp("[a-z-A-Z_]+[\s{0:1}][a-z-A-Z]+")
        name_validator = QRegExpValidator(name_reg_text)
        self.input_fname.setValidator(name_validator)
        self.input_lname.setValidator(name_validator)

        screen_vbox = QVBoxLayout(self)

        top_hbox = QHBoxLayout(self)

        left_vbox = QVBoxLayout(self)
        username_hbox = QHBoxLayout(self)
        username_hbox.addWidget(self.reg_username)
        username_hbox.addWidget(self.input_username)
        fname_hbox = QHBoxLayout(self)
        fname_hbox.addWidget(self.reg_fname)
        fname_hbox.addWidget(self.input_fname)
        password_hbox = QHBoxLayout(self)
        password_hbox.addWidget(self.reg_password)
        password_hbox.addWidget(self.input_password)
        left_vbox.addLayout(username_hbox)
        left_vbox.addLayout(fname_hbox)
        left_vbox.addLayout(password_hbox)

        right_vbox = QVBoxLayout(self)
        email_hbox = QHBoxLayout(self)
        email_hbox.addWidget(self.reg_email)
        email_hbox.addWidget(self.input_email)
        lname_hbox = QHBoxLayout(self)
        lname_hbox.addWidget(self.reg_lname)
        lname_hbox.addWidget(self.input_lname)
        confirm_password_hbox = QHBoxLayout(self)
        confirm_password_hbox.addWidget(self.reg_confirm_password)
        confirm_password_hbox.addWidget(self.input_confirm_password)
        right_vbox.addLayout(email_hbox)
        right_vbox.addLayout(lname_hbox)
        right_vbox.addLayout(confirm_password_hbox)

        top_hbox.addLayout(left_vbox)
        top_hbox.addLayout(right_vbox)

        ###
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.student_tab = QWidget()
        self.employee_tab = QWidget()

        # Add tabs
        self.tabs.addTab(self.student_tab, "Student")
        self.tabs.addTab(self.employee_tab, "Employee")

        # Create student tab
        self.student_tab_hbox = QHBoxLayout(self)
        self.housing_type = QLabel("Housing Type")
        self.location = QLabel("Location")
        self.housing_dropdown = QComboBox(self)
        self.housing_dropdown.addItem("")
        self.housing_dropdown.addItem("Student Housing")
        self.housing_dropdown.addItem("Greek Housing")
        self.housing_dropdown.addItem("Off-campus House")
        self.housing_dropdown.addItem("Off-campus Apartment")
        self.location_dropdown = QComboBox(self)
        self.location_dropdown.addItem("")
        self.location_dropdown.addItem("East")
        self.location_dropdown.addItem("West")
        self.student_tab_hbox.addWidget(self.housing_type)
        self.student_tab_hbox.addWidget(self.housing_dropdown)
        self.student_tab_hbox.addWidget(self.location)
        self.student_tab_hbox.addWidget(self.location_dropdown)
        self.student_tab.setLayout(self.student_tab_hbox)

        # Create employee tab
        self.employee_tab_hbox = QHBoxLayout(self)
        self.phone_num = QLabel("Phone No.")
        self.input_phone_num = QLineEdit(self)
        self.input_phone_num.setMaxLength(10)
        self.employee_tab_hbox.addWidget(self.phone_num)
        self.employee_tab_hbox.addWidget(self.input_phone_num)

        self.employee_tab_vbox = QVBoxLayout(self)
        self.sitetester_check = QCheckBox('Site Tester?  ', self)
        self.labtech_check = QCheckBox('Lab Tech?  ', self)
        self.sitetester_check.setLayoutDirection(Qt.RightToLeft)
        self.labtech_check.setLayoutDirection(Qt.RightToLeft)
        self.employee_tab_vbox.addWidget(self.sitetester_check)
        self.employee_tab_vbox.addWidget(self.labtech_check)

        self.employee_tab_hbox.addLayout(self.employee_tab_vbox)

        self.employee_tab.setLayout(self.employee_tab_hbox)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        ###
        bot_hbox = QHBoxLayout(self)
        self.back_to_login = QPushButton("Back to Login")
        self.registry = QPushButton("Register")
        bot_hbox.addWidget(self.back_to_login)
        bot_hbox.addWidget(self.registry)
        self.back_to_login.clicked.connect(self.activate_back_to_login)

        screen_vbox.addLayout(top_hbox)
        screen_vbox.addLayout(self.layout)
        screen_vbox.addLayout(bot_hbox)

        self.housing_dropdown.activated[str].connect(self.disable_employee_tab)
        self.location_dropdown.activated[str].connect(self.disable_employee_tab)
        self.sitetester_check.stateChanged.connect(self.disable_student_tab)
        self.labtech_check.stateChanged.connect(self.disable_student_tab)
        self.input_phone_num.textChanged[str].connect(self.disable_student_tab)

        self.registry.clicked.connect(self.register_check)

    def disable_employee_tab(self):
        if self.housing_dropdown.currentIndex() != 0 or self.location_dropdown.currentIndex() != 0:
            self.tabs.setTabEnabled(1, False)
        else:
            self.tabs.setTabEnabled(1, True)

    def disable_student_tab(self):
        self.housing_dropdown.setCurrentIndex(0)
        self.location_dropdown.setCurrentIndex(0)
        if self.sitetester_check.isChecked() or self.labtech_check.isChecked() or len(self.input_phone_num.text()) > 0:
            self.tabs.setTabEnabled(0, False)
        else:
            self.tabs.setTabEnabled(0, True)

    def activate_back_to_login(self):
        self.close()
        src.app.DbLoginDialog().exec()

    def register_check(self):
        self.cursor.execute("select username, email from user;")
        self.check_exist = self.cursor.fetchall()
        self.exist_check = {}
        self.exist_email = []
        for i in self.check_exist:
            self.exist_check[i["username"]] = i["email"]
            self.exist_email.append(i["email"])
        username_condition = self.input_username.text().lower() not in self.exist_check
        email_exist_condition = self.input_email.text() not in self.exist_email
        email_regex_condition = (re.search('^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$',
                                           self.input_email.text()) != None) and (
                                            len(self.input_email.text()) >= 5) and (len(self.input_email.text()) <= 25)
        password_condition = len(self.input_password.text()) >= 8
        confirm_password_condition = password_condition and len(
            self.input_confirm_password.text()) >= 8 and self.input_confirm_password.text() == self.input_password.text()
        all_field_condition = (len(self.input_username.text()) >= 1) and (len(self.input_email.text()) >= 1) and (
                    len(self.input_fname.text()) >= 1) and (len(self.input_lname.text()) >= 1) and (
                                          len(self.input_password.text()) >= 1) and (
                                          len(self.input_confirm_password.text()) >= 1)
        student_field_condition = self.housing_dropdown.currentIndex() != 0 and self.location_dropdown.currentIndex() != 0
        employee_field_condition = len(self.input_phone_num.text()) > 0 and (
                    self.labtech_check.isChecked() or self.sitetester_check.isChecked())
        try:
            k = int(self.input_phone_num.text())
            phone_num_int_condition = True
        except:
            phone_num_int_condition = False

        if len(self.input_phone_num.text()) != 10:
            phone_num_int_condition = False

        if username_condition and email_exist_condition and email_regex_condition and password_condition and confirm_password_condition and all_field_condition and (
                student_field_condition or (employee_field_condition and phone_num_int_condition)):
            if student_field_condition:
                self.connect_register_notification("success_student")
            elif employee_field_condition:
                self.connect_register_notification("success_employee")
            else:
                print("this line is impossible to print, try me~~~")
        elif not username_condition:
            self.connect_register_notification("Username Already Exist")
        elif not email_exist_condition:
            self.connect_register_notification("Email Already Exist")
        elif not email_regex_condition:
            self.connect_register_notification("Invalid Email Format")
        elif not password_condition:
            self.connect_register_notification("Password Must Have 8 Or More Characters")
        elif not confirm_password_condition:
            self.connect_register_notification("Password Does Not Match")
        elif not all_field_condition:
            self.connect_register_notification("Must Fill All Sections")
        elif not phone_num_int_condition or len(self.input_phone_num.text()) != 10:
            self.connect_register_notification("Phone Number Can Only Have Digits and Have Exact 10 Digits")
        elif not student_field_condition or not employee_field_condition:
            self.connect_register_notification("Must Fullfill All Fields")

    def connect_register_notification(self, status):
        if status == "success_student" or status == "success_employee":
            if status == "success_student":
                self.cursor.execute("CALL register_student('{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
                    self.input_username.text().lower(), self.input_email.text().lower(),
                    self.input_fname.text()[0].upper() + self.input_fname.text()[1:].lower(),
                    self.input_lname.text()[0].upper() + self.input_lname.text()[1:].lower(),
                    self.location_dropdown.currentText(), self.housing_dropdown.currentText(),
                    self.input_password.text()))
            # print("CALL register_student('{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
            # self.input_username.text(), self.input_email.text(), self.input_fname.text(), self.input_lname.text(),
            # self.location_dropdown.currentText(), self.housing_dropdown.currentText(), self.input_password.text()))
            elif status == "success_employee":
                self.cursor.execute("CALL register_employee('{}', '{}', '{}', '{}', '{}', {}, {}, '{}');".format(
                    self.input_username.text().lower(), self.input_email.text().lower(),
                    self.input_fname.text()[0].upper() + self.input_fname.text()[1:].lower(),
                    self.input_lname.text()[0].upper() + self.input_lname.text()[1:].lower(),
                    self.input_phone_num.text(), self.labtech_check.isChecked(),
                    self.sitetester_check.isChecked(), self.input_password.text()))
            # print("CALL register_employee('{}', '{}', '{}', '{}', '{}', {}, {}, '{}');".format(
            # self.input_username.text(), self.input_email.text(), self.input_fname.text(), self.input_lname.text(),
            # self.input_phone_num.text(), self.labtech_check.isChecked(), self.sitetester_check.isChecked(), self.input_password.text()))

            self.close()
            succ_register_notification(status, self.connection).exec()
        else:
            fail_register_notification(status).exec()


class succ_register_notification(QDialog):
    def __init__(self, status, connection):
        super(succ_register_notification, self).__init__()
        self.connection = connection
        self.setWindowTitle('Register Notification')

        user_type_msg = ""
        if status == "success_student":
            user_type_msg = "Successfully Registered as Student"
        elif status == "success_employee":
            user_type_msg = "Successfully Registered as Employee"
        self.succ_back = QPushButton("Go To Login")
        self.succ_msg = QLabel(user_type_msg)

        succ_vbox1 = QVBoxLayout(self)
        succ_vbox1.addWidget(self.succ_msg)
        succ_vbox1.addWidget(self.succ_back)

        self.succ_back.clicked.connect(self.reg_succ)

    def reg_succ(self):
        self.connection.commit()
        self.close()
        src.app.DbLoginDialog().exec()


class fail_register_notification(QDialog):
    def __init__(self, status):
        super(fail_register_notification, self).__init__()
        self.setWindowTitle('Fail Register Notification')

        self.fail_close = QPushButton("close")
        self.fail_msg = QLabel(status)

        fail_vbox1 = QVBoxLayout(self)
        fail_vbox1.addWidget(self.fail_msg)
        fail_vbox1.addWidget(self.fail_close)

        self.fail_close.clicked.connect(self.reg_fail)

    def reg_fail(self):
        self.close()

