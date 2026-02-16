from PIL import Image, ImageEnhance, ImageOps
import numpy as np

def contrast(image, factor):
    """
    Adjusts the contrast of the image.

    Parameters:
        image (PIL.Image): The input image.
        factor (float): A factor by which to adjust the contrast. 
                       1.0 means no change, less than 1.0 reduces contrast, greater than 1.0 increases contrast.

    Returns:
        PIL.Image: The modified image.
    """
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)

def posterize(image, levels):
    """
    Reduces the number of colors in the image to the specified number of levels.

    Parameters:
        image (PIL.Image): The input image.
        levels (int): The number of levels for posterization (2 to 256).

    Returns:
        PIL.Image: The modified image.
    """
    return ImageOps.posterize(image, levels)

def hue(image, factor):
    """
    Adjusts the hue of the image.

    Parameters:
        image (PIL.Image): The input image.
        factor (float): A factor by which to adjust the hue. 
                       1.0 means no change.

    Returns:
        PIL.Image: The modified image.
    """
    hsv_arr = np.array(image.convert('HSV'))
    hsv_arr[..., 0] = np.clip(hsv_arr[..., 0].astype(float) * factor, 0, 255).astype(np.uint8)
    return Image.fromarray(hsv_arr, 'HSV').convert('RGB')

def blackpoint(image, threshold):
    """
    Sets all pixels below a certain threshold to black.

    Parameters:
        image (PIL.Image): The input image.
        threshold (int): The pixel value below which to set to black.

    Returns:
        PIL.Image: The modified image.
    """
    img_arr = np.array(image)
    img_arr[img_arr < threshold] = 0
    return Image.fromarray(img_arr)
