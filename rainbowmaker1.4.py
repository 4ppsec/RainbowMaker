from Tkinter import *

import threading
import tkFileDialog, ttk, tkFont, tkMessageBox
import os, base64, time, datetime, string
import hashlib

import ttkcalendar, tkSimpleDialog


# this class is for the calendar dialog when selecting dates for time stamp mode
class CalendarDialog(tkSimpleDialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""
    def body(self, master):
        self.calendar = ttkcalendar.Calendar(master)
        self.calendar.pack()

    def apply(self):
        self.result = self.calendar.selection

# app main class
class App:
    
    def __init__(self, master):
        # Variables #
        self.stringMode             = StringVar()
        self.FileName               = StringVar()
        self.newString              = StringVar()
        self.dateEntryTo            = StringVar()
        self.dateEntryFrom          = StringVar()
        self.endStamp               = StringVar()
        self.startStamp             = StringVar()
        self.xMode                  = IntVar()
        self.isAutoSelect           = IntVar()
        self.isTimeStamp            = 0
        self.startPressed           = 0
        self.getFileFromHost        = 0
        self.lastLocation           = 0
        self.stopThread             = 0
        self.forcedPaused           = 0
        self.isLengthOK             = 0
        self.tester                 = 0
        self.isTimeStampDisabled    = 1
        self.filesToClose           = []
        self.hashList               = []
        self.timeStampList          = []
        self.startTime              = None
        self.stopTime               = None
        self.totalRunTime           = None

        
        self.osname = os.name
        self.WinLnxAdj()
        
   # visual adjustments for linux     
    def WinLnxAdj(self):
        if self.osname == "nt":
            self.topWidth       = 51
            self.to_fromWidth   = 24
            self.topButtonX     = 320
            self.calToFromX     = 353
            self.calButtonFromY = 35
            self.calButtonToY   = 12
            self.hashWidth      = 25
            self.listWidth      = 25
            self.strWidth       = 15
            self.strX           = 90
            self.strY           = 20
            self.txtSize        = 9
            self.calButtonText  = 9
            self.delX           = 45
            self.ulX            = 118
            self.ulButton       = " Browse... "
            self.addButton      = " Add "
            self.delButton      = "Delete Row(s)"
            self.clrButton      = "Clear List"
        else:
            self.topWidth       = 36
            self.to_fromWidth   = 23
            self.topButtonX     = 300
            self.calToFromX     = 344
            self.calButtonFromY = 38
            self.calButtonToY   = 13
            self.hashWidth      = 20
            self.listWidth      = 19
            self.strWidth       = 10
            self.strX           = 100
            self.strY           = 17
            self.txtSize        = 7
            self.calButtonText  = 5
            self.delX           = 60
            self.ulX            = 100
            self.ulButton       = "Browse..."
            self.addButton      = "Add"
            self.delButton      = "Delete"
            self.clrButton      = "Clear"
            
        
        self.sessionFile            = "session.rain"
        ## TODO: give the possibility to manually add delimiters
        self.listCombinations       = [ ":", "-", "=", "#", "@", "%", "&", "^", "$", "*", "|", ";", "~", " ", "_", ".", ",", "+", "" ]
                                       #, ">", "->", "-->", "::", "__", "@@", "!", "?", "%%", "&&", "/", "\\", "==", "--", "=>", ">>", "||", "<=>", "<->" ]
        ## TODO: create more combinations (e.g. [user]:[password])
        self.listSpecialConbination = ["[]", "<>", "()", "{}", "\"\"", "''", "``"]
        self.sizeOfCombinations     = len(self.listCombinations)
        self.sizeOfSpecial          = len(self.listSpecialConbination)
        self.totalCombinations      = (self.sizeOfCombinations + self.sizeOfSpecial)

        self.localPath = os.path.join(os.getcwd())
        self.tabs =  ttk.Notebook(root)
        tab_HackTheHash = ttk.Frame(self.tabs, width=400, height=400)
        self.tabs.add(tab_HackTheHash, text='')

        self.tabs.pack()


        ########## Manue Bar #########
        self.menu = Menu(tearoff=0)
        root.config(menu = self.menu)
        self.fileMenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu = self.fileMenu)
        self.fileMenu.add_command(label='Run', command=self.executeRun)
        #self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Stop', command=self.stopPressed)
        self.fileMenu.add_separator()
        # to do - write save and load sessions !!!
        self.fileMenu.add_command(label='Save', command=self.SaveSession)
        self.fileMenu.add_command(label='Restore', command=self.LoadSession)
        self.fileMenu.add_separator()  
        self.fileMenu.add_command(label='Exit', command=self.executeQuit)

        #mode menu
        self.confMenu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Mode', menu = self.confMenu)
        self.confMenu.add_radiobutton(label='Hack the Hash'         , variable=self.xMode, value=1, command=self.hackORmake)
        self.confMenu.add_separator()
        self.confMenu.add_radiobutton(label='Create a Rainbow Table', variable=self.xMode, value=2, command=self.hackORmake)
        self.xMode.set(1)
        
        #options menu
        self.optionMenu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Options', menu = self.optionMenu)
        self.optionMenu.add_command(label='Paste from Clipboard', command=self.pasteFromClipboard)
        self.optionMenu.add_separator()
        self.optionMenu.add_command(label='Clear Data', command=self.cleanContent)
        self.optionMenu.add_separator()
        self.optionMenu.add_command(label='Upload File', command=self.browseFile)

        #log menu - currently disabled!
        self.LogMenu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Log', menu = self.LogMenu, state=DISABLED)
        self.LogMenu.add_command(label='Clear Log')
        
        #helpmenu = self.conf_menu = None
        self.helpMenu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Help', menu = self.helpMenu)
        self.helpMenu.add_command(label='About', command=self.openAboutPopup)

        self.framer_1 = Frame(tab_HackTheHash, relief=RAISED, width=375, height=70, bd=0)
        self.framer_1.place(bordermode=OUTSIDE, x=12, y=10)
        self.framer_2 = Frame(tab_HackTheHash, relief=RAISED, width=375, height=270, bd=0)
        self.framer_2.place(bordermode=OUTSIDE, x=12, y=70)

        # entry::hash string to MATCH
        self.text_match = Entry(self.framer_1, width=self.topWidth, foreground="grey")
        self.text_match.place(bordermode=OUTSIDE, x=5, y=6)
        self.text_match.insert(0, "Hash to match...")
        self.text_match.bind('<FocusIn>', self.clearText)
        self.text_match.bind('<FocusOut>', self.fillText)
        # button:: paste from clipboard
        self.button_paste = Button(self.framer_1, text="< Paste", command=self.pasteFromClipboard)
        self.button_paste.place(bordermode=OUTSIDE, x=self.topButtonX, y=1)
        # checkbox::add timestamp
        self.checkbox_timestamp = Checkbutton(self.framer_1, text='Add timestamp',
                                               variable=self.isTimeStamp, offvalue=0, onvalue=1, command=self.changeTimeStamp)
        self.checkbox_timestamp.place(bordermode=OUTSIDE, x=5, y=38)
        self.checkbox_timestamp.deselect()
        # time-from button
        self.button_time_from = Button(self.framer_1, width=1, text='#', font=("Calibri", self.calButtonText))
        self.button_time_from.place(bordermode=OUTSIDE, x=self.calToFromX, y=self.calButtonFromY)
        self.button_time_from.bind('<ButtonRelease-1>', self.SelectFromDate)
        # time-from entry
        self.entry_time_from = Entry(self.framer_1, width=self.to_fromWidth, foreground="gray66", font=("Calibri", self.txtSize),  textvariable=self.dateEntryFrom)
        self.entry_time_from.place(bordermode=OUTSIDE, x=201, y=40)
        self.entry_time_from.insert(0, "From: yyyy-mm-dd 00:00:00")
        self.entry_time_from.config(state=DISABLED)
        self.entry_time_from.bind('<FocusOut>', self.DateFromOut)
        self.entry_time_from.bind('<FocusIn>', self.DateFromIn)
        # time-to button
        self.button_time_to = Button(self.framer_2, width=1, text='#', font=("Calibri", self.calButtonText))
        self.button_time_to.place(bordermode=OUTSIDE, x=self.calToFromX, y=self.calButtonToY)
        self.button_time_to.bind('<ButtonRelease-1>', self.SelectToDate)
        # time-to entry
        self.entry_time_to = Entry(self.framer_2, width=self.to_fromWidth, foreground="gray66", font=("Calibri", self.txtSize), textvariable=self.dateEntryTo)
        self.entry_time_to.place(bordermode=OUTSIDE, x=201, y=15)
        self.entry_time_to.insert(0, "To:     yyyy-mm-dd 00:00:00")
        self.entry_time_to.config(state=DISABLED)
        self.entry_time_to.bind('<FocusOut>', self.DateToOut)
        self.entry_time_to.bind('<FocusIn>', self.DateToIn)
        
        # radiobutton::add string
        self.radiobutton_getFilefromHost = Radiobutton(self.framer_2, text='Add string',
                                                       command=self.setFileMode, variable=self.stringMode, value='1')
        self.radiobutton_getFilefromHost.place(bordermode=OUTSIDE, x=5, y=15)
        self.radiobutton_getFilefromHost.select()
        # textfield::addString
        self.text_string = Entry(self.framer_2, width=self.strWidth)
        self.text_string.place(bordermode=OUTSIDE, x=self.strX, y=self.strY)
        # Button::Add string to list
        self.button_addString = Button(self.framer_2, text=self.addButton, command=self.addString)
        self.button_addString.place(bordermode=OUTSIDE, x=4, y=55)
        # Button::Clear List
        self.button_clearList = Button(self.framer_2, text=self.clrButton, command=self.clearList)
        self.button_clearList.place(bordermode=OUTSIDE, x=130, y=55)
        # Button::Delete row
        self.button_clearList = Button(self.framer_2, text=self.delButton, command=self.deleteRows)
        self.button_clearList.place(bordermode=OUTSIDE, x=self.delX, y=55)
        # label::Upload File
        self.radiobutton_uploadFile = Radiobutton(self.framer_2, text='Upload list', command=self.setFileMode, variable=self.stringMode, value='2')
        self.radiobutton_uploadFile.place(bordermode=OUTSIDE, x=5, y=100)
        # button::Upload File
        self.upload_button = Button(self.framer_2, text=self.ulButton, command=self.browseFile, disabledforeground="gray", state=DISABLED)
        self.upload_button.place(bordermode=OUTSIDE, x=self.ulX, y=100)
        # frame::List of strings
        self.stringFrame = Frame(self.framer_2)
        self.stringFrame.place(bordermode=OUTSIDE, x=200, y=50)
        # Scroll Bar - vertical
        self.stringScrollBar_v = Scrollbar(self.stringFrame, orient="vertical")
        self.stringScrollBar_v.pack(side=RIGHT, fill=Y)
        # Scroll Bar - horizontal
        self.stringScrollBar_h = Scrollbar(self.stringFrame, orient="horizontal")
        self.stringScrollBar_h.pack(side=BOTTOM, fill=X)
        # listbox::List of strings
        self.listbox_strings = Listbox(self.stringFrame, selectmode=EXTENDED, width=self.listWidth, height=12, exportselection=0,
                                       yscrollcommand=self.stringScrollBar_v.set, xscrollcommand=self.stringScrollBar_h.set)
        self.listbox_strings.pack()
        self.listbox_strings.select_set(2)
        self.stringScrollBar_v.configure(command=self.listbox_strings.yview)
        self.stringScrollBar_h.configure(command=self.listbox_strings.xview)
        # frame::List of HASH Alg.
        self.codeFrame2 = Frame(self.framer_2)
        self.codeFrame2.place(bordermode=OUTSIDE, x=11, y=140)
        # Scroll Bar
        self.codeScrollBar2 = Scrollbar(self.codeFrame2)
        self.codeScrollBar2.pack(side=RIGHT, fill=Y)
        # listbox:list of hash algorithms
        self.listbox_HashAlgorithms = Listbox(self.codeFrame2, selectmode=SINGLE, exportselection=0, width=self.hashWidth, height=6,
                                              yscrollcommand=self.codeScrollBar2.set)
        listofCodes2 = [
                        'md5',
                        'sha1',
                        'sha224',
                        'sha256',
                        'sha384',
                        'sha512'
                        ]
        
        for item in listofCodes2:
            self.listbox_HashAlgorithms.insert(END, item)
            self.hashList.append(item)

        self.listbox_HashAlgorithms.pack()
        self.listbox_HashAlgorithms.select_clear(0, END)
        self.listbox_HashAlgorithms.bind('<<ListboxSelect>>', self.onHashSelect)
        self.codeScrollBar2.configure(command=self.listbox_strings.yview)

        # checkbox::auto select possible hash algorithms by size
        self.checkbox_autoselect = Checkbutton(self.framer_2, text='Autoselect',
                                               variable=self.isAutoSelect, offvalue=0, onvalue=1, command=self.changeAutoSelect)
        self.checkbox_autoselect.place(bordermode=OUTSIDE, x=5, y=242)
        self.checkbox_autoselect.select()

        # Status bars     
        self.text_status = Text(tab_HackTheHash, state=NORMAL, width=92, height=2, background="#DDDDDD", foreground="#990000")
        self.text_status.insert(INSERT, "Status")
        self.text_status.pack()
        self.text_status.configure(state=DISABLED)
        self.text_status.place(bordermode=OUTSIDE, x=0, y=350)
        # Progress bar
        self.progress = ttk.Progressbar(tab_HackTheHash, orient="horizontal", length=400, mode="determinate")
        #self.progress.pack()
        self.progress.place(bordermode=OUTSIDE, x=0, y=383)

        self.tabs.select(self.tabs.tabs()[0])



