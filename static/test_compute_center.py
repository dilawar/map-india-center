import cv2
import numpy as np

img = cv2.imread('./india.clipped.png', 0)

wx, wy, vs = 0, 0, 0
for (x, y), v in np.ndenumerate(img):
    wx += x * v
    wy += y * v
    vs += v

center = wy//vs, wx//vs
print('center', center)
img = cv2.circle(img, center, 10, 255, -1)
cv2.imwrite('temp.png', img)
