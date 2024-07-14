import cv2
import numpy as np

def display(img):
    resizedImage = cv2.resize(img, (int(img.shape[1] / 4), int(img.shape[0] / 4)))
    cv2.imshow('Frame View', resizedImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def writeCropped(filename, img, x, y, w, h, grayscale=False):
    cropped = img[y:y + h, x:x + w]
    if (grayscale == True):
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(filename, cropped)

def main():
    img = cv2.imread('test5.jpg')
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, thresh = cv2.threshold(img, 130, 255, 0)

    lower = np.array([135, 135, 135])
    upper = np.array([255, 255, 255])
    mask = cv2.inRange(img, lower, upper)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(contours, key = cv2.contourArea)
    x,y,w,h = cv2.boundingRect(cnt)
    # cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)

    writeCropped("crop.jpg", img, x, y, w, h, True)

main()
