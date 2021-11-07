# screen 17

import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, \
    QScrollArea, QWidget, QGroupBox, QListView

import src.home_screens.lab_tester_home as lab_tester_home
import src.home_screens.tester_home as tester_home


class ChangeSite(QDialog):
    def __init__(self, connection, user_type, username):
        super(ChangeSite, self).__init__()
        self.setWindowTitle('Tester Change Testing Site')
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.user_type = user_type
        self.username = username
        self.initUi()

    def initUi(self):
        self.cursor.execute(
            "select sitetester.sitetester_username as \"Username\", concat(user.fname, ' ',user.lname) as \"Name\", employee.phone_num as \"Phone Number\", working_at.site as \"Assigned Sites\" from sitetester join employee on sitetester.sitetester_username = employee.emp_username join user on sitetester.sitetester_username = user.username left join working_at on sitetester.sitetester_username = working_at.username where sitetester_username = \"{}\";".format(
                self.username))
        k = self.cursor.fetchall()
        sitetester_list = []
        tester_site = {}
        for i in k:
            temp = {"Username": i['Username'], "Name": i["Name"], "Phone Number": i["Phone Number"]}
            if temp not in sitetester_list:
                sitetester_list.append(temp)
                tester_site[i['Username']] = []
        for ii in k:
            user = ii['Username']
            tester_site[ii['Username']].append(ii["Assigned Sites"])

        for i in sitetester_list:
            for ii in tester_site:
                if i['Username'] == ii:
                    i["Assigned Sites"] = tester_site[ii]

        self.original_site_list = []
        for i in tester_site:
            original_query = "insert into working_at values "
            for ii in tester_site[i]:
                original_query = original_query + "('{}', '{}')".format(i, ii) + ", "
            if "None" not in original_query:
                self.original_site_list.append(original_query)

        self.original_site_list = [i[:-2] + ";" for i in self.original_site_list]

        self.layoutV = QVBoxLayout(self)
        self.area = QScrollArea(self)
        self.area.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(0, 0, 200, 100)

        self.bot_hbox = QHBoxLayout(self)
        self.back_home = QPushButton("Back (Home)", self)
        self.update = QPushButton("Update", self)
        self.bot_hbox.addWidget(self.back_home)
        self.bot_hbox.addWidget(self.update)

        self.layoutH = QHBoxLayout(self.scrollAreaWidgetContents)
        self.gridLayout = QGridLayout()
        self.layoutH.addLayout(self.gridLayout)

        self.area.setWidget(self.scrollAreaWidgetContents)
        self.layoutV.addWidget(self.area)
        self.layoutV.addLayout(self.bot_hbox)

        for i in sitetester_list:
            self.widget = tExampleWidget(self.connection, i)
            self.gridLayout.addWidget(self.widget)

        self.setGeometry(0, 0, 1300, 300)

        self.t_site = tester_site
        if self.user_type == "tester":
            self.back_home.clicked.connect(self.tester_back)
        elif self.user_type == "labtester":
            self.back_home.clicked.connect(self.labtester_back)
        self.update.clicked.connect(self.handle_update)

    def tester_back(self):
        for i in self.t_site:
            self.cursor.execute("DELETE FROM working_at WHERE username = \"{}\";".format(i))
            # print("DELETE FROM working_at WHERE username = \"{}\";".format(i))
        for ii in self.original_site_list:
            self.cursor.execute("{}".format(ii))
            # print("{}".format(ii))
        self.close()
        tester_home.TesterHome(self.connection, self.username).exec()

    def labtester_back(self):
        for i in self.t_site:
            self.cursor.execute("DELETE FROM working_at WHERE username = \"{}\";".format(i))
            # print("DELETE FROM working_at WHERE username = \"{}\";".format(i))
        for ii in self.original_site_list:
            self.cursor.execute("{}".format(ii))
            # print("{}".format(ii))
        self.close()
        lab_tester_home.LabTesterHome(self.connection, self.username).exec()

    def handle_update(self):
        self.connection.commit()
        if self.user_type == "tester":
            self.close()
            tester_home.TesterHome(self.connection, self.username).exec()
        elif self.user_type == "labtester":
            self.close()
            lab_tester_home.LabTesterHome(self.connection, self.username).exec()


