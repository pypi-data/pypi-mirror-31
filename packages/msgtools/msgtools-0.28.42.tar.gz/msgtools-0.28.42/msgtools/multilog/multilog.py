#!/usr/bin/env python3

# TODO
#   add hotkey support (already reading options for it on cmdline)
#  Add annotation field.
#         text gets inserted in log whenever you hit enter in annotation box or click 'note' button next to annotate box.

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from time import strftime

try:
    from msgtools.lib.messaging import Messaging
except ImportError:
    import os
    srcroot=os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/../..")
    sys.path.append(srcroot)
    from msgtools.lib.messaging import Messaging
import msgtools.lib.gui
import msgtools.lib.txtreewidget

plottingLoaded=0
try:
    from msgtools.lib.msgplot import MsgPlot
    plottingLoaded=1
except ImportError as e:
    print("Error loading plot interface ["+str(e)+"]")
    print("Perhaps you forgot to install pyqtgraph.")
except RuntimeError as e:
    print("Error loading plot interface ["+str(e)+"]")
    print("Perhaps you need to install the PyQt5 version of pyqtgraph.")

def removePrefix(text, prefix):
    return text[len(prefix):] if text.startswith(prefix) else text
    
class Multilog(msgtools.lib.gui.Gui):
    def __init__(self, argv, parent=None):
        if(len(argv) < 2):
            exit('''
Invoke like this
    ./path/to/Multilog.py --field=LABEL1 --field=LABEL2 --button=hotkey:X,tag:TAG1,label:LABEL3  --button=hotkey:X,tag:TAG2,label:LABEL4 --show=MSGNAME --plot=MSGNAME[fieldname1,fieldname2] --send=MSGNAME
    
each --field adds a text field named the specified LABEL, and the value of the text field will become part of the filename.
each --button adds a pushbutton named for the specified LABEL, with a hotkey of the specified key, and the tag value will become part of the filename
each --show adds a table view of that MSGNAME
each --plot adds a plot of the fields within MSGNAME.  If fields left off, all fields are plotted
each --send adds a tree view to edit a message with a 'send' button to send it

pressing a button starts/stops a log file
underscores in label or field are replaced with spaces for display (to make entering command-line args easier)

filenames will be composed like so:
    YEAR_MONTH_DAY.TEXT1.TEXT2.TAG1.log
''')

        options = ['field=', 'button=', 'show=', 'plot=', 'send=']
        msgtools.lib.gui.Gui.__init__(self, "Multilog 0.1", argv, options, parent)
        
        # event-based way of getting messages
        self.RxMsg.connect(self.ProcessMessage)
        
        # handling of messages by sub-widgets
        self.msgHandlers = {}

        # tab widget to show multiple messages, one per tab
        widget = QtWidgets.QWidget(self)
        vLayout = QtWidgets.QVBoxLayout(widget)
        self.setCentralWidget(widget)
        self.statusMsg = QtWidgets.QLabel("NOT logging")
        vLayout.addWidget(self.statusMsg)

        hLayout = QtWidgets.QHBoxLayout()
        vLayout.addLayout(hLayout)
        lvLayout = QtWidgets.QVBoxLayout()
        rvLayout = QtWidgets.QVBoxLayout()
        hLayout.addLayout(lvLayout)
        hLayout.addLayout(rvLayout)

        splitter = QtWidgets.QSplitter(parent)
        splitter.setOrientation(QtCore.Qt.Vertical)
        vLayout.addWidget(splitter)
        
        self.lineEdits = []
        self.buttons = []
        self.activeLogButton = None
        txMsgs = None
        for option in self.optlist:
            if option[0] == '--field':
                label = option[1].replace("_"," ")

                # add text field
                lvLayout.addWidget(QtWidgets.QLabel(label))
                lineEdit = QtWidgets.QLineEdit()
                rvLayout.addWidget(lineEdit)
                self.lineEdits.append(lineEdit)
            elif option[0] == '--button':
                arg = option[1]
                parts = arg.split(",")
                options = {}
                for option in parts:
                    key, value = option.split(":")
                    options[key] = value

                # add button
                label = options["label"].replace("_"," ")
                button = QtWidgets.QPushButton(label)
                # how to set hot key?  do it at window level, or at button level?  or something else?
                #button.hotKey = options["hotkey"]
                button.label = label
                self.buttons.append(button)
                if "tag" in options:
                    button.tag = options["tag"]
                else:
                    button.tag = None
                vLayout.addWidget(button)
                
                button.clicked.connect(self.HandleButtonPress)
            elif option[0] == '--show':
                msgname = option[1]
                subWidget = QtWidgets.QWidget()
                subLayout = QtWidgets.QVBoxLayout()
                subWidget.setLayout(subLayout)
                splitter.addWidget(subWidget)
                subLayout.addWidget(QtWidgets.QLabel(msgname))
                msgClass = self.msgLib.MsgClassFromName[msgname]
                msgWidget = msgtools.lib.gui.MsgTreeWidget(msgClass, None, 1, 1)
                subLayout.addWidget(msgWidget)
                if not msgClass.ID in self.msgHandlers:
                    self.msgHandlers[msgClass.ID] = []
                self.msgHandlers[msgClass.ID].append(msgWidget)
            elif option[0] == '--plot':
                if plottingLoaded:
                    msgname = option[1].split("[")[0]
                    try:
                        fieldNames = option[1].split("[")[1].replace("]","").split(',')
                    except IndexError:
                        fieldNames = []
                    subWidget = QtWidgets.QWidget()
                    subLayout = QtWidgets.QVBoxLayout()
                    subWidget.setLayout(subLayout)
                    splitter.addWidget(subWidget)
                    subLayout.addWidget(QtWidgets.QLabel(msgname))
                    msgClass = self.msgLib.MsgClassFromName[msgname]
                    # should plot only fields specified, if user specified fields
                    firstTime = True
                    for fieldInfo in msgClass.fields:
                        if fieldInfo.name in fieldNames or not fieldNames:
                            if firstTime:
                                msgWidget = MsgPlot(msgClass, fieldInfo, 0) # non-zero for subsequent elements of arrays!
                                firstTime = False
                            else:
                                msgWidget.addPlot(msgClass, fieldInfo, 0) # non-zero for subsequent elements of arrays!
                    subLayout.addWidget(msgWidget)
                    if not msgClass.ID in self.msgHandlers:
                        self.msgHandlers[msgClass.ID] = []
                    self.msgHandlers[msgClass.ID].append(msgWidget)
            elif option[0] == '--send':
                msgname = option[1]
                msgClass = self.msgLib.MsgClassFromName[msgname]
                if not txMsgs:
                    txMsgs = QtWidgets.QTreeWidget(parent)
                    txMsgs.setColumnCount(4)
                    txMsgsHeader = QtWidgets.QTreeWidgetItem(None, ["Message", "Field", "Value", "Units", "Description"])
                    txMsgs.setHeaderItem(txMsgsHeader)
                    splitter.addWidget(txMsgs)
                
                msg = msgClass()
                # set fields to defaults
                msgWidget = msgtools.lib.txtreewidget.EditableMessageItem(txMsgs, msg)
                msgWidget.qobjectProxy.send_message.connect(self.on_tx_message_send)


        # create a new file
        self.file = None

    def on_tx_message_send(self, msg):
        if not self.connected:
            self.OpenConnection()
        self.SendMsg(msg)

    def ProcessMessage(self, msg):
        if msg.ID in self.msgHandlers:
            handlersList = self.msgHandlers[msg.ID]
            for handler in handlersList:
                handler.addData(msg)
        # if user specified allowed messages...
        if self.allowedMessages:
            # only log this message if it's in that list
            if not msg.MsgName() in self.allowedMessages:
                return
        
        if self.file is not None:
            #write to a single binary log file
            self.file.write(hdr.rawBuffer())

            # if you want to write to multiple CSV files, look at lumberjack for an example of how to do so.
            # for each message, you'll need to
            # 1) open a file (store handles to files in a hash based on msg id)
            # 2) look up the MsgNameFromID
            # 3) look up the MsgClassFromName
            # 4) then iterate through the msgClass.fields and msgClass.bitFields
            #  a. to get() the field value as a string for each field, and write them to the file
            # you might also consider using the --msg option to set allowedMessages
            # then you'd get a csv file for each of the messages you care about (and not for the ones you don't)

    def CreateLogFile(self, tag):
        self.CloseLogFile()

        filename = strftime("%Y_%m_%d")
        for lineEdit in self.lineEdits:
            filename += "." + lineEdit.text().replace(" ","_")
        
        if tag is not None:
            filename += "." + tag
        filename += ".log"
        
        # note this opens one binary file to write all the data to.
        self.file = open(filename, 'wb')
        self.statusMsg.setText("Logging to " + filename)

    def CloseLogFile(self):
        if self.file is not None:
            self.file.close()
            self.file = None
            self.statusMsg.setText("NOT Logging")

    def HandleButtonPress(self):
        # when a button is used to start a log, the text of that button changes to "Stop".
        # starting any other log will stop the current one (changing it's text back to normal)
        button = self.sender()
        if button == self.activeLogButton:
            self.CloseLogFile()
            button.setText(button.label)
            self.activeLogButton = None
        else:
            if self.activeLogButton != None:
                self.activeLogButton.setText(self.activeLogButton.label)
            tag = button.tag
            self.CreateLogFile(tag)
            button.setText("Stop")
            self.activeLogButton = button

def main(args=None):
    app = QtWidgets.QApplication(sys.argv)
    msgApp = Multilog(sys.argv)
    msgApp.show()
    sys.exit(app.exec_())

# main starts here
if __name__ == '__main__':
    main()