## ================ ##
#   UI-FUNCTUIONS   #
## =============== ##

    ## mode (xMode) selection
    ## 1 - to crack the has
    ## 2 - to create a rainbow table file    
    def hackORmake(self):
        if (self.xMode.get() == 1):
            self.text_match.destroy()
            self.text_match = Entry(self.framer_1, width=self.topWidth, foreground="grey")
            self.text_match.place(bordermode=OUTSIDE, x=5, y=6)
            self.text_match.insert(0, "Hash to match...")
            self.text_match.bind('<FocusIn>', self.clearText)
            self.button_paste.destroy()
            self.button_paste = Button(self.framer_1, text="< Paste", command=self.pasteFromClipboard)
            self.button_paste.place(bordermode=OUTSIDE, x=self.topButtonX, y=1)
            self.checkbox_autoselect.configure(state=NORMAL)
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.listbox_HashAlgorithms.configure(selectmode=SINGLE)
            self.checkbox_autoselect.select()
            self.editStatus('Selected Mode: Crack the Hash', 1)
            self.fileMenu.entryconfig(3, state=NORMAL)
            self.fileMenu.entryconfig(4, state=NORMAL)
            self.checkbox_timestamp.config(state=NORMAL)
            self.progress['value'] = 0
            
        else:
            self.text_match.destroy()
            self.text_match = Entry(self.framer_1, width=self.topWidth)
            self.text_match.place(bordermode=OUTSIDE, x=5, y=6)
            self.text_match.insert(END, os.getcwd())
            self.button_paste.destroy()
            self.button_paste = Button(self.framer_1, text="Browse", command=self.pasteFromClipboard)
            self.button_paste.place(bordermode=OUTSIDE, x=self.topButtonX, y=1)
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.listbox_HashAlgorithms.configure(selectmode=EXTENDED)
            self.checkbox_autoselect.deselect()
            self.checkbox_autoselect.configure(state=DISABLED)
            self.editStatus('Selected Mode: Create a Rainbow Table', 1)
            self.fileMenu.entryconfig(3, state=DISABLED)
            self.fileMenu.entryconfig(4, state=DISABLED)
            self.isTimeStamp = 0
            self.isTimeStampDisabled = 1
            self.checkbox_timestamp.deselect()
            self.checkbox_timestamp.config(state=DISABLED)
            self.entry_time_from.config(state=DISABLED)
            self.entry_time_to.config(state=DISABLED)
            self.progress['value'] = 0


    ## Select TimeStamp dates...
    def SelectToDate(self, event):
        #print self.dateEntryTo.get()
        self.openCaledarDialog("to") 
    def SelectFromDate(self, event):
        #print self.dateEntryFrom.get()
        self.openCaledarDialog("from")
  
    ## Calendar dialog from time stamp
    def openCaledarDialog(self, x):
        if self.isTimeStampDisabled == 0:
            cd = CalendarDialog(root)
            res = str(cd.result)
            #print cd.result
            if (x == "from"):
                if res == "N":
                    pass
                else:
                    self.entry_time_from.delete(0,END)
                    self.entry_time_from.config(foreground="black")
                    self.entry_time_from.insert(0, res)
            if (x == "to"):
                if res == "N":
                    pass
                else:
                    self.entry_time_to.delete(0,END)
                    self.entry_time_to.config(foreground="black")
                    self.entry_time_to.insert(0, res)
        else:
            self.editStatus("Timestamp mode is Disabled...", 1)


    ## handle time stamp entries events
    def DateFromOut(self, event):
        if "yyyy-mm-dd 00:00:00" in self.entry_time_from.get() or self.entry_time_from.get() == "":
            self.entry_time_from.delete(0, END)
            self.entry_time_from.config(foreground="grey66")
            self.entry_time_from.insert(0, "From: yyyy-mm-dd 00:00:00")    
        
    def DateFromIn(self, event): 
        if self.entry_time_from.get()[0:2] == "Fr":
            self.entry_time_from.delete(0, END)
            self.entry_time_from.config(foreground="black")
            self.entry_time_from.insert(0, "yyyy-mm-dd 00:00:00")          
        
    def DateToOut(self, event):
        if "yyyy-mm-dd 00:00" in self.entry_time_to.get() or self.entry_time_to.get() == "":
            self.entry_time_to.delete(0, END)
            self.entry_time_to.config(foreground="grey66")
            self.entry_time_to.insert(0, "To:     yyyy-mm-dd 00:00:00")    

    def DateToIn(self, event):
        if self.entry_time_to.get()[0:2] == "To":
            self.entry_time_to.delete(0, END)
            self.entry_time_to.config(foreground="black")
            self.entry_time_to.insert(0, "yyyy-mm-dd 00:00:00")    

    ## clears entry's text
    def clearText(self, event):
        if self.text_match.get() == "Hash to match...":
            self.text_match.delete(0, END)
            self.text_match.configure(foreground="black")
        
    ## fill default entry's text
    def fillText(self, event):
        if self.text_match.get() == "":
            self.text_match.configure(foreground="grey")
            self.text_match.insert(0, "Hash to match...")


    ## if xMode = 1 : paste (hash) value from clipboard
    ## if xMode = 2 : Open the select directory dialog
    ## also called : Select Location (xMode = 2)        
    def pasteFromClipboard(self):
        # crack hash mode
        text = ""
        if (self.xMode.get() == 1):
            try:
                text = root.clipboard_get()
            except:
                self.editStatus("Could not access clipboard or nothing to paste...", 1)

            if (len(text) < 2):
                self.editStatus("Nothing to paste...", 1)
            elif (len(text) < 130):
                self.text_match.configure(foreground="black")
                self.text_match.delete(0, END)
                try:
                    self.text_match.insert(0, text)
                    self.doAutoSelectHashAlgorithm()
                except:
                    pass
            else:
                self.editStatus("string too long...", 1)

        # create rainbow table mode...                
        else:
            self.selectFolder = tkFileDialog.askdirectory()
            if (len(self.selectFolder) != 0):
                self.text_match.delete(0, END)
                self.text_match.insert(0, self.selectFolder)
            #self.editStatus(os.path.isdir(self.selectFolder), 1)
            try:
                isFolderExist = os.path.isdir(self.selectFolder)

            except:
                self.editStatus('No folder was selected...', 1)

            if (isFolderExist == 0 and len(self.selectFolder) > 1):
                doCreateFolder = tkMessageBox.askquestion("Folder doesn't exist",
                                                          os.path.abspath(self.selectFolder) + "  does not exist.\n\nDo you want to create it?",
                                                          icon='question', parent=root)
                 
                if (doCreateFolder == 'yes'):
                        os.makedirs(self.selectFolder)
                        self.editStatus('folder: ' + os.path.abspath(self.selectFolder) +' was created', 1)
                else:
                    self.text_match.delete(0, END)
            #self.editStatus(self.selectFolder[:49]+"\n"+self.selectFolder[50:], 1)



    ## use timestamp in signatures
    def changeTimeStamp(self):
        # was off = 0, on = 1
        if (self.isTimeStamp == 1):
            self.entry_time_from.config(state=DISABLED)
            self.entry_time_to.config(state=DISABLED)
            self.isTimeStampDisabled = 1
            self.editStatus("Timestamp mode - Off.", 1)
            self.isTimeStamp = 0
        else:
            self.editStatus("Timestamp mode - On! Runtime will be longer...", 1)
            self.entry_time_from.config(state=NORMAL)
            self.entry_time_to.config(state=NORMAL)
            self.isTimeStampDisabled = 0
            self.isTimeStamp = 1


    ## autoselect checkbox button
    ## if selected -> automatically selects hash algorithm according to string's length
    def changeAutoSelect(self):
        if (self.isAutoSelect.get() == 1):
            self.checkbox_autoselect.select()
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.doAutoSelectHashAlgorithm()
        else:
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.isLengthOK = 1


    ## if manually selected hash algorithm -> removes the check from the autoselect checkbox
    def onHashSelect(self, event):
        if (len(self.getHashSelection()) > 0):
            self.checkbox_autoselect.deselect()
        
    
    ## pops up about message
    def openAboutPopup(self):
        header = "About "+ myName
        link = 'http://sl.owasp.org/rainbow'
        email = 'rainbow@appsec.it'
        msg = "Welcome to " + myName + "\n\nContact us: \n------------\n" + email + "\n" + link
        #iconImage = PhotoImage("icon.png")
        helpPopup = tkMessageBox.showinfo(header, msg, parent=root)

    ## add string to list
    def addString(self):
        self.newString = self.text_string.get()
        if len(self.newString) > 0:
            self.listbox_strings.insert(END, self.newString)
            self.text_string.delete(0, END)
        else:
            self.editStatus("Cannot add an empty string", 1)


    ## clear list of strings
    def clearList(self):
        self.listbox_strings.delete(0, END)


    ## delete selected row(s) from list
    def deleteRows(self):
        listOfSelected = self.listbox_strings.curselection()
        for j in reversed(listOfSelected):
            self.listbox_strings.delete(j, last=None)
        

    ## add list taken from uploaded file
    def addListFromFile(self):
        for item in self.listOfLines:
            itemLength = len(item)
            if (itemLength > 0 and itemLength < 130):
                self.listbox_strings.insert(END, item)


    ## clean all content before loading
    def cleanContent(self):
        self.editStatus('', 1)
        self.text_string.delete(0, END)
        self.text_match.delete(0, END)
        self.listbox_strings.delete(0, END)
        self.listbox_HashAlgorithms.selection_clear(0, END)
        self.checkbox_autoselect.select()
        

    ## 1 - to manually add strings to list
    ## 2 - to upload a list from file
    def setFileMode(self):
        if self.stringMode.get() == '1':
            self.button_addString.configure(state=NORMAL)
            self.upload_button.configure(state=DISABLED)
        else:
            self.upload_button.configure(state=NORMAL)
            self.button_addString.configure(state=DISABLED)


    ## Browse file system to get file to use for requests
    def browseFile(self):
        self.selectedFile = tkFileDialog.askopenfilename(filetypes = ( ("Text files", "*.txt"), ("All files", "*.*") ))
        try:
            listFile = open(self.selectedFile, 'r')
            self.editStatus('opened: %s' %self.selectedFile, 1)
            self.listOfLines = listFile.read().split('\n')
            listFile.close()
            self.addListFromFile()
            
        except:
            self.editStatus('Error! file does not exist', 1)

    ## saves configuration for file
    def SaveSession(self):
        f = open(self.sessionFile, "w")
        f.write("[~hash~]="+self.text_match.get()+"\n")
        list = self.listbox_strings.get(0, END)
        f.write("[~list~]="+str(list)+"\n")
        f.write("[~isTimeStamp~]="+str(self.isTimeStamp)+"\n")
        if int(self.isTimeStamp) == 1:
            f.write("[~from~]="+self.entry_time_from.get()+"\n")
            f.write("[~to~]="+self.entry_time_to.get()+"\n")
        f.close()
        self.editStatus('Session was saved.\nTo load the session: File->Restore', 1)
        
    def LoadSession(self):
        if os.path.isfile(self.sessionFile):
            f = open(self.sessionFile).readlines()
            for line in f:
                if line.find("[~hash~]=") == 0:
                    self.text_match.delete(0, END)
                    self.text_match.configure(foreground="black")
                    self.text_match.insert(0, line[9:].rstrip())
                if line.find('[~list~]=') == 0:
                    tmplist = line[9:].rstrip().strip(" '()").split(",")
                    for item in tmplist:
                        item = item.strip("'()")
                        if item != "":
                            self.listbox_strings.insert(END, item)
                if line.find("[~isTimeStamp~]=1") == 0:
                    self.isTimeStamp = 0
                    self.checkbox_timestamp.select()
                    self.changeTimeStamp()
                if line.find("[~from~]=") == 0:
                    if self.isTimeStamp == 1:
                        self.entry_time_from.delete(0, END)
                        self.entry_time_from.config(foreground="black")
                        self.entry_time_from.insert(0, line[9:].rstrip())
                if line.find("[~to~]=") == 0:
                    if self.isTimeStamp == 1:
                        self.entry_time_to.delete(0, END)
                        self.entry_time_to.config(foreground="black")
                        self.entry_time_to.insert(0, line[7:].rstrip())
        else:
            self.editStatus('Could not find session file.', 1)
        



