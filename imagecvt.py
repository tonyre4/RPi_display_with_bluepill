import numpy as np
import cv2

b64 = [ 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9','+','/']

def encode(pix):
    n = format(pix[0], '08b') + format(pix[1], '08b') + format(pix[0], '08b')
    #print(n)

    u = int(n[:6],2)
    d = int(n[6:12],2)
    t = int(n[12:18],2)
    c = int(n[18:],2)

    return b64[u]+b64[d]+b64[t]+b64[c]


height,width = 400, 250


img = cv2.imread("ad.jpg")

img2 = cv2.resize(img,(width,height))

with open("f.txt","w+") as f:
    for ff in img2:
        for e in ff:
                f.write(encode(e)+',')
        f.write("\n")

