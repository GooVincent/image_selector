import os
import gradio as gr
import numpy as np
import shutil
import random
import cv2
from PIL import Image
from typing import Tuple
import yaml


class ImageFileIndicator:
    def __init__(self):
        self.dir = None
        self.candidated_images = []
        self.index = -1

    # Function to list image files in a directory
    def list_image_files(self):
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
        image_files = [file for file in os.listdir(self.dir) if os.path.splitext(file)[-1].lower() in image_extensions]
        return sorted(image_files)

    def update_candidated_images(self, dir, keep_index: int=None):
        self.dir = dir
        self.candidated_images = self.list_image_files()

        if keep_index is not None:
            self.index = keep_index
        else:
            self.index = 0

    def current_candidated_image(self) -> str:
        if self.index < 0 or len(self.candidated_images) == 0:
            return None

        if self.index >= len(self.candidated_images):
            print('illegal index , return the last image')
            return self.candidated_images[-1]
        else:
            return self.candidated_images[self.index]

    def next(self):
        if self.index < len(self.candidated_images) - 1:  # current index indicate the last image
            self.index = (self.index + 1) % len(self.candidated_images)

    def prev(self):
        if self.index > 0:
            self.index = (self.index - 1) % len(self.candidated_images)

    def current(self):
        return self.index


image_file_indicator: ImageFileIndicator = ImageFileIndicator()


def archive_resize_img_and_name(dir: str, file_name: str) -> Tuple[np.ndarray, str]:

    if dir is None or file_name is None:
        return None, '/no_file_found'

    display_img_path = os.path.join(dir, file_name)
    org_img = cv2.imread(display_img_path)
    return (cv2.resize(org_img, (512, 512))[..., ::-1],
            f'[{image_file_indicator.index+1}/{len(image_file_indicator.candidated_images)}] {dir}/{file_name}')


def mv_file(src_dir: str, dst_dir: str, file_name: str):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    src_file_path = f'{src_dir}/{file_name}'
    dst_file_path = f'{dst_dir}/{file_name}'
    print(f'mv file {src_file_path} to {dst_file_path}')
    shutil.move(src_file_path, dst_file_path)


def select_file(src_dir: str, dst_dir: str, sub_folder: str):
    # mv current file into the dst folder
    selected_image_filename = image_file_indicator.current_candidated_image()
    mv_file(src_dir, f'{dst_dir}/{sub_folder}', selected_image_filename)

    index = image_file_indicator.current()
    # update folder
    image_file_indicator.update_candidated_images(src_dir, keep_index=index)

    # display the next image
    return archive_resize_img_and_name(src_dir, image_file_indicator.current_candidated_image())


def del_file(src_dir: str):
    # mv current file into the dst folder
    selected_image_filename = image_file_indicator.current_candidated_image()
    os.remove(f'{src_dir}/{selected_image_filename}')

    index = image_file_indicator.current()
    # update folder
    image_file_indicator.update_candidated_images(src_dir, keep_index=index)

    # display the next image
    return archive_resize_img_and_name(src_dir, image_file_indicator.current_candidated_image())


def dispaly_previous_img(dir: str):
    image_file_indicator.prev()
    selected_image_filename = image_file_indicator.current_candidated_image()

    return archive_resize_img_and_name(dir, selected_image_filename)


def dispaly_next_img(dir: str):
    image_file_indicator.next()
    selected_image_filename = image_file_indicator.current_candidated_image()

    return archive_resize_img_and_name(dir, selected_image_filename)


def refresh_candidated_imgs(dir: str):
    global image_file_indicator

    total_image_number = len(image_file_indicator.candidated_images)
    if total_image_number > 0:
        random_index = random.randint(0, total_image_number-1)
    else:
        random_index = 0

    image_file_indicator.update_candidated_images(dir, keep_index=random_index)
    selected_image_filename = image_file_indicator.current_candidated_image()

    return archive_resize_img_and_name(dir, selected_image_filename)

def read_file_path():
    if os.path.exists('dir_config.yaml'):
        with open('dir_config.yaml', 'r') as input_file:
            yaml_data = yaml.safe_load(input_file)
            return yaml_data['src_dir'], yaml_data['dst_dir']
    else:
        return '/', '/'

def update_config(src_dir: str, dst_dir: str):
    yaml_data = dict()
    with open('dir_config.yaml', 'w') as output_file:
        yaml_data['src_dir'] = src_dir
        yaml_data['dst_dir'] = dst_dir
        yaml.dump(yaml_data, output_file, default_flow_style=False)

def main():
    history_src_dir, history_dst_dir = read_file_path()
    with gr.Blocks() as select_tab:
        gr.Markdown("select positive and negative images.")
        with gr.Tab("choose image"):
            with gr.Row():
                src_dir = gr.Textbox(label='src dir', value=history_src_dir)
                dst_dir = gr.Textbox(label='dst dir', value=history_dst_dir)
                refresh_button = gr.Button(value="refresh")

                gr_img, display_file_path = refresh_candidated_imgs(src_dir.value)

            display_img = gr.Image(label='candidated', height=512, width=512, value=gr_img)
            dispaly_img_path = gr.Textbox(label='path', value='no file found' if display_file_path is not None else display_file_path)
            with gr.Row():
                prev_button = gr.Button(value="prev")
                next_button = gr.Button(value="next")
                move_button = gr.Button(value="move to pos")
                del_button = gr.Button("del")

            positive_button = gr.Button(value="pos")
            negative_button = gr.Button(value="neg")

        src_dir.change(update_config, inputs=[src_dir, dst_dir])
        dst_dir.change(update_config, inputs=[src_dir, dst_dir])

        positive_button.click(select_file, inputs=[src_dir, dst_dir, gr.State('pos')], outputs=[display_img, dispaly_img_path])
        negative_button.click(select_file, inputs=[src_dir, dst_dir, gr.State('neg')], outputs=[display_img, dispaly_img_path])

        refresh_button.click(refresh_candidated_imgs, inputs=src_dir, outputs=[display_img, dispaly_img_path])
        prev_button.click(dispaly_previous_img, inputs=src_dir, outputs=[display_img, dispaly_img_path])
        next_button.click(dispaly_next_img, inputs=src_dir, outputs=[display_img, dispaly_img_path])
        move_button.click(select_file, inputs=[src_dir, dst_dir, gr.State('pos')], outputs=[display_img, dispaly_img_path])
        del_button.click(del_file, inputs=[src_dir], outputs=[display_img, dispaly_img_path])

    select_tab.launch(server_name='10.23.2.12')


if __name__ == '__main__':
    main()