## =================== ##
#  Execution Functions  #
## =================== ##

    ## run button from top menu was selected
    def runPressed(self):
        try:
            self.stopThread = 0
            self.executeRun()
        except:
            self.progress["value"] = 0
            self.lastLocation = 0
            self.editStatus("Could not start , something's wrong...", 1)
        

    ## stop button from top menu was selected
    def stopPressed(self):
        self.tester = 1
        #self.mainThread.quit()
        self.progress["value"] = 0           
        self.stopThread = 1
        self.editStatus('stopping... please wait.', 1)

    ## Pre-execution tests and validations
    def executeRun(self):
        self.menu.entryconfigure(1, state=DISABLED)
        self.menu.entryconfigure(2, state=DISABLED)
        #self.menu.entryconfigure(3, state=DISABLED)
        self.menu.entryconfigure(4, state=DISABLED)
        self.stopThread = 0
        #print self.startTime
        if ( self.xMode.get() == 1):
            if (self.isAutoSelect.get() == 1):
                self.doAutoSelectHashAlgorithm()
                if (self.isLengthOK == 0):
                    self.editStatus('Could not identify hash algorithem.\nPlease check your string...', 1)
                    return 0
            
                if (self.listbox_strings.size() == 0):
                    self.editStatus("Can't start - empty list!", 1)
                    return 0
                
        if self.isTimeStampDisabled:
            pass
        else:
            if (self.isBadTimeStamp() == 1):
                return 0
            #else:
                #print self.isTimeStamp
                #self.timeStampList = self.generateTimeStampList()
        
        if (self.findIfMissing() == 1):
            return 0
            
        isMissing = 0
        self.getTotal = self.calculateTotal()
        self.progress["value"] = 1
        
        self.mainThread = threading.Thread(target=self.startRainbow, args=())
        try:
            self.mainThread.start()
        except Exception as e:
            self.editStatus(str(e), 1)


    ## called from 'findIfMissing' if xMode = 2
    ## tries to create the CSV file
    ## return 1 - if succeeded
    def createRainbowTable(self):
        location = self.text_match.get()
        if (len(location) > 0):
            locationAbsPath = os.path.abspath(location)
            if (os.path.isdir(locationAbsPath)):
                self.rainbowFile = locationAbsPath + '\\RainbowTable.txt'
                self.editStatus('output file: ' + self.rainbowFile, 1)
                return 1
            
            else:
                doCreateFolder = tkMessageBox.askquestion("Folder doesn't exist",
                                                          locationAbsPath + "  does not exist.\n\nDo you want to create it?",
                                                          icon='question', parent=root)
                if (doCreateFolder == 'yes'):
                    os.makedirs(locationAbsPath)
                    if (os.path.isdir(locationAbsPath)):
                        self.editStatus('folder: ' + locationAbsPath +' was created', 1)
                        self.rainbowFile = locationAbsPath + '\\RainbowTable.txt'
                        self.editStatus('output file: ' + self.rainbowFile, 1)
                        return 1
                    else:
                        self.editStatus('Error! could not create folder', 1)
                        self.text_match.delete(0, END)
                        return 0
                else:
                    self.text_match.delete(0, END)
                    return 0
        else:
            self.editStatus('Output folder was not selected.', 1);
            return 0
            

    ## rainbow maker!
    ## if xMode = 1: tries to mactch the hash entered
    ## if xMode = 2: writes all hash values to file       
    def startRainbow(self):
        self.startTime = time.time()
        #self.stopThread = 0
        #self.fileMenu.entryconfig(0, state=DISABLED)
        if ( self.isAutoSelect.get() == 1):
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.doAutoSelectHashAlgorithm()
   
        self.listOfStrings = list(self.listbox_strings.get(0, END))
        self.listOfStrings = self.listOfStrings
        listOfChosenHash = self.getHashSelection()
        self.listLength = len(self.listOfStrings)
        if self.isTimeStamp == 1:
            print int(self.startStamp)
            print int(self.endStamp)
            self.listLength = self.listLength + int(self.endStamp) - int(self.startStamp)
        self.progress["value"] = 0
        self.total = round(100 / self.listLength)
        if (self.xMode.get() == 1 and self.stopThread == 0):
            myHash = listOfChosenHash[0]
            self.CrackIt(myHash)
        else:
            try:
                file = open(self.rainbowFile, 'w')
                file.close
            except:
                self.editStatus('Something went wrong, could not open file...', 1)
                self.stopThread = 1
                return 0
            
            for myHash in listOfChosenHash:
                self.CrackIt(myHash) 

    ## called by 'startRainbow'
    ## starts running according to xMode
    def CrackIt(self, myHash):
        grandTotal = 100
        if self.listLength * self.listLength > 100:
            grandTotal = self.listLength*len(self.listOfStrings)/100
        else:
            grandTotal = 100 / self.listLength
        toMatch = self.text_match.get()
        z = 0
        countStr = 0
        if (self.xMode.get() == 2):
            try:
                file = open(self.rainbowFile, 'a')
                file.close()
            except:
                self.editStatus('Error opening file', 1)
                
        if (self.stopThread == 0):
            for currentStr in self.listOfStrings:
                countStr = countStr + 1
                countOtherStr = 0
                if (self.stopThread == 0):
                    # run on list of string
                    listToTest = self.listOfStrings
                    if (self.stopThread == 0):
                        if self.isTimeStamp == 1:
                            listToTest = range(int(self.startStamp), int(self.endStamp))
                        for otherStr in listToTest:
                            if (self.stopThread == 0):
                                self.editStatus("Running... Please hold!", 1)
                                z = z + 1
                                self.value = z / grandTotal
                                self.progressThread = threading.Thread(target=self.updateProgressBar, args=())
                                try:
                                    self.progressThread.start()
                                except Exception as e:
                                    self.editStatus(str(e), 1)
                                otherStr = str(otherStr)
                                countOtherStr = countOtherStr + 1
                                countSeparator = 0
                                if (self.stopThread == 0):
                                    for mySeparator in self.listCombinations:
                                        countSeparator = countSeparator + 1
                                        countSpecialSeparator = 0
                                        if (self.stopThread == 0):
                                            for mySpecialSeparator in self.listSpecialConbination:
                                                countSpecialSeparator = countSpecialSeparator + 1
                                                tmpList = self.getListOfStringtoHash(currentStr, otherStr, mySeparator, mySpecialSeparator,
                                                                                     countStr, countOtherStr, countSeparator, countSpecialSeparator)
                                                for myString in tmpList:
                                                    if (self.stopThread == 1):
                                                        self.stopping()
                                                    
                                                    elif (type(myString) != type('~Sp3c1al#!HASH!#5tr1n9~')):
                                                        pass
                                                    
                                                    else:
                                                        if (myHash == "md5"):
                                                            hashValue = hashlib.md5(myString).hexdigest()
                                                        elif (myHash == "sha1"):
                                                            hashValue = hashlib.sha1(myString).hexdigest()
                                                        elif (myHash == "sha224"):
                                                            hashValue = hashlib.sha224(myString).hexdigest()
                                                        elif (myHash == "sha256"):
                                                            hashValue = hashlib.sha256(myString).hexdigest()
                                                        elif (myHash == "sha384"):
                                                            hashValue = hashlib.sha384(myString).hexdigest()
                                                        elif (myHash == "sha512"):
                                                            hashValue = hashlib.sha512(myString).hexdigest()
                                                        else:
                                                            self.editStatus("Error! no such algorithm??? [" + myHash + "]", 1)
                                                            return 0
                                                        
                                                        if (self.xMode.get() == 1):
                                                            if (hashValue == toMatch):
                                                                self.finito(myString, myHash, 1)
                                                                return 1
                                                        else:
                                                            try:
                                                                file = open(self.rainbowFile, 'a')
                                                                file.write(myString + '\t' + hashValue + '\t' + myHash + '\n')
                                                            except:
                                                                self.editStatus('Error! file does not exist...', 1)
                                        else:
                                            self.stopping()            
                                else:
                                    self.stopping()  
                            else:
                                self.stopping()
                    else:
                        self.stopping()
                else: #stopThread == 1
                    self.stopping()

            try:
                file.close()
            except:
                pass
            if (self.xMode.get() == 1):
                if (self.stopThread == 0):
                    self.finito('', '', 0)
                else:
                    self.finito('Stopped.', '', 4)
            else:
                if (self.stopThread == 0):
                    self.finito('Done. Output file: ' + self.rainbowFile, '', 3)
                else:
                    self.finito('Stopped.', '', 4)
        else:
            self.stopping()


    ## updates progress bar  
    def updateProgressBar(self):
        self.progress["value"] = self.value


    ## stopping threads...
    def stopping(self):
        try:
            while (self.mainThread.isAlive() or self.progressThread.isAlive()):
                self.stopThread = 1
                self.mainThread.exit()
                self.mainThread.stop()
                self.progressThread.exit()
                self.progressThread.stop()
                self.editStatus('Please hold while stopping...', 1)
            self.menu.entryconfigure(1, state=NORMAL)
            self.menu.entryconfigure(2, state=NORMAL)
            time.sleep(1)
        except:
            pass
            #self.editStatus('Please wait...', 1)
            #self.finito('Stopped.', '', 4)
            #self.editStatus('', 1)
            #self.stopThread = 0
            #self.fileMenu.entryconfig(0, state=NORMAL)
            
        if (self.xMode.get() == 2):
            try:
                file.close()
            except:
                pass


    ## creates a list of string with the special seperators
    ## str1 - running string from list
    ## str2 - current string in the listOfSrings
    ## separator - current regular separator (:, ;, -, etc.)
    ## special - current special separator ([], {}, (), etc.)
    def getListOfStringtoHash(self, myStr1, myStr2, separator, special, indexStr1, indexStr2, indexSeparator, indexSpecial):
        tmpList = []
        if (indexSpecial == 1):
            tmpList.append(myStr1 + separator + myStr2)

            if (indexSeparator == 1):
                tmpList.append(myStr1 + myStr2)
                
                if (indexStr2 == 1):
                    tmpList.append(myStr1)
                    if (len(special) > 1):
                        first = special[0]
                        last = special[1]
                        tmpList.append(first + myStr1 + last)
            
                #if (indexStr1 == 1): 
            
        if (len(special) > 1):
            first = special[0]
            last = special[1]
            
            tmpList.append(first + myStr1 + myStr2 + last)              
            tmpList.append(first + myStr1 + separator + myStr2 + last)
            tmpList.append(first + myStr1 + last + first + myStr2 + last)
            tmpList.append(first + myStr1 + last + separator + first + myStr2 + last)
        else:
            pass

        return tmpList
        
           
    ## select hash algorithm according to the string entered in the match field
    def doAutoSelectHashAlgorithm(self):
        autoLength = len(self.text_match.get())
        
        if (autoLength == 32):
            self.isLengthOK = 1
            self.listbox_HashAlgorithms.selection_set(0, last=None)
            self.editStatus("Hash algorithm selected: " + self.getHashSelection()[0], 1)
            
        elif (autoLength == 40):
            self.isLengthOK = 1
            self.listbox_HashAlgorithms.selection_set(1, last=None)
            self.editStatus("Hash algorithm selected: " + self.getHashSelection()[0], 1)
            
        elif (autoLength == 56):
            self.isLengthOK = 1
            self.listbox_HashAlgorithms.selection_set(2, last=None)
            self.editStatus("Hash algorithm selected: " + self.getHashSelection()[0], 1)
          
        elif (autoLength == 64):
            self.isLengthOK = 1
            self.listbox_HashAlgorithms.selection_set(3, last=None)
            self.editStatus("Hash algorithm selected: " + self.getHashSelection()[0], 1)
           
        elif (autoLength == 96):
            self.isLengthOK = 1
            self.listbox_HashAlgorithms.selection_set(4, last=None)
            self.editStatus("Hash algorithm selected: " + self.getHashSelection()[0], 1)
            
        elif (autoLength == 128):
            self.isLengthOK = 1
            self.listbox_HashAlgorithms.selection_set(5, last=None)
            self.editStatus("Hash algorithm selected: " + self.getHashSelection()[0], 1)
            
        else:
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.editStatus("Unknown hash length, please check your string" +"\n" + "or manually select hash algorithm(s)", 1)
            self.isLengthOK = 0
            self.checkbox_autoselect.deselect()
            
    ## check if timestamp is wrong...
    def isBadTimeStamp(self):
        # todo -> convert UTC to local
        if self.isTimeStampDisabled == 0:
            x = self.entry_time_from.get()
            y = self.entry_time_to.get()
            err = 0
            try:
                self.startStamp = time.mktime(datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timetuple())
            except:
                self.editStatus("From time - wrong format! [yyyy-mm-dd 00:00:00]", 1)
                return 1
            try:
                self.endStamp = time.mktime(datetime.datetime.strptime(y, "%Y-%m-%d %H:%M:%S").timetuple())
            except: 
                self.editStatus("To time - wrong format! [yyyy-mm-dd 00:00:00]", 1)
                return 1
            
            timeDiff = self.endStamp - self.startStamp
            if (timeDiff > 0 and timeDiff < 86401):
                return 0
            elif (timeDiff > 86400):
                warningMsg = "You are about to run with a Timestamp of more than 24 hours.\nRuntime can be very long...\n\nIf you want to proceed - click Yes.   Click No to modify the dates."
                if (tkMessageBox.askyesno("Warning - Long runtime!", warningMsg, parent=root)):
                    return 0
                else:
                    return 1
            else:
                self.editStatus("TO date must be later then FROM date...", 1)
                return 1
            
        # no timestamp is used    
        else:
            return 0


    ## Check if mendatory fields are missing, if so - colors in Red
    def findIfMissing(self):
        isMissing = 0
        if (self.xMode.get() == 1):
            # is match text missing?
            text = self.text_match.get()
            if (len(text) < 1):
                isMissing = 1
                self.editStatus("Missing string to match.\nPlease fill in and press Run again.", 1)
                #self.addStar(self.label_match)
            else:
                #self.removeStar(self.label_match)
                pass

            hash = self.listbox_HashAlgorithms.curselection()
            if ( (len(hash) < 1) and ( self.isAutoSelect.get() == 0) ):
                isMissing = 1
                self.editStatus("You must select at least one hash algorithm...", 1)          
        else:
            tmplist = self.listbox_HashAlgorithms.curselection()
            if (self.createRainbowTable() == 0):
                self.editStatus('You must select an output directory...', 1)
                isMissing = 1
                
            elif (self.listbox_strings.size() == 0):
                self.editStatus('You must add at least 1 string...', 1)
                isMissing = 1
                
            elif (len(tmplist) == 0):
                self.editStatus('You select at least 1 hash algorithm...', 1)
                isMissing = 1
                
            else:
                pass
            
        return isMissing    


    ## only one string was selected - create rainbow table with selected hash algorithms
    ## Currently - not in use
    def makeSingleRainbow(self):
        self.editStatus('Not yet implemented... maybe next version :)\nPlease add at least one more string', 1)
        pass


    ## calculate total combinations to run
    def calculateTotal(self):
        amountOfStrings = self.listbox_strings.size()
        return (self.totalCombinations ** amountOfStrings)


    ## grand finale!
    ## called was status = 1 - if hash was cracked with the values
    ## called with status = 0 - if nothing was found
    ## 3 = finished creating rainbow table file
    ## 4 = stopped.
    ## else = currently unknown
    def finito(self, msg, myHash, status):
        self.startPressed = 0
        self.lineCounter = 0
        self.progress["value"] = 100
        self.stopTime = time.time()
        self.totalRunTime = self.stopTime - self.startTime + 0.25
        timr = str(self.totalRunTime)
        dez = timr.find('.')
        self.menu.entryconfigure(1, state=NORMAL)
        self.menu.entryconfigure(2, state=NORMAL)
        #self.menu.entryconfigure(3, state=NORMAL)
        self.menu.entryconfigure(4, state=NORMAL)
        
        if (dez != -1):
            totalTime = timr[:dez]+ '.' + timr[dez+1]
        else:
            totalTime = timr
            
        if (status == 0):
            self.editStatus("(" + totalTime + "s) Sorry, no luck!", 1)
            return 0
        elif (status == 1):
            self.editStatus("(" + totalTime + "s) Cracked! Combination found: [" + myHash + "]\n" + msg, 1)
            return 1
        elif (status == 3):
            self.editStatus(msg, 1)
        elif (status == 4):
            time.sleep(1)
            self.editStatus('', 1)
            self.progress['value'] = 0
            self.stopThread = 0
        else: #unkown status
            self.editStatus('Error! unknown ending...', 1)
            return 1
        
    ## returns list of  selected hash algorithms
    def getHashSelection(self):
        #i = 0
        selectedHashList = []
        #tmpList = self.listbox_HashAlgorithms.get(0, END)
        listLength = len(self.hashList)
        for i in range(listLength):
            if (self.listbox_HashAlgorithms.selection_includes(i) == True):
                #self.checkbox_autoselect.deselect()
                code = self.hashList[i]
                selectedHashList.append(code)
            else:
                pass
        
        return selectedHashList        



    ## currently - only 1 is in use...
    ## if '1' is passed - echos String to Status
    ## if '2' is passed - echos String to Log Tab
    ## if '3' is passed - 1 + 2
    ## if '4' is passed - echos String to Results Tab
    ## if '5' is passed - echos String to Results file
    ## if '6' is passed - echos String to debug file
    ## if 'else' is passed - echos String to I/O
    def editStatus(self, newStatus, toLog):
        if (newStatus.find('\n') == -1):
            newString = newStatus[:49] +'\n'+ newStatus[49:]
        else:
            newString = newStatus
            
        if toLog == 1:
            #newString = newStatus[:49] +'\n'+ newStatus[49:]
            self.text_status.configure(state=NORMAL)
            self.text_status.delete(1.0, END)
            self.text_status.insert(END, newString)
            self.text_status.configure(state=DISABLED)
            
        elif toLog == 2:
            #self.log_text.configure(state=NORMAL)
            #self.log_text.insert(END, newStatus +'\n')
            #self.log_text.configure(state=DISABLED)
            pass

        elif toLog == 3:
            self.text_status.configure(state=NORMAL)
            self.text_status.delete(1.0, END)
            self.text_status.insert(END, newStatus)
            self.text_status.configure(state=DISABLED)
            #self.log_text.configure(state=NORMAL)
            #self.log_text.insert(END, newStatus +'\n')
            #self.log_text.configure(state=DISABLED)  

        elif toLog == 4:
            #self.results_text.configure(state=NORMAL)
            #self.results_text.insert(END, newStatus +'\n')
            #self.results_text.configure(state=DISABLED)
            pass

        elif toLog == 5:
            #self.reqFile.write(newStatus +'\n')
            pass

        elif toLog == 6:
            try:
                file = open('debug.txt', 'a')
            except:
                file = open('debug.txt', 'w')
            file.write(newStatus + '\n')
            file.close()
            self.text_status.configure(state=NORMAL)
            self.text_status.delete(1.0, END)
            self.text_status.insert(END, newStatus)
            self.text_status.configure(state=DISABLED)
            #self.log_text.configure(state=NORMAL)
            #self.log_text.insert(END, newStatus +'\n')
            #self.log_text.configure(state=DISABLED) 

        else:
            pass
            #pr int str(newStatus) +'\n'
            

    ## receives an object to color in RED
    def addStar(self, obj):
        pass
        obj.configure(foreground='red')

    ## receives an object to color in BLACK
    def removeStar(self, obj):
        pass
        obj.configure(foreground='black')


    ## 'Exist' button clicked - closes window
    def executeQuit(event=None):
        root.destroy()




