import tkinter as tk
from tkinter import messagebox
from tkinter import font

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
        self.WDnames_short = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        with open('data.dat', 'b+r') as data:
            self.current_time = int.from_bytes(data.read(), "little")

    def save(self):
        with open('data.dat', 'b+w') as data:
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
        self.time_display = tk.Label(self)
        self.time_display['text'] = self.calendar.datestring()
        self.time_display['pady'] = 10
        self.time_display['padx'] = 2
        self.time_display.grid(columnspan = 7, sticky='W')

        self.left_padding = tk.Label(self, text=' ').grid(row = 1, column = 0)
        self.right_padding = tk.Label(self, text=' ').grid(row = 1, column = 7)

        canvas_width = 280
        boxes_wide = self.calendar.d_w
        boxes_high = (self.calendar.d_M//self.calendar.d_w)+2
        boxes_dim = canvas_width//(boxes_wide)
        vert_offset = 40
        canvas_height = boxes_high*boxes_dim+vert_offset
        self.textids = []
        self.boxids = []
        for i in range(boxes_high*boxes_wide):
            self.textids.append(0)
            self.boxids.append(0)
        self.cboxes = tk.Canvas(self, width = canvas_width, height = canvas_height )
        self.cboxes['bg'] = 'lightgrey'
        self.cboxMY = self.cboxes.create_text(canvas_width*0.5, vert_offset//4+2, text = self.calendar.Mnames[self.calendar.month_of_year()] + ' ' + str(self.calendar.current_year()))
        for i in range(boxes_wide):
            self.cboxes.create_text(boxes_dim*(i+0.5), vert_offset*3//4+2, text = self.calendar.WDnames_short[i])
        for i in range(boxes_high):
            for j in range(boxes_wide):
                self.boxids[i*boxes_wide+j] = self.cboxes.create_rectangle(2+boxes_dim*j,vert_offset+2+boxes_dim*i,boxes_dim*(j+1),vert_offset+boxes_dim*(i+1))
                self.textids[i*boxes_wide+j] = self.cboxes.create_text(boxes_dim*(j+0.5),vert_offset+boxes_dim*(i+0.5),text='test')
        self.cboxes.grid(row = 1, column = 1, columnspan = 6)

        self.add_label = tk.Label(self, text='Add time:').grid(row = 2, column = 1, columnspan = 2, pady=(5,0), sticky = 'SW')
        
        time_label_row = 4
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

##        self.below_label_padding = tk.Label(self, text=' ').grid(row = tlr+1)
        
        self.reset_button = tk.Button(self)
        self.reset_button['text'] = 'RESET'
        self.reset_button['font'] = font.Font(size=6)
        self.reset_button['command'] = self.reset
        self.reset_button['bg'] = 'red'
        self.reset_button['fg'] = 'white'
        self.reset_button.grid(row = tlr+3, column = 3)

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

        self.save = tk.Button(self)
        self.save['width'] = 5
        self.save['text'] = 'Save'
        self.save['bg'] = 'blue'
        self.save['fg'] = 'white'
        self.save['command'] = self.calendar.save
        self.save.grid(row = tlr+3, column = 2)

        self.undo_button = tk.Button(self)
        self.undo_button['width'] = 5
        self.undo_button['text'] = 'Undo'
        self.undo_button['bg'] = 'orange'
        self.undo_button['command'] = self.undo
        self.undo_button.grid(row = tlr+2, column = 1)

        self.redo_button = tk.Button(self)
        self.redo_button['width'] = 5
        self.redo_button['text'] = 'Redo'
        self.redo_button['bg'] = 'orange'
        self.redo_button['fg'] = 'white'
        self.redo_button['command'] = self.redo
        self.redo_button.grid(row = tlr+2, column = 2)

        self.clear = tk.Button(self)
        self.clear['width'] = 5
        self.clear['text'] = 'Clear'
        self.clear['fg'] = 'red'
        self.clear['bg'] = 'lightgrey'
        self.clear['command'] = self.clear_entries
        self.clear.grid(row = tlr+2, column = 5)

        self.quit_button = tk.Button(self)
        self.quit_button['width'] = 5
        self.quit_button['text'] = 'QUIT'
        self.quit_button['bg'] = 'red'
        self.quit_button['fg'] = 'white'
        self.quit_button['command'] = self.quit
        self.quit_button.grid(row = tlr+3, column = 1)

        self.bottom_text = tk.Label(self)
        self.bottom_text['text'] = 'A bad calendar app version 0.2 alpha 11 June 2020'
        self.bottom_text['fg'] = 'lightgrey'
        self.bottom_text.grid(row = tlr+4, columnspan = 7)

    def update_time(self):
        self.time_display['text'] = self.calendar.datestring()
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
        if self.hour_entry.get().isdecimal():
            self.calendar.add_time(-int(self.hour_entry.get()), 'hours')
        if self.day_entry.get().isdecimal():
            self.calendar.add_time(-int(self.day_entry.get()), 'days')
        if self.week_entry.get().isdecimal():
            self.calendar.add_time(-int(self.week_entry.get()), 'weeks')
        if self.month_entry.get().isdecimal():
            self.calendar.add_time(-int(self.month_entry.get()), 'months')
        if self.year_entry.get().isdecimal():
            self.calendar.add_time(-int(self.year_entry.get()), 'years')
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
