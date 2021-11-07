###########################################################################################################################################
########################################################## @screen15 ######################################################################
###########################################################################################################################################

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
import re

import src.home_screens.admin_home as admin_home


class Create_Testing_Site(QDialog):
    def __init__(self, connection, username):
        super(Create_Testing_Site, self).__init__()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.username = username

        self.setWindowTitle('Create a Testing Site')
        self.site_name_label = QLabel("Site Name:")
        self.site_name = QLineEdit()

        self.street_address_label = QLabel("Street Address:")
        self.street_address = QLineEdit()

        self.city_label = QLabel("City:")
        self.city = QLineEdit()

        self.state = QLabel("State:")
        self.us_states = [  "", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", \
                            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", \
                            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", \
                            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", \
                            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

        self.comboBox = QComboBox(self)
        self.comboBox.addItems(self.us_states)
        self.comboBox.maximumHeight()


        self.zip_code_label = QLabel("Zip Code:")
        self.zip_code = QLineEdit()

        self.location_label = QLabel("Location:")
        self.comboBox1 = QComboBox(self)
        self.comboBox1.addItems(["", "East", "West"])

        self.site_tester_label = QLabel("Site Tester:")

        self.cursor.execute("SELECT concat(fname, ' ', lname) AS sitetester_name FROM covidtest_fall2020.user WHERE username in (SELECT DISTINCT sitetester_username FROM covidtest_fall2020.sitetester);")
        names = self.cursor.fetchall()
        self.list_of_names = [""]
        for i in names:
            self.list_of_names.append(i["sitetester_name"])


        self.comboBox2 = QComboBox(self)
        self.comboBox2.addItems(self.list_of_names)

        self.create_site = QPushButton("Create Site")
        self.create_site.clicked.connect(self.create_site_func)
        self.back = QPushButton("Back (Home)", self)
        self.back.clicked.connect(self.backHome)

        Create_Testing_Site_vbox = QVBoxLayout(self)

        Create_Testing_Site_hbox1 = QHBoxLayout(self)
        Create_Testing_Site_hbox1.addWidget(self.city_label)
        Create_Testing_Site_hbox1.addWidget(self.city)
        Create_Testing_Site_hbox1.addWidget(self.state)
        Create_Testing_Site_hbox1.addWidget(self.comboBox)

        Create_Testing_Site_hbox2 = QHBoxLayout(self)
        Create_Testing_Site_hbox2.addWidget(self.zip_code_label)
        Create_Testing_Site_hbox2.addWidget(self.zip_code)
        Create_Testing_Site_hbox2.addWidget(self.location_label)
        Create_Testing_Site_hbox2.addWidget(self.comboBox1)

        Create_Testing_Site_hbox3 = QHBoxLayout(self)
        Create_Testing_Site_hbox3.addWidget(self.back)
        Create_Testing_Site_hbox3.addWidget(self.create_site)

        Create_Testing_Site_vbox.addWidget(self.site_name_label)
        Create_Testing_Site_vbox.addWidget(self.site_name)
        Create_Testing_Site_vbox.addWidget(self.street_address_label)
        Create_Testing_Site_vbox.addWidget(self.street_address)
        Create_Testing_Site_vbox.addLayout(Create_Testing_Site_hbox1)
        Create_Testing_Site_vbox.addLayout(Create_Testing_Site_hbox2)
        Create_Testing_Site_vbox.addWidget(self.site_tester_label)
        Create_Testing_Site_vbox.addWidget(self.comboBox2)
        Create_Testing_Site_vbox.addLayout(Create_Testing_Site_hbox3)


    def backHome(self):
        self.close()
        admin_home.AdminHome(self.connection, self.username).exec()

    def create_site_func(self):
        count = 0
        if self.site_name.text() == "" or self.street_address.text() == "" or self.city.text() == "" or self.comboBox.currentText() == "" or self.zip_code.text() == "" or self.comboBox1.currentText() == "" or self.comboBox2.currentText() == "":
            QMessageBox.about(self, "Error!", "There is some missing information!")
        else:
            if len(self.zip_code.text()) != 5 or len(re.findall(r"\D", self.zip_code.text())) != 0:
                QMessageBox.about(self, "Error!", "Zipcode must be 5 digits")
            else:
                # check for duplicates
                self.cursor.execute("SELECT * FROM covidtest_fall2020.SITE;")
                results = self.cursor.fetchall()

                for i in results:
                    if  self.site_name.text() == i['site_name'] and \
                        self.street_address.text() == str(i['street']) and \
                        self.city.text() == str(i['city']) and \
                        self.comboBox.currentText() == i['state'] and \
                        self.zip_code.text() == str(i['zip']) and \
                        self.comboBox1.currentText() == str(i['location']):

                        QMessageBox.about(self, "ERROR!", "Site already exists!")
                        count += 1
                        break

                # if site, street address, city names are too long
                if len(self.site_name.text()) > 40:
                    QMessageBox.about(self, "ERROR!", "Site Name too long.")
                elif len(self.street_address.text()) > 40:
                    QMessageBox.about(self, "ERROR!", "Street Address too long.")
                elif len(self.city.text()) > 40:
                    QMessageBox.about(self, "ERROR!", "City Name too long.")
                # if no duplicates
                elif count == 0:
                    split_names = self.comboBox2.currentText().split()
                    self.cursor.execute("SELECT username FROM user WHERE fname = %s AND lname = %s;", (split_names[0], split_names[1],))
                    username_dict = self.cursor.fetchall()
                    username = [name["username"] for name in username_dict][0]


                    self.cursor.callproc("create_testing_site", (self.site_name.text(), self.street_address.text(), self.city.text(), self.comboBox.currentText(), self.zip_code.text(), self.comboBox1.currentText(), username))
                    self.connection.commit()
                    QMessageBox.about(self, "SUCCESS!", "You have successfully created a testing site!")

                    # clear everything
                    self.site_name.clear()
                    self.street_address.clear()
                    self.city.clear()
                    self.comboBox.setCurrentText("")
                    self.zip_code.clear()
                    self.comboBox1.setCurrentText("")
                    self.comboBox2.setCurrentText("")

