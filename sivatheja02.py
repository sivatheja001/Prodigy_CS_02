import sys
from PIL import Image
import random

def swap_pixels(image, key):
    random.seed(key)
    pixel_data = list(image.getdata())
    indices = list(range(len(pixel_data)))
    random.shuffle(indices)
    shuffled_pixel_data = [pixel_data[i] for i in indices]
    return shuffled_pixel_data, indices

def unswap_pixels(image, key, indices):
    random.seed(key)
    width, height = image.size
    pixel_data = [None] * (width * height)
    for original_index, shuffled_index in enumerate(indices):
        pixel_data[shuffled_index] = image.getpixel((original_index % width, original_index // width))
    return pixel_data

def apply_key_to_pixels(pixel_data, key, operation):
    transformed_pixel_data = []
    for pixel in pixel_data:
        transformed_pixel = tuple((p + key) % 256 if operation == "encrypt" else (p - key) % 256 for p in pixel)
        transformed_pixel_data.append(transformed_pixel)
    return transformed_pixel_data

def transform_image(image_path, key, output_path, action, method):
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")
        return
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    width, height = image.size
    if method == "swap":
        if action == "encrypt":
            transformed_pixel_data, indices = swap_pixels(image, key)
            image.putdata(transformed_pixel_data)
            with open(output_path + ".key", 'w') as key_file:
                key_file.write(",".join(map(str, indices)))
        else:  # decrypt
            try:
                with open(output_path + ".key", 'r') as key_file:
                    indices = list(map(int, key_file.read().strip().split(',')))
            except FileNotFoundError:
                print(f"Error: Key file '{output_path}.key' not found.")
                return
            except Exception as e:
                print(f"Error reading key file: {e}")
                return

            if len(indices) != width * height:
                print("Error: Key indices length does not match image size.")
                return

            transformed_pixel_data = unswap_pixels(image, key, indices)
            image.putdata(transformed_pixel_data)
    else:  # method == "math"
        pixel_data = list(image.getdata())
        transformed_pixel_data = apply_key_to_pixels(pixel_data, key, action)
        image.putdata(transformed_pixel_data)

    try:
        image.save(output_path)
        print(f"Image {action}ed successfully and saved to {output_path}!")
    except Exception as e:
        print(f"Error saving image: {e}")

def main():
    if len(sys.argv) != 6:
        print("Usage: python script.py <encrypt/decrypt> <input_path> <key> <output_path> <method>")
        print("Method can be 'swap' or 'math'.")
        return

    action = sys.argv[1]
    input_path = sys.argv[2]
    key = int(sys.argv[3])
    output_path = sys.argv[4]
    method = sys.argv[5]

    if method not in ["swap", "math"]:
        print("Invalid method. Use 'swap' or 'math'.")
        return

    if action not in ["encrypt", "decrypt"]:
        print("Invalid operation. Use 'encrypt' or 'decrypt'.")
        return

    transform_image(input_path, key, output_path, action, method)

if __name__ == "__main__":
    main()
