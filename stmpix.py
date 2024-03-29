from glob import glob
import numpy as np
import cv2

height,width = 320, 480
ou = ""

for im in glob("./imgs/*"):
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
            #ou += "{:05d},".format(col)
            col = str(col)[::-1]
            ou += "{},".format(col)
            #f.write("{:05d},".format(col))
        ou+= "\n"
        #f.write("\n")

with open("dec.txt", "w+") as f:
    f.write(ou)



