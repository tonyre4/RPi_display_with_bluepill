from glob import glob
import numpy as np
import cv2

height,width = 320, 480
fcntr = 0

for im in glob("./imgs/*"):
    ou = ""
    img = cv2.imread(im)
    
    
    img2 = cv2.resize(img,(width,height))
    img2 = np.flip(img2,axis=0)
    
    b,g,r = cv2.split(img2)
    
    #b = b*31/255
    #r = r*31/255
    #g = g*63/255
    
    b = np.right_shift(b,3)
    g = np.right_shift(g,2)
    r = np.right_shift(r,3)
    
    rn = np.array((width,height),np.uint16)
    rn = np.left_shift(r.astype(np.uint16),11)
    gn = np.array((width,height),np.uint16)
    gn = np.left_shift(g.astype(np.uint16),5)
    bn = np.array((width,height),np.uint16)
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

    with open("./decimgs/ima{}.txt".format(fcntr), "w+") as f:
        f.write(ou)
        #f.write("%")
    fcntr +=1



