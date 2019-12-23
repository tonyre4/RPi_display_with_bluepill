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
    result = []
    ps = ['USB','ACM','COM']
    
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
        for port in ports:
            for p in ps:
                if p in port:
                    result.append(port)
                    break
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    
    return result

class app:
    
    def __init__(self):
        #constants
        self.imgs = []
        self.sats = []
        self.brs = []

        self.imgcnt = 0
        self.window = Tk()
        self.window.title("AdCharger uploader")
        self.window.geometry('600x600')
        self.gr = np.ones((480,320,3),np.uint8)*127  
        self.grTk = self.cv2totk(self.gr)
        self.drawWidgets()

        self.indImg = -1
        self.indPort = -1

        ##transmission vars
        self.t = 0.00001
        self.dev = ''
        self.baud = 500000
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
        b,g,r = cv2.split(self.img)
        b = np.bitwise_and(b,0xF8)
        g = np.bitwise_and(g,0xFC)
        r = np.bitwise_and(r,0xF8)
        self.img = cv2.merge([b,g,r])

        h,w,_ = self.img.shape
        print(h,w)
        if h<w:
            self.img = np.rot90(self.img)
        self.ish = cv2.resize(self.img,(320,480))
        return self.ish

    def roti(self):
        try:
            self.imgs[self.indImg] = np.rot90(self.imgs[self.indImg],k=2)
            self.loadimgp(self.indImg)
        except:
            pass

    def selectport(self,evt):
        w = evt.widget
        self.indPort = int(w.curselection()[0])
        value = w.get(self.indPort)
        self.dev = value
        self.status.set("Status: Puerto %s seleccionado" % value)
        print(self.dev)

    def loadimg(self):
        file = filedialog.askopenfilename()
        self.status.set("Status: Archivo %s cargado" % file)
        self.imgs.append(self.cvtimg(file))
        self.brs.append(0)
        self.sats.append(0)
        self.listbox.insert(END,file)
        self.indImg = len(self.imgs)-1
        ##self.listbox.focus(self.indImg)
        self.loadimgp()

    def loadimgp(self,index=-1):
        if index<0:
            index = self.indImg

        im = self.imgs[index].copy()
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)
        
        #Saturating
        s = s.astype(np.int32)
        s += self.sats[index]
        np.clip(s,0,255,s)
        s = s.astype(np.uint8)

        #brightness
   #     v = v.astype(np.int32)
   #     v += self.brs[index]
   #     np.clip(v,0,255,v)
   #     v = v.astype(np.uint8)
        
        hsv = cv2.merge([h,s,v])
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        b,g,r = cv2.split(img)
        b = b.astype(np.int32)
        g = g.astype(np.int32)
        r = r.astype(np.int32)

        b += self.brs[index]
        g += self.brs[index]
        r += self.brs[index]

        np.clip(b,0,255,b)
        np.clip(g,0,255,g)
        np.clip(r,0,255,r)

        b = b.astype(np.uint8)
        g = g.astype(np.uint8)
        r = r.astype(np.uint8)

        img = cv2.merge([b,g,r])


        self.img = self.cv2totk(img)  
        self.canvas.create_image(20, 20, anchor=NW, image=self.img) 

    def upload(self):
        self.trans()

    def deli(self):
        self.listbox.delete(self.indImg)
        self.imgs.pop(self.indImg)
        self.sats.pop(self.indImg)
        self.brs.pop(self.indImg)
        
        if len(self.imgs==0):
            self.indImg=-1
            self.setgrayimg()
        else:
            self.indImg=0
            self.loadimgp(0)

    def onselect(self,evt):
        w = evt.widget
        self.indImg = int(w.curselection()[0])
        value = w.get(self.indImg)
        self.loadimgp(self.indImg)
        #print ('You selected item %d: "%s"' % (index, value))

    def updbright(self,evt):
        self.brs[self.indImg] = self.br.get()
        self.loadimgp(self.indImg)
        
    def updsat(self,evt):
        self.sats[self.indImg] = self.sat.get()
        self.loadimgp(self.indImg)


    def updports(self):
        prts = serial_ports()
        print(prts)
        self.ports.delete(0,END)
        
        for p in prts:
            self.ports.insert(END,p)
        
        if len(prts)==1:
            self.setDev(prts[0])
            self.status.set("Puerto %s seleccionado" % prts[0])
            self.setBaud()
            self.connect()

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


        

        self.br = Scale(self.window, from_=-255, to=255,label="Brillo",command=self.updbright)
        self.br.set(0)
        self.sat = Scale(self.window, from_=-255, to=255,label="Saturacion",command=self.updsat)
        self.sat.set(0)

        self.br.grid(column=3,rowspan=2,row=0,sticky=N+S)
        self.sat.grid(column=3,rowspan=2,row=2,sticky=N+S)

        self.status = StringVar(value="Status: Bienvenido!")

        statusbar = Label(self.window, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W)
        statusbar.grid(column=0,columnspan=4,row=9, sticky=W+E)


        self.bar = Progressbar(self.window, length=200)
        self.bar.grid(column=0,columnspan=4,row=10,sticky=W+E)
        
        self.updports()

        #self.window.grid_rowconfigure(5,weight=1)
       
    ######################
    ##Transmission classes
    ######################

    def connect(self):
        self.ser = serial.Serial(self.dev,self.baud)
        self.status.set("Conectando con dispositivo...")
        if not self.ser.isOpen():
            self.ser.open()
            print('com3 is open', self.ser.isOpen())
        self.ser.write('&&&&&&&&&&&&&'.encode())

    def setDev(self,st):
        #if st.find("COM")>-1:
            #st = st.replace("COM","")
            #st = int(st)
        self.dev=st

    def setBaud(self,b=500000):
        self.baud = b

    def trans(self):
        self.status.set("Iniciando transferencia")
        if not self.ser.isOpen():
            self.connect()
        self.fcntr = 0
        self.ser.write('d'.format().encode())
        self.status.set("Borrando imagenes almacenadas")
        for i,im in enumerate(self.imgs):
            self.status.set("Subiendo imagen %d de %d" % (i+1,len(self.imgs)))
            ou = ""
           
            sval  = self.sats[i]
            vval  = self.brs[i]

            hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
            h,s,v = cv2.split(hsv)

            #Saturating 
            s = s.astype(np.int)
            s += sval
            np.clip(s,0,255,s)
            s = s.astype(np.uint8)
            
            ##reducing brightness
            #v = v.astype(np.int)
            #v += vval
            #np.clip(v,0,255,v)
            #v = v.astype(np.uint8)

            hsv = cv2.merge([h,s,v])

            img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            b,g,r = cv2.split(img)
            b = b.astype(np.int32)
            g = g.astype(np.int32)
            r = r.astype(np.int32)
    
            b += self.brs[i]
            g += self.brs[i]
            r += self.brs[i]
    
            np.clip(b,0,255,b)
            np.clip(g,0,255,g)
            np.clip(r,0,255,r)
    
            b = b.astype(np.uint8)
            g = g.astype(np.uint8)
            r = r.astype(np.uint8)
    
            img = cv2.merge([b,g,r])

            
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
    


