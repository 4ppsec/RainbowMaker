
from Tkinter import *
import threading

import tkFileDialog, ttk, tkFont, tkMessageBox
import os, base64, time, string
import hashlib
#import paramiko
#from datetime import datetime



class App:
    
    def __init__(self, master):
        # Variables #
        self.stringMode             = StringVar()
        self.FileName               = StringVar()
        self.newString              = StringVar()
        self.xMode                  = IntVar()
        self.isAutoSelect           = IntVar()
        self.startPressed           = 0
        self.getFileFromHost        = 0
        self.lastLocation           = 0
        self.stopThread             = 0
        self.forcedPaused           = 0
        self.isLengthOK             = 0
        self.tester                 = 0
        self.filesToClose           = []
        self.hashList               = []
        
        self.listCombinations	                = [
                                                    ":", "::", "-", "=", "#", "@", "%", "&", "&", "^",
                                                    "$", "*", "|", ">", "->", "-->", ";", "~", " ", "_",
                                                    "__", "@@", "!", "?", "%%", "&&", "/", "\\", ".", ",",
                                                    "+", "==", "--", "=>", ">>", "||", "<=>", "<->"
                                                   ]
        ## TODO: give the possibility to manually add delimiters
        
        self.listSpecialConbination             = ["[]", "<>", "()", "{}", "\"\"", "''", "``"]
        ## TODO: create more combinations (e.g. [user]:[password])
        self.sizeOfCombinations                 = len(self.listCombinations)
        self.sizeOfSpecial		                = len(self.listSpecialConbination)
        self.totalCombinations	                = (self.sizeOfCombinations + self.sizeOfSpecial)
        #self.checkbox_autoselect.isAutoSelect   = StringVar()
        
        self.localPath = os.path.join(os.getcwd())

        self.tabs =  ttk.Notebook(root)
        tab_HackTheHash = ttk.Frame(self.tabs, width=400, height=400)
        self.tabs.add(tab_HackTheHash, text='')
        ##tab_MakeRainbowTable = ttk.Frame(self.tabs, width=400, height=400)       
        ##self.tabs.add(tab_MakeRainbowTable, text='Create a Rainbow Table')

        self.tabs.pack()


        ########## Manue Bar #########

        self.menu = Menu(tearoff=0)
        root.config(menu = self.menu)

        
        #self.filemenu = self.file_menu = None
        self.fileMenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu = self.fileMenu)
       
        self.fileMenu.add_command(label='Run', command=self.executeRun)
        #self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Stop', command=self.stopPressed)#, state=DISABLED)
        self.fileMenu.add_separator()        
        self.fileMenu.add_command(label='Exit', command=self.executeQuit)

        #mode menu
        self.confMenu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Mode', menu = self.confMenu)
        self.confMenu.add_radiobutton(label='Hack the Hash'         , variable=self.xMode, value=1, command=self.hackORmake)
        self.confMenu.add_separator()
        self.confMenu.add_radiobutton(label='Create a Rainbow Table', variable=self.xMode, value=2, command=self.hackORmake)
        self.xMode.set(1)
        
        #confmenu = self.conf_menu = None
        self.confMenu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Options', menu = self.confMenu)
        self.confMenu.add_command(label='Paste from Clipboard', command=self.pasteFromClipboard)
        self.confMenu.add_separator()
        self.confMenu.add_command(label='Clear Data', command=self.cleanContent)
        self.confMenu.add_separator()
        self.confMenu.add_command(label='Upload File', command=self.browseFile)
        #confmenu.add_separator()

        #logmenu = self.conf_menu = None
        self.LogMenu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Log', menu = self.LogMenu, state=DISABLED)
        
        self.LogMenu.add_command(label='Clear Log')
        
        #helpmenu = self.conf_menu = None
        self.helpMenu = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='Help', menu = self.helpMenu)
        self.helpMenu.add_command(label='About', command=self.openAboutPopup)


        ######################
        #    Main Frame:     #
        ######################
        
        self.framer_1 = Frame(tab_HackTheHash, relief=RAISED, width=375, height=70, bd=0)
        self.framer_1.place(bordermode=OUTSIDE, x=12, y=10)
    
        self.framer_2 = Frame(tab_HackTheHash, relief=RAISED, width=375, height=270, bd=0)
        self.framer_2.place(bordermode=OUTSIDE, x=12, y=70)
        

        ############################# FRAMER 1 ############################
        # label::match
        self.label_match = Label(self.framer_1, text="Match: ", foreground="black")
        self.label_match.place(bordermode=OUTSIDE, x=5, y=7)

        # entry::hash string to MATCH
        self.text_match = Entry(self.framer_1, width=51, insertwidth=3)
        self.text_match.place(bordermode=OUTSIDE, x=55, y=8)

        # button:: paste from clipboard
        self.button_paste = Button(self.framer_1, text=" Paste from Clipboard ", command=self.pasteFromClipboard)
        self.button_paste.place(bordermode=OUTSIDE, x=140, y=30)
        #self.button_paste.bind("<Button-1>", self.pasteFromClipboard)

        ############################# FRAMER 2 ###########################
        
        # radiobutton::add string
        self.radiobutton_getFilefromHost = Radiobutton(self.framer_2, text='Add string',
                                                       command=self.setFileMode, variable=self.stringMode, value='1')
        self.radiobutton_getFilefromHost.place(bordermode=OUTSIDE, x=5, y=15)
        self.radiobutton_getFilefromHost.select()
        
        # textfield::addString
        self.text_string = Entry(self.framer_2, width=15, insertwidth=3)
        self.text_string.place(bordermode=OUTSIDE, x=90, y=20)
        #self.text_string.bind('<FocusIn>', self.addStringFocusIn)
        #self.text_string.bind('<FocusOutn>', self.addStringFocusOut)

        # Button::Add string to list
        self.button_addString = Button(self.framer_2, text=" Add ", command=self.addString)
        self.button_addString.place(bordermode=OUTSIDE, x=4, y=55)

        # Button::Clear List
        self.button_clearList = Button(self.framer_2, text="Clear list", command=self.clearList)
        self.button_clearList.place(bordermode=OUTSIDE, x=47, y=55)


        # Button::Delete row
        self.button_clearList = Button(self.framer_2, text="Delete row(s)", command=self.deleteRows)
        self.button_clearList.place(bordermode=OUTSIDE, x=106, y=55)

        #################################################################################
        # label::Upload File
        self.radiobutton_uploadFile = Radiobutton(self.framer_2, text='Upload list', command=self.setFileMode, variable=self.stringMode, value='2')
        self.radiobutton_uploadFile.place(bordermode=OUTSIDE, x=5, y=100)

        # button::Upload File
        self.upload_button = Button(self.framer_2, text="  Browse... ", command=self.browseFile, disabledforeground="gray", state=DISABLED)
        self.upload_button.place(bordermode=OUTSIDE, x=118, y=100)
        
        # frame::List of strings
        self.stringFrame = Frame(self.framer_2)
        self.stringFrame.place(bordermode=OUTSIDE, x=200, y=18)

        # Scroll Bar - vertical
        self.stringScrollBar_v = Scrollbar(self.stringFrame, orient="vertical")
        self.stringScrollBar_v.pack(side=RIGHT, fill=Y)

        # Scroll Bar - horizontal
        self.stringScrollBar_h = Scrollbar(self.stringFrame, orient="horizontal")
        self.stringScrollBar_h.pack(side=BOTTOM, fill=X)

        # listbox::List of strings
        self.listbox_strings = Listbox(self.stringFrame, selectmode=EXTENDED, width=24, height=14, exportselection=0,
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
        self.listbox_HashAlgorithms = Listbox(self.codeFrame2, selectmode=SINGLE, exportselection=0, width=25, height=6,
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


        ######################
        #      Main TAB:     # 
        ######################

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





## ============================================================================================================================= ##
## ======================================================  FUNCTUIONS  ========================================================= ##
## ============================================================================================================================= ##


    ## mode (xMode) selection
    ## 1 - to crack the has
    ## 2 - to create a rainbow table file    
    def hackORmake(self):
        if (self.xMode.get() == 1):
            self.label_match.destroy()
            self.label_match = Label(self.framer_1, text="Match: ", foreground="black")
            self.label_match.place(bordermode=OUTSIDE, x=5, y=7)
            self.text_match.destroy()
            self.text_match = Entry(self.framer_1, width=51, insertwidth=3)
            self.text_match.place(bordermode=OUTSIDE, x=55, y=8)
            self.button_paste.destroy()
            self.button_paste = Button(self.framer_1, text=" Paste from Clipboard ", command=self.pasteFromClipboard)
            self.button_paste.place(bordermode=OUTSIDE, x=140, y=30)
            self.checkbox_autoselect.configure(state=NORMAL)
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.listbox_HashAlgorithms.configure(selectmode=SINGLE)
            self.checkbox_autoselect.select()
            self.editStatus('Selected Mode: Crack the Hash', 1)
            self.progress['value'] = 0
            
        else:
            self.label_match.destroy()
            self.label_match = Label(self.framer_1, text="Output Folder: ", foreground="black")
            self.label_match.place(bordermode=OUTSIDE, x=5, y=7)
            self.text_match.destroy()
            self.text_match = Entry(self.framer_1, width=45, insertwidth=3)
            self.text_match.place(bordermode=OUTSIDE, x=91, y=8)
            self.text_match.insert(END, os.getcwd())
            self.button_paste.destroy()
            self.button_paste = Button(self.framer_1, text="    Select Location    ", command=self.pasteFromClipboard)
            self.button_paste.place(bordermode=OUTSIDE, x=140, y=30)
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.listbox_HashAlgorithms.configure(selectmode=EXTENDED)
            self.checkbox_autoselect.deselect()
            self.checkbox_autoselect.configure(state=DISABLED)
            self.editStatus('Selected Mode: Create a Rainbow Table', 1)
            self.progress['value'] = 0



    ## if xMode = 1 : paste (hash) value from clipboard
    ## if xMode = 2 : Open the select directory dialog
    ## also called : Select Location (xMode = 2)        
    def pasteFromClipboard(self):
        # crack hash mode
        if (self.xMode.get() == 1):
            #self.fileMenu.entryconfig(0, state=DISABLED)
            text = root.clipboard_get()
            if (len(text) < 130):
                self.text_match.delete(0, END)
                try:
                    self.text_match.insert(0, text)
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
        iconImage = PhotoImage("c:\\Users\\keizer\\Desktop\\1.jpg")
        helpPopup = tkMessageBox.showinfo("About "+ myName, "Welcome to " + myName
                                          + "\nFor any information please contact: rainbow@appsec.it", parent=root)
        



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



#####################################################################################################################
#########################################         START OF RUN()       ##############################################
#####################################################################################################################

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


        

############################################################################################################################################
        ############################################################ RUN #########################################################
                ############################################################################################################

    ## first function called by the Run button
    def executeRun(self):
        self.stopThread = 0
        if ( self.xMode.get() == 1):
            if (self.isAutoSelect.get() == 1):
                self.doAutoSelectHashAlgorithm()
                if (self.isLengthOK == 0):
                    self.editStatus('Could not identify hash algorithem.\nPlease check your string...', 1)
                    return 0

                #if (self.listbox_strings.size() == 1):
                    #self.makeSingleRainbow()
            
                if (self.listbox_strings.size() == 0):
                    self.editStatus("Can't start - empty list!", 1);
                    return 0
         
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
        #self.stopThread = 0
        self.fileMenu.entryconfig(0, state=DISABLED)
        #self.fileMenu.entryconfig(1, state=NORMAL)
        if ( self.isAutoSelect.get() == 1):
            self.listbox_HashAlgorithms.selection_clear(0, END)
            self.doAutoSelectHashAlgorithm()
   
        self.listOfStrings = list(self.listbox_strings.get(0, END))
        listOfChosenHash = self.getHashSelection()
        self.listLength = len(self.listOfStrings)
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
                    self.editStatus("Running... Please hold!", 1)
                z = z + 1         
                self.value = self.total * z
                if (self.stopThread == 0):
                    self.progressThread = threading.Thread(target=self.updateProgressBar, args=())
                    try:
                        self.progressThread.start()
                    except Exception as e:
                        self.editStatus(str(e), 1)

                    # run on list of string
                    if (self.stopThread == 0):
                        for otherStr in self.listOfStrings:
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
            time.sleep(1)
            #self.editStatus('', 1)
            #self.stopThread = 0
            #self.fileMenu.entryconfig(0, state=NORMAL)
            #self.fileMenu.entryconfig(1, state=DISABLED)
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
            #self.fileMenu.entryconfig(1, state=DISABLED)


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


#####################################################################################################################

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
        if (status == 0):
            self.editStatus("Sorry, no luck!", 1)
            self.fileMenu.entryconfig(0, state=NORMAL)
            return 0
        
        elif (status == 1):
            self.editStatus("Cracked! combination found:  " + msg +" ["+ myHash + "]", 1)
            self.fileMenu.entryconfig(0, state=NORMAL)
            return 1
        
        elif (status == 3):
            self.editStatus(msg, 1)
            self.fileMenu.entryconfig(0, state=NORMAL)

        elif (status == 4):
            time.sleep(1)
            self.editStatus('', 1)
            self.progress['value'] = 0
            self.stopThread = 0
            self.fileMenu.entryconfig(0, state=NORMAL)

        else: #unkown status
            self.editStatus('Error! unknown ending...', 1)
            self.fileMenu.entryconfig(0, state=NORMAL)
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
myName = "RainbowMaker v1.2"
root.title(myName)
# use .ico file as icon
ico_encoded ="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of/+/v7//v7+//7+/v/+/v7//v7+//7+/v/+/v7//v7+//7+/v/+/v7//v7+//7+/v/+/v7//v7+//39/f/+/f7/+/7+//79/f/+/v3/W1rx/wCB9/8A55r/pIUZ/78AFf/PYKP//f7+//X9+//9/f7//v7+//7+/v/+/v7//v7+//7+/v/+/v7//v7+//7+/v/+/v7//v7+//7+/v/+/v7//v3+//z+/v/9/f3//v7+/1pd7/8Ge/v/AOOm/5yHGP++ABL/ykaH//z+/v/2/v3//f3+//7+/v/+/v7//v7+//79/f/9/vv//f7+//7+/v/8/f7//f78//7++//+/P7//v3+//7+/v/+/v7/+/79//7+/f9hWPP/A3n+/wDppv+ihxX/uAAZ/9k3f//8/v7//P7+//79/v/+/v7//v79//39/v/3+vr/9vr5//r+/v/1/vn/9vr7//v7+P/1+PP/7/r3//z8/v/+/v7//v7+//3+/v/+/v3/YVju/wCD+P8B6ar/rYAS/6UAFv/VOoD//v7+//3+/v/+/vz//v7+//v8/P/4/Pz/7P78/+zo+P/DRm//y1k6/2Hbt/8/h/H/gnXq//f+9v/7+/P//f7+//7+/v/+/P3//v7+/4CD2/8Ffu//AuPO/5ePHf+9CAL/zz14//7+/v/4/v7//f38//z9/f/6/f3/9/3+//b+/v/syuP/mwAY/6JYAf8M4cT/AE3w/3t+1v/+/vf//Pr0//3+/v/+/v7//vz9//7+/P+xsez/Azzv/wDd9v9MzGj/zzgD/60HMP/btsz//v7+//n9+f/2/P3/9vv9//z++//49fv/vEds/8sLBf+IqDH/AL7i/xwz7v/Ry/D/+vz4//z79//+/v7//v7+//z8+//9/vf/4eD0/ygc3/8Dm/v/C+uz/5aWGv/LCwT/oRpT/+jO7P/0/v7/9/78/+7+/v/g9/7/vkV6/8MACv+jfhX/C+6e/w1i8v+ZieL//v78//n59//8+vz//v7+//39/f/8/Pz/+/v4//7+8/+ql+T/CTrd/wPI9f8g45T/rXsR/8kNAP+vBUL/1abD//r0/f/bvdX/vkd2/7gADv+wXQT/ONB//wDW7v8vSNf/7Of0//7+/P/9/Pn//v3+//7+/v/9/f3//f39//z7+f/5+vj/+v7x/3to4/8EOu//EM3+/xjkn/+Ilyj/xC8A/8ECFP+5Hlf/owA1/7gFA/+5bBD/RdFv/wTk6f8AVvf/mozh//7+8P/9/fz/+fz7//z+/f/+/v7//f39//z8/P/8/Pv//vf4//v5+f/6+/j/cGXv/ws/5f8Gtv7/A+zD/0bNVv+fbxf/m04A/75dAP+Zhif/EuaP/w3R8/8GXOv/U0bh//nx7f/8+PD//vv+//78+//+/v3//v7+//7+/v/9/f3//f39//3++P/6+fn/9/7u//7+9/+ckOb/HTbg/wBx+v8Gx/D/EeDC/yfilv8n2Z7/DunW/xC39/8FQeL/Z2fZ//bx8P/9/ff/+fn6//7+/v/+/v7//v7+//7+/v/+/v7//v7+//7+/v/8/P3//f71//32/f/++/b//v7s/+Le7f+DdeP/Izjg/w5i8v8AjOr/AKzy/wV59P8eONn/lZbc//z78v/+/vL/+vz5//39/v/+/v7//v7+//7+/v/+/v7//v7+//7+/v/+/v7//Pz+//z+/f/+9/7//fn6//j76//+/vb//v70/+jh7/+qoN3/nJ3U/5ur4v+Spdj/09js//7++v/++/P//fj5//z8/P/+/v7//v7+//7+/v/+/v7//v7+//7+/v/+/v7//v7+//3++v/9/vv/+/75//n8/f/++P7/9/zv/+r77f/+/vb//v7+//7+/v/+/vn//v7+//7+9//6+vj//P35//76+//++/7//v7+//7+/v/+/v7//v7+/wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
ico_decoded = base64.b64decode(ico_encoded)
temp_file = "pt.ico"
fout = open(temp_file,"wb")
fout.write(ico_decoded)
fout.close()
root.wm_iconbitmap(temp_file)
#remove temp file
os.remove(temp_file)

app = App(root)

root.mainloop()
