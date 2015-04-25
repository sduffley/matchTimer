
import datetime
import Tkinter as tk
import ttk
import tkMessageBox as box
import tkFileDialog as fileBox
import pickle

#Globals
DELAY = 0
TEAM_NUM = '246'
TEAM_COLOR = '#FF0000'
TEAM_COLOR_TABLE = '#FF4D4D' #So can see black text, make lighter, eg 8080FF for blue, FF4D4D for red, and 6FFF6F for green
CYCLETIME = 100

def addDelay(time):
    """Adds DELAY minutes to the time"""
    #extract hours/mins
    hours = time[0]
    mins = time[1]

    #add delay
    mins += DELAY
    if mins >= 60:
        mins -= 60
        hours += 1
    elif mins < 0:
        mins += 60
        hours -= 1
    else:
        pass

    return (hours,mins)

def toTimeString(num):
    """Makes integer always take two digits"""
    if isinstance(num, str):
        return num
    if num>9:
        return str(num)
    return '0'+str(num)


class Match():
    """All useful info about each match"""

    def __init__(self, number, day, time, teamsR, teamsB, practice=False):

        self.day = day
        self.time = time
        self.matchtime = self.makeMatchTime(self.day,self.time)
        self.number = number
        self.teamsR = teamsR
        self.teamsB = teamsB
        if practice:
            self.ourColor = 'p'
            self.number = 'Practice'
            self.teamsR = [' ', ' ', ' ']
            self.teamsB = [' ', ' ', ' ']
        elif TEAM_NUM in self.teamsR:
            self.ourColor = 'r'
        elif TEAM_NUM in self.teamsB:
            self.ourColor = 'b'
        else:
            self.ourColor = 'p'

    def makeMatchTime(self, day, time):
        """Returns datetime object with match time built in"""

        #Find current day
        today = datetime.date.today()
        currWeekDay = today.weekday()

        #Find match day as equivalent number
        if day == 'Wednesday':
            dayNum = 2
        elif day == 'Thursday':
            dayNum = 3
        elif day == 'Friday':
            dayNum = 4
        elif day == 'Saturday':
            dayNum = 5
        elif day == 'Sunday':
            dayNum = 6
        else:
            raise TypeError #at least until I do better error handling

        #Find day difference
        dayDiff = dayNum-currWeekDay

        #Separate out time
        matchHours = time[0]
        matchMinutes = time[1]

        #create and return the object
        return datetime.datetime(today.year,today.month,today.day+dayDiff,matchHours,matchMinutes)

    def getMatchInfo(self):
        """Returns strings for each necessary bit"""
        if self.ourColor == 'r':
            ourNums = self.teamsR
            theirNums = self.teamsB
        else:
            ourNums = self.teamsB
            theirNums = self.teamsR

        #check for if practice and add delay or not
        if self.ourColor != 'p':
            estimatedMatchTime = addDelay(self.time)
        else:
            estimatedMatchTime = self.time

        return self.number, self.ourColor, self.day, self.time, estimatedMatchTime, ourNums, theirNums

    def getTimeTill(self):
        """Returns estimated time until this match"""

        #find difference as timedelta instance
        delta = self.matchtime - self.matchtime.now()

        #pull out seconds until
        tot_secs_till = int(delta.total_seconds())

        #convert into hours/mins/secs
        hours = tot_secs_till/3600
        minutes = (tot_secs_till-hours*3600)/60
        seconds = tot_secs_till-hours*3600-minutes*60

        #add the delay in, but only if not a practice match
        if self.ourColor != 'p':
            hours, minutes = addDelay((hours, minutes))

        return hours, minutes, seconds
        
