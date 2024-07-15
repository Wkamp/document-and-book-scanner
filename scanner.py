import cv2
import numpy as np
import img2pdf
from PIL import Image
import os

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


def createPdf(mode):
    print('TODO')


def inputMenuValidation(menu, numOptions):
    print(menu)

    user = input('> ')
    while len(user) > 1 or user.isdigit() == False or int(user) > numOptions or int(user) <= 0:
        print('ERROR: Invalid Input\n')
        print(menu)
        user = input('> ')

    return int(user)

def inputScannerSettings():
    mode = inputMenuValidation('Enter the number of an option:\n\t1. Document Mode\n\t2. Book Mode', 2)
    if mode == 1:
        mode = 'document'
    elif mode == 2:
        mode = 'book'

    grayscale = inputMenuValidation('Enter the number of an option:\n\t1. Color \n\t2. Grayscale', 2)
    if grayscale == 2:
        grayscale = True
    else:
        grayscale = False

    print('Input filename:')

    filename = input('> ')
    if filename[-4:] != '.pdf':
        filename += '.pdf'

    return mode, grayscale, filename

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
    mode, grayscale, filename = inputScannerSettings()

    imagesPath = os.getcwd() + '/' + filename[:-4]
    if os.path.exists(imagesPath) != True:
        os.mkdir(imagesPath)



    print("Press 'spacebar' to take picture, press 'q' to quit")

    capture = cv2.VideoCapture(0)
    imagesTaken = 0

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
                imagesTaken += 1 
                print(f'Page {imagesTaken} taken')
                writeCroppedImage(os.path.join(imagesPath, f'p{imagesTaken}.jpg'), frame, x, y, w, h, grayscale)
            else:
                print('WRITE FAILED: No Contours Found!')

    capture.release()
    cv2.destroyAllWindows()
    createPdf(mode)

main()
