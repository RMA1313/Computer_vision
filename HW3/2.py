import cv2
import numpy as np

clean_img = cv2.imread(r'HW3\1.bmp', cv2.IMREAD_GRAYSCALE)
noisy_img = cv2.imread(r'HW3\2.bmp', cv2.IMREAD_GRAYSCALE)

if clean_img is None or noisy_img is None:
    print("Error: Could not load one or both images.")
    exit()

noisy_img = cv2.resize(noisy_img, (clean_img.shape[1], clean_img.shape[0]))

clean_img = clean_img.astype(np.float32)
noisy_img = noisy_img.astype(np.float32)

mean_clean = clean_img.mean()
mean_noisy = noisy_img.mean()
noisy_img -= (mean_noisy - mean_clean)

f_clean = np.fft.fft2(clean_img)
f_noisy = np.fft.fft2(noisy_img)

f_noise = f_noisy - f_clean

f_noise[0, 0] = 0

def get_spectrum_image(f):
    f_shifted = np.fft.fftshift(f)
    magnitude = np.abs(f_shifted)
    magnitude = np.log(1 + magnitude)
    spectrum_8bit = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    return spectrum_8bit.astype(np.uint8)

# Save the three spectra
cv2.imwrite('1_clean_spectrum.jpg', get_spectrum_image(f_clean))
cv2.imwrite('2_noisy_spectrum.jpg', get_spectrum_image(f_noisy))
cv2.imwrite('3_noise_mask.jpg', get_spectrum_image(f_noise))

print("Done! Generated files:")
print("   1_clean_spectrum.jpg")
print("   2_noisy_spectrum.jpg")
print("   3_noise_mask.jpg  <- This is your final periodic noise mask (center is now dark)")