from PyQt5 import QtWidgets, uic, QtGui, QtCore
from edgar_scraper import *
import sys
from PyQt5.QtWidgets import QMessageBox
import nyc_bg # Import the background image, to convert the image use the following command: pyrcc5 nyc.qrc -o nyc_bg.py

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        #Load the UI Page
        uic.loadUi('sec.gov.ui', self)
        self.setWindowIcon(QtGui.QIcon("icon.ico"))
        self.check_box_list = []
        self.textbox1_tuple = ()
        self.textbox2_tuple = ()
        self.textbox3_tuple = ()
        self.cik_box1_tuple = ()
        self.cik_box2_tuple = ()
        self.cik_box3_tuple = ()
        self.cik_box4_tuple = ()
        self.cik_box5_tuple = ()

        self.label_12.setOpenExternalLinks(True)

        # Connect the user input for database name
        self.lineEdit_box1_2.textChanged.connect(self.textbox_db_name)
        # Connect the user input for folder directory
        self.lineEdit_box1_3.textChanged.connect(self.textbox_dir)

        # Connect CIK number line edit boxes to user input
        self.lineEdit_box1_4.textChanged.connect(self.textbox1_cik)
        self.lineEdit_box1_5.textChanged.connect(self.textbox2_cik)
        self.lineEdit_box1_6.textChanged.connect(self.textbox3_cik)
        self.lineEdit_box1_7.textChanged.connect(self.textbox4_cik)
        self.lineEdit_box1_8.textChanged.connect(self.textbox5_cik)

        # Connect form slection check boxes to user input
        self.checkBox_10k.stateChanged.connect(self.state_changed_10k)
        self.checkBox_10q.stateChanged.connect(self.state_changed_10q)
        self.checkBox_8k.stateChanged.connect(self.state_changed_8k)
        # Connect form slection line edit boxes to user input
        self.lineEdit_box1.textChanged.connect(self.textbox1)
        self.lineEdit_box2.textChanged.connect(self.textbox2)
        self.lineEdit_box3.textChanged.connect(self.textbox3)

        # Connect date inputs from the user to the program.
        self.dateEdit_start_date = self.findChild(QtWidgets.QDateEdit, 'dateEdit_start_date')
        self.dateEdit_start_date.setCalendarPopup(True)
        self.dateEdit_start_date.dateChanged.connect(self.start_date_change)

        self.dateEdit_end_date = self.findChild(QtWidgets.QDateEdit, 'dateEdit_end_date')
        self.dateEdit_end_date.setCalendarPopup(True)
        self.dateEdit_end_date.dateChanged.connect(self.end_date_change)

        # Connect button click inputs from the user.
        self.generate_DB_button = self.findChild(QtWidgets.QPushButton, 'pushButton_generate_DB')
        self.generate_DB_button.clicked.connect(self.append_textbox_input)
        self.generate_DB_button.clicked.connect(connection1.create_folder)
        self.generate_DB_button.clicked.connect(filings1.Get_Filing_Links)
        if not UserParameters.error_messages:
            self.generate_DB_button.clicked.connect(filings1.get_table_links)
        if not UserParameters.error_messages:
            self.generate_DB_button.clicked.connect(data1.get_tables)
        if not UserParameters.error_messages:
            self.generate_DB_button.clicked.connect(self.clear_lists)
        self.generate_DB_button.clicked.connect(self.error_window)
        # add line to clear error list


        self.normalize_DB_button = self.findChild(QtWidgets.QPushButton, 'pushButton_normalize_DB')
        self.normalize_DB_button.clicked.connect(self.append_textbox_input)
        if not UserParameters.error_messages:
            self.normalize_DB_button.clicked.connect(data1.transpose)
        else:
            self.generate_DB_button.clicked.connect(self.error_window)

    # Format the date inputs from the user.
    def start_date_change(self, start_date):
        formatted_start_date = '{0}-{1}-{2}'.format(start_date.year(), start_date.day(), start_date.month())
        print(f"Starting date has been changed to : {formatted_start_date}") 
        UserParameters.start_date = formatted_start_date
    def end_date_change(self, end_date):
        formatted_end_date = '{0}-{1}-{2}'.format(end_date.year(), end_date.day(), end_date.month())
        print(f"Ending date has been changed to : {formatted_end_date}") 
        UserParameters.end_date = formatted_end_date
    # Add or remove selected forms to/from filing_types list.
    def state_changed_10k(self, int):
        if self.checkBox_10k.isChecked():
            print('10k checked')  
            self.check_box_list.append('10-K')
        else:
            print('10k unchecked') 
            self.check_box_list.remove('10-K') # Remove 10-k from the lsit
        print(f'filing_types list : {UserParameters.filing_types}')
    def state_changed_10q(self, int):
        if self.checkBox_10q.isChecked():
            print('10q checked')  
            self.check_box_list.append('10-Q')
        else:
            print('10q unchecked') 
            self.check_box_list.remove('10-Q') # Remove 10-q from the lsit
        print(f'filing_types list : {UserParameters.filing_types}')
    def state_changed_8k(self, int):
        if self.checkBox_8k.isChecked():
            print('8k checked') 
            self.check_box_list.append('8-K')
        else:
            print('8k unchecked')  
            self.check_box_list.remove('8-K') # Remove 10-k from the lsit
        print(f'filing_types list : {UserParameters.filing_types}')

    # Add custom user-input for form types from the text boxes
    def textbox1(self, text_input):
        self.textbox1_tuple = text_input
        print(f'Custom box 1 : {self.textbox1_tuple}')
    def textbox2(self, text_input):
        self.textbox2_tuple = text_input
        print(f'Custom box 2 : {self.textbox2_tuple}')
    def textbox3(self, text_input):
        self.textbox3_tuple = text_input
        print(f'Custom box 3 : {self.textbox3_tuple}')
    # Add custom user-input for form types from the text boxes
    def textbox1_cik(self, cik_input):
        self.cik_box1_tuple  = cik_input
        print(f'CIK box 1 : {self.cik_box1_tuple}')
    def textbox2_cik(self, cik_input):
        self.cik_box2_tuple  = cik_input
        print(f'CIK box 2 : {self.cik_box2_tuple}')
    def textbox3_cik(self, cik_input):
        self.cik_box3_tuple  = cik_input
        print(f'CIK box 3 : {self.cik_box3_tuple}')
    def textbox4_cik(self, cik_input):
        self.cik_box4_tuple  = cik_input
        print(f'CIK box 4 : {self.cik_box4_tuple}')
    def textbox5_cik(self, cik_input):
        self.cik_box5_tuple  = cik_input
        print(f'CIK box 5 : {self.cik_box5_tuple}')

    # Whenever the button is clicked to generate the database, append tuples to their respective lists.
    def append_textbox_input(self):

        if self.textbox1_tuple:
            UserParameters.filing_types.append(self.textbox1_tuple)
        if self.textbox2_tuple:
            UserParameters.filing_types.append(self.textbox2_tuple)
        if self.textbox3_tuple:
            UserParameters.filing_types.append(self.textbox3_tuple)

        if self.cik_box1_tuple:
            UserParameters.company_CIKs.append(self.cik_box1_tuple)
        if self.cik_box2_tuple:
            UserParameters.company_CIKs.append(self.cik_box2_tuple)
        if self.cik_box3_tuple:
            UserParameters.company_CIKs.append(self.cik_box3_tuple)
        if self.cik_box4_tuple:
            UserParameters.company_CIKs.append(self.cik_box4_tuple)
        if self.cik_box5_tuple:
            UserParameters.company_CIKs.append(self.cik_box5_tuple)

        if self.check_box_list:
            UserParameters.filing_types.extend(self.check_box_list)

        if UserParameters.folder_path and UserParameters.db_name:
            UserParameters.db_path = f"{UserParameters.folder_path}\{UserParameters.db_name}"
        else:
            UserParameters.error_messages = 'Check to make sure you have typed the correct directory.'


    # Store directory input in UserParameters.folder_path
    def textbox_dir(self, text_input):
        UserParameters.folder_path = text_input
        print(f'UserParameters.folder_path : {UserParameters.folder_path}')
    # Store database name input in UserParameters.db_name
    def textbox_db_name(self, text_input):
        UserParameters.db_name = text_input + '.db'
        print(f'UserParameters.db_name : {UserParameters.db_name}')

    # Clear lsits
    def clear_lists(self):
        print(f'Appended form types list : {UserParameters.filing_types}')
        print(f'Appended CIK list : {UserParameters.company_CIKs}')
        print(f'Start date : {UserParameters.start_date}')
        print(f'End end : {UserParameters.end_date}')
        print(f'DB name : {UserParameters.db_name}')
        print(f'DB folder path : {UserParameters.folder_path}')
        print(f'DB path : {UserParameters.db_path}')
        if UserParameters.company_CIKs:
            UserParameters.company_CIKs.clear()
        if UserParameters.filing_types:
            UserParameters.filing_types.clear()
        print(f'Cleared: Appended form types list : {UserParameters.filing_types}')
        print(f'Cleared: Appended CIK list : {UserParameters.company_CIKs}')
        print(f'Cleared DB name : {UserParameters.db_name}')
        print(f'Cleared DB folder path : {UserParameters.folder_path}')
        print(f'Cleared DB path : {UserParameters.db_path}')



    def error_window(self):
        if UserParameters.error_messages:
            QMessageBox.about(self, "Error Messages", ','.join(str(v) for v in UserParameters.error_messages))
        else:
            QMessageBox.about(self, "Message", 'Program execution completed.')
        UserParameters.error_messages.clear()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    main()