class MatchApplication(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        #init match list
        self.matchList = []

        #Create styles
        style = ttk.Style()
        style.configure('redmainHeader.TLabel', foreground='red', font=('Helvetica',36,'bold'))
        style.configure('redtime.TLabel', foreground='red', font=('Helvetica',72,'bold'))
        style.configure('bluemainHeader.TLabel', foreground='blue', font=('Helvetica',36,'bold'))
        style.configure('bluetime.TLabel', foreground='blue', font=('Helvetica',72,'bold'))
        style.configure('defaultmainHeader.TLabel', foreground=TEAM_COLOR, font=('Helvetica',36,'bold'))
        style.configure('defaulttime.TLabel', foreground=TEAM_COLOR, font=('Helvetica',36,'bold'))
        style.configure('matchTable.TLabel', background='white', font=('Helvetica', 11))
        style.configure('redMatchTable.TLabel', background='#FF4D4D', font=('Helvetica',10,'bold'))
        style.configure('blueMatchTable.TLabel', background='#8080FF', font=('Helvetica',10,'bold'))
        style.configure('blankMatchTable.TLabel', background='white', font=('Helvetica',10,'bold'))
        style.configure('practiceMatchTable.TLabel', background=TEAM_COLOR_TABLE, font=('Helvetica', 10, 'bold'))
        style.configure('gridGaps.TLabel', background='#515151', foregroud='#515151', font = ('Helvetica', .1))

        #Create blank match info
        self.blankMatch = ('##', 'w', '######', ('##', '##'), ('##', '##'), ['###', '###', '###'], ['###', '###', '###'])

        #create tk objects
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.createWidgets()

        #update everything (self restarts every CYCLETIME ms)
        self.updateWidgets()

    def addMatch(self, number, day, time, teamsR, teamsB, practice=False):
        """Adds match"""

        #Make the match
        newMatch = Match(number, day, time, teamsR, teamsB, practice=practice)

        #Add it to the list and sort by time 'till
        self.matchList.append(newMatch)
        self.matchList.sort(key=lambda match: match.getTimeTill())

    def decreaseDelay(self):
        """Recreases DELAY by 5"""
        global DELAY
        DELAY -= 5

    def increaseDelay(self):
        """Increases DELAY by 5"""
        global DELAY
        DELAY += 5

    def resetDelay(self):
        """Resets the delay"""
        global DELAY
        DELAY = 0

    def doNothing(self):
        """Does nothing for right now"""
        pass

    def makeGuiList(self, displayNum=5, startAtCurr=True):
        """Creates the list of info for the GUI"""
        #Find first match to come
        if startAtCurr:
            indFirst = self.findCurrentMatch()
        else:
            indFirst = 0

        #If there are no matches, return a list of 5 blanks
        if indFirst == None:
            return [self.blankMatch for i in range(displayNum)]

        #Find that and next displayNum
        endIndex = indFirst+displayNum
        if endIndex >= len(self.matchList):
            endIndex = len(self.matchList)
        displayMatchList = self.matchList[indFirst:endIndex]
        
        #Pull relevant data
        matchInfo = [match.getMatchInfo() for match in displayMatchList]

        #Ensure full 5 slots are filled
        while len(matchInfo) < displayNum:
            matchInfo.append(self.blankMatch)

        return matchInfo

    def findCurrentMatch(self):
        """Finds current match"""
        #Walk through each match and find the first one with a positive time till
        for i,match in enumerate(self.matchList):
            if match.getTimeTill()[0] >= 0:
                return i
        return None

    def createWidgets(self):
        """Creates all the widgets"""
        #make things resize
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        
        #config grid
        self.rowconfigure(0, weight=1)
        self.rowconfigure(7, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)

        #major labels
        self.mainLabel = ttk.Label(self, text = TEAM_NUM+' NEXT MATCH IN:', style='defaultmainHeader.TLabel', anchor='center')
        self.timeLabel = ttk.Label(self, text = '00:00:00', style='defaulttime.TLabel', anchor='center')
        self.delayLabel = ttk.Label(self, text = 'Currently running '+str(DELAY)+ ' min late', anchor='center')
        self.upcomingLabel = ttk.Label(self, text = 'Upcoming Matches:')

        #major buttons
        self.earlierButton = ttk.Button(self, text = '5 Min Earlier', command = self.decreaseDelay)
        self.laterButton = ttk.Button(self, text = '5 Min Later', command = self.increaseDelay)
        self.resetButton = ttk.Button(self, text = 'Reset Delay', command = self.resetDelay)
        self.showListButton = ttk.Button(self, text = 'Full Match List', command = self.showMatchList)
        self.addMatchButton = ttk.Button(self, text = 'Add Match', command = self.addMatchGUI)

        #Frame for match table
        self.tableFrame = ttk.Frame(self)

        #place major widgets
        self.mainLabel.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.timeLabel.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.delayLabel.grid(row=3, column=2,  padx=5, pady=5, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.upcomingLabel.grid(row=4, column=1, padx=5, pady=5)
        self.earlierButton.grid(row=2, column=1, padx=5, pady=5)
        self.laterButton.grid(row=2, column=4, padx=5, pady=5)
        self.resetButton.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W)
        self.showListButton.grid(row=6, column=1, padx=5, pady=10)
        self.addMatchButton.grid(row=6, column=4, padx=5, pady=10)
        self.tableFrame.grid(row=5, column=1, columnspan=4, sticky=(tk.N,tk.S,tk.E,tk.W))

        #hacky solution for centering
        self.fooLabels = [ttk.Label(self, text = ' ') for i in range(10)]

        #place centering
        self.fooLabels[0].grid(row=0,column=0)
        self.fooLabels[1].grid(row=7,column=5)

        ########################
        # match table elements #
        ########################

        #Create nec match table data
        GUIMatchList = self.makeGuiList()

        #set column stretchiness
        self.tableFrame.columnconfigure(0, weight=1)
        self.tableFrame.columnconfigure(2, weight=1)
        self.tableFrame.columnconfigure(4, weight=1)
        self.tableFrame.columnconfigure(5, weight=1)
        self.tableFrame.columnconfigure(7, weight=1, minsize=50)
        self.tableFrame.columnconfigure(8, weight=1, minsize=50)
        self.tableFrame.columnconfigure(9, weight=1, minsize=50)
        self.tableFrame.columnconfigure(11, weight=1, minsize=50)
        self.tableFrame.columnconfigure(12, weight=1, minsize=50)
        self.tableFrame.columnconfigure(13, weight=1, minsize=50)
        self.tableFrame.columnconfigure(15, weight=1)

        #Make and place table Headers
        self.frameNumberTitle = ttk.Label(self.tableFrame, text = 'Match #', style='matchTable.TLabel', anchor='center')
        self.frameTimeTitle = ttk.Label(self.tableFrame, text = 'Time', style='matchTable.TLabel', anchor='center')
        self.frameWeTitle = ttk.Label(self.tableFrame, text = 'Our Alliance', style='matchTable.TLabel', anchor='center')
        self.frameTheyTitle = ttk.Label(self.tableFrame, text = 'Their Alliance', style='matchTable.TLabel', anchor='center')
        self.frameNumberTitle.grid(row=2, column=2, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.frameTimeTitle.grid(row=2, column=4, columnspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.frameWeTitle.grid(row=2, column=7, columnspan=3, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.frameTheyTitle.grid(row=2, column=11, columnspan=3, sticky=(tk.N,tk.S,tk.E,tk.W))

        #Add row and column separator bars
        self.tableHeaderGridGap = [( ttk.Label(self.tableFrame, text = ' ', style = 'gridGaps.TLabel') ) for i in range(8) ]
        self.tableHeaderGridGap[0].grid(row=2, column=1, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.tableHeaderGridGap[1].grid(row=2, column=3, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.tableHeaderGridGap[2].grid(row=2, column=6, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.tableHeaderGridGap[3].grid(row=2, column=10, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.tableHeaderGridGap[4].grid(row=2, column=14, sticky=(tk.N,tk.S,tk.E,tk.W))
        
        self.tableHeaderGridGap[5].grid(row=1, column=1, columnspan=14, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.tableHeaderGridGap[6].grid(row=3, column=1, columnspan=14, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.tableHeaderGridGap[7].grid(row=4, column=1, columnspan=14, sticky=(tk.N,tk.S,tk.E,tk.W))

        #initialize lists of table elements
        self.matchNumber = []
        self.matchInfo1 = []
        self.matchInfo2 = []
        self.matchTime1 = []
        self.matchTime2 = []
        self.matchTeam1 = []
        self.matchTeam2 = []
        self.matchTeam3 = []
        self.matchTeam4 = []
        self.matchTeam5 = []
        self.matchTeam6 = []
        self.matchGridGap = []
        
        #table elements
        for i,matchData in enumerate(GUIMatchList):
            #Set styles
            if matchData[1] == 'r':
                homeStyle = 'redMatchTable.TLabel'
                awayStyle = 'blueMatchTable.TLabel'
            elif matchData[1] == 'b':
                homeStyle = 'blueMatchTable.TLabel'
                awayStyle = 'redMatchTable.TLabel'
            elif matchData[1] == 'p':
                homeStyle = 'practiceMatchTable.TLabel'
                awayStyle = 'practiceMatchTable.TLabel'
            else:
                homeStyle = 'blankMatchTable.TLabel'
                awayStyle = 'blankMatchTable.TLabel'

            #Make time strings
            matchTime1String = toTimeString(matchData[3][0]) + ':' + toTimeString(matchData[3][1])
            matchTime2String = toTimeString(matchData[4][0]) + ':' + toTimeString(matchData[4][1])

            #Make Labels
            self.matchNumber.append( ttk.Label(self.tableFrame, text = matchData[0], style=homeStyle, anchor='center') )
            self.matchInfo1.append( ttk.Label(self.tableFrame, text = matchData[2] +' at:  ', style=homeStyle, anchor='e') )
            self.matchInfo2.append( ttk.Label(self.tableFrame, text = 'Est start time:  ', style=homeStyle, anchor='e') )
            self.matchTime1.append( ttk.Label(self.tableFrame, text = matchData[3], style = homeStyle, anchor='w') )
            self.matchTime2.append( ttk.Label(self.tableFrame, text = matchData[4], style = homeStyle, anchor='w') )
            self.matchTeam1.append( ttk.Label(self.tableFrame, text = matchData[5][0], style = homeStyle, anchor='center') )
            self.matchTeam2.append( ttk.Label(self.tableFrame, text = matchData[5][1], style = homeStyle, anchor='center') )
            self.matchTeam3.append( ttk.Label(self.tableFrame, text = matchData[5][2], style = homeStyle, anchor='center') )
            self.matchTeam4.append( ttk.Label(self.tableFrame, text = matchData[6][0], style = awayStyle, anchor='center') )
            self.matchTeam5.append( ttk.Label(self.tableFrame, text = matchData[6][1], style = awayStyle, anchor='center') )
            self.matchTeam6.append( ttk.Label(self.tableFrame, text = matchData[6][2], style = awayStyle, anchor='center') )
            self.matchGridGap.append( [ttk.Label(self.tableFrame, text = ' ', style = 'gridGaps.TLabel') for i2 in range(6)] )

        #place match table info
        for i in range(len(GUIMatchList)):
            self.matchGridGap[i][0].grid(row=3*i+5, column=1, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchNumber[i].grid(row=3*i+5, column=2, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchGridGap[i][1].grid(row=3*i+5, column=3, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchInfo1[i].grid(row=3*i+5, column=4, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchInfo2[i].grid(row=3*i+6, column=4, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchTime1[i].grid(row=3*i+5, column=5, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchTime2[i].grid(row=3*i+6, column=5, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchGridGap[i][2].grid(row=3*i+5, column=6, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchTeam1[i].grid(row=3*i+5, column=7, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchTeam2[i].grid(row=3*i+5, column=8, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchTeam3[i].grid(row=3*i+5, column=9, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchGridGap[i][3].grid(row=3*i+5, column=10, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchTeam4[i].grid(row=3*i+5, column=11, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchTeam5[i].grid(row=3*i+5, column=12, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchTeam6[i].grid(row=3*i+5, column=13, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchGridGap[i][4].grid(row=3*i+5, column=14, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.matchGridGap[i][5].grid(row=3*i+7, column=1, columnspan=14, sticky=(tk.N,tk.S,tk.E,tk.W))

        #Give add match button focus so can add things faster
        self.addMatchButton.focus_set()

    def updateWidgets(self):
        """Updates all changing bits of the GUI"""

        #Get current time till and matchlist
        currMatch = self.findCurrentMatch()
        if currMatch != None:
            currTimeTill = self.matchList[currMatch].getTimeTill()
            currColor = self.matchList[currMatch].ourColor
        GUIMatchList = self.makeGuiList()

        #Make timeLabel string
        if currMatch == None:
            timeLabelString = '##:##:##'
        else:
            timeLabelString =  toTimeString(currTimeTill[0]) + ':' + toTimeString(currTimeTill[1]) + ':' + toTimeString(currTimeTill[2])
        
        #Change color of header stuffs
        if currMatch == None or currColor == 'p':
            self.mainLabel.configure(style='defaultmainHeader.TLabel')
            self.timeLabel.configure(style='defaulttime.TLabel')
        elif currColor == 'r':
            self.mainLabel.configure(style='redmainHeader.TLabel')
            self.timeLabel.configure(style='redtime.TLabel')
        elif currColor == 'b':
            self.mainLabel.configure(style='bluemainHeader.TLabel')
            self.timeLabel.configure(style='bluetime.TLabel')
        else:
            raise TypeError #at least until I do better error handling

        #Change big time till
        self.timeLabel.configure(text = timeLabelString)

        #Change current delay display
        self.delayLabel.configure(text = 'Currently running '+str(DELAY)+ ' min late')

        #Update match list
        for i,matchData in enumerate(GUIMatchList):
            #Set styles
            if matchData[1] == 'r':
                homeStyle = 'redMatchTable.TLabel'
                awayStyle = 'blueMatchTable.TLabel'
            elif matchData[1] == 'b':
                homeStyle = 'blueMatchTable.TLabel'
                awayStyle = 'redMatchTable.TLabel'
            elif matchData[1] == 'p':
                homeStyle = 'practiceMatchTable.TLabel'
                awayStyle = 'practiceMatchTable.TLabel'
            else:
                homeStyle = 'blankMatchTable.TLabel'
                awayStyle = 'blankMatchTable.TLabel'

            #Make time strings
            matchTime1String = toTimeString(matchData[3][0]) + ':' + toTimeString(matchData[3][1])
            matchTime2String = toTimeString(matchData[4][0]) + ':' + toTimeString(matchData[4][1])

            #Update Labels
            self.matchNumber[i].configure(text = matchData[0], style = homeStyle)
            self.matchInfo1[i].configure(text = matchData[2] +' at:', style=homeStyle)
            self.matchInfo2[i].configure(text = 'Est start time:', style=homeStyle)
            self.matchTime1[i].configure(text = matchTime1String, style = homeStyle)
            self.matchTime2[i].configure(text = matchTime2String, style = homeStyle)
            self.matchTeam1[i].configure(text = matchData[5][0], style = homeStyle)
            self.matchTeam2[i].configure(text = matchData[5][1], style = homeStyle)
            self.matchTeam3[i].configure(text = matchData[5][2], style = homeStyle)
            self.matchTeam4[i].configure(text = matchData[6][0], style = awayStyle)
            self.matchTeam5[i].configure(text = matchData[6][1], style = awayStyle)
            self.matchTeam6[i].configure(text = matchData[6][2], style = awayStyle)

        #resize font
        timeWidth = self.winfo_width() #get size
        fontSize = timeWidth/12 #width -> font size
        fontSize = (fontSize/8)*8 # to make not jumpy, make discrete font choices
        if fontSize < 72: fontSize=72 #set min font size
        self.timeLabel.configure(font= ('Helvetica',fontSize,'bold'))

        self.after(CYCLETIME, self.updateWidgets)

    def addMatchGUI(self):
        """Makes a separate window to input more matches"""

        #Create the window, frame in it, and have the frame fill the window
        self.addMatchWindow = tk.Toplevel(self)
        self.addMatchWinFrame = ttk.Frame(self.addMatchWindow)
        self.addMatchWinFrame.grid(padx=10, pady=10, sticky=(tk.N+tk.S+tk.E+tk.W))
        self.addMatchWindow.title('Add Match')

        #Add bullshit content to get padding
        self.fooLabelsMatchWin = [ttk.Label(self.addMatchWinFrame, text = ' ') for i in range(10)]
        
        #Create and place match entry
        self.addMatchNumberLabel = ttk.Label(self.addMatchWinFrame, text = 'Match #:', font = ('Helvetica',10,'bold'))
        self.addMatchNumberEntry = ttk.Entry(self.addMatchWinFrame, width=4, justify='center')
        self.addMatchNumberLabel.grid(row=1, column=1, padx=5, pady=5)
        self.addMatchNumberEntry.grid(row=2, column=1)

        #Create and place day dropdown
        self.addMatchDayLabel = ttk.Label(self.addMatchWinFrame, text = 'Day:', font = ('Helvetica',10,'bold'))
        self.addMatchDayDropdown = ttk.Combobox(self.addMatchWinFrame)
        self.addMatchDayDropdown['values'] = ('Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
        self.addMatchDayDropdown.configure(state='readonly')
        self.addMatchDayLabel.grid(row=1, column=3, padx=5, pady=5)
        self.addMatchDayDropdown.grid(row=2, column=3)

        #Create and place time entries
        self.addMatchTimeLabel = ttk.Label(self.addMatchWinFrame, text = 'Time:', font = ('Helvetica',10,'bold'))
        self.addMatchTime1 = ttk.Entry(self.addMatchWinFrame, width=4, justify='center')
        self.addMatchTimeColon = ttk.Label(self.addMatchWinFrame, text = ':', anchor='center')
        self.addMatchTime2 = ttk.Entry(self.addMatchWinFrame, width=4, justify='center')
        self.addMatchTimeLabel.grid(row=1, column=5, columnspan=3, padx=5, pady=5)
        self.addMatchTime1.grid(row=2, column=5)
        self.addMatchTimeColon.grid(row=2, column=6)
        self.addMatchTime2.grid(row=2, column=7)

        #Create and place red teams
        self.addMatchRedLabel = ttk.Label(self.addMatchWinFrame, text = 'Red Teams:', foreground='red', font = ('Helvetica',10,'bold'))
        self.addMatchRedTeam1 = ttk.Entry(self.addMatchWinFrame, width=6, foreground='red', justify='center')
        self.addMatchRedTeam2 = ttk.Entry(self.addMatchWinFrame, width=6, foreground='red', justify='center')
        self.addMatchRedTeam3 = ttk.Entry(self.addMatchWinFrame, width=6, foreground='red', justify='center')
        self.addMatchRedLabel.grid(row=1, column=9, columnspan=3, padx=5, pady=5)
        self.addMatchRedTeam1.grid(row=2, column=9, padx=5)
        self.addMatchRedTeam2.grid(row=2, column=10, padx=5)
        self.addMatchRedTeam3.grid(row=2, column=11, padx=5)

        #Create and place blue teams
        self.addMatchBlueLabel = ttk.Label(self.addMatchWinFrame, text = 'Blue Teams:', foreground='blue', font = ('Helvetica',10,'bold'))
        self.addMatchBlueTeam1 = ttk.Entry(self.addMatchWinFrame, width=6, foreground='blue', justify='center')
        self.addMatchBlueTeam2 = ttk.Entry(self.addMatchWinFrame, width=6, foreground='blue', justify='center')
        self.addMatchBlueTeam3 = ttk.Entry(self.addMatchWinFrame, width=6, foreground='blue', justify='center')
        self.addMatchBlueLabel.grid(row=1, column=13, columnspan=3, padx=5, pady=5)
        self.addMatchBlueTeam1.grid(row=2, column=13, padx=5)
        self.addMatchBlueTeam2.grid(row=2, column=14, padx=5)
        self.addMatchBlueTeam3.grid(row=2, column=15, padx=5)

        #Create and place checkbutton for practice matches
        self.addMatchPracticeFrame = ttk.Frame(self.addMatchWinFrame)
        self.addMatchPracticeFrame.grid(row=3, column=1, columnspan=15, sticky=tk.E)
        self.practiceFlag = tk.IntVar()
        def removeData():
            if self.practiceFlag.get():
                self.addMatchNumberLabel.grid_remove()
                self.addMatchNumberEntry.grid_remove()
                self.addMatchRedLabel.grid_remove()
                self.addMatchRedTeam1.grid_remove()
                self.addMatchRedTeam2.grid_remove()
                self.addMatchRedTeam3.grid_remove()
                self.addMatchBlueLabel.grid_remove()
                self.addMatchBlueTeam1.grid_remove()
                self.addMatchBlueTeam2.grid_remove()
                self.addMatchBlueTeam3.grid_remove()
                self.fooLabelsMatchWin[0].grid_remove()
                self.fooLabelsMatchWin[2].grid_remove()
                self.fooLabelsMatchWin[3].grid_remove()
                self.addMatchPracticeFrame.grid(columnspan=7)
                self.addMatchButtonFrame.grid(columnspan=7)
            else:
                self.addMatchNumberLabel.grid()
                self.addMatchNumberEntry.grid()
                self.addMatchRedLabel.grid()
                self.addMatchRedTeam1.grid()
                self.addMatchRedTeam2.grid()
                self.addMatchRedTeam3.grid()
                self.addMatchBlueLabel.grid()
                self.addMatchBlueTeam1.grid()
                self.addMatchBlueTeam2.grid()
                self.addMatchBlueTeam3.grid()
                self.fooLabelsMatchWin[0].grid()
                self.fooLabelsMatchWin[2].grid()
                self.fooLabelsMatchWin[3].grid()
                self.addMatchPracticeFrame.grid(columnspan=15)
                self.addMatchButtonFrame.grid(columnspan=15)
        self.addMatchPracticeCheck = tk.Checkbutton(self.addMatchPracticeFrame, text='Practice Field', onvalue=1, offvalue=0, variable=self.practiceFlag, command=removeData)
        self.addMatchPracticeCheck.pack(side=tk.RIGHT, padx=5, pady=20)
        self.practiceFlag.set(0)
        
        #Create and place add and cancel buttons in new frame
        self.addMatchButtonFrame = ttk.Frame(self.addMatchWinFrame)
        self.addMatchButtonFrame.grid(row=4, column=1, columnspan=15, sticky=(tk.E, tk.W))
        self.addMatchButton = ttk.Button(self.addMatchButtonFrame, text = 'Add Match', command = self.addMatchDo)
        self.addMatchCancel = ttk.Button(self.addMatchButtonFrame, text = 'Cancel', command = self.addMatchWindow.destroy)
        self.addMatchCancel.pack(side=tk.RIGHT, padx=5, pady=10)
        self.addMatchButton.pack(side=tk.RIGHT, padx=5, pady=10)

        #Place hacky/bullshit content for padding
        self.fooLabelsMatchWin[0].grid(row=0, column=2, padx=5)
        self.fooLabelsMatchWin[1].grid(row=0, column=4, padx=5)
        self.fooLabelsMatchWin[2].grid(row=0, column=8, padx=5)
        self.fooLabelsMatchWin[3].grid(row=0, column=12, padx=5)

        #Add defaults
        self.addMatchNumberEntry.insert(0, '##')
        self.addMatchTime1.insert(0, 'HH')
        self.addMatchTime2.insert(0, 'MM')
        self.addMatchRedTeam1.insert(0, '###')
        self.addMatchRedTeam2.insert(0, '###')
        self.addMatchRedTeam3.insert(0, '###')
        self.addMatchBlueTeam1.insert(0, '###')
        self.addMatchBlueTeam2.insert(0, '###')
        self.addMatchBlueTeam3.insert(0, '###')

        #Give focus to match number
        self.addMatchNumberEntry.select_range(0, 2)
        self.addMatchNumberEntry.focus_set()

    def throwError(self, message, window, entry, selectRange=None):
        """Makes error box, then returns focus to entry in window"""
        
        #Make error box
        box.showerror('Error', message)

        #Bring window to the front
        window.lift()

        #Give focus appropriately
        window.focus_set()
        if selectRange:
            entry.select_range(selectRange[0], selectRange[1])
        entry.focus_set()

    def addMatchDo(self):
        """Checks then adds match data"""

        #First, we get all the strings
        number = self.addMatchNumberEntry.get()
        day = self.addMatchDayDropdown.get()
        hour = self.addMatchTime1.get()
        minute = self.addMatchTime2.get()
        red1 = self.addMatchRedTeam1.get()
        red2 = self.addMatchRedTeam2.get()
        red3 = self.addMatchRedTeam3.get()
        blue1 = self.addMatchBlueTeam1.get()
        blue2 = self.addMatchBlueTeam2.get()
        blue3 = self.addMatchBlueTeam3.get()

        #Then, we check that things aren't default values
        if number == '##' and not self.practiceFlag.get():
            self.throwError('You must enter a match number', self.addMatchWindow, self.addMatchNumberEntry, (0,2))
            return 0

        if day == '':
            self.throwError('You must enter a day', self.addMatchWindow, self.addMatchDayDropdown)
            return 0

        if hour == 'HH':
            self.throwError('You must enter an hour', self.addMatchWindow, self.addMatchTime1, (0,2))
            return 0

        if minute == 'MM':
            self.throwError('You must enter a minute', self.addMatchWindow, self.addMatchTime2, (0,2))
            return 0

        if red1 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchRedTeam1, (0,3))
            return 0

        if red2 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchRedTeam2, (0,3))
            return 0

        if red3 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchRedTeam3, (0,3))
            return 0

        if blue1 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchBlueTeam1, (0,3))
            return 0

        if blue2 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchBlueTeam2, (0,3))
            return 0

        if blue3 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchBlueTeam3, (0,3))
            return 0

        #Then we check that values are ok for times
        try:
            hourInt = int(hour)
        except: #hackily catching all the errors
            self.throwError('Hour value must be an integer', self.addMatchWindow, self.addMatchTime1, (0, len(hour)))
            return 0
        
        if hourInt < 0 or hourInt > 23: #if not a valid hour
            self.throwError('Hour value must be between 0 and 24', self.addMatchWindow, self.addMatchTime1, (0, len(hour)))

        #Now we check minute the same way
        try:
            minInt = int(minute)
        except: #hackily catching all the errors
            self.throwError('Minute value must be an integer', self.addMatchWindow, self.addMatchTime2, (0, len(minute)))
            return 0
        if minInt < 0 or minInt > 59: #if not a valid minute
            self.throwError('Minute value must be between 0 and 60', self.addMatchWindow, self.addMatchTime2, (0, len(minute)))
            return 0
        
        #Check if our team has been entered
        if not TEAM_NUM in [red1, red2, red3, blue1, blue2, blue3] and not self.practiceFlag.get():
            self.throwError('Our team number was not entered', self.addMatchWindow, self.addMatchRedTeam1, (0,len(red1)))
            return 0

        #Everything else stays as strings, so that's fine
        #And now we actually add the match
        self.addMatch(number, day, (hourInt, minInt), [red1, red2, red3], [blue1, blue2, blue3], practice=bool(self.practiceFlag.get()))

        #And, because nothing went wrong, we tell people we added the match
        self.addMatchWindow.destroy() #destroy current window
        self.addAnotherMatch(number, day,(hourInt, minInt), [red1, red2, red3], [blue1, blue2, blue3])

    def addAnotherMatch(self, number, day, time, teamsr, teamsb):
        """Asks if want to add another match"""
        
        #Create the window, frame in it, and have the frame fill the window
        self.addAnotherWindow = tk.Toplevel(self)
        self.addAnotherWinFrame = ttk.Frame(self.addAnotherWindow)
        self.addAnotherWinFrame.grid(sticky=(tk.N+tk.S+tk.E+tk.W))
        self.addAnotherWindow.title('Add Another')

        #Add bullshit content to get padding
        self.fooLabelsAnotherWin = [ttk.Label(self.addAnotherWinFrame, text = ' ') for i in range(2)]

        #Create string
        if self.practiceFlag.get():
            infoString = 'Successfully created practice match for ' + day + ' at ' + toTimeString(time[0]) + ':' + toTimeString(time[1])
        else:
            infoString = 'Successfully created match:\n\n'# #' + number + ' on ' + day + ' at '
            infoString = infoString + '#' + number + ': ' + day + ' at '
            infoString = infoString + toTimeString(time[0]) + ':' + toTimeString(time[1]) + '.  '
            infoString = infoString + 'Red teams: ' + teamsr[0] + ', ' + teamsr[1] + ', ' + teamsr[2] + '.  '
            infoString = infoString + 'Blue teams: ' + teamsb[0] + ', ' + teamsb[1] + ', ' + teamsb[2] + '.'

        #Display info just added
        self.addAnotherInfoLabel = ttk.Label(self.addAnotherWinFrame, text = infoString)
        self.addAnotherInfoLabel.grid(row=1, column=1, columnspan=2, padx=5, pady=10)

        #Make and place buttons
        self.addAnotherButtonFrame = ttk.Frame(self.addAnotherWinFrame)
        self.addAnotherButtonFrame.grid(row=2, column=1, columnspan=2, sticky=tk.E)
        self.addAnotherDoneButton = ttk.Button(self.addAnotherButtonFrame, text = 'Done Adding', command = self.addAnotherWindow.destroy)
        def addAnother():
            self.addAnotherWindow.destroy()
            self.addMatchGUI()
        self.addAnotherAddButton = ttk.Button(self.addAnotherButtonFrame, text = 'Add Another', command = addAnother)
        self.addAnotherDoneButton.pack(side=tk.RIGHT, padx=5, pady=10)
        self.addAnotherAddButton.pack(side=tk.RIGHT, padx=5, pady=10)

        #Place bullshit spacing content
        self.fooLabelsAnotherWin[0].grid(row=0,column=0)
        self.fooLabelsAnotherWin[1].grid(row=3, column=3)

        #Because almost always going to be adding more than one, give focus there
        self.addAnotherWindow.focus_set()
        self.addAnotherAddButton.focus_set()
        
    def showMatchList(self):
        """Creates window that shows full match list"""
        
        #Create the window, frame in it, and have the frame fill the window
        self.listWindow = tk.Toplevel(self)
        self.listWinFrame = ttk.Frame(self.listWindow)
        self.listWinFrame.grid(padx=10, sticky=(tk.N+tk.S+tk.E+tk.W))
        self.listWindow.title('Full Match List')
        self.listWindow.rowconfigure(0,weight=1)
        self.listWindow.columnconfigure(0,weight=1)

        #Set column stretchiness
        self.listWinFrame.columnconfigure(0, weight=1)
        self.listWinFrame.columnconfigure(3, weight=1)
        self.listWinFrame.columnconfigure(5, weight=1)
        self.listWinFrame.columnconfigure(6, weight=1)
        self.listWinFrame.columnconfigure(8, weight=1, minsize=50)
        self.listWinFrame.columnconfigure(9, weight=1, minsize=50)
        self.listWinFrame.columnconfigure(10, weight=1, minsize=50)
        self.listWinFrame.columnconfigure(12, weight=1, minsize=50)
        self.listWinFrame.columnconfigure(13, weight=1, minsize=50)
        self.listWinFrame.columnconfigure(14, weight=1, minsize=50)
        self.listWinFrame.columnconfigure(16, weight=1)

        #Create hacky spacers
        self.fooLabelsListWin = [ttk.Label(self.listWinFrame, text = '     ') for i in range(2)]

        #Make and place table Headers
        self.listNumberTitle = ttk.Label(self.listWinFrame, text = 'Match #', style='matchTable.TLabel', anchor='center')
        self.listTimeTitle = ttk.Label(self.listWinFrame, text = 'Time', style='matchTable.TLabel', anchor='center')
        self.listWeTitle = ttk.Label(self.listWinFrame, text = 'Our Alliance', style='matchTable.TLabel', anchor='center')
        self.listTheyTitle = ttk.Label(self.listWinFrame, text = 'Their Alliance', style='matchTable.TLabel', anchor='center')
        self.listNumberTitle.grid(row=2, column=3, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listTimeTitle.grid(row=2, column=5, columnspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listWeTitle.grid(row=2, column=8, columnspan=3, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listTheyTitle.grid(row=2, column=12, columnspan=3, sticky=(tk.N,tk.S,tk.E,tk.W))
        
        #Add row and column separator bars
        self.listHeaderGridGap = [( ttk.Label(self.listWinFrame, text = ' ', style = 'gridGaps.TLabel') ) for i in range(8) ]
        self.listHeaderGridGap[0].grid(row=2, column=2, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listHeaderGridGap[1].grid(row=2, column=4, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listHeaderGridGap[2].grid(row=2, column=7, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listHeaderGridGap[3].grid(row=2, column=11, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listHeaderGridGap[4].grid(row=2, column=15, sticky=(tk.N,tk.S,tk.E,tk.W))
        
        self.listHeaderGridGap[5].grid(row=1, column=2, columnspan=14, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listHeaderGridGap[6].grid(row=3, column=2, columnspan=14, sticky=(tk.N,tk.S,tk.E,tk.W))
        self.listHeaderGridGap[7].grid(row=4, column=2, columnspan=14, sticky=(tk.N,tk.S,tk.E,tk.W))

        #Create nec match table data
        GUIMatchList = self.makeGuiList(displayNum=len(self.matchList), startAtCurr=False)

        #match table elements
        #initialize
        self.listWinNumber = []
        self.listWinInfo1 = []
        self.listWinInfo2 = []
        self.listWinTime1 = []
        self.listWinTime2 = []
        self.listWinTeam1 = []
        self.listWinTeam2 = []
        self.listWinTeam3 = []
        self.listWinTeam4 = []
        self.listWinTeam5 = []
        self.listWinTeam6 = []
        self.listWinGridGap = []
        self.matchIntVars = []
        self.listCheckbuttons = []

        #set
        for i,matchData in enumerate(GUIMatchList):
            
            #Set styles
            if matchData[1] == 'r':
                homeStyle = 'redMatchTable.TLabel'
                awayStyle = 'blueMatchTable.TLabel'
            elif matchData[1] == 'b':
                homeStyle = 'blueMatchTable.TLabel'
                awayStyle = 'redMatchTable.TLabel'
            elif matchData[1] == 'p':
                homeStyle = 'practiceMatchTable.TLabel'
                awayStyle = 'practiceMatchTable.TLabel'
            else:
                homeStyle = 'blankMatchTable.TLabel'
                awayStyle = 'blankMatchTable.TLabel'

            #Make time strings
            matchTime1String = toTimeString(matchData[3][0]) + ':' + toTimeString(matchData[3][1])
            matchTime2String = toTimeString(matchData[4][0]) + ':' + toTimeString(matchData[4][1])

            #Make Labels
            self.listWinNumber.append( ttk.Label(self.listWinFrame, text = matchData[0], style=homeStyle, anchor='center') )
            self.listWinInfo1.append( ttk.Label(self.listWinFrame, text = matchData[2] +' at:  ', style=homeStyle, anchor='e') )
            self.listWinInfo2.append( ttk.Label(self.listWinFrame, text = 'Est start time:  ', style=homeStyle, anchor='e') )
            self.listWinTime1.append( ttk.Label(self.listWinFrame, text = matchTime1String, style = homeStyle, anchor='w') )
            self.listWinTime2.append( ttk.Label(self.listWinFrame, text = matchTime2String, style = homeStyle, anchor='w') )
            self.listWinTeam1.append( ttk.Label(self.listWinFrame, text = matchData[5][0], style = homeStyle, anchor='center') )
            self.listWinTeam2.append( ttk.Label(self.listWinFrame, text = matchData[5][1], style = homeStyle, anchor='center') )
            self.listWinTeam3.append( ttk.Label(self.listWinFrame, text = matchData[5][2], style = homeStyle, anchor='center') )
            self.listWinTeam4.append( ttk.Label(self.listWinFrame, text = matchData[6][0], style = awayStyle, anchor='center') )
            self.listWinTeam5.append( ttk.Label(self.listWinFrame, text = matchData[6][1], style = awayStyle, anchor='center') )
            self.listWinTeam6.append( ttk.Label(self.listWinFrame, text = matchData[6][2], style = awayStyle, anchor='center') )
            self.listWinGridGap.append( [ttk.Label(self.listWinFrame, text = ' ', style = 'gridGaps.TLabel') for i2 in range(6)] )
            #Make Checkbutton elementsts
            self.matchIntVars.append(tk.IntVar())
            self.listCheckbuttons.append( tk.Checkbutton(self.listWinFrame, onvalue=i, offvalue=-1, variable=self.matchIntVars[i], command=self.listEnableEdit) )
            self.matchIntVars[i].set(-1)

        #place match table info and check button
        for i in range(len(GUIMatchList)):
            self.listWinGridGap[i][0].grid(row=3*i+5, column=2, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinNumber[i].grid(row=3*i+5, column=3, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinGridGap[i][1].grid(row=3*i+5, column=4, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinInfo1[i].grid(row=3*i+5, column=5, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinInfo2[i].grid(row=3*i+6, column=5, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinTime1[i].grid(row=3*i+5, column=6, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinTime2[i].grid(row=3*i+6, column=6, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinGridGap[i][2].grid(row=3*i+5, column=7, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinTeam1[i].grid(row=3*i+5, column=8, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinTeam2[i].grid(row=3*i+5, column=9, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinTeam3[i].grid(row=3*i+5, column=10, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinGridGap[i][3].grid(row=3*i+5, column=11, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinTeam4[i].grid(row=3*i+5, column=12, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinTeam5[i].grid(row=3*i+5, column=13, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinTeam6[i].grid(row=3*i+5, column=14, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinGridGap[i][4].grid(row=3*i+5, column=15, rowspan=2, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listWinGridGap[i][5].grid(row=3*i+7, column=2, columnspan=14, sticky=(tk.N,tk.S,tk.E,tk.W))
            self.listCheckbuttons[i].grid(row=3*i+5, column=0, rowspan=2, sticky=tk.E)
            

        #Make and place edit matches button in new frame
        self.listWinButtonFrame = ttk.Frame(self.listWinFrame)
        self.listWinButtonFrame.grid(row=3*len(GUIMatchList)+8, column=1, columnspan=15, sticky=(tk.S,tk.E,tk.W))
        self.listWinEditButton = ttk.Button(self.listWinButtonFrame, text = 'Edit Match', command=self.editMatchGUI)
        self.listWinEditButton.pack(side=tk.RIGHT, padx=5, pady=10)
        self.listWinEditButton.configure(state='disabled') #can't press until a checkbutton has been pressed
        
        #make and place ok button in button frame
        self.listWinOKButton = ttk.Button(self.listWinButtonFrame, text = 'OK', command=self.listWindow.destroy)
        self.listWinOKButton.pack(side=tk.RIGHT, padx=5, pady=10)
        self.listWinOKButton.focus_set()

        #make and place load button
        self.listWinLoadButton = ttk.Button(self.listWinButtonFrame, text = 'Load Match List', command=self.loadMatchList)
        self.listWinLoadButton.pack(side=tk.LEFT, padx=5, pady=10)

        #make and place save button
        self.listWinSaveButton = ttk.Button(self.listWinButtonFrame, text = 'Save Match List', command=self.saveMatchList)
        self.listWinSaveButton.pack(side=tk.LEFT, padx=5, pady=10)
        
        #make mark on current match
        currInd = self.findCurrentMatch()
        if currInd != None:
            self.mark = ttk.Label(self.listWinFrame, text='  ', background='green')
            self.mark.grid(row=currInd*3+5, column=0, rowspan=2, sticky=(tk.E,tk.N,tk.S))
            self.greenOn=True

        #place hacky spacers
        self.fooLabelsListWin[0].grid(row=0, column=0)
        self.fooLabelsListWin[1].grid(row=0, column=16)

        #Set row stretchiness (needed last row)
        self.listWinFrame.rowconfigure(0, weight=1)
        self.listWinFrame.rowconfigure(3*len(GUIMatchList)+8, weight=1)

        #make mark blink
        if currInd != None:
            self.currBG = ttk.Style().lookup('TLabel', 'background')
            self.listWinFrame.after(500, self.blinkMark)

    def blinkMark(self):
        """Blinks the green mark"""
        currInd = self.findCurrentMatch()
        if currInd != None:
            if self.greenOn:
                self.mark.configure(background=self.currBG)
                self.greenOn=False
            else:
                self.mark.configure(background='green')
                self.greenOn=True
            self.mark.grid(row=currInd*3+5, column=0, rowspan=2, sticky=(tk.E,tk.N,tk.S))
            self.listWinFrame.after(500, self.blinkMark)

    def findToEdit(self):
        """Returns index number of match to edit or None"""
        for var in self.matchIntVars:
            toEdit = var.get()
            if toEdit != -1:
                break
            else:
                continue
        if toEdit == -1:
            self.toEdit = None
        else:
            self.toEdit = toEdit
    
    def listEnableEdit(self):
        """Toggles edit button state in list edit button"""
        self.findToEdit()
        if self.toEdit != None:
            self.listWinEditButton.configure(state='normal')
        else:
            self.listWinEditButton.configure(state='disabled')

    def deleteToEdit(self):
        """Deletes match in matchList at self.toEdit"""
        if self.toEdit != None:
            self.matchList.remove(self.matchList[self.toEdit])
        else:
            raise TypeError #until create real error

    def saveMatchList(self):
        """Saves match list with tkFileDialog"""

        #supported file formats:
        matchListFormats = [
            ('Match List', '.mlist'),
            ('Comma Separated Value', '.csv')]

        #get file name from tkFileDialog
        fname = fileBox.asksaveasfilename(parent=self.listWindow, filetypes=matchListFormats, defaultextension='.mlist')

        #if canceled, just exit
        if fname == '':
            return 0

        #save file. Currently just pickles, will handle csv's later
        with open(fname,'w') as f:
            pickle.dump(self.matchList, f)

    def loadMatchList(self):
        """Loads match list with tkFileDialog"""

        #supported file formats:
        matchListFormats = [
            ('Match List', '.mlist'),
            ('Comma Separated Value', '.csv')]

        #get file name from tkFileDialog
        fname = fileBox.askopenfilename(parent=self.listWindow, filetypes=matchListFormats, defaultextension='.mlist')

        #if canceled, just exit
        if fname == '':
            return 0

        #save file. Currently just pickles, will handle csv's later
        with open(fname) as f:
            listToAdd = pickle.load(f)

        #add the matches to the list, then sort
        for match in listToAdd:
            self.matchList.append(match)
        self.matchList.sort(key=lambda match: match.getTimeTill())

        #hackily kill existing list window and redisplay to update
        self.listWindow.destroy() 
        self.showMatchList() 


    def editMatchGUI(self):
        """Edits selected match"""
        #Check for intvar that's not -1 as that's the one that gets edited
        self.findToEdit()
        
        #Pull match
        matchToEdit = self.matchList[self.toEdit]

        #open addMatchGUI window
        self.addMatchGUI()

        #override those inputs and window title
        self.addMatchWindow.title('Edit Match')
        
        self.addMatchNumberEntry.delete(0, tk.END)
        self.addMatchTime1.delete(0, tk.END)
        self.addMatchTime2.delete(0, tk.END)
        self.addMatchRedTeam1.delete(0, tk.END)
        self.addMatchRedTeam2.delete(0, tk.END)
        self.addMatchRedTeam3.delete(0, tk.END)
        self.addMatchBlueTeam1.delete(0, tk.END)
        self.addMatchBlueTeam2.delete(0, tk.END)
        self.addMatchBlueTeam3.delete(0, tk.END)
        
        self.addMatchNumberEntry.insert(0, matchToEdit.number)
        self.addMatchTime1.insert(0, toTimeString(matchToEdit.time[0]))
        self.addMatchTime2.insert(0, toTimeString(matchToEdit.time[1]))
        self.addMatchRedTeam1.insert(0, matchToEdit.teamsR[0])
        self.addMatchRedTeam2.insert(0, matchToEdit.teamsR[1])
        self.addMatchRedTeam3.insert(0, matchToEdit.teamsR[2])
        self.addMatchBlueTeam1.insert(0, matchToEdit.teamsB[0])
        self.addMatchBlueTeam2.insert(0, matchToEdit.teamsB[1])
        self.addMatchBlueTeam3.insert(0, matchToEdit.teamsB[2])

        self.addMatchDayDropdown.current(self.addMatchDayDropdown['values'].index(matchToEdit.day))

        #toggle practice
        if matchToEdit.ourColor == 'p':
            self.addMatchPracticeCheck.invoke()

        #add delete button
        self.addMatchDeleteButton = ttk.Button(self.addMatchButtonFrame, text = 'Delete', command=self.checkDelete)
        self.addMatchDeleteButton.pack(side = tk.LEFT, padx=5, pady=10)

        #change addmatch button to editmatch - which will call variation on the add match
        self.addMatchButton.configure(text = 'Edit Match', command=self.editMatchDo)

    def checkDelete(self):
        """Checks if really want to delete then does or doesn't"""
        #Create the window, frame in it, and have the frame fill the window
        self.deleteWindow = tk.Toplevel(self)
        self.deleteWinFrame = ttk.Frame(self.deleteWindow)
        self.deleteWinFrame.grid(padx=20, pady=20, sticky=(tk.N+tk.S+tk.E+tk.W))
        self.deleteWindow.title('Confirm Delete')
        self.deleteWindow.rowconfigure(0,weight=1)
        self.deleteWindow.columnconfigure(0,weight=1)

        #create label
        self.deleteLabel = ttk.Label(self.deleteWinFrame, text='Are you sure you want to delete?')

        #create buttons
        def doDelete():
            self.deleteToEdit() #delete
            self.deleteWindow.destroy()
            self.addMatchWindow.destroy()
            self.listWindow.destroy() #get rid of all the stacked windows
            self.showMatchList() #re-show list (totally hacky instead of updating 'cause I'm lazy)
        self.deleteButton = ttk.Button(self.deleteWinFrame, text = 'Delete', command=doDelete)
        self.delCancelButton = ttk.Button(self.deleteWinFrame, text = 'Cancel', command=self.deleteWindow.destroy)

        self.deleteLabel.pack(padx=5, pady=5)
        self.delCancelButton.pack(side=tk.RIGHT, padx=5, pady=10)
        self.deleteButton.pack(side=tk.RIGHT, padx=5, pady=10)

        #give focus
        self.deleteWindow.focus_set()
        self.deleteButton.focus_set()

    def editMatchDo(self):
        """Checks data, edits match, then calls add another with some edits"""
        
        #First, we get all the strings
        number = self.addMatchNumberEntry.get()
        day = self.addMatchDayDropdown.get()
        hour = self.addMatchTime1.get()
        minute = self.addMatchTime2.get()
        red1 = self.addMatchRedTeam1.get()
        red2 = self.addMatchRedTeam2.get()
        red3 = self.addMatchRedTeam3.get()
        blue1 = self.addMatchBlueTeam1.get()
        blue2 = self.addMatchBlueTeam2.get()
        blue3 = self.addMatchBlueTeam3.get()

        #Then, we check that things aren't default values
        if number == '##' and not self.practiceFlag.get():
            self.throwError('You must enter a match number', self.addMatchWindow, self.addMatchNumberEntry, (0,2))
            return 0

        if day == '':
            self.throwError('You must enter a day', self.addMatchWindow, self.addMatchDayDropdown)
            return 0

        if hour == 'HH':
            self.throwError('You must enter an hour', self.addMatchWindow, self.addMatchTime1, (0,2))
            return 0

        if minute == 'MM':
            self.throwError('You must enter a minute', self.addMatchWindow, self.addMatchTime2, (0,2))
            return 0

        if red1 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchRedTeam1, (0,3))
            return 0

        if red2 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchRedTeam2, (0,3))
            return 0

        if red3 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchRedTeam3, (0,3))
            return 0

        if blue1 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchBlueTeam1, (0,3))
            return 0

        if blue2 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchBlueTeam2, (0,3))
            return 0

        if blue3 == '###' and not self.practiceFlag.get():
            self.throwError('You must enter all team numbers', self.addMatchWindow, self.addMatchBlueTeam3, (0,3))
            return 0

        #Then we check that values are ok for times
        try:
            hourInt = int(hour)
        except: #hackily catching all the errors
            self.throwError('Hour value must be an integer', self.addMatchWindow, self.addMatchTime1, (0, len(hour)))
            return 0
        
        if hourInt < 0 or hourInt > 23: #if not a valid hour
            self.throwError('Hour value must be between 0 and 24', self.addMatchWindow, self.addMatchTime1, (0, len(hour)))

        #Now we check minute the same way
        try:
            minInt = int(minute)
        except: #hackily catching all the errors
            self.throwError('Minute value must be an integer', self.addMatchWindow, self.addMatchTime2, (0, len(minute)))
            return 0
        if minInt < 0 or minInt > 59: #if not a valid minute
            self.throwError('Minute value must be between 0 and 60', self.addMatchWindow, self.addMatchTime2, (0, len(minute)))
            return 0
        
        #Check if our team has been entered
        if not TEAM_NUM in [red1, red2, red3, blue1, blue2, blue3] and not self.practiceFlag.get():
            self.throwError('Our team number was not entered', self.addMatchWindow, self.addMatchRedTeam1, (0,len(red1)))
            return 0

        #Everything else stays as strings, so that's fine
        #And now we actually edit the match by deleting and re-adding
        self.deleteToEdit()
        self.addMatch(number, day, (hourInt, minInt), [red1, red2, red3], [blue1, blue2, blue3], practice=bool(self.practiceFlag.get()))

        #And, because nothing went wrong, we tell people we added the match
        self.addMatchWindow.destroy() #destroy current window
        self.showEdited(number, day,(hourInt, minInt), [red1, red2, red3], [blue1, blue2, blue3])

    def showEdited(self, number, day, time, teamsr, teamsb):
        """Tells edited match"""
        
        #Create the window, frame in it, and have the frame fill the window
        self.editedWindow = tk.Toplevel(self)
        self.editedWinFrame = ttk.Frame(self.editedWindow)
        self.editedWinFrame.grid(padx=20, pady=20, sticky=(tk.N+tk.S+tk.E+tk.W))
        self.editedWindow.title('Success')

        #Create string
        if self.practiceFlag.get():
            infoString = 'Successfully edited practice match for ' + day + ' at ' + toTimeString(time[0]) + ':' + toTimeString(time[1])
        else:
            infoString = 'Successfully edited match:\n\n'# #' + number + ' on ' + day + ' at '
            infoString = infoString + '#' + number + ': ' + day + ' at '
            infoString = infoString + toTimeString(time[0]) + ':' + toTimeString(time[1]) + '.  '
            infoString = infoString + 'Red teams: ' + teamsr[0] + ', ' + teamsr[1] + ', ' + teamsr[2] + '.  '
            infoString = infoString + 'Blue teams: ' + teamsb[0] + ', ' + teamsb[1] + ', ' + teamsb[2] + '.'

        #Display info just added
        self.editedInfoLabel = ttk.Label(self.editedWinFrame, text = infoString)
        self.editedInfoLabel.pack(padx=5, pady=5)

        #Make and place button
        def doneEditing():
            self.editedWindow.destroy()
            self.listWindow.destroy() #get rid of all the stacked windows
            self.showMatchList() #re-show list (totally hacky instead of updating 'cause I'm lazy)
        self.editedButton = ttk.Button(self.editedWinFrame, text = 'OK', command = doneEditing)
        self.editedButton.pack(side=tk.RIGHT, padx=5, pady=10)

        #Because almost always going to be adding more than one, give focus there
        self.editedWindow.focus_set()
        self.editedButton.focus_set()



#Optionally add some test matches - flag and function to do so
addTestCases = False

def addMatches(app):
    """Adds matches"""
    app.addMatch('P2', 'Wednesday', (9,20), ['246','88','1519'], ['230','69','5968'])
    app.addMatch('P5', 'Wednesday', (10,20), ['230','69','5968'], ['246','88','1519'])
    app.addMatch('4', 'Wednesday', (11,10), ['246','88','1519'], ['230','69','5968'])
    app.addMatch('11', 'Wednesday', (12,00), ['246','88','1519'], ['230','69','5968'])
    app.addMatch('14', 'Wednesday', (23,05), ['230','69','5968'], ['246','88','1519'])
    app.addMatch('18', 'Wednesday', (23,10), ['230','69','5968'], ['246','88','1519'])
    app.addMatch('24', 'Wednesday', (16,30), ['246','88','1519'], ['230','69','5968'])
    app.addMatch('26', 'Wednesday', (17,50), ['246','88','1519'], ['230','69','5968'])

def main():

    root = tk.Tk()
    app = MatchApplication(root)
    app.master.title('Match Timer')
    if addTestCases: addMatches(app)
    app.mainloop()

if __name__ == '__main__':
    main()

