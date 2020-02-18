from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import numpy as np
from math import log
import geosoft.gxpy.gx as gx
import geosoft.gxpy.gdb as gxdb
gsc=gx.GXpy()

class Root(Tk):
    def __init__(self):
        super (Root, self).__init__()
        self.minsize(400,400)
        self.title('Time decay constant')
               
        self.button=ttk.Button(self, text='Open GDB file', command=self.openDB).pack()
        self.label=ttk.Label(self,text='__GDB file__')
        self.label.pack()
        self.buttonrd=ttk.Button(self,text='Read GDB file', command=self.read_DB)
        self.buttonrd.pack()
        self.EM_channel=StringVar()
        self.comboxchan=ttk.Combobox(self, postcommand=self.InitUI, textvariable=self.EM_channel)
        self.comboxchan.pack()
        self.labelnumchannel=ttk.Label(self, text='Number of channels used for calculation :').pack()
        self.numberusedchannel=IntVar()
        self.boxnumber=ttk.Entry(self, textvariable=self.numberusedchannel)
        self.boxnumber.pack()
        
        self.buttontime=ttk.Button(self, text='Open TEM file', command=self.openTEM).pack()
        self.labeltime=ttk.Label(self, text='__TEM file__')
        self.labeltime.pack()
        self.labelnoise=ttk.Label(self, text='Noise level :').pack()

        self.nl=DoubleVar()
        self.boxnoise=ttk.Entry(self, textvariable=self.nl)
        self.boxnoise.pack()
        
        self.labeltauname=ttk.Label(self, text='TAU channel name :').pack()

        self.Tau_name=StringVar()
        self.boxTau_name=ttk.Entry(self, textvariable=self.Tau_name)
        self.boxTau_name.pack()
        self.labelbottom=ttk.Label(self, text=' ').pack()

        self.buttonRun=ttk.Button(self, text='TAU calculation', command=self.run_Tau)
        self.buttonRun.pack()
        self.progress_bar=ttk.Progressbar(self,orient='horizontal',length=200, mode='determinate')
        self.progress_bar.pack()
        
    def openDB(self):
        self.root1=Tk()
        self.root1.withdraw()
        self.db_file_path=filedialog.askopenfilename(filetypes=[("Geosoft database",".gdb")])
        self.label.config(text=self.db_file_path)
        
    def read_DB(self):
        with gxdb.Geosoft_gdb.open(self.db_file_path) as self.gdb:
            self.channels=list(self.gdb.list_channels())

    def InitUI(self):
        self.comboxchan['values']=self.channels
        
    def openTEM (self):
        self.root2=Tk()
        self.root2.withdraw()
        self.time_file_path=filedialog.askopenfilename(filetypes=[("Comma separated varlues",".csv")])
        self.labeltime.config(text=self.time_file_path)  
    
    def run_Tau(self):
        self.EM_array=self.EM_channel.get()
        self.noise_level=self.nl.get()
        self.number_of_used_channels=self.numberusedchannel.get()
        self.Tau_channel_name=self.Tau_name.get()
        self.Time_gates=np.genfromtxt(self.time_file_path, delimiter=',')
        
        with gxdb.Geosoft_gdb.open(self.db_file_path) as self.gdb:
            self.new_Tau_channel= gxdb.Channel.new (self.gdb,self.Tau_channel_name, replace=True)
            self.number_of_arrays=self.gdb.channel_width(self.EM_array)
            self.number_of_lines=len(self.gdb.list_lines())
            self.progress_bar['maximum']=int(self.number_of_lines)
            self.linecount=0
            for self.line in self.gdb.list_lines():
                self.linecount+=1
                self.progress_bar['value']= self.linecount
                self.progress_bar.update()
                print (self.line)
                self.data, self.channels_read, self.fid= self.gdb.read_line(self.line,channels=self.EM_array)
                self.number_of_rows=self.data.shape[0]
                self.Tau_Fid=np.zeros((self.number_of_rows,1))

                for self.row in range (0,self.number_of_rows):
                    if self.data[self.row,self.number_of_used_channels-1] >self.noise_level:
                    
                        for self.col in range (self.number_of_arrays-1,self.number_of_used_channels-2,-1):
                                                        
                            if self.data[self.row, self.col]< self.noise_level: # check if the secondary field is greater than the assigned noise level
                                continue # if it is less than noise level, take the second latest channel, and ...
                            else:          # if it is greater than the noise level, take the current column as the latest    
                                self.last_col=self.col+1
                                self.first_col=self.col-(self.number_of_used_channels-1)  # and move x window backward to take earliest channel for Tau calculation 
                                
                                if self.col == self.number_of_arrays-1: # special case if the last time gate should be included
                                    self.sliced_data=self.data[self.row,self.first_col:]
                                    self.Time_gate_used= self.Time_gates [self.first_col:]
                                else:
                                    self.sliced_data=self.data[self.row,self.first_col:self.last_col]
                                    self.Time_gate_used= self.Time_gates [self.first_col:self.last_col] 
    
                            break
                
                        
                        if np.any (self.sliced_data<self.noise_level): # if any one the selected channels are less than noise level, disregard the record
                            pass
                            #break # and go to the next row
                        else: 
                            
                            self.SF_used=np.log10(self.sliced_data) #slice the secondary data for Tau calculation

                            self.Time_gate_alg = np.vstack([self.Time_gate_used, np.ones(len(self.Time_gate_used))]).T # should be genrated as required by linalg.lstsq
                            self.m, self.c=np.linalg.lstsq(self.Time_gate_alg, self.SF_used)[0] # taking slope and intercept from regression for time gates and secondary field data  
                        
                            self.Tau_Fid[self.row,0]=-1/self.m # converts the slope to the time constant
                        
                    else:
                        continue
                    
                self.gdb.write_channel(self.line, self.new_Tau_channel, self.Tau_Fid, self.fid)

root=Root()
root.mainloop()