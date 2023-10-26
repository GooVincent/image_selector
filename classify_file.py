import os
import shutil


def run_classify(dir:str):
    new_folder1 = 'bigger_confidence'
    new_folder2 = 'smaller_confidence'

    if not os.path.exists(f'{dir}/{new_folder1}'):
        os.makedirs(f'{dir}/{new_folder1}')

    if not os.path.exists(f'{dir}/{new_folder2}'):
        os.makedirs(f'{dir}/{new_folder2}')

    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    all_images = [file for file in os.listdir(dir) if os.path.splitext(file)[-1].lower() in image_extensions]

    for img in all_images:
        if int(img.split('.')[-2]) > 50:
            shutil.move(f'{dir}/{img}', f'{dir}/{new_folder1}/{img}')
        else:
            shutil.move(f'{dir}/{img}', f'{dir}/{new_folder2}/{img}')

if __name__ == '__main__':
    import sys

    run_classify(sys.argv[1])
