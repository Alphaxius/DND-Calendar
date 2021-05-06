import tkinter as tk
from tkinter import messagebox
import math

class Calendar():

    def __init__(self):
        #current_time is minutes since midnight, January 1st, 0
        self.current_time = 0

        self.m_h = 60
        self.h_d = 24
        self.d_w = 7
        self.d_M = 30
        self.M_y = 12
        self.Mnames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        self.WDnames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        with open('data', 'b+r') as data:
            self.current_time = int.from_bytes(data.read(), "little")

    def save(self):
        with open('data', 'b+w') as data:
            big = 256
            nob = 1
            while self.current_time > big:
                big = big * 256
                nob = nob + 1
            bytea = self.current_time.to_bytes(nob, "little")
            data.write(bytea)

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
        return math.floor((self.current_time%(self.m_h*self.h_d))/self.m_h)

    def minute_of_hour(self):
        return self.current_time%(self.m_h)

    def day_of_month(self):
        return math.floor(self.current_time/(self.m_h*self.h_d))%self.d_M+1

    def day_of_week(self):
        return math.floor(self.current_time/(self.m_h*self.h_d))%self.d_w
        
    def month_of_year(self):
        return math.floor(self.current_time/(self.m_h*self.h_d*self.d_M))%self.M_y

    def current_year(self):
        return math.floor(self.current_time/(self.m_h*self.h_d*self.d_M*self.M_y))

    def day_of_year(self):
        return math.floor(self.current_time/(self.m_h*self.h_d))%(self.d_M*self.M_y)+1

    def datestring(self):
        return str(self.hour_of_day()) + ':' + \
               str(self.minute_of_hour()) + ', ' + \
               self.WDnames[self.day_of_week()] + ', ' + \
               str(self.day_of_month()) + ' ' + \
               self.Mnames[self.month_of_year()] + ' ' + \
               str(self.current_year()) + '; (' + \
               str(self.day_of_year()) + '/' + \
               str(self.d_M*self.M_y) + ')'

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
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.time_display = tk.Label(self)
        self.time_display['text'] = self.calendar.datestring()
        self.time_display['pady'] = 10
        self.time_display['padx'] = 2
        self.time_display.grid(columnspan = 7, sticky='W')

        self.reset_button = tk.Button(self)
        self.reset_button['text'] = ' RESET '
        self.reset_button['command'] = self.reset
        self.reset_button['bg'] = 'red'
        self.reset_button['fg'] = 'black'
        self.reset_button.grid(row = 0, column = 5, columnspan = 2, sticky='E')

        self.left_padding = tk.Label(self, text=' ').grid(row = 1, column = 0)
        self.right_padding = tk.Label(self, text=' ').grid(row = 1, column = 7)

        self.hour = tk.Label(self, text='hours').grid(row = 2, column = 5)
        self.hour_entry = tk.Entry(self)
        self.hour_entry['width'] = 7
        self.hour_entry.insert(2, '0')
        self.hour_entry.grid(row = 1, column = 5)
        self.hour_entry.bind("<Return>", self.add_time)
        self.hour_entry.bind("<Control-z>", self.undo)
        self.hour_entry.bind("<Control-y>", self.redo)

        self.minute = tk.Label(self, text='minutes').grid(row = 2, column = 6)
        self.minute_entry = tk.Entry(self)
        self.minute_entry['width'] = 7
        self.minute_entry.insert(2, '0')
        self.minute_entry.grid(row = 1, column = 6)
        self.minute_entry.bind("<Return>", self.add_time)
        self.minute_entry.bind("<Control-z>", self.undo)
        self.minute_entry.bind("<Control-y>", self.redo)
        
        self.day = tk.Label(self, text='days').grid(row = 2, column = 4)
        self.day_entry = tk.Entry(self)
        self.day_entry['width'] = 7
        self.day_entry.insert(2, '0')
        self.day_entry.grid(row = 1, column = 4)
        self.day_entry.bind("<Return>", self.add_time)
        self.day_entry.bind("<Control-z>", self.undo)
        self.day_entry.bind("<Control-y>", self.redo)

        self.week = tk.Label(self, text='weeks').grid(row = 2, column = 3)
        self.week_entry = tk.Entry(self)
        self.week_entry['width'] = 7
        self.week_entry.insert(2, '0')
        self.week_entry.grid(row = 1, column = 3)
        self.week_entry.bind("<Return>", self.add_time)
        self.week_entry.bind("<Control-z>", self.undo)
        self.week_entry.bind("<Control-y>", self.redo)

        self.month = tk.Label(self, text='months').grid(row = 2, column = 2)
        self.month_entry = tk.Entry(self)
        self.month_entry['width'] = 7
        self.month_entry.insert(2, '0')
        self.month_entry.grid(row = 1, column = 2)
        self.month_entry.bind("<Return>", self.add_time)
        self.month_entry.bind("<Control-z>", self.undo)
        self.month_entry.bind("<Control-y>", self.redo)

        self.year = tk.Label(self, text='years').grid(row = 2, column = 1)
        self.year_entry = tk.Entry(self)
        self.year_entry['width'] = 7
        self.year_entry.insert(2, '0')
        self.year_entry.grid(row = 1, column = 1)
        self.year_entry.bind("<Return>", self.add_time)
        self.year_entry.bind("<Control-z>", self.undo)
        self.year_entry.bind("<Control-y>", self.redo)

        self.add = tk.Button(self)
        self.add['text'] = 'Add'
        self.add['bg'] = 'lightgrey'
        self.add['fg'] = 'blue'
        self.add['command'] = self.add_time
        self.add.grid(row = 4, column = 1)

        self.save = tk.Button(self)
        self.save['text'] = 'Save'
        self.save['bg'] = 'blue'
        self.save['fg'] = 'white'
        self.save['command'] = self.calendar.save
        self.save.grid(row = 4, column = 5)

        self.undo_button = tk.Button(self)
        self.undo_button['text'] = 'Undo'
        self.undo_button['bg'] = 'orange'
        self.undo_button['command'] = self.undo
        self.undo_button.grid(row = 4, column = 3)

        self.redo_button = tk.Button(self)
        self.redo_button['text'] = 'Redo'
        self.redo_button['bg'] = 'orange'
        self.redo_button['fg'] = 'white'
        self.redo_button['command'] = self.redo
        self.redo_button.grid(row = 4, column = 4)

        self.clear = tk.Button(self)
        self.clear['text'] = 'Clear'
        self.clear['fg'] = 'red'
        self.clear['bg'] = 'lightgrey'
        self.clear['command'] = self.clear_entries
        self.clear.grid(row = 4, column = 2)

        self.quit_button = tk.Button(self)
        self.quit_button['text'] = 'QUIT'
        self.quit_button['bg'] = 'red'
        self.quit_button['fg'] = 'white'
        self.quit_button['command'] = self.quit
        self.quit_button.grid(row = 4, column = 6)

        self.bottom_text = tk.Label(self)
        self.bottom_text['text'] = 'A bad calendar app version alpha 3 June 2020'
        self.bottom_text['fg'] = 'lightgrey'
        self.bottom_text.grid(row = 5, columnspan = 7)

    def update_time(self):
        self.time_display['text'] = self.calendar.datestring()

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
        
    def push_to_undo(self):
        self.undo_stack[self.undo_stack_location][0] = int(self.year_entry.get())
        self.undo_stack[self.undo_stack_location][1] = int(self.month_entry.get())
        self.undo_stack[self.undo_stack_location][2] = int(self.week_entry.get())
        self.undo_stack[self.undo_stack_location][3] = int(self.day_entry.get())
        self.undo_stack[self.undo_stack_location][4] = int(self.hour_entry.get())
        self.undo_stack[self.undo_stack_location][5] = int(self.minute_entry.get())
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
