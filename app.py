from tkinter.ttk import Progressbar
import serial
import time
from tkinter import *
import tkinter.ttk
from tkinter import filedialog
from PIL import ImageTk,Image
import cv2
import numpy as np
import sys
import glob


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class app:
    
    def __init__(self):
        #constants
        self.imgs = [] 
        self.imgcnt = 0
        self.window = Tk()
        self.window.title("AdCharger uploader")
        self.window.geometry('600x600')
        self.gr = np.ones((480,320,3),np.uint8)*127  
        self.grTk = self.cv2totk(self.gr)
        self.drawWidgets()

        ##transmission vars
        self.t = 0.00001
        self.dev = ''
        self.baud = 115200
        self.height,self.width = 320, 480

        #init app
        self.window.mainloop()

    def setgrayimg(self):
        self.canvas.create_image(20, 20, anchor=NW, image=self.grTk) 

    def cv2totk(self,img):
        b,g,r = cv2.split(img)
        img = cv2.merge((r,g,b))
        im = Image.fromarray(img)
        return ImageTk.PhotoImage(image=im)

    def cvtimg(self,path):
        self.img = cv2.imread(path)
        h,w,_ = self.img.shape
        print(h,w)
        if h<w:
            self.img = np.rot90(self.img)
        self.ish = cv2.resize(self.img,(320,480))
        return self.ish

    def roti(self):
        try:
            index = int(self.listbox.curselection()[0])
            self.imgs[index] = np.rot90(self.imgs[index],k=2)
            self.loadimgp(index)
        except:
            pass

    def selectport(self,evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.dev = value
        self.status.set("Status: Puerto %s seleccionado" % value)
        print(self.dev)

    def loadimg(self):
        file = filedialog.askopenfilename()
        self.status.set("Status: Archivo %s cargado" % file)
        self.imgs.append(self.cvtimg(file))
        self.img = self.cv2totk(self.imgs[-1])  
        self.canvas.create_image(20, 20, anchor=NW, image=self.img) 
        self.listbox.insert(END,file)

    def loadimgp(self,index):
        self.img = self.cv2totk(self.imgs[index])  
        self.canvas.create_image(20, 20, anchor=NW, image=self.img) 

    def upload(self):
        self.trans()

    def deli(self):
        index = int(self.listbox.curselection()[0])
        self.listbox.delete(index)
        self.imgs.pop(index)
        self.setgrayimg()

    def onselect(self,evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.loadimgp(index)
        #print ('You selected item %d: "%s"' % (index, value))

    def updports(self):
        prts = serial_ports()
        #print(prts)
        #print("no hay ni mergas")
        for p in prts:
            self.ports.insert(END,p)
        
        if len(prts)==1:
            self.setDev(prts[0])
            self.status.set("Puerto %s seleccionado" % prts[0])

    def drawWidgets(self):
        ###################
        #first row
        lbl = Label(self.window, text="Vista previa")
        lbl.grid(column=0, row=0)
        
        tkinter.ttk.Separator(self.window, orient=VERTICAL).grid(column=1, row=0, rowspan=2, sticky='ns')
        
        lbl2 = Label(self.window, text="Lista de imagenes")
        lbl2.grid(column=2, row=0)
        
        ####################
        #Second
        self.canvas = Canvas(self.window, width = 320, height = 480)      
        self.canvas.grid(column=0,row=1,rowspan=3)
        self.setgrayimg()
        self.listbox = Listbox(self.window,name='lb')
        self.listbox.grid(column=2,row=1,sticky=W+E)
        self.listbox.bind('<<ListboxSelect>>', self.onselect)
        lbl3 = Label(self.window, text= "Puertos:")
        lbl3.grid(column=2,row=2)
        self.ports = Listbox(self.window,name='ports')
        self.ports.grid(column=2,row=2,sticky=W+E)
        self.ports.bind('<<ListboxSelect>>', self.selectport)


        ####################
        #Third row  	
        btn = Button(self.window, text="Agregar...", command=self.loadimg)
        btn.grid(column=0,row=4)
        btn1 = Button(self.window, text="Quitar", command=self.deli)
        btn1.grid(column=0,row=5)
        btn3 = Button(self.window, text="Rotar", command=self.roti)
        btn3.grid(column=2,row=4)
        btn2 = Button(self.window, text="Subir!", command=self.upload)
        btn2.grid(column=2,row=5)
        
        btn4 = Button(self.window, text="Actualizar puertos", command=self.updports)
        btn4.grid(column=2,row=6)

        self.status = StringVar(value="Status: Bienvenido!")

        statusbar = Label(self.window, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W)
        statusbar.grid(column=0,columnspan=4,row=7, sticky=W+E)


        self.bar = Progressbar(self.window, length=200)
        self.bar.grid(column=0,columnspan=4,row=8,sticky=W+E)
        
        self.updports()

        #self.window.grid_rowconfigure(5,weight=1)
       
    ######################
    ##Transmission classes
    ######################

    def connect(self):
        self.ser = serial.Serial(self.dev,self.baud)
        self.status.set("Conectando con dispositivo...")

    def setDev(self,st):
        self.dev=st

    def setBaud(self,b):
        self.baud = b

    def trans(self):
        self.status.set("Iniciando transferencia")
        self.connect()
        self.fcntr = 0
        self.ser.write('d'.format().encode())
        self.status.set("Borrando imagenes almacenadas")
        for i,im in enumerate(self.imgs):
            self.status.set("Subiendo imagen %d de %d" % (i+1,len(self.imgs)))
            ou = ""
            img = im
            
            #img2 = cv2.resize(img,(self.width,self.height))
            img2 = np.rot90(img,k=1)
            img2 = np.flip(img2,axis=0)
            
            b,g,r = cv2.split(img2)
            
            #b = b*31/255
            #r = r*31/255
            #g = g*63/255
            
            b = np.right_shift(b,3)
            g = np.right_shift(g,2)
            r = np.right_shift(r,3)
            
            rn = np.array((self.width,self.height),np.uint16)
            rn = np.left_shift(r.astype(np.uint16),11)
            gn = np.array((self.width,self.height),np.uint16)
            gn = np.left_shift(g.astype(np.uint16),5)
            bn = np.array((self.width,self.height),np.uint16)
            bn = np.left_shift(b.astype(np.uint16),0)
            
            last = rn+gn+bn
        
        #with open("dec.txt", "w+") as f:
            ou += "&"
            for row in last:
                for col in row:
                    s ="{:0x}".format(col)
                    ss = ''
                    #print(s,end='')
                    for c in s:
                        if c == "a":
                            ss += chr(ord('0')+10)
                            continue
                        if c == "b":
                            ss += chr(ord('0')+11)
                            continue
                        if c == "c":
                            ss += chr(ord('0')+12)
                            continue
                        if c == "d":
                            ss += chr(ord('0')+13)
                            continue
                        if c == "e":
                            ss += chr(ord('0')+14)
                            continue
                        if c == "f":
                            ss += chr(ord('0')+15)
                            continue
                        ss+=c
                    #print(ss)
                    ou += ss[::-1]+','
                    #ou += "{:05d},".format(col)
                    #col = str(col)[::-1]
                    #ou += "{},".format(col)
                    #f.write("{:05d},".format(col))
                ou+= "\n"
                #f.write("\n")

            ou+="z"
        
            #with open("./decimgs/ima{}.txt".format(fcntr), "w+") as f:
            #    f.write(ou)
            #    f.write("z")
            
            self.ser.write('p{}.'.format(self.fcntr).encode())
            #with open("./decimgs/ima{}.txt".format(fcntr), "r") as f:
            #    for l in f:
            #        for c in l:
            for ii,c in enumerate(ou):
                self.ser.write('{}'.format(c).encode())
                if ii%100==0:
                    self.bar['value']= int(ii*100/(len(ou)))
                    self.window.update_idletasks()
            self.fcntr +=1
            
        self.ser.write('!'.format().encode())
        self.ser.close()

        self.bar['value'] = 100
        self.status.set("Imagenes subidas correctamente!")


if __name__ == "__main__":
    a = app()
    


