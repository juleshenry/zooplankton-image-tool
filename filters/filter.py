from PIL import Image, ImageEnhance, ImageOps

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
                       0.0 means no change, 1.0 means 360 degrees shift.

    Returns:
        PIL.Image: The modified image.
    """
    # Convert the image to HSV mode
    hsv_image = image.convert('HSV')
    
    # Separate H, S, and V channels
    h, s, v = hsv_image.split()
    
    # Apply hue adjustment
    h = h.point(lambda p: p * factor)
    
    # Merge the modified channels back into an HSV image
    modified_hsv_image = Image.merge('HSV', (h, s, v))
    
    # Convert back to RGB mode
    return modified_hsv_image.convert('RGB')

def blackpoint(image, threshold):
    """
    Sets all pixels below a certain threshold to black.

    Parameters:
        image (PIL.Image): The input image.
        threshold (int): The pixel value below which to set to black.

    Returns:
        PIL.Image: The modified image.
    """
    return image.point(lambda p: 0 if p < threshold else p)

# Example usage:

# Load an image
input_image = Image.open('input_image.jpg')

# Adjust contrast
output_image_contrast = contrast(input_image, 1.5)

# Posterize
output_image_posterize = posterize(input_image, 5)

# Adjust hue
output_image_hue = hue(input_image, 0.5)

# Set black point
output_image_blackpoint = blackpoint(input_image, 100)

# Save the modified images
output_image_contrast.save('output_contrast.jpg')
output_image_posterize.save('output_posterize.jpg')
output_image_hue.save('output_hue.jpg')
output_image_blackpoint.save('output_blackpoint.jpg')
