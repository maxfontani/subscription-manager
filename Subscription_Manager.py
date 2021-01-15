from datetime import date, datetime
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QHeaderView
from PyQt5.QtWidgets import QAbstractItemView, QStatusBar, QLabel, QFileDialog
import classes
import db
import logging
import re
import sys
import sqlite3

class MainWindow(QMainWindow):
    # Main window initialization block
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(r'UI\\Subscription_Manager.ui', self)
        self.button1.clicked.connect(self.clicked_button1)
        self.button2.clicked.connect(self.clicked_button2)
        self.button3.clicked.connect(self.clicked_button3)
        self.button4.clicked.connect(self.clicked_button4)
        self.button5.clicked.connect(self.clicked_button5)
        self.button6.clicked.connect(self.clicked_button6)

        self.action_clients.triggered.connect(self.triggered_action_clients)
        self.action_subs.triggered.connect(self.triggered_action_subs)
        self.action_stat.triggered.connect(self.triggered_action_stat)
        self.action_backup.triggered.connect(self.triggered_action_backup)
        self.action_db.triggered.connect(self.triggered_action_db)

        self.table_widget1.itemSelectionChanged.connect(self.table_widget1_selection_changed)
        self.table_widget1.itemDoubleClicked.connect(self.table_widget1_item_double_clicked)
        self.table_widget1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.line_edit1.textChanged.connect(self.line_edit1_text_changed)
        self.current_name = ''
        self.current_ID = -1

        self.setWindowIcon(QIcon(r'UI\\Subscription_Manager.ico'))

        # Set resize mode for each table_widget1 column
        header = self.table_widget1.horizontalHeader()                  
        for i in range(0, self.table_widget1.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        # Display the currently connected database on the status bar
        self.status_bar = QStatusBar()
        self.status_label = QLabel()
        self.status_label.setText(f'CURRENT DB: {db.DB_PATH}')
        self.setStatusBar(self.status_bar)
        self.status_bar.addPermanentWidget(self.status_label)

        # Establish the log file
        logging.basicConfig(filename='History.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')

        # Fill the tables with recently ended/ending subscriptions
        self.show_recent()

        # Show the main window
        self.show()

    # Generic error message function
    def show_err_message(self,text):
        msg = QMessageBox(QMessageBox.Critical,'Error!',text)
        msg.exec_()

    # Generic message function
    def show_message(self,text):
        msg = QMessageBox(QMessageBox.Information,'Success!',text)
        msg.exec_()

    # Function to call upon pressing the Clients menu
    def triggered_action_clients(self, search_id=False):

        # Function to call upon clicking the Add Client button
        def clients_window_button1_clicked():

            # Function to call upon clicking the Add button
            def add_client_dialog_button1_clicked(self):
                try:
                    client_name = add_client_dialog.line_edit1.text()
                    client_tel = add_client_dialog.line_edit2.text()
                    if add_client_dialog.line_edit3.text() != '':
                        client_email = add_client_dialog.line_edit3.text()
                    else:
                        client_email = None
                    client_level = add_client_dialog.combo_box1.currentText()
                    client = classes.Client(client_name, client_tel, client_email,client_level)
                    conn,cursor = db.connect_db()
                    db.add_client(client,conn,cursor)
                    main_window.show_message('Client added successfully!')

                    # Refresh the Clients window
                    add_client_dialog.close()
                    clients_window.close()
                    main_window.triggered_action_clients()

                except Exception as ex:
                    text = 'Error while eding a client!\n' + str(ex)
                    main_window.show_err_message(text)
                    add_client_dialog.close()

            # Load the QDialog Add_Client.ui
            add_client_dialog = QtWidgets.QDialog()
            uic.loadUi(r'UI\\Add_Client.ui', add_client_dialog)

            add_client_dialog.button1.clicked.connect(add_client_dialog_button1_clicked)

            add_client_dialog.exec_()

        # Function to call upon clicking the Edit Client button
        def clients_window_button2_clicked():
            # Check the ID of the selected client
            current_row = clients_window.table_widget.currentRow()
            current_client_id = int(clients_window.table_widget.item(current_row,0).text())

            # Function to call upon pressing the Edit subscription button
            def edit_client_button1_clicked(self):
                try:
     
                    # Check if the values were changed and update them
                    if edit_client_dialog.line_edit1.text() != current_name:
                        # Connect to the database and update the information
                        conn, cursor = db.connect_db()
                        with conn:
                            new_name = edit_client_dialog.line_edit1.text()

                            # Check whether the name already exists in the DB
                            cursor.execute("SELECT name FROM clients")
                            name_list = [row[0] for row in cursor.fetchall()]
                            if new_name in name_list:
                                raise Exception('THE NAME ALREADY EXISTS IN THE DB!')

                            cursor.execute('UPDATE clients SET name = (?) WHERE client_ID = (?)',(new_name,current_client_id))

                    if edit_client_dialog.line_edit2.text() != current_tel:
                        # Connect to the database, check its format, and update the information
                        new_tel = edit_client_dialog.line_edit2.text()
                        conn, cursor = db.connect_db()
                        with conn:

                            # Telephone number format restrictions: 10-digit without spaces, start with "0"
                            pattern = re.compile(r"^0[1-9]\d{8}$")
                            check = pattern.fullmatch(new_tel)

                            if check == None:
                                raise ValueError('WRONG TEL FORMAT!')

                            # Check whether the tel number already exists in the DB
                            cursor.execute("SELECT tel FROM clients")
                            tel_list = [row[0] for row in cursor.fetchall()]
                            if new_tel in tel_list:
                                raise Exception('THE TEL NUMBER ALREDY EXISTS IN THE DB!')

                            cursor.execute('UPDATE clients SET tel = (?) WHERE client_ID = (?)',(new_tel,current_client_id))

                    if edit_client_dialog.line_edit3.text() != current_email:
                        new_email = edit_client_dialog.line_edit3.text()

                        pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
                        check = pattern.fullmatch(new_email)

                        if check == None:
                            raise ValueError('WRONG EMAIL FORMAT!')

                        conn, cursor = db.connect_db()
                        with conn:
                            cursor.execute('UPDATE clients SET email = (?) WHERE client_ID = (?)',(new_email,current_client_id))

                    if edit_client_dialog.combo_box1.currentText() != current_level:
                        new_level = edit_client_dialog.combo_box1.currentText()

                        conn, cursor = db.connect_db()
                        with conn:
                            cursor.execute('UPDATE clients SET level = (?) WHERE client_ID = (?)',(new_level,current_client_id))

                    if edit_client_dialog.date_edit1.date() != current_last_active_date:
                        new_last_active_date = edit_client_dialog.date_edit1.date().toString('dd/MM/yyyy')
                        conn, cursor = db.connect_db()
                        with conn:
                            cursor.execute('UPDATE clients SET last_active_date = (?) WHERE client_ID = (?)',(new_last_active_date,current_client_id))

                    main_window.show_message('The data has been updated!')
                    edit_client_dialog.close()
                    clients_window.close()
                    main_window.triggered_action_clients()

                except Exception as ex:
                    text = 'Error while updating data!\n'
                    main_window.show_err_message(text + str(ex))
                    edit_client_dialog.close()

            # Load the Qdialog Edit_Client.ui
            edit_client_dialog = QtWidgets.QDialog()
            uic.loadUi(r'UI\\Edit_Client.ui', edit_client_dialog)

            # Fill the dialog with client's current info
            current_name = clients_window.table_widget.item(current_row,1).text()
            current_tel = clients_window.table_widget.item(current_row,2).text()
            current_email = clients_window.table_widget.item(current_row,3).text()
            current_level = clients_window.table_widget.item(current_row,4).text()
            current_last_active_date = QtCore.QDate.fromString(clients_window.table_widget.item(current_row,5).text(), 'dd/MM/yyyy')

            edit_client_dialog.line_edit1.setText(current_name)
            edit_client_dialog.line_edit2.setText(current_tel)
            edit_client_dialog.line_edit3.setText(current_email)
            edit_client_dialog.combo_box1.setCurrentText(current_level)
            edit_client_dialog.date_edit1.setDate(current_last_active_date)

            # Connect the Edit button to its function
            edit_client_dialog.button1.clicked.connect(edit_client_button1_clicked)

            # Show the Dialog window
            edit_client_dialog.exec_()

        # Function to call upon clicking the Delete Client button
        def clients_window_button3_clicked():

            # Display a confirmation window before deleting the client
            box = QMessageBox()
            box.setIcon(QMessageBox.Question)
            box.setWindowTitle('Confirmation')
            box.setText('Are you sure you wish to delete the Client entry and all of their Subscriptions?')
            box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            buttonY = box.button(QMessageBox.Yes)
            buttonN = box.button(QMessageBox.No)
            box.exec_()

            if box.clickedButton() == buttonN:
                pass
            elif box.clickedButton() == buttonY:
                current_row = clients_window.table_widget.currentRow()
                current_client_id = clients_window.table_widget.item(current_row,0).text()

                conn,cursor = db.connect_db()
                with conn:
                    try:
                        cursor.execute("DELETE FROM subscriptions WHERE holder = (?)", (current_client_id,))
                        conn.commit()
                        cursor.execute("DELETE FROM clients WHERE client_ID = (?)", (current_client_id,))
                        conn.commit()
                        main_window.show_message('The Client entry has been removed!')
                        main_window.line_edit1.setText('')

                    except Exception as ex:
                        text = 'Error while removing the Client entry!' + str(ex)
                        main_window.show_err_message(text)

                clients_window.close()
                main_window.show_recent()
                main_window.triggered_action_clients()

        # The function enables the editing buttons only when a row in the Clients table is selected
        def clients_table_widget_selection_changed():
            if clients_window.table_widget.selectedItems() == []:
                clients_window.button2.setEnabled(False)
                clients_window.button3.setEnabled(False)
            else:
                clients_window.button2.setEnabled(True)
                clients_window.button3.setEnabled(True)

        # Clicks the edit client button upon double clicking a row in the Clients table
        def clients_window_table_widget_item_double_clicked():
            clients_window_button2_clicked()

        # Load the Clients window UI
        clients_window = QtWidgets.QDialog(self)
        uic.loadUi(r'UI\\Clients.ui', clients_window)

        # CONNECT TO THE DB
        conn,cursor = db.connect_db()

        # Fill the All Clients table
        with conn:
            row_count = cursor.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            clients_window.table_widget.setRowCount(row_count)

            cursor.execute('SELECT client_ID,name,tel,email,level,last_active_date FROM clients')
            for row, form in enumerate(cursor.fetchall()):
                for column, item in enumerate(form):
                    clients_window.table_widget.setItem(row, column, QTableWidgetItem(str(item)))

        # Disable editing table items
        clients_window.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set resize mode for each table_widget2 column
        header = clients_window.table_widget.horizontalHeader()
        for i in range(0, clients_window.table_widget.columnCount()-1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Sort the table_widget1 by the descending date_issued
        clients_window.table_widget.setSortingEnabled(True)
        clients_window.table_widget.sortItems(1, order = 1)

        # Allow to select only entire rows in table_widget1
        clients_window.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        clients_window.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)

        # Connect the buttons to the respective functions
        clients_window.button1.clicked.connect(clients_window_button1_clicked)
        clients_window.button2.clicked.connect(clients_window_button2_clicked)
        clients_window.button3.clicked.connect(clients_window_button3_clicked)
        clients_window.table_widget.itemDoubleClicked.connect(clients_window_table_widget_item_double_clicked)
        clients_window.table_widget.itemSelectionChanged.connect(clients_table_widget_selection_changed)

        # If a name was parsed, select it in the All Clients list
        if search_id != False:
            for row in range(row_count):
                if clients_window.table_widget.item(row,0).text() == str(search_id):
                    clients_window.table_widget.selectRow(row)
                    break

        clients_window.exec_()

    # Function to call upon pressing the Subscriptions menu
    def triggered_action_subs(self):

        def subs_window_button1_clicked(self):

            # Function to call upon clicking the Freeze All button
            def freeze_sub_dialog_clicked_button1():
                # Display the confirmation window and check the input
                box = QMessageBox()
                box.setIcon(QMessageBox.Question)
                box.setWindowTitle('Confirmation')
                box.setText('Are you sure you wish to freeze ALL of the ACTIVE subscriptions?')
                box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                buttonY = box.button(QMessageBox.Yes)
                buttonN = box.button(QMessageBox.No)
                box.exec_()

                if box.clickedButton() == buttonN:
                    freeze_sub_dialog.close()
                    subs_window.close()
                    main_window.triggered_action_subs()

                # If confirmed, connect to the DB and freeze all of the active subscriptions
                elif box.clickedButton() == buttonY:
                    try:
                        days_to_freeze = freeze_sub_dialog.spin_box1.value()
                        db.update_sub_status()
                        conn, cursor = db.connect_db()
                        with conn:
                            cursor.execute("SELECT sub_ID FROM subscriptions WHERE status = 'ACTIVE'")

                        for sid in cursor.fetchall():
                            db.freeze_sub(sid[0],days_to_freeze,conn,cursor)

                        logging.info(f'FROZEN ALL subscriptions. Days: {days_to_freeze}.')

                        main_window.show_message('ALL ACTIVE subscriptions have been frozen!')
                        freeze_sub_dialog.close()
                        subs_window.close()
                        main_window.show_recent()
                        main_window.triggered_action_subs()

                    except Exception as ex:
                        text = 'Error while freezing subscriptions!\n'
                        main_window.show_err_message(text + str(ex))
                        freeze_sub_dialog.close()

            # Load the Freeze window UI
            freeze_sub_dialog = QtWidgets.QDialog()
            uic.loadUi(r'UI\\Freeze_Sub.ui', freeze_sub_dialog)
            freeze_sub_dialog.label1.setText('FREEZE ALL SUBS')
            freeze_sub_dialog.button1.clicked.connect(freeze_sub_dialog_clicked_button1)
            freeze_sub_dialog.exec_()

        # Load the Subscriptions window UI
        subs_window = QtWidgets.QDialog(self)
        uic.loadUi(r'UI\\Subs.ui', subs_window)

        # CONNECT TO THE DB
        conn,cursor = db.connect_db()

        # Fill the All Subs table
        with conn:
            row_count = cursor.execute("SELECT COUNT(*) FROM subscriptions").fetchone()[0]
            subs_window.table_widget.setRowCount(row_count)

            cursor.execute('SELECT sub_ID,date_issued,date_ends,sub_type,status,days_frozen FROM subscriptions')
            for row, form in enumerate(cursor.fetchall()):
                for column, item in enumerate(form):
                    # In order for QTableWidget to sort dates, they need to be passed in a special format
                    if column == 1 or column == 2:
                        tw_item = QTableWidgetItem()
                        tw_item.setData(0, QtCore.QDate.fromString(item, 'dd/MM/yyyy'))
                        subs_window.table_widget.setItem(row, column, tw_item)
                    else:
                        subs_window.table_widget.setItem(row, column, QTableWidgetItem(str(item)))

        # Disable editing table items
        subs_window.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set resize mode for each table_widget2 column
        header = subs_window.table_widget.horizontalHeader()
        for i in range(0, subs_window.table_widget.columnCount()-2):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(subs_window.table_widget.columnCount()-1, QHeaderView.Stretch)

        # Sort the table_widget1 by the descending date_issued
        subs_window.table_widget.setSortingEnabled(True)
        subs_window.table_widget.sortItems(1, order = 1)

        # Allow to select only entire rows in table_widget1
        subs_window.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        subs_window.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)

        # Connect the buttons to the respective functions
        subs_window.button1.clicked.connect(subs_window_button1_clicked)

        subs_window.exec_()

    # Function to call upon pressing the Statistics menu
    def triggered_action_stat(self):

        # Load the Statistics window UI
        stat_window = QtWidgets.QDialog(self)
        uic.loadUi(r'UI\\Statistics.ui', stat_window)

        # Function to call upon pressing the Refresh button
        def stat_window_button1_clicked():
            db.update_sub_status()
            main_window.show_recent()
            fill_statistics_table()

        # Function to fill the Statistics table
        def fill_statistics_table():
            try:
                stat_window.table_widget.clearContents()
                stat_window.table_widget.setRowCount(0)                
                stat_window.table_widget.setSortingEnabled(False)

                # CONNECT TO THE DB
                conn,cursor = db.connect_db()
                with conn:

                    if stat_window.radio_button3.isChecked():
                        current_days = 8
                    elif stat_window.radio_button4.isChecked():
                        current_days = 15
                    elif stat_window.radio_button5.isChecked():
                        current_days = 32

                    today = date.today()
                    if stat_window.radio_button1.isChecked():
                        # Collect all of the active subscriptions
                        cursor.execute("SELECT sub_ID,holder,date_ends FROM subscriptions WHERE status = 'ACTIVE'")
                        sub_list = [(x,y,z) for x,y,z in cursor.fetchall()]

                        # Fill the table with subscriptions ending soon
                        current_row = 0
                        current_status = 'ACTIVE'
                        stat_window.table_widget.setHorizontalHeaderItem(4,QTableWidgetItem('Days left'))
                        for elem in sub_list:
                            date_obj = datetime.strptime(elem[2],'%d/%m/%Y').date()
                            date_diff = date_obj - today
                            if 0 <= date_diff.days < current_days:
                                stat_window.table_widget.setRowCount(current_row+1)
                                stat_window.table_widget.setItem(current_row, 0, QTableWidgetItem(str(elem[0])))
                                cursor.execute("SELECT name, tel, level FROM clients WHERE client_ID = (?)",(elem[1],))
                                current_name_level = cursor.fetchone()
                                # Parse the date difference into the table widget in data format for sorting to work properly
                                tw_item =QTableWidgetItem()
                                tw_item.setData(0,date_diff.days)
                                stat_window.table_widget.setItem(current_row, 1, QTableWidgetItem(str(current_name_level[0])))
                                stat_window.table_widget.setItem(current_row, 2, QTableWidgetItem(str(current_name_level[1])))
                                stat_window.table_widget.setItem(current_row, 3, QTableWidgetItem(str(current_name_level[2])))
                                stat_window.table_widget.setItem(current_row, 4, tw_item)
                                stat_window.table_widget.setItem(current_row, 5, QTableWidgetItem(str(current_status)))
                                current_row += 1

                    elif stat_window.radio_button2.isChecked():
                        # Collect all of the ended subscriptions
                        cursor.execute("SELECT sub_ID, holder,date_ends FROM subscriptions WHERE status = 'ENDED'")
                        sub_list = [(x,y,z) for x,y,z in cursor.fetchall()]

                        # Fill the table with subscriptions that ended recently
                        current_row = 0
                        current_status = 'ENDED'
                        stat_window.table_widget.setHorizontalHeaderItem(4,QTableWidgetItem('Days ago'))
                        for elem in sub_list:
                            date_obj = datetime.strptime(elem[2],'%d/%m/%Y').date()
                            date_diff = today - date_obj
                            if 0 < date_diff.days < current_days:
                                stat_window.table_widget.setRowCount(current_row+1)
                                stat_window.table_widget.setItem(current_row, 0, QTableWidgetItem(str(elem[0])))
                                cursor.execute("SELECT name, tel, level FROM clients WHERE client_ID = (?)",(elem[1],))
                                current_name_level = cursor.fetchone()
                                # Parse the date difference into the table widget in data format for sorting to work properly
                                tw_item =QTableWidgetItem()
                                tw_item.setData(0,date_diff.days)
                                stat_window.table_widget.setItem(current_row, 1, QTableWidgetItem(str(current_name_level[0])))
                                stat_window.table_widget.setItem(current_row, 2, QTableWidgetItem(str(current_name_level[1])))
                                stat_window.table_widget.setItem(current_row, 3, QTableWidgetItem(str(current_name_level[2])))
                                stat_window.table_widget.setItem(current_row, 4, tw_item)
                                stat_window.table_widget.setItem(current_row, 5, QTableWidgetItem(str(current_status)))
                                current_row += 1

                    # Sort the table_widget1 by the descending date_issued
                    stat_window.table_widget.setSortingEnabled(True)
                    stat_window.table_widget.sortItems(4, order = 0)

            except Exception as ex:
                text = 'Error while displaying the statistics!\n'
                main_window.show_err_message(text + str(ex))

        # Disable editing table items
        stat_window.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set resize mode for each table_widget2 column
        header = stat_window.table_widget.horizontalHeader()
        for i in range(0, stat_window.table_widget.columnCount()-1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Allow to select only entire rows in table_widget1
        stat_window.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        stat_window.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)

        # Connect the buttons to the respective functions
        stat_window.button1.clicked.connect(stat_window_button1_clicked)
        stat_window.radio_button1.toggled.connect(fill_statistics_table)
        stat_window.radio_button2.toggled.connect(fill_statistics_table)
        stat_window.radio_button3.toggled.connect(fill_statistics_table)
        stat_window.radio_button4.toggled.connect(fill_statistics_table)
        stat_window.radio_button5.toggled.connect(fill_statistics_table)

        # Call the function to fill the table and display the Statistics window
        fill_statistics_table()
        stat_window.exec_()

    # Function to call upon pressing the Create backup menu
    def triggered_action_backup(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle('Confirmation')
        box.setText(f'Do you wish to create a backup copy of {db.DB_PATH}?')
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        buttonY = box.button(QMessageBox.Yes)
        buttonN = box.button(QMessageBox.No)
        box.exec_()

        if box.clickedButton() == buttonY:
            db.backup_db()
        else:
            pass

    # Function to call upon clicking the Change Database menu item
    def triggered_action_db(self):
        # Function to call upon clikcing the Feeling Lucky button
        def action_db_button_clicked():
            entered_pwd = action_db_dialog.line_edit.text()

            # If the password matches, open a File dialog to choose another DB
            # the default password is 'admin'
            if db.hashed(entered_pwd) == 'd033e22ae348aeb5660fc2140aec35850c4da997':
                fname = QFileDialog.getOpenFileName(self, 'Select the DB', 'DB','DB files (*.db)')
                db.DB_PATH = fname[0]
                action_db_dialog.close()
                # Update the DB displayed on the status bar
                main_window.status_label.setText(f'CURRENT DB: {db.DB_PATH}')
                main_window.update()
            else:
                main_window.show_err_message('WRONG PASSWORD!')

        # Load the Password check UI
        action_db_dialog = QtWidgets.QDialog(self)
        uic.loadUi(r'UI\\Password.ui', action_db_dialog)

        # Connect the Feeling Lucky button to its function
        action_db_dialog.button.clicked.connect(action_db_button_clicked)

        # Show the Dialog window
        action_db_dialog.exec_()

    # Function called when clicking the Search button
    def clicked_button1(self):
        #  Clear the previous table_widget1 data
        self.table_widget1.clearContents()
        self.table_widget1.setRowCount(0)

        # Update the subscriptions' statuses if they have expired and refresh the statistics
        db.update_sub_status()
        main_window.show_recent()

        try:
            # If line_edit1 is empty, raise Exception
            if self.line_edit1.text() == '':
                raise Exception

            # CONNECT TO THE DB
            conn,cursor = db.connect_db()

            with conn:
                # Check whether the NAME or TEL are entered into the Search field
                client_entered = self.line_edit1.text()
                pattern = re.compile(r"\d{10}$")
                check = pattern.fullmatch(client_entered)

                if check != None:
                    param = 'tel'
                else:
                    param = 'name'

                #Find the client_ID through the entered TEL or NAME
                client_entered_ID = cursor.execute("SELECT client_ID FROM clients WHERE {} = (?)".format(param),(client_entered,)).fetchone()[0]
                self.current_ID = client_entered_ID

                # Enable the Open Profile button
                self.button6.setEnabled(True)

                # Determine the holder's name and display it above the table_widget
                self.current_name = cursor.execute("SELECT name FROM clients WHERE client_ID = (?)", (client_entered_ID,)).fetchone()[0]
                self.label2.setText(f'Subscriptions of {self.current_name}')

                # Fill the table_widget1
                # Determine the number of rows to display
                row_count = cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE holder = (?)", (client_entered_ID,)).fetchone()[0]

                # Check if the client has any subscriptions
                if row_count == 0:
                    self.show_message(f'{self.current_name} has no subs yet.')
                    self.button2.setEnabled(True)
                else:

                    self.table_widget1.setSortingEnabled(False)
                    self.table_widget1.setRowCount(row_count)

                    # Fill the table_widget1 with data
                    cursor.execute("SELECT sub_ID,date_issued,date_ends,sub_type,status,days_frozen FROM subscriptions WHERE holder = (?)", (client_entered_ID,))
                    for row, form in enumerate(cursor.fetchall()):
                        # In order for QTableWidget to sort dates correctly, they need to be passed in a special format
                        for column, item in enumerate(form):
                            if column == 1 or column == 2:
                                tw_item = QTableWidgetItem()
                                tw_item.setData(0, QtCore.QDate.fromString(item, 'dd/MM/yyyy'))
                                self.table_widget1.setItem(row, column, tw_item)
                            else:
                                self.table_widget1.setItem(row, column, QTableWidgetItem(str(item)))

                    # Sort the table_widget1 by the descending date_issued
                    self.table_widget1.setSortingEnabled(True)
                    self.table_widget1.sortItems(1, order = 1)

                    # Allow to select only entire rows in table_widget1
                    self.table_widget1.setSelectionBehavior(QAbstractItemView.SelectRows)
                    self.table_widget1.setSelectionMode(QAbstractItemView.SingleSelection)

                    # Enable the button to edit subscriptions for the clinet
                    self.button2.setEnabled(True)

        except ValueError as ex:
            self.button2.setEnabled(False)
            self.show_err_message(str(ex))
        except Exception:
            if self.line_edit1.text() == '':
                text = 'Please enter search data (Name/Tel)!'
                self.button2.setEnabled(False)
                self.show_err_message(text)
            else:
                text = 'Client not found.\n'
                self.button2.setEnabled(False)
                self.show_err_message(text)

    # Function to call upon clicking the Add Subscription button
    def clicked_button2(self):
        # Allow only one radio button to be enabled
        def radio2_toggled(self):
            if add_sub_dialog.radio2.isChecked():
                add_sub_dialog.date_edit.setEnabled(True)
            else:
                add_sub_dialog.date_edit.setEnabled(False)

        # Function to call upon clicking the Add button
        def add_sub_dialog_button1_clicked(self):

            # Record the desired subscription type
            sub_type_combo_box = int(add_sub_dialog.combo_box1.currentText())

            # Set the desired issue date
            if add_sub_dialog.radio1.isChecked():
                new_sub = classes.Subscription(id, sub_type=sub_type_combo_box)
            else:
                current_date = add_sub_dialog.date_edit.date().toString(format = 4)
                new_sub = classes.Subscription(id, date_issued=current_date, sub_type=sub_type_combo_box)
            
            try:        
                date_ends_check = datetime.strptime(new_sub.date_ends,'%d/%m/%Y').date()
                if date_ends_check <= date.today():
                    raise ValueError

                conn, cursor = db.connect_db()
                db.add_sub(new_sub, conn, cursor)
                add_sub_dialog.close()

            except ValueError as ex:
                text = 'The ending date must not precede today!\n' + str(ex)
                main_window.show_err_message(text)
                add_sub_dialog.close()
                main_window.button2.setEnabled(False)
            except Exception as ex:
                text = 'Error while adding a subscription!\n' + str(ex)
                main_window.show_err_message(text)
                add_sub_dialog.close()
                main_window.button2.setEnabled(False)

        # Parse the currently entered ID futher
        id = self.current_ID

        # Load the QDialog Add_Sub.ui
        add_sub_dialog = QtWidgets.QDialog(self)
        uic.loadUi(r'UI\\Add_Sub.ui', add_sub_dialog)

        # Display the name of the new subscription's holder
        add_sub_dialog.label1.setText(self.current_name)

        add_sub_dialog.button1.clicked.connect(add_sub_dialog_button1_clicked)
        add_sub_dialog.radio2.toggled.connect(radio2_toggled)

        # Display today's date
        add_sub_dialog.date_edit.setDate(date.today())

        # Show the Dialog window and refresh the search table upon closing it
        add_sub_dialog.exec_()
        self.clicked_button1()

    # Function to call upon clicking the Freeze button
    def clicked_button3(self):
        # Check the ID of the selected subscription
        current_row = self.table_widget1.currentRow()
        current_sub_id = int(self.table_widget1.item(current_row,0).text())

        # Function to call upon pressing the Freeze subscription button
        def freeze_sub_button1_clicked(self):
            try:
                # Connect to the database and update the information
                days_to_freeze = freeze_sub_dialog.spin_box1.value()
                conn, cursor = db.connect_db()
                db.freeze_sub(current_sub_id, days_to_freeze, conn, cursor)

                # Log the freeze sub event
                logging.info(f'FROZEN Client: {freeze_sub_dialog.label1.text()}. Sub ID: {current_sub_id}. Days: {days_to_freeze}.')

                main_window.show_message('Subscription frozen successfully!')
                freeze_sub_dialog.close()
                main_window.clicked_button1()

            except Exception as ex:
                text = 'Error while freezing the subscription!\n'
                main_window.show_err_message(text + str(ex))
                freeze_sub_dialog.close()

        # Load the Qdialog Freeze_Sub.ui
        freeze_sub_dialog = QtWidgets.QDialog(self)
        uic.loadUi(r'UI\\Freeze_Sub.ui', freeze_sub_dialog)
        freeze_sub_dialog.label1.setText(self.current_name)

        # Connect the Freeze button to its function
        freeze_sub_dialog.button1.clicked.connect(freeze_sub_button1_clicked)

        # Show the Dialog window
        freeze_sub_dialog.exec_()

    # Function to call upon clicking the Edit Sub button
    def clicked_button4(self):
        # Check the ID of the selected subscription
        current_row = self.table_widget1.currentRow()
        current_sub_id = int(self.table_widget1.item(current_row,0).text())

        # Function to call upon pressing the Edit subscription button
        def edit_sub_button1_clicked(self):

            try:
                # Check if the fields were changed and update the subscriptions in the DB accordingly
                if edit_sub_dialog.date_edit1.date() != current_date_issued:
                    # The issued date must not exceed the ending date
                    if edit_sub_dialog.date_edit1.date() > edit_sub_dialog.date_edit2.date():
                        main_window.show_err_message('The issue date must not exceed the end date!')
                        raise ValueError

                    # Connect to the database and update the information
                    conn, cursor = db.connect_db()
                    with conn:
                        new_date_issued = edit_sub_dialog.date_edit1.text()
                        cursor.execute('UPDATE subscriptions SET date_issued = (?) WHERE sub_ID = (?)',(new_date_issued,current_sub_id))

                if edit_sub_dialog.date_edit2.date() != current_date_ends:
                    # The date end must not preceede the issue date
                    if edit_sub_dialog.date_edit1.date() > edit_sub_dialog.date_edit2.date():
                        main_window.show_err_message('The issue date must not exceed the end date!')
                        raise ValueError

                    # Connect to the database and update the information
                    conn, cursor = db.connect_db()
                    with conn:
                        new_date_ends = edit_sub_dialog.date_edit2.text()
                        cursor.execute('UPDATE subscriptions SET date_ends = (?) WHERE sub_ID = (?)',(new_date_ends,current_sub_id))
                        logging.info(f'EDITED End date. Client {edit_sub_dialog.label1.text()}. Sub ID: {current_sub_id}. Old date: {current_date_ends.toString(format = 4)}. New date: {new_date_ends}.')

                if int(edit_sub_dialog.combo_box1.currentText()) != current_type:
                    # Connect to the database and update the information
                    conn, cursor = db.connect_db()
                    with conn:
                        new_sub_type = edit_sub_dialog.combo_box1.currentText()
                        cursor.execute('UPDATE subscriptions SET sub_type = (?) WHERE sub_ID = (?)',(new_sub_type,current_sub_id))

                if edit_sub_dialog.line_edit1.text() != current_days_frozen:
                    if edit_sub_dialog.line_edit1.text().isdigit():
                        # Connect to the database and update the information
                        conn, cursor = db.connect_db()
                        with conn:
                            new_days_frozen = edit_sub_dialog.line_edit1.text()
                            cursor.execute('UPDATE subscriptions SET days_frozen = (?) WHERE sub_ID = (?)',(new_days_frozen,current_sub_id))
                            logging.info(f'EDITED Days frozen. Client {edit_sub_dialog.label1.text()}. Sub ID: {current_sub_id}. Old number of days: {current_days_frozen}. New number of days: {new_days_frozen}.')

                    else:
                        raise ValueError

                main_window.show_message('Successful data update!')
                edit_sub_dialog.close()
                main_window.clicked_button1()

            except Exception as ex:
                text = 'Error while updating data!\n'
                main_window.show_err_message(text + str(ex))
                edit_sub_dialog.close()

        # Load the Qdialog Edit_Sub.ui
        edit_sub_dialog = QtWidgets.QDialog(self)
        uic.loadUi(r'UI\\Edit_Sub.ui', edit_sub_dialog)

        # Fill the dialog with subscription's info
        edit_sub_dialog.label1.setText('Sub no.'+str(current_sub_id))
        current_row = self.table_widget1.currentRow()

        current_type = int(self.table_widget1.item(current_row,3).text())
        if current_type == 1:
            edit_sub_dialog.combo_box1.setCurrentIndex(0)
        elif current_type == 3:
            edit_sub_dialog.combo_box1.setCurrentIndex(1)
        elif current_type == 6:
            edit_sub_dialog.combo_box1.setCurrentIndex(2)
        elif current_type == 12:
            edit_sub_dialog.combo_box1.setCurrentIndex(3)


        current_date_issued = self.table_widget1.item(current_row,1).data(0)
        edit_sub_dialog.date_edit1.setDate(current_date_issued)
        current_date_ends = self.table_widget1.item(current_row,2).data(0)
        edit_sub_dialog.date_edit2.setDate(current_date_ends)
        current_days_frozen = self.table_widget1.item(current_row,5).text()
        edit_sub_dialog.line_edit1.setText(current_days_frozen)

        # Connect the Edit button to its function
        edit_sub_dialog.button1.clicked.connect(edit_sub_button1_clicked)

        # Show the Dialog window
        edit_sub_dialog.exec_()

    # Function to call upon clicking the Delete button
    def clicked_button5(self):
        current_row = self.table_widget1.currentRow()
        current_sub_ID = self.table_widget1.item(current_row,0).text()

        conn,cursor = db.connect_db()
        with conn:
            try:
                cursor.execute("DELETE FROM subscriptions WHERE sub_ID = (?)", (current_sub_ID,))
                self.show_message('The subscription has been removed!')

            except Exception as ex:
                text = 'Error while removing the subscription!' + str(ex)
                self.show_err_message(text)

        self.clicked_button1()

    # Function to call upon clicking the Open Profile button
    def clicked_button6(self):
        self.triggered_action_clients(self.current_ID)

    # Function to call upon selection changes in Subscriptions table
    def table_widget1_selection_changed(self):

        #  Enable editing buttons only when a row in Subscriptions table is selected. Enable freezing only for active subs.
        if self.table_widget1.selectedItems() == []:
            self.button3.setEnabled(False)
            self.button4.setEnabled(False)
            self.button5.setEnabled(False)
        elif self.table_widget1.selectedItems()[4].text() != 'ACTIVE':
            self.button3.setEnabled(False)
            self.button4.setEnabled(True)
            self.button5.setEnabled(True)                
        else:
            self.button3.setEnabled(True)
            self.button4.setEnabled(True)
            self.button5.setEnabled(True)

    # Function to call the edit dialog upon double clicking a subscription row on the main window
    def table_widget1_item_double_clicked(self):
        self.clicked_button4()

    # Disables the buttons, clears the table, and resets the label upon any changes to the search field
    def line_edit1_text_changed(self):
        self.table_widget1.clearContents()
        self.table_widget1.setRowCount(0)
        self.button2.setEnabled(False)
        self.button3.setEnabled(False)
        self.button4.setEnabled(False)
        self.button5.setEnabled(False)
        self.button6.setEnabled(False)
        self.label2.setText('Subscriptions')


    # Function to display the soon-ending subscriptions on the main window
    def show_recent(self):
        # Clear the previous data
        self.table_widget2.clearContents()
        self.table_widget3.clearContents()
        self.table_widget2.setRowCount(0)
        self.table_widget3.setRowCount(0)


        self.table_widget2.setSortingEnabled(False)
        self.table_widget3.setSortingEnabled(False)

        # Disable editing table items
        self.table_widget2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget3.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set resize mode for each table column
        header = self.table_widget2.horizontalHeader()
        for i in range(0, self.table_widget2.columnCount()-1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        header = self.table_widget3.horizontalHeader()
        for i in range(0, self.table_widget3.columnCount()-1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Allow to select only entire rows in the tables
        self.table_widget2.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget3.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget3.setSelectionMode(QAbstractItemView.SingleSelection)

        try:
            # Connect to the database to obtain ending dates and holder IDs
            conn, cursor = db.connect_db()
            with conn:
                # Collect all of the active subscriptions
                cursor.execute("SELECT sub_ID, holder,date_ends FROM subscriptions WHERE status = 'ACTIVE'")
                sub_list = [(x,y,z) for x,y,z in cursor.fetchall()]

                # Convert all dates to the yyyymmdd format for easy comparison
                today = date.today()

                # Fill the table with subscriptions ending within a week
                current_row = 0
                for elem in sub_list:
                    date_obj = datetime.strptime(elem[2],'%d/%m/%Y').date()
                    date_diff = date_obj - today
                    if 0 <= date_diff.days < 8:
                        self.table_widget2.setRowCount(current_row+1)
                        self.table_widget2.setItem(current_row, 0, QTableWidgetItem(str(elem[0])))
                        cursor.execute("SELECT name, level FROM clients WHERE client_ID = (?)",(elem[1],))
                        current_name_level = cursor.fetchone()
                        tw_item =QTableWidgetItem()
                        tw_item.setData(0,date_diff.days)
                        self.table_widget2.setItem(current_row, 1, QTableWidgetItem(str(current_name_level[0])))
                        self.table_widget2.setItem(current_row, 2, QTableWidgetItem(str(current_name_level[1])))
                        self.table_widget2.setItem(current_row, 3, tw_item)
                        current_row += 1

                # Collect all of the ended subscriptions
                cursor.execute("SELECT sub_ID, holder,date_ends FROM subscriptions WHERE status = 'ENDED'")
                sub_list = [(x,y,z) for x,y,z in cursor.fetchall()]

                # Fill the table with subscriptions that ended within a week
                current_row = 0
                for elem in sub_list:
                    date_obj = datetime.strptime(elem[2],'%d/%m/%Y').date()
                    date_diff = today - date_obj 
                    if 0 < date_diff.days < 8:
                        self.table_widget3.setRowCount(current_row+1)
                        self.table_widget3.setItem(current_row, 0, QTableWidgetItem(str(elem[0])))
                        cursor.execute("SELECT name, level FROM clients WHERE client_ID = (?)",(elem[1],))
                        current_name_level = cursor.fetchone()
                        tw_item =QTableWidgetItem()
                        tw_item.setData(0,date_diff.days)
                        self.table_widget3.setItem(current_row, 1, QTableWidgetItem(str(current_name_level[0])))
                        self.table_widget3.setItem(current_row, 2, QTableWidgetItem(str(current_name_level[1])))
                        self.table_widget3.setItem(current_row, 3, tw_item)
                        current_row += 1

            # Sort the tables by the names
            self.table_widget2.setSortingEnabled(True)
            self.table_widget2.sortItems(3, order = 0)
            self.table_widget3.setSortingEnabled(True)
            self.table_widget3.sortItems(3, order = 0)

        except Exception as ex:
            text = 'Error while displaying the statistics!\n'
            self.show_err_message(text + str(ex))


if __name__ == "__main__":
    # Update the subscription statuses
    db.update_sub_status()
    # Launch the main application window
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

