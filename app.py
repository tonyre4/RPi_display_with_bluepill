from tkinter.ttk import Progressbar
import imutils
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


timestr = ["1","3","5","7","10","13","15"]
times = [1000,3000,5000,7000,10000,13000,15000]

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

############################################
class IMG:
    def __init__(s,path):
        s.path = path
        s.time = 2 #index
        s.imread()

    def imread(s):
        s.img= cv2.imread(s.path)
        h,w,_ = s.img.shape
        if h<w:
            s.img = np.rot90(s.img)
        s.img = cv2.resize(s.img,(320,480))

        s.orient = 0
        
        b,g,r = cv2.split(s.img)
        b = np.bitwise_and(b,0xF8)
        g = np.bitwise_and(g,0xFC)
        r = np.bitwise_and(r,0xF8)
        s.orig = cv2.merge([b,g,r])  #original image (no changes)
        s.img = s.orig.copy() #image no processing but rotated
        s.shimg = s.orig.copy() #image to show
        s.sat = 0
        s.bright = 0

    def rotate(s):
        if s.orient == 0:
            s.img = imutils.rotate(s.orig, 90)
            s.img = cv2.resize(s.img,(320,480))
            
        elif s.orient == 1:
            s.img = np.rot90(s.orig,2)

        elif s.orient == 2:
            s.img = imutils.rotate(s.orig, 270)
            s.img = cv2.resize(s.img,(320,480))
        elif s.orient == 3:
            s.img = s.orig
            s.orient = -1

        s.orient += 1
        print(s.orient)
        s.procIMG()


    def getIMG(s):
        s.procIMG()
        return s.shimg

    def procIMG(s):
        im = s.img
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        h,ss,v = cv2.split(hsv)
        
        #Saturating
        ss = ss.astype(np.int32)
        ss += s.sat
        np.clip(ss,0,255,ss)
        ss = ss.astype(np.uint8)

        #brightness
   #     v = v.astype(np.int32)
   #     v += self.brs[index]
   #     np.clip(v,0,255,v)
   #     v = v.astype(np.uint8)
        
        hsv = cv2.merge([h,ss,v])
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        b,g,r = cv2.split(img)
        b = b.astype(np.int32)
        g = g.astype(np.int32)
        r = r.astype(np.int32)

        b += s.bright
        g += s.bright
        r += s.bright

        np.clip(b,0,255,b)
        np.clip(g,0,255,g)
        np.clip(r,0,255,r)

        b = b.astype(np.uint8)
        g = g.astype(np.uint8)
        r = r.astype(np.uint8)

        s.shimg = cv2.merge([b,g,r])
###################################################