root = Tk()
myName = "RainbowMaker v1.4"
root.title(myName)

# use .ico file as icon on Windows
if os.name == "nt":
    ico_encoded ="AAABAAEAEBAAAAEACABoBQAAFgAAACgAAAAQAAAAIAAAAAEACAAAAAAAAAEAAAAAAAAAAAAAAAEAAAAAAAAAAAAAlorjAAEAAAAQgewAMMmdAAkJCQATgewAsA6SABIKDgC3JToAHg6wAAsLCwCzEy8AJNB/ALCwsADACyUAB7vsAIoA1ACwORYAKir3ABINDQCbj+sAYGriABTDxwDBGAkAJtKHAAAA/wBLv20AQUG6ADjRigCwEyYACAgIABEREQCivfEAca1DACMjIwABAQEAE9zBAJqa4AANmPUAsjEdALQIJwBLceoABQMCAHqaQAC8LVQACgkKAAQAAQAQodoADg8SAImMLgCr7NgAOm7uAAWL8gACAgMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAkAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAJAsAAAAAAAAAAAAAAAAAAAAOAA4AAAAAAAAAAAAAAAAADg4OAAAAAAAAAAAAACs2LwIjAAAAAAAAAAAAAAsUCDEFLgUFBQUfAAAAAAAAKh0JAAAAAAAAAAAAAAAAABoNDwAAAAAAAAAAAAAAAAATGSkAAAAABzMhAAAAAAAAESUYAAAAAB4EFgAAAAAAAAo1IgwAAC0yAwAAAAAAAAAAFScbEigsEAEAAAAAAAAAAAAcNDAXBiYAAAAAAAAAAAAAAAAcHAAAAAAAAOADAADgAwAA4IMAAOCDAADggwAA4AMAAOADAADgAwAA8f8AAPH/AADx4wAA8eMAAPDHAAD4BwAA/A8AAP8/AAA="
    ico_decoded = base64.b64decode(ico_encoded)
    temp_file = "pt.ico"
    fout = open(temp_file, "wb")
    fout.write(ico_decoded)
    fout.close()
    root.wm_iconbitmap(temp_file)
    os.remove(temp_file)

app = App(root)

root.mainloop()
