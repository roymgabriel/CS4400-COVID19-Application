###########################################################################################################################################
########################################################## @screen12 ######################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,\
                            QMessageBox

from datetime import datetime

import src.home_screens.admin_home as admin_home
import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.tester_home as tester_home

class Create_Appointment(QDialog):
    def __init__(self, connection, user_type, username):
        super(Create_Appointment, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Create an Appointment')
        self.user_type = user_type

        self.site_name = QLabel("Site Name:")

        self.cursor.execute("SELECT DISTINCT site FROM covidtest_fall2020.WORKING_AT;")
        self.list_of_sites = []
        sites = self.cursor.fetchall()
        for i in sites:
            self.list_of_sites.append(i["site"])

        self.comboBox = QComboBox(self) # need to find way to make it dynamic when adding a testing site...
        self.comboBox.addItems(self.list_of_sites)


        self.date_label = QLabel("Date:")
        self.date = QLineEdit()
        self.date.setPlaceholderText("YYYY-MM-DD")
        self.time_label = QLabel("Time:")
        self.time = QLineEdit()
        self.time.setPlaceholderText("HH:MM")

        self.create_appointment = QPushButton("Create Appointment") # might change to submit
        self.back_home = QPushButton("Back (Home)", self)

        Create_Appointment_vbox = QVBoxLayout(self)

        Create_Appointment_hbox = QHBoxLayout(self)
        Create_Appointment_hbox.addWidget(self.site_name)
        Create_Appointment_hbox.addWidget(self.comboBox)
        Create_Appointment_hbox.addWidget(self.date_label)
        Create_Appointment_hbox.addWidget(self.date)
        Create_Appointment_hbox.addWidget(self.time_label)
        Create_Appointment_hbox.addWidget(self.time)

        Create_Appointment_hbox1 = QHBoxLayout(self)
        Create_Appointment_hbox1.addWidget(self.back_home)
        Create_Appointment_hbox1.addWidget(self.create_appointment)



        Create_Appointment_vbox.addLayout(Create_Appointment_hbox)
        Create_Appointment_vbox.addLayout(Create_Appointment_hbox1)

        if self.user_type == "tester":
            self.back_home.clicked.connect(self.tester_back)
        elif self.user_type == "admin":
            self.back_home.clicked.connect(self.admin_back)
        elif self.user_type == "labtester":
            self.back_home.clicked.connect(self.labtester_back)

        self.create_appointment.clicked.connect(self.create_app)

    def tester_back(self):
        self.close()
        tester_home.TesterHome(self.connection, self.username).exec()
    def admin_back(self):
        self.close()
        admin_home.AdminHome(self.connection, self.username).exec()
    def labtester_back(self):
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.username).exec()

    def create_app(self):
        if self.date.text() and self.time.text():

            # if duplicate entry the message will appear but the appt will only have 1 entry
            if self.user_type == "admin":
                count = 0
                try:
                    # self.test = datetime.datetime(int(self.date.text().split("-")[0]), int(self.date.text().split("-")[1]), int(self.date.text().split("-")[2]),\
                    # int(self.time.text().split(":")[0]), int(self.time.text().split(":")[1]), int(self.time.text().split(":")[2]))
                    self.test_date = str(datetime.strptime(self.date.text(), '%Y-%m-%d')).split()[0]
                    self.test_time = str(datetime.strptime(self.time.text(), '%H:%M')).split()[1][:5]
                except:
                    count += 1

                if count:
                    QMessageBox.about(self, "ERROR!", "Date and/or Time are in the wrong format!")
                else:
                    self.cursor.execute("SELECT * FROM covidtest_fall2020.APPOINTMENT;")
                    results = self.cursor.fetchall()

                    # check for duplicate appts
                    for i in results:
                        temp_date = str(datetime.strptime(str(i['appt_date']), '%Y-%m-%d')).split()[0]
                        temp_time = str(datetime.strptime(str(i['appt_time']), '%H:%M:%S')).split()[1][:5]

                        if  self.comboBox.currentText() == str(i['site_name']) and \
                            self.test_date == temp_date and \
                            self.test_time == temp_time:

                            QMessageBox.about(self, "ERROR!", "Appointment already exists!")
                            count += 1
                            break

                    # check for max capacity
                    self.cursor.execute("(SELECT count(*) as num FROM appointment WHERE site_name = %s AND appt_date= %s);", (self.comboBox.currentText(), self.date.text()))
                    results1 = self.cursor.fetchall()

                    self.cursor.execute("(SELECT count(username)*10 as num2 FROM working_at WHERE site= %s);", (self.comboBox.currentText()))
                    results2 = self.cursor.fetchall()

                    if int(results1[0]['num']) >= int(results2[0]['num2']):
                        QMessageBox.about(self, "ERROR!", f"Appointments on {self.date.text()} at {self.comboBox.currentText()} have reached max capacity!")
                        count += 1

                    # create appointment if all is well
                    if count == 0:
                        self.cursor.callproc("create_appointment", (self.comboBox.currentText(), self.date.text(), self.time.text()))
                        self.connection.commit()
                        QMessageBox.about(self, "SUCCESS!", "You successfully created an appointment!")


            elif self.user_type == "tester" or self.user_type == "labtester":
                print(self.user_type)
                count = 0
                try:
                    self.test_date = str(datetime.strptime(self.date.text(), '%Y-%m-%d')).split()[0]
                    self.test_time = str(datetime.strptime(self.time.text(), '%H:%M')).split()[1][:5]
                except:
                    count += 1

                if count:
                    QMessageBox.about(self, "ERROR!", "Date and/or Time are in the wrong format!")
                else:
                    self.cursor.execute("SELECT * FROM covidtest_fall2020.APPOINTMENT;")
                    self.connection.commit()
                    results = self.cursor.fetchall()

                    for i in results:

                        temp_date = str(datetime.strptime(str(i['appt_date']), '%Y-%m-%d')).split()[0]
                        temp_time = str(datetime.strptime(str(i['appt_time']), '%H:%M:%S')).split()[1][:5]

                        if  self.comboBox.currentText() == str(i['site_name']) and \
                            self.test_date == temp_date and \
                            self.test_time == temp_time:

                            QMessageBox.about(self, "ERROR!", "Appointment already exists!")
                            count += 1
                            break

                        # if count != 0:
                        #     break


                    # check for max capacity
                    self.cursor.execute("(SELECT count(*) as num FROM appointment WHERE site_name = %s AND appt_date= %s);", (self.comboBox.currentText(), self.date.text()))
                    self.connection.commit()
                    results1 = self.cursor.fetchall()

                    self.cursor.execute("(SELECT count(username)*10 as num2 FROM working_at WHERE site= %s);", (self.comboBox.currentText()))
                    self.connection.commit()
                    results2 = self.cursor.fetchall()

                    if int(results1[0]['num']) >= int(results2[0]['num2']):
                        QMessageBox.about(self, "ERROR!", f"Appointments on {self.date.text()} at {self.comboBox.currentText()} have reached max capacity!")
                        count += 1

                    # check to see if tester is creating an appt at the site they work at
                    self.cursor.execute("SELECT site FROM covidtest_fall2020.WORKING_AT WHERE username = %s", (self.username))
                    self.connection.commit()
                    results3 = self.cursor.fetchall()
                    sites = [i['site'] for i in results3]

                    if not sites:
                        QMessageBox.about(self, "ERROR!", "It seems that you are not working for any site at the moment!")
                        count += 1
                    elif self.comboBox.currentText() in sites:
                        if count == 0:
                            self.cursor.callproc("create_appointment", (self.comboBox.currentText(), self.date.text(), self.time.text()))
                            self.connection.commit()
                            QMessageBox.about(self, "SUCCESS!", "You successfully created an appointment!")

                    else:
                        QMessageBox.about(self, "ERROR!", "You can only create an appointment where you work at!")
        else:
            QMessageBox.about(self, "ERROR!", "Please fill out all the fields!")