class tCheckableComboBox(QComboBox):
    def __init__(self, connection, parent=None):
        super(tCheckableComboBox, self).__init__(parent)
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.parent = parent
        self.setView(QListView(self))
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)

        self.cursor.execute(
            "select count(distinct username) from working_at where site = \"{}\" and username not like \"{}\";".format(
                item.text(), self.parent.get_username))
        self.empty_site_condition = self.cursor.fetchall()[0]["count(distinct username)"] != 0

        if item.checkState() == Qt.Checked and self.empty_site_condition:
            item.setCheckState(Qt.Unchecked)
            self.on_selectedItems()
        elif not self.empty_site_condition:
            self.connect_warn(item.text())
        else:
            item.setCheckState(Qt.Checked)
            self.on_selectedItems()

    def connect_warn(self, empty_site):
        twarn_empty_site(empty_site).exec()

    def checkedItems(self):
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == Qt.Checked:
                checkedItems.append(item)
        return checkedItems

    def on_selectedItems(self):
        selectedItems = self.checkedItems()
        self.parent.lblSelectItem.setText("")
        for item in selectedItems:
            self.parent.lblSelectItem.setText("{} *{}*  "
                                              "".format(self.parent.lblSelectItem.text(), item.text()))

        edit_site_list = re.findall("\*(.*?)\*+", self.parent.lblSelectItem.text())
        sql_site_list = ["(\"" + self.parent.get_username + "\", \"" + s + "\")" for s in edit_site_list]
        query_string = "insert into working_at values "
        for i in sql_site_list:
            query_string = query_string + i + ","
        query_string = query_string[:-1] + ";"

        if len(sql_site_list) == 0:
            self.cursor.execute("DELETE FROM working_at WHERE username = \"{}\";".format(self.parent.get_username))
        else:
            self.cursor.execute("DELETE FROM working_at WHERE username = \"{}\";".format(self.parent.get_username))
            self.cursor.execute(query_string)


class twarn_empty_site(QDialog):
    def __init__(self, warnsite):
        super(twarn_empty_site, self).__init__()
        self.setWindowTitle('WARNING')

        self.close_warn = QPushButton("close")
        self.waning_msg1 = QLabel("Invalid Action!")
        self.waning_msg2 = QLabel("{} Will Be Empty!".format(warnsite))

        warn_vbox1 = QVBoxLayout(self)
        warn_vbox1.addWidget(self.waning_msg1)
        warn_vbox1.addWidget(self.waning_msg2)
        warn_vbox1.addWidget(self.close_warn)

        self.close_warn.clicked.connect(self.closewarn)

    def closewarn(self):
        self.close()


class tExampleWidget(QGroupBox):
    def __init__(self, connection, tester_info):
        self.tester_info = tester_info
        self.connection = connection
        self.cursor = self.connection.cursor()
        QGroupBox.__init__(self)
        self.setTitle(tester_info["Name"])
        self.initSubject()
        self.organize()

    def initSubject(self):
        lbl = "Username: {}".format(self.tester_info["Username"])
        self.lblName = QLabel(lbl, self)
        self.get_username = self.tester_info["Username"]
        self.get_ass_list = self.tester_info["Assigned Sites"]
        self.lblSelectItem = QLabel(self)
        self.teachersselect = tCheckableComboBox(self.connection, self)
        self.cursor.execute("select site_name from site;")
        site_fetch = self.cursor.fetchall()
        site_list = []
        for i in site_fetch:
            site_list.append(i["site_name"])
        self.teachersselect.addItems(site_list)
        for i in range(len(site_list)):
            num_list = []
            for k in self.tester_info["Assigned Sites"]:
                if self.teachersselect.findText(k) >= 0:
                    num_list.append(self.teachersselect.findText(k))
            item = self.teachersselect.model().item(i, 0)
            if i in num_list:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def organize(self):
        grid = QGridLayout(self)
        self.setLayout(grid)
        grid.addWidget(self.lblName, 0, 0, 1, 3)
        grid.addWidget(self.lblSelectItem, 1, 0, 1, 2)
        grid.addWidget(self.teachersselect, 0, 2)