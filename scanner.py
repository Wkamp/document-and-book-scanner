import cv2
import numpy as np
import os
from PIL import Image
from math import ceil

def displayFrame(frame, reduceSize=1):
    if reduceSize <= 0:
        reduceSize = 1

    resizedFrame = cv2.resize(frame, (int(frame.shape[1] / reduceSize), int(frame.shape[0] / reduceSize)))
    cv2.imshow('Frame View', resizedFrame)

def writeCroppedImage(filepath, img, x, y, w, h, grayscale=False):
    cropped = img[y:y + h, x:x + w]
    if (grayscale == True):
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(filepath, cropped)


def createPdf(filepath, filename, numPages):
    images = []
    for i in range(1, numPages + 1):
        images.append(Image.open(os.path.join(filepath, f'p{i}.jpg')))

    images[0].save(
        filename + '.pdf', "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
    )    

def inputMenuValidation(menu, numOptions):
    print(menu)

    user = input('> ')
    while len(user) > 1 or user.isdigit() == False or int(user) > numOptions or int(user) <= 0:
        print('ERROR: Invalid Input\n')
        print(menu)
        user = input('> ')

    return int(user)

def inputScannerSettings():
    pageDelta = 0 # used only when book mode chosen

    print('Enter camera index:\n(input 0 if you have only one camera connected to your pc)\n')

    camIndex = input('> ')
    while (camIndex.isdigit() == False):
        print("ERROR: input not a number")
        camIndex = input('> ')

    mode = inputMenuValidation('Enter the number of an option:\n\t1. Document Mode\n\t2. Book Mode', 2)
    if mode == 1:
        mode = 'document'
    elif mode == 2:
        mode = 'book'

        print('\nEnter first page number: ')
        first = input('> ')
        while first.isdigit() == False:
            print('ERROR: Invalid Input\n')
            print('Enter first page number: ')
            first = input('> ')

        print('\nEnter last page number: ')
        last = input('> ')
        while last.isdigit() == False:
            print('ERROR: Invalid Input\n')
            print('Enter last page number: ')
            first = input('> ')

        last = int(last)
        first = int(first)
        pageDelta = abs(last - first)

    grayscale = inputMenuValidation('Enter the number of an option:\n\t1. Color \n\t2. Grayscale', 2)
    if grayscale == 2:
        grayscale = True
    else:
        grayscale = False

    print('Enter output pdf filename:')

    filename = input('> ')
    if filename[-4:] == '.pdf':
        filename = filename[:-4]

    return mode, pageDelta, grayscale, filename, camIndex

def contour(frame):
    lower = np.array([135, 135, 135])
    upper = np.array([255, 255, 255])
    mask = cv2.inRange(frame, lower, upper)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) < 1:
        return frame

    cnt = max(contours, key = cv2.contourArea)
    x,y,w,h = cv2.boundingRect(cnt)

    return frame, x, y, w, h

def main():
    mode, pageDelta, grayscale, filename, camIndex = inputScannerSettings()
    rightSideTaken = False
    numRightPages = ceil(pageDelta / 2)
    if pageDelta % 2 == 0:
        numRightPages += 1

    imagesPath = os.path.join(os.getcwd(), filename + 'Images')
    if os.path.exists(imagesPath) != True:
        os.mkdir(imagesPath)
    
    if mode == 'document':
        print('\n*** Document Mode Instructions ***')
        print("Press 'spacebar' to take a picture, press 'q' to exit\n")
    else:
        print('\n*** Book Mode Instructions ***')
        print("Press 'spacebar' to take a picture, press 'q' to exit early\n")
        print('1. Take a picture of every right-side page')
        print('2. Take a picture of every left-side page')

    capture = cv2.VideoCapture(int(camIndex))
    
    imagesTaken = 0
    pageNum = 0 
    if mode == 'book' and pageDelta % 2 == 0:
        pageNum = -1

    while capture.isOpened():
        ret, frame = capture.read()
        contourDisplayFrame = frame.copy()
        
        contourInfo = contour(frame)
        contourFound = True
        
        if len(contourInfo) == 5:
            frame, x, y, w, h = contourInfo
            cv2.rectangle(contourDisplayFrame, (x,y), (x+w, y+h), (0,255,0), 2) # draws contour bounding box on separate frame, so it's not in the final image 
            displayFrame(contourDisplayFrame)
        else:
            contourFound = False
            displayFrame(frame)

        waitKey = cv2.waitKey(1)
 
        if waitKey % 256 == 113: # exits capture on 'q' key pressed
            break

        if waitKey % 256 == 32: # takes picture on 'spacebar' key pressed
            if contourFound == True:
                if mode != 'book':
                    pageNum += 1
                else:
                    pageNum += 2

                imagesTaken += 1
                print(f'Page {pageNum} taken')
                writeCroppedImage(os.path.join(imagesPath, f'p{pageNum}.jpg'), frame, x, y, w, h, grayscale)
            else:
                print('WRITE FAILED: No Contours Found!')
        
        if mode == 'book' and rightSideTaken == False and numRightPages == imagesTaken:
            rightSideTaken = True
            if pageDelta % 2 != 0:
                pageNum = -1
            else:
                pageNum = 0
            print('\n*** Right Pages Recorded ***\n')

        elif mode == 'book' and pageDelta + 1 == imagesTaken:
            print('\n*** Left Pages Recorded ***\n')
            break

    capture.release()
    cv2.destroyAllWindows()
   
    print("Creating pdf...")
    createPdf(imagesPath, filename, imagesTaken)
main()