class app:
    
    def __init__(self):
        #constants
        self.imgs = []

        self.imgcnt = 0
        self.window = Tk()
        self.window.title("AdCharger uploader")
        self.window.resizable(width=False, height=False)

        #self.window.geometry('600x600')
        self.window.grid_propagate(1)
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

    def roti(self):
        self.imgs[self.indImg].rotate()
        self.refreshimg(self.indImg)

    def selectport(self,evt):
        w = evt.widget
        self.indPort = int(w.curselection()[0])
        value = w.get(self.indPort)
        self.dev = value
        self.status.set("Status: Puerto %s seleccionado" % value)
        print(self.dev)
        self.connect()

    def loadimg(self):
        f = filedialog.askopenfilenames(title="Elige las imagenes a cargar" ,filetypes=[("Archivos de imagen", ".jpg .png .jpeg"),("Cualquier tipo","*")])
        f = list(f)
        for file in f:
            self.status.set("Status: Archivo %s cargado" % file)
            self.imgs.append(IMG(file))
            self.listbox.insert(END,file)
            self.indImg = len(self.imgs)-1
            self.listbox.selection_set(self.indImg)
            self.combo.current(2)
            self.refreshimg()

    def refreshimg(self,index=-1):
        if index<0:
            index = self.indImg
        img = self.imgs[index].getIMG()
        #cv2.imshow("a",img)
        #cv2.waitKey(0)
        #print(img.shape)
        self.tkimg = self.cv2totk(img)
        self.canvas.create_image(0, 0, anchor=NW, image=self.tkimg) 
        #self.canvas.itemconfig(self.canvas,image = tkimg)

    def upload(self):
        self.trans()

    def deli(self):
        self.listbox.delete(self.indImg)
        self.imgs.pop(self.indImg)
        
        if len(self.imgs==0):
            self.indImg=-1
            self.setgrayimg()
        else:
            self.indImg=0
            self.refreshimg(0)

    def onselect(self,evt):
        w = evt.widget
        self.indImg = int(w.curselection()[0])
        value = w.get(self.indImg)
        self.refreshimg(self.indImg)
        self.br.set(self.imgs[self.indImg].bright)
        self.sat.set(self.imgs[self.indImg].sat)
        self.combo.current(self.imgs[self.indImg].time)
        #print ('You selected item %d: "%s"' % (index, value))

    def updbright(self,evt):
        self.imgs[self.indImg].bright = self.br.get()
        self.refreshimg(self.indImg)
        
    def updsat(self,evt):
        self.imgs[self.indImg].sat = self.sat.get()
        self.refreshimg(self.indImg)

    def upsel(self):
        if self.indImg==0:
            return
        else:
            nwind = self.indImg-1
            self.imgs.insert(nwind, self.imgs.pop(self.indImg))
            path = self.listbox.get(self.indImg)
            self.listbox.delete(self.indImg)
            self.listbox.insert(nwind,path)
            self.indImg-=1
            self.listbox.selection_set(self.indImg)
            self.refreshimg()


    def dwsel(self):
        if self.indImg==len(self.imgs)-1:
            return
        else:
            nwind = self.indImg+1
            self.imgs.insert(nwind, self.imgs.pop(self.indImg))
            path = self.listbox.get(self.indImg)
            self.listbox.delete(self.indImg)
            self.listbox.insert(nwind,path)
            self.indImg+=1
            self.listbox.selection_set(self.indImg)
            self.refreshimg()


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
            #self.connect()

    def updtime(self,evt):
        if self.indImg>=0:
            self.imgs[self.indImg].time = self.combo.current()
            print(times[self.imgs[self.indImg].time])

    def drawWidgets(self):
        ######################
        #Separators


        ###################
        #first row
        Label(self.window, text="Vista previa").grid(column=0, row=0)
        
        #tkinter.ttk.Separator(self.window, orient=VERTICAL).grid(column=1, row=0, rowspan=5, sticky='ns')
        
        Label(self.window, text="Lista de imagenes").grid(column=2, row=0)
        Label(self.window, text="Ajuste de imagen").grid(column=4, row=0)
        
        ####################
        #Second
        self.canvas = Canvas(self.window, width = 320, height = 480)      
        self.canvas.grid(column=0,row=1,rowspan=4)
        self.setgrayimg()

        self.listbox = Listbox(self.window,name='lb')
        self.listbox.grid(column=2,row=1,columnspan=2,sticky=W+E)
        self.listbox.bind('<<ListboxSelect>>', self.onselect)

        btnup = Button(self.window, text="Subir", command=self.upsel)
        btnup.grid(column=2,row=2)
        btndw = Button(self.window, text="Bajar", command=self.dwsel)
        btndw.grid(column=3,row=2)

        
        Label(self.window, text= "Puertos:").grid(column=2,row=3)
        Label(self.window, text= "Tiempo (s):").grid(column=3,row=3)

        self.combo = ttk.Combobox(self.window,width=10)
        self.combo["values"] = timestr
        self.combo.current(2)
        self.combo.bind('<<ComboboxSelected>>', self.updtime)
        self.combo.grid(column=4,row=3)

        self.ports = Listbox(self.window,name='ports')
        self.ports.grid(column=2,columnspan=2,row=4,sticky=W+E)
        self.ports.bind('<<ListboxSelect>>', self.selectport)

        self.br = Scale(self.window, from_=-255, to=255,command=self.updbright)
        self.br.set(0)
        self.br.grid(column=4,rowspan=1,row=1,sticky=N+S)

        self.sat = Scale(self.window, from_=-255, to=255,command=self.updsat)
        self.sat.set(0)

        self.sat.grid(column=4,row=4,sticky=N+S)

        Label(self.window, text="Brillo").grid(column=4, row=2)
        Label(self.window, text="Saturacion").grid(column=4, row=5)


        ####################
        #Third row  	
        btn = Button(self.window, text="Agregar...", command=self.loadimg)
        btn.grid(column=0,row=5)
        btn1 = Button(self.window, text="Quitar", command=self.deli)
        btn1.grid(column=0,row=6)
        btn3 = Button(self.window, text="Rotar", command=self.roti)
        btn3.grid(column=2,columnspan=2,row=5)
        btn2 = Button(self.window, text="Cargar!", command=self.upload)
        btn2.grid(column=4,row=6)
        
        btn4 = Button(self.window, text="Actualizar puertos", command=self.updports)
        btn4.grid(column=2,columnspan=2,row=6)

        self.status = StringVar(value="Status: Bienvenido!")

        statusbar = Label(self.window, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W)
        statusbar.grid(column=0,columnspan=5,row=8, sticky=W+E)


        self.bar = Progressbar(self.window, length=200)
        self.bar.grid(column=0,columnspan=5,row=9,sticky=W+E)
        
        self.updports()

        #self.window.grid_rowconfigure(5,weight=1)
       
    ######################
    ##Transmission classes
    ######################

    def connect(self):
        try:
            if self.ser:
                self.ser.close()
            self.stablish()
        except:
            self.stablish()

    def stablish(self):
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
           
            #sval  = im.sat
            #vval  = im.bright

            #hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
            #h,s,v = cv2.split(hsv)

            #Saturating 
            #s = s.astype(np.int)
            #s += sval
            #np.clip(s,0,255,s)
            #s = s.astype(np.uint8)
            
            ##reducing brightness
            #v = v.astype(np.int)
            #v += vval
            #np.clip(v,0,255,v)
            #v = v.astype(np.uint8)

            #hsv = cv2.merge([h,s,v])

            #img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            #b,g,r = cv2.split(img)
            #b = b.astype(np.int32)
            #g = g.astype(np.int32)
            #r = r.astype(np.int32)
    
            #b += self.brs[i]
            #g += self.brs[i]
            #r += self.brs[i]
    
            #np.clip(b,0,255,b)
            #np.clip(g,0,255,g)
            #np.clip(r,0,255,r)
    
            #b = b.astype(np.uint8)
            #g = g.astype(np.uint8)
            #r = r.astype(np.uint8)
    
            #img = cv2.merge([b,g,r])

            
            #img2 = cv2.resize(img,(self.width,self.height))
            #img2 = np.rot90(img,k=1)
            #img2 = np.flip(img2,axis=0)

            img2 = im.shimg.copy()
            img2 = np.rot90(img2)
            
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
            ou+=str(im.time)
        
            #with open("./decimgs/ima{}.txt".format(fcntr), "w+") as f:
            #    f.write(ou)
            #    f.write("z")
            
            #self.ser.write('p{}.'.format(self.fcntr).encode())
            self.ser.write('p.'.format(self.fcntr).encode())
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
    


