import cv2
import numpy as np

def displayFrame(frame, reduceSize=1):
    if reduceSize <= 0:
        reduceSize = 1

    resizedFrame = cv2.resize(frame, (int(frame.shape[1] / reduceSize), int(frame.shape[0] / reduceSize)))
    cv2.imshow('Frame View', resizedFrame)

def writeCroppedImage(filename, img, x, y, w, h, grayscale=False):
    cropped = img[y:y + h, x:x + w]
    if (grayscale == True):
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(filename, cropped)


def createPdf():
    print('TODO')


def inputScannerSettings():
    print('TODO')

def main():
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
                print(f'Image {imagesTaken} taken')
                writeCroppedImage(f'testImage{imagesTaken}.jpg', frame, x, y, w, h, True)
                imagesTaken += 1
            else:
                print('WRITE FAILED: No Contours Found!')

    capture.release()
    cv2.destroyAllWindows()
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

main()
