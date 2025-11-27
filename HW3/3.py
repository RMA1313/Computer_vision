import cv2
import numpy as np

drop = cv2.imread(r'HW3\3.jpg', cv2.IMREAD_GRAYSCALE)
if drop is None:
    print("Error: HW3\\3.jpg not found!")
    exit()

drop = drop.astype(np.float32)
drop -= drop.mean()                     

f = np.fft.fft2(drop)
f_shifted = np.fft.fftshift(f)
pattern = np.real(np.fft.ifft2(np.fft.ifftshift(f_shifted)))

cv2.imwrite('noise.png', pattern + 128)

def add_noise(image_path, save_as='noisy.jpg'):
    img = cv2.imread(image_path)
    if img is None:
        print("Image not found:", image_path)
        return
    noise = cv2.resize(pattern, (img.shape[1], img.shape[0]))
    if len(img.shape) == 3:
        noise = cv2.cvtColor(noise, cv2.COLOR_GRAY2BGR)
    result = img.astype(np.float32) + noise 
    result = np.clip(result, 0, 255).astype(np.uint8)
    cv2.imwrite(save_as, result)

# Use it like this:
add_noise(r'HW3\4.bmp', save_as='4.jpg')
