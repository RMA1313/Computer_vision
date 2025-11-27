import cv2
import numpy as np

clean_img = cv2.imread(r'HW3\1.bmp', cv2.IMREAD_GRAYSCALE)
noisy_img = cv2.imread(r'HW3\2.bmp', cv2.IMREAD_GRAYSCALE)

if clean_img is None or noisy_img is None:
    print("Error: Could not find images. Please check 'clean_image.jpg' and 'noisy_image.jpg'.")
    exit()
dim = (clean_img.shape[1], clean_img.shape[0])
noisy_img = cv2.resize(noisy_img, dim)

f_clean = np.fft.fft2(clean_img)
f_noisy = np.fft.fft2(noisy_img)

f_noise_mask = f_noisy - f_clean

def get_spectrum_for_display(f_shift):
    spectrum = np.fft.fftshift(f_shift)
    magnitude = np.log(1 + np.abs(spectrum))
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
cv2.imwrite('1_clean_spectrum.jpg', get_spectrum_for_display(f_clean))
cv2.imwrite('2_noisy_spectrum.jpg', get_spectrum_for_display(f_noisy))
cv2.imwrite('3_noise_mask.jpg', get_spectrum_for_display(f_noise_mask))


print("All done! The following files have been created:")
print("- 1_clean_spectrum.jpg")
print("- 2_noisy_spectrum.jpg")
print("- 3_noise_mask.jpg (This is your final noise mask)")
