import tkinter as tk
from tkinter import messagebox
from tkinter import font
import os.path
from os import path
from shutil import copy

### TODO:
# Add settings menu
# Refactor into main, file manager, the calendar ui, calendar functionality (three files?)

def st(n):
    n1 = n%10
    if n >= 11 and n <= 13:
        append = 'th'
    elif n1 == 1:
        append = 'st'
    elif n1 == 2:
        append = 'nd'
    elif n1 == 3:
        append = 'rd'
    else:
        append = 'th'
    return '%d%s'%(n,append)

class Calendar():

    def __init__(self, mypath='./'):
        #current_time is minutes since midnight, January 1st, 0
        self.mypath = mypath
        self.current_time = 0

        with open(self.mypath+'settings.txt', 'r') as settings:
            settings_lines = settings.readlines()
            self.m_h = int(settings_lines[0])
            self.h_d = int(settings_lines[1])
            self.d_w = int(settings_lines[2])
            self.d_M = int(settings_lines[3])
            self.M_y = int(settings_lines[4])
            self.Mnames = []
            self.WDnames = []
            for i in range(5, 5+self.M_y):
                self.Mnames.append(settings_lines[i][0:len(settings_lines[i])-1])
            for i in range(5+self.M_y, 5+self.M_y+self.d_w):
                self.WDnames.append(settings_lines[i][0:len(settings_lines[i])-1])
        
        with open(self.mypath+'data.dat', 'b+r') as data:
            self.current_time = int.from_bytes(data.read(), "little")

    def save(self):
        with open(self.mypath+'data.dat', 'b+w') as data:
            big = 256
            nob = 1
            while self.current_time > big:
                big = big * 256
                nob = nob + 1
            bytea = self.current_time.to_bytes(nob, "little")
            data.write(bytea)

    def update_settings(self, mh, hd, dw, dm, my, wn, mn):
        with open(self.mypath+'settings.txt', 'w') as settings:
            settings.write(str(mh)+'\n'+str(hd)+'\n'+str(dw)+'\n'+str(dm)+'\n'+str(my)+'\n')
            for n in mn:
                settings.write(n+'\n')
            for n in wn:
                settings.write(n+'\n')

    #add a number of minutes to the calendar
    def add_time(self, to_add, unit='minutes'):
        if to_add < 0:
            if -to_add > self.current_time:
                return False
        if unit == 'minutes':
            self.current_time = self.current_time + to_add
        elif unit == 'hours':
            self.current_time = self.current_time + to_add * self.m_h
        elif unit == 'days':
            self.current_time = self.current_time + to_add * self.m_h * self.h_d
        elif unit == 'weeks':
            self.current_time = self.current_time + to_add * self.m_h * self.h_d * self.d_w
        elif unit == 'months':
            self.current_time = self.current_time + to_add * self.m_h * self.h_d * self.d_M
        elif unit == 'years':
            self.current_time = self.current_time + to_add * self.m_h * self.h_d * self.d_M * self.M_y
        return True

    def reset(self):
        self.current_time = 0

    def hour_of_day(self):
        return (self.current_time%(self.m_h*self.h_d))//self.m_h

    def minute_of_hour(self):
        return self.current_time%(self.m_h)

    def day_of_month(self):
        return (self.current_time//(self.m_h*self.h_d))%self.d_M+1

    def day_of_week(self):
        return (self.current_time//(self.m_h*self.h_d))%self.d_w
        
    def month_of_year(self):
        return (self.current_time//(self.m_h*self.h_d*self.d_M))%self.M_y

    def current_year(self):
        return (self.current_time//(self.m_h*self.h_d*self.d_M*self.M_y))

    def day_of_year(self):
        return (self.current_time//(self.m_h*self.h_d))%(self.d_M*self.M_y)+1

    def first_day_of_week(self):
        dm = self.day_of_month()
        dw = self.day_of_week()
        while dm > 0:
            dw = ( dw - 1 ) % self.d_w
            dm = dm - 1
        return dw

    def datestring(self):
        return "%02d" % self.hour_of_day() + ':' + \
               "%02d" % self.minute_of_hour() + ', ' + \
               self.WDnames[self.day_of_week()] + ', ' + \
               self.Mnames[self.month_of_year()] + ' ' + \
               st(self.day_of_month()) + ', ' + \
               str(self.current_year()) + '; (' + \
               str(self.day_of_year()) + '/' + \
               str(self.d_M*self.M_y) + ')'

class SettingsPopup(tk.Frame):
    done = False
    m_h_value = 60
    h_d_value = 24
    d_w_value = 7
    d_M_value = 30
    M_y_value = 12
    Wnames = []
    Mnames = []
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('Settings')
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.status = tk.Label(self, text='Settings!')
        self.status.grid(row = 0, column = 0, columnspan = 10, sticky='W')
        self.m_h = tk.Label(self, text='1. Minutes per hour: ').grid(row = 1, column = 0, sticky='W')
        self.m_h_entry = tk.Entry(self, width = 10)
        self.m_h_entry.grid(row = 1, column = 1, padx = (20,0))
        self.h_d = tk.Label(self, text='2. Hours per day: ').grid(row = 2, column = 0, sticky='W')
        self.h_d_entry = tk.Entry(self, width = 10)
        self.h_d_entry.grid(row = 2, column = 1, padx = (20,0))
        self.d_w = tk.Label(self, text='3. Days per week: ').grid(row = 3, column = 0, sticky='W')
        self.d_w_entry = tk.Entry(self, width = 10)
        self.d_w_entry.grid(row = 3, column = 1, padx = (20,0))
        self.d_M = tk.Label(self, text='4. Days per month: ').grid(row = 4, column = 0, sticky='W')
        self.d_M_entry = tk.Entry(self, width = 10)
        self.d_M_entry.grid(row = 4, column = 1, padx = (20,0))
        self.M_y = tk.Label(self, text='5. Months per year: ').grid(row = 5, column = 0, sticky='W')
        self.M_y_entry = tk.Entry(self, width = 10)
        self.M_y_entry.grid(row = 5, column = 1, padx = (20,0))
        self.Wnames = tk.Label(self, justify='left', text = '6. Names of the days of the week\n\tPlease separate with ", " (comma, space)')
        self.Wnames.grid(row = 6, columnspan= 10, sticky = 'W')
        self.Wnames_entry = tk.Text(self, height=3)
        self.Wnames_entry.grid(row = 7, columnspan = 10)
        self.Mnames = tk.Label(self, justify='left', text = '7. Names of the months\n\tPlease separate with ", " (comma, space)')
        self.Mnames.grid(row = 8, columnspan=10, sticky='W')
        self.Mnames_entry = tk.Text(self, height=3)
        self.Mnames_entry.grid(row=9, columnspan = 10)
        self.button = tk.Button(self, text='Verify', bg='yellow', command=self.verify)
        self.button.grid(row = 10, column = 0, sticky='W')

    def verify(self):
        self.status['text']='Settings!'
        m_h_value_temp = self.m_h_entry.get()
        h_d_value_temp = self.h_d_entry.get()
        d_w_value_temp = self.d_w_entry.get()
        d_M_value_temp = self.d_M_entry.get()
        M_y_value_temp = self.M_y_entry.get()
        if\
            m_h_value_temp.isdecimal() and\
            h_d_value_temp.isdecimal() and\
            d_w_value_temp.isdecimal() and\
            d_M_value_temp.isdecimal() and\
            M_y_value_temp.isdecimal()\
        :
            m_h_value_temp = int(m_h_value_temp)
            h_d_value_temp = int(h_d_value_temp)
            d_w_value_temp = int(d_w_value_temp)
            d_M_value_temp = int(d_M_value_temp)
            M_y_value_temp = int(M_y_value_temp)
        else:
            self.status['text']='Please enter positive integers in boxes 1-5'
            return
        if\
            m_h_value_temp <= 0 or\
            h_d_value_temp <= 0 or\
            d_w_value_temp <= 0 or\
            d_M_value_temp <= 0 or\
            M_y_value_temp <= 0\
        :
            self.status['text']='Please enter positive integers in boxes 1-5'
            return
        Wnames_value_temp = self.Wnames_entry.get('1.0', tk.END).split(', ')
        Mnames_value_temp = self.Mnames_entry.get('1.0', tk.END).split(', ')
        if not len(Wnames_value_temp) == d_w_value_temp:
            self.status['text']='Number of names in box 6 must match number in box 3'
            return
        if not len(Mnames_value_temp) == M_y_value_temp:
            self.status['text']='Number of names in box 7 must match number in box 5'
            return
        self.m_h_value = m_h_value_temp
        self.h_d_value = h_d_value_temp
        self.d_w_value = d_w_value_temp
        self.d_M_value = d_M_value_temp
        self.M_y_value = M_y_value_temp
        Mnames_value_temp[len(Mnames_value_temp)-1] = Mnames_value_temp[len(Mnames_value_temp)-1][0:len(Mnames_value_temp[len(Mnames_value_temp)-1])-1]
        Wnames_value_temp[len(Wnames_value_temp)-1] = Wnames_value_temp[len(Wnames_value_temp)-1][0:len(Wnames_value_temp[len(Wnames_value_temp)-1])-1]
        self.Mnames = Mnames_value_temp
        self.Wnames = Wnames_value_temp
        print(self.Wnames)
        print(self.Mnames)
        self.button['bg'] = 'blue'
        self.button['fg'] = 'white'
        self.button['command'] = self.finalize
        self.button['text'] = 'Save Settings'
        self.status['text'] = 'Settings verified, saving cannot be undone! Close window to cancel.'

    def finalize(self):
        self.done = True
        self.master.destroy()
        

class Application(tk.Frame):
    calendar = Calendar()
    undo_stack = [[0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0]]
    undo_stack_location = 0

    redo_stack = [[0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0],
                  [0,0,0,0,0,0]]
    redo_stack_location = 0
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('Calendar()')
        self.grid()
        self.create_widgets()
        self.update_time()

    def create_widgets(self):

        ## plain text time display
        self.time_display = tk.Text(self)
        self.time_display['height'] = 1
        self.time_display['width'] = 50
        self.time_display['pady'] = 10
        self.time_display['padx'] = 2
        self.time_display.bind('<Return>', self.open_file)
        self.time_display.insert(1.0, self.calendar.datestring())
        self.time_display.configure(state='disabled')
        self.time_display.grid(row = 1, columnspan = 8)

        #$ global padding on either side
        self.left_padding = tk.Label(self, text=' ').grid(row = 2, column = 0)
        self.right_padding = tk.Label(self, text=' ').grid(row = 2, column = 7)

        #GUI calendar
        self.draw_gui_calendar(destroy='nodestroy')

        ## Add time entry
        self.add_label = tk.Label(self, text='Add time:').grid(row = 3, column = 1, columnspan = 6, pady=(5,0), sticky = 'SW')
        
        time_label_row = 5
        tlr = time_label_row
        time_entry_row = tlr-1
        ter = time_entry_row
        time_label_font = font.Font(size=7, weight='bold')

        self.hour = tk.Label(self, text='HOURS', font=time_label_font).grid(row = tlr, column = 5, sticky='NE')
        self.hour_entry = tk.Entry(self)
        self.hour_entry['width'] = 7
        self.hour_entry.insert(2, '0')
        self.hour_entry.grid(row = ter, column = 5)
        self.hour_entry.bind("<Return>", self.add_time)
        self.hour_entry.bind("<Control-z>", self.undo)
        self.hour_entry.bind("<Control-y>", self.redo)

        self.minute = tk.Label(self, text='MINUTES', font=time_label_font).grid(row = tlr, column = 6, sticky='NE')
        self.minute_entry = tk.Entry(self)
        self.minute_entry['width'] = 7
        self.minute_entry.insert(2, '0')
        self.minute_entry.grid(row = ter, column = 6)
        self.minute_entry.bind("<Return>", self.add_time)
        self.minute_entry.bind("<Control-z>", self.undo)
        self.minute_entry.bind("<Control-y>", self.redo)
        
        self.day = tk.Label(self, text='DAYS', font=time_label_font).grid(row = tlr, column = 4, sticky='NE')
        self.day_entry = tk.Entry(self)
        self.day_entry['width'] = 7
        self.day_entry.insert(2, '0')
        self.day_entry.grid(row = ter, column = 4)
        self.day_entry.bind("<Return>", self.add_time)
        self.day_entry.bind("<Control-z>", self.undo)
        self.day_entry.bind("<Control-y>", self.redo)

        self.week = tk.Label(self, text='WEEKS', font=time_label_font).grid(row = tlr, column = 3, sticky='NE')
        self.week_entry = tk.Entry(self)
        self.week_entry['width'] = 7
        self.week_entry.insert(2, '0')
        self.week_entry.grid(row = ter, column = 3)
        self.week_entry.bind("<Return>", self.add_time)
        self.week_entry.bind("<Control-z>", self.undo)
        self.week_entry.bind("<Control-y>", self.redo)

        self.month = tk.Label(self, text='MONTHS', font=time_label_font).grid(row = tlr, column = 2, sticky='NE')
        self.month_entry = tk.Entry(self)
        self.month_entry['width'] = 7
        self.month_entry.insert(2, '0')
        self.month_entry.grid(row = ter, column = 2)
        self.month_entry.bind("<Return>", self.add_time)
        self.month_entry.bind("<Control-z>", self.undo)
        self.month_entry.bind("<Control-y>", self.redo)

        self.year = tk.Label(self, text='YEARS', font=time_label_font).grid(row = tlr, column = 1, pady=(0,6), sticky='NE')
        self.year_entry = tk.Entry(self)
        self.year_entry['width'] = 7
        self.year_entry.insert(2, '0')
        self.year_entry.grid(row = ter, column = 1)
        self.year_entry.bind("<Return>", self.add_time)
        self.year_entry.bind("<Control-z>", self.undo)
        self.year_entry.bind("<Control-y>", self.redo)

        ## buttons
        
        self.reset_button = tk.Button(self)
        self.reset_button['text'] = 'RESET'
        self.reset_button['font'] = font.Font(size=6)
        self.reset_button['command'] = self.reset
        self.reset_button['bg'] = 'red'
        self.reset_button['fg'] = 'white'
        self.reset_button.grid(row = 0, column = 5, pady=(0,5), sticky = 'E')

        self.quit_button = tk.Button(self)
        self.quit_button['width'] = 5
        self.quit_button['text'] = 'QUIT'
        self.quit_button['bg'] = 'red'
        self.quit_button['fg'] = 'white'
        self.quit_button['command'] = self.quit
        self.quit_button.grid(row = 0, column = 6, pady=(0,5), sticky = 'E')

        self.undo_button = tk.Button(self)
        self.undo_button['width'] = 5
        self.undo_button['text'] = 'Undo'
        self.undo_button['bg'] = 'orange'
        self.undo_button['command'] = self.undo
        self.undo_button.grid(row = 0, column = 2, pady=(0,5), sticky = 'W')

        self.redo_button = tk.Button(self)
        self.redo_button['width'] = 5
        self.redo_button['text'] = 'Redo'
        self.redo_button['bg'] = 'orange'
        self.redo_button['fg'] = 'white'
        self.redo_button['command'] = self.redo
        self.redo_button.grid(row = 0, column = 3, pady=(0,5), sticky = 'W')

        self.file_button = tk.Button(self)
        self.file_button['width'] = 5
        self.file_button['text'] = 'File'
        self.file_button['bg'] = 'tan'
        self.file_button['command'] = self.file_pressed
        self.file_button.grid(row = 0, column = 1, pady=(0,5), sticky = 'W')

        self.open_button = tk.Button(self)
        self.open_button['width'] = 5
        self.open_button['text'] = 'Open'
        self.open_button['bg'] = 'white'
        self.open_button['command'] = self.choose_file
        self.open_button.grid(row = 0, column = 1, pady=(0,5), sticky = 'W')
        self.open_button.grid_remove()
        
        self.cancel = tk.Button(self)
        self.cancel['width'] = 5
        self.cancel['text'] = 'Cancel'
        self.cancel['bg'] = 'red'
        self.cancel['command'] = self.cancel_choose
        self.cancel.grid(row = 0, column = 1, pady=(0,5), sticky = 'W')
        self.cancel.grid_remove()

        self.save_button = tk.Button(self)
        self.save_button['width'] = 5
        self.save_button['text'] = 'Save'
        self.save_button['bg'] = 'blue'
        self.save_button['fg'] = 'white'
        self.save_button['command'] = self.save_calendar
        self.save_button.grid(row = 0, column = 2, pady=(0,5), sticky = 'W')
        self.save_button.grid_remove()

        self.settings_button = tk.Button(self)
        self.settings_button['width'] = 5
        self.settings_button['text'] = 'Settings'
        self.settings_button['bg'] = 'black'
        self.settings_button['fg'] = 'lightgrey'
        self.settings_button['command'] = self.settings
        self.settings_button.grid(row = 0, column = 3, pady = (0,5), sticky = 'W')
        self.settings_button.grid_remove()

        self.subtract = tk.Button(self)
        self.subtract['width'] = 5
        self.subtract['text'] = 'Minus'
        self.subtract['bg'] = 'darkgrey'
        self.subtract['fg'] = 'cyan'
        self.subtract['command'] = self.minus_time
        self.subtract.grid(row = tlr+3, column = 6)

        self.add = tk.Button(self)
        self.add['width'] = 5
        self.add['text'] = 'Plus'
        self.add['bg'] = 'darkgrey'
        self.add['fg'] = 'yellow'
        self.add['command'] = self.add_time
        self.add.grid(row = tlr+2, column = 6)

        self.clear = tk.Button(self)
        self.clear['width'] = 5
        self.clear['text'] = 'Clear'
        self.clear['fg'] = 'red'
        self.clear['bg'] = 'lightgrey'
        self.clear['command'] = self.clear_entries
        self.clear.grid(row = tlr+2, column = 5)
        
        ## bottom text
        self.bottom_text = tk.Label(self)
        self.bottom_text['text'] = 'A bad calendar app version 0.3 alpha 15 June 2020'
        self.bottom_text['fg'] = 'lightgrey'
        self.bottom_text.grid(row = tlr+4, columnspan = 7)

        self.cover = tk.Canvas(self, width = 420, height = 800)
        self.cover.create_rectangle(0,0, 420, 800)
        self.cover.grid(row=0, column=0, rowspan=10, columnspan=10)
        self.cover.grid_forget()

    def settings(self):
        popuproot = tk.Tk()
        popup = SettingsPopup(popuproot)
        popup.mainloop()

        ### TODO: this just doesn't work
        self.cover.grid()
        while not popup.done:
            continue
        self.cover.grid_forget()
        
        self.calendar.update_settings(popup.m_h_value,\
                                      popup.h_d_value,\
                                      popup.d_w_value,\
                                      popup.d_M_value,\
                                      popup.M_y_value,\
                                      popup.Wnames,\
                                      popup.Mnames)
        ### TODO: redraw ###
        self.draw_gui_calendar()

    def draw_gui_calendar(self, destroy='destroy'):
        if destroy == 'destroy':
            self.cboxes.destroy()
        canvas_width = 400
        boxes_wide = self.calendar.d_w
        boxes_high = (self.calendar.d_M//self.calendar.d_w)+2
        boxes_dim = canvas_width//(boxes_wide)
        vert_offset = 54
        canvas_height = boxes_high*boxes_dim+vert_offset
        self.textids = []
        self.boxids = []
        for i in range(boxes_high*boxes_wide):
            self.textids.append(0)
            self.boxids.append(0)
        self.cboxes = tk.Canvas(self, width = canvas_width, height = canvas_height )
        self.cboxes['bg'] = 'lightgrey'
        self.cboxMY = self.cboxes.create_text(canvas_width*0.5, vert_offset//2-8, text = self.calendar.Mnames[self.calendar.month_of_year()] + ' ' + str(self.calendar.current_year()), font=font.Font(size=16))
        for i in range(boxes_wide):
            self.cboxes.create_text(boxes_dim*(i+0.5), vert_offset-8, text = self.calendar.WDnames[i][0:3])
        for i in range(boxes_high):
            for j in range(boxes_wide):
                self.boxids[i*boxes_wide+j] = self.cboxes.create_rectangle(2+boxes_dim*j,vert_offset+2+boxes_dim*i,boxes_dim*(j+1),vert_offset+boxes_dim*(i+1))
                self.textids[i*boxes_wide+j] = self.cboxes.create_text(boxes_dim*(j+0.5),vert_offset+boxes_dim*(i+0.5),text='test')
        self.cboxes.grid(row = 2, column = 1, columnspan = 6)

    def save_calendar(self):
        self.calendar.save()
        self.cancel_choose()

    def file_pressed(self):
        self.save_button.grid()
        self.settings_button.grid()
        self.open_button.grid()

    def choose_file(self):
        self.cancel.grid()
        self.time_display.configure(state='normal')
        self.time_display.delete(1.0, tk.END)
        self.time_display.insert(1.0, 'Type file name here then press "Enter"')
        self.time_display.focus_set()
        self.time_display.tag_add(tk.SEL, '1.0', tk.END)

    def cancel_choose(self):
        self.open_button.grid_remove()
        self.update_time()
        self.cancel.grid_remove()
        self.save_button.grid_remove()
        self.settings_button.grid_remove()

    def open_file(self, event=None):
        # get contents of text box as a string
        user_path = self.time_display.get('1.0',tk.END)
        user_path = user_path[0:len(user_path)-1]
        # check that string is not a disallowed string (default, Include, lib2to3, tcl, tk)
        if \
           user_path == 'default' or\
           user_path == 'Include' or\
           user_path == 'lib2to3' or\
           user_path == 'tcl' or\
           user_path == 'tk':
            self.cancel_choose()
            return
        # warn about not saving
        msg = tk.messagebox.askquestion('Open New File','Are you sure you want to open?\nThis will not save the calendar state.',icon='warning')
        if msg == 'yes':
            # if directory does not exist, create directory and copy default files into new directory
            if not path.exists(user_path):
                os.mkdir(user_path)
                copy('default\\data.dat',user_path)
                copy('default\\settings.txt',user_path)
            # set self.calendar to a new calendar
            self.calendar = Calendar(mypath=user_path+'\\')
            self.master.title(user_path)
            ### TODO: REDRAW ###
            self.draw_gui_calendar()
        # exit this state
        self.cancel_choose()

    def update_time(self):
        self.time_display.configure(state='normal')
        self.time_display.delete(1.0, tk.END)
        self.time_display.insert(1.0, self.calendar.datestring())
        self.time_display.configure(state='disabled')
        self.cboxes.itemconfigure(self.cboxMY, text = self.calendar.Mnames[self.calendar.month_of_year()] + ' ' + str(self.calendar.current_year()))
        offset = ( self.calendar.first_day_of_week() + 1 ) % 7
        for i in range(((self.calendar.d_M//self.calendar.d_w)+2)*self.calendar.d_w):
            self.cboxes.itemconfigure(self.boxids[i], fill = 'lightgrey')
            if i < offset or i > self.calendar.d_M+offset-1:
                self.cboxes.itemconfigure(self.textids[i], text = ' ')
            else:
                self.cboxes.itemconfigure(self.textids[i], text = str(i-offset+1))
        self.cboxes.itemconfigure(self.boxids[self.calendar.day_of_month()+offset-1], fill = 'pink')

    def add_time(self, event = None):
        if self.minute_entry.get().isdecimal():
            self.calendar.add_time(int(self.minute_entry.get()), 'minutes')
        else:
            self.minute_entry.delete(0, 'end')
            self.minute_entry.insert(2, '0')
        if self.hour_entry.get().isdecimal():
            self.calendar.add_time(int(self.hour_entry.get()), 'hours')
        else:
            self.hour_entry.delete(0, 'end')
            self.hour_entry.insert(2, '0')
        if self.day_entry.get().isdecimal():
            self.calendar.add_time(int(self.day_entry.get()), 'days')
        else:
            self.day_entry.delete(0, 'end')
            self.day_entry.insert(2, '0')
        if self.week_entry.get().isdecimal():
            self.calendar.add_time(int(self.week_entry.get()), 'weeks')
        else:
            self.week_entry.delete(0, 'end')
            self.week_entry.insert(2, '0')
        if self.month_entry.get().isdecimal():
            self.calendar.add_time(int(self.month_entry.get()), 'months')
        else:
            self.month_entry.delete(0, 'end')
            self.month_entry.insert(2, '0')
        if self.year_entry.get().isdecimal():
            self.calendar.add_time(int(self.year_entry.get()), 'years')
        else:
            self.year_entry.delete(0, 'end')
            self.year_entry.insert(2, '0')
        self.update_time()
        self.push_to_undo()
        self.clear_entries()

    def minus_time(self, event = None):
        if self.minute_entry.get().isdecimal():
            self.calendar.add_time(-int(self.minute_entry.get()), 'minutes')
        else:
            self.minute_entry.delete(0, 'end')
            self.minute_entry.insert(2, '0')
        if self.hour_entry.get().isdecimal():
            self.calendar.add_time(-int(self.hour_entry.get()), 'hours')
        else:
            self.hour_entry.delete(0, 'end')
            self.hour_entry.insert(2, '0')
        if self.day_entry.get().isdecimal():
            self.calendar.add_time(-int(self.day_entry.get()), 'days')
        else:
            self.day_entry.delete(0, 'end')
            self.day_entry.insert(2, '0')
        if self.week_entry.get().isdecimal():
            self.calendar.add_time(-int(self.week_entry.get()), 'weeks')
        else:
            self.week_entry.delete(0, 'end')
            self.week_entry.insert(2, '0')
        if self.month_entry.get().isdecimal():
            self.calendar.add_time(-int(self.month_entry.get()), 'months')
        else:
            self.month_entry.delete(0, 'end')
            self.month_entry.insert(2, '0')
        if self.year_entry.get().isdecimal():
            self.calendar.add_time(-int(self.year_entry.get()), 'years')
        else:
            self.year_entry.delete(0, 'end')
            self.year_entry.insert(2, '0')
        self.update_time()
        self.push_to_undo('-')
        self.clear_entries()

    def clear_entries(self):
        self.minute_entry.delete(0, 'end')
        self.hour_entry.delete(0, 'end')
        self.day_entry.delete(0, 'end')
        self.week_entry.delete(0, 'end')
        self.month_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')
        self.minute_entry.insert(2, '0')
        self.hour_entry.insert(2, '0')
        self.day_entry.insert(2, '0')
        self.week_entry.insert(2, '0')
        self.month_entry.insert(2, '0')
        self.year_entry.insert(2, '0')
        
    def push_to_undo(self, sign='+'):
        s = 1
        if sign == '-':
            s = -1
        self.undo_stack[self.undo_stack_location][0] = s*int(self.year_entry.get())
        self.undo_stack[self.undo_stack_location][1] = s*int(self.month_entry.get())
        self.undo_stack[self.undo_stack_location][2] = s*int(self.week_entry.get())
        self.undo_stack[self.undo_stack_location][3] = s*int(self.day_entry.get())
        self.undo_stack[self.undo_stack_location][4] = s*int(self.hour_entry.get())
        self.undo_stack[self.undo_stack_location][5] = s*int(self.minute_entry.get())
        self.undo_stack_location = ( self.undo_stack_location + 1 ) % 10

    def undo(self, event=None):
        self.undo_stack_location = ( self.undo_stack_location - 1 ) % 10
        self.calendar.add_time(-self.undo_stack[self.undo_stack_location][0], 'years')
        self.calendar.add_time(-self.undo_stack[self.undo_stack_location][1], 'months')
        self.calendar.add_time(-self.undo_stack[self.undo_stack_location][2], 'weeks')
        self.calendar.add_time(-self.undo_stack[self.undo_stack_location][3], 'days')
        self.calendar.add_time(-self.undo_stack[self.undo_stack_location][4], 'hours')  
        self.calendar.add_time(-self.undo_stack[self.undo_stack_location][5], 'minutes')
        for i in range(6):
            self.redo_stack[self.redo_stack_location][i] = self.undo_stack[self.undo_stack_location][i]
            self.undo_stack[self.undo_stack_location][i] = 0
        self.redo_stack_location = ( self.redo_stack_location + 1 ) % 10
        self.update_time()

    def redo(self, event=None):
        self.redo_stack_location = ( self.redo_stack_location - 1 ) % 10
        self.calendar.add_time(self.redo_stack[self.redo_stack_location][0], 'years')
        self.calendar.add_time(self.redo_stack[self.redo_stack_location][1], 'months')
        self.calendar.add_time(self.redo_stack[self.redo_stack_location][2], 'weeks')
        self.calendar.add_time(self.redo_stack[self.redo_stack_location][3], 'days')
        self.calendar.add_time(self.redo_stack[self.redo_stack_location][4], 'hours')  
        self.calendar.add_time(self.redo_stack[self.redo_stack_location][5], 'minutes')
        for i in range(6):
            self.undo_stack[self.undo_stack_location][i] = self.redo_stack[self.redo_stack_location][i]
            self.redo_stack[self.redo_stack_location][i] = 0
        self.undo_stack_location = ( self.undo_stack_location + 1 ) % 10
        self.update_time()

    def reset(self):
        msg = tk.messagebox.askquestion('RESET','Are you sure you want to reset the calendar?\nThis will reset the calendar to 0 time.\nTHIS CANNOT BE UNDONE.',icon='warning')
        if msg == 'yes':
            self.calendar.reset()
            self.update_time()
        else:
            tk.messagebox.showinfo('Reset cancelled','The calendar was NOT reset')

    def quit(self):
        msg = tk.messagebox.askquestion('QUIT','Are you sure you want to exit?\nThis will not save the calendar state.',icon='warning')
        if msg == 'yes':
            self.master.destroy()
        

root = tk.Tk()
app = Application(master=root)
app.mainloop()
