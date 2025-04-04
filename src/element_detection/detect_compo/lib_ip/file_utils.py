import os
import pandas as pd
import json
from os.path import join as pjoin
import cv2


def save_corners(file_path, corners, compo_name, clear=True):
    try:
        df = pd.read_csv(file_path, index_col=0)
    except:
        df = pd.DataFrame(
            columns=['component', 'x_max', 'x_min', 'y_max', 'y_min', 'height', 'width'])

    if clear:
        df = df.drop(df.index)
    for corner in corners:
        (up_left, bottom_right) = corner
        c = {'component': compo_name}
        (c['y_min'], c['x_min']) = up_left
        (c['y_max'], c['x_max']) = bottom_right
        c['width'] = c['y_max'] - c['y_min']
        c['height'] = c['x_max'] - c['x_min']
        df = df.append(c, True)
    df.to_csv(file_path)


def save_corners_json(file_path, compos, full_screen):
    img_shape = compos[0].image_shape
    output = {'img_shape': img_shape, 'full_screen': full_screen, 'compos': []}
    f_out = open(file_path, 'w')

    for compo in compos:
        c = {'id': compo.id, 'class': compo.category}
        x_min, y_min, x_max, y_max = compo.put_bbox()
        relative_x_min = (x_min / img_shape[1]) * 100
        relative_y_min = (y_min / img_shape[0]) * 100
        relative_x_max = (x_max / img_shape[1]) * 100
        relative_y_max = (y_max / img_shape[0]) * 100
        relative_centre_coordinates = (
            round((relative_x_min + relative_x_max) / 2, 2), round((relative_y_min + relative_y_max) / 2, 2))

        (c['relative_x_min'], c['relative_y_min'], c['relative_x_max'], c['relative_y_max']) = (
            round(relative_x_min, 2), round(relative_y_min, 2), round(relative_x_max, 2), round(relative_y_max, 2))
        c['relative_centre_coordinates'] = relative_centre_coordinates
        output['compos'].append(c)

    json.dump(output, f_out, indent=4)


def save_clipping(org, output_root, corners, compo_classes, compo_index):
    if not os.path.exists(output_root):
        os.mkdir(output_root)
    pad = 2
    for i in range(len(corners)):
        compo = compo_classes[i]
        (up_left, bottom_right) = corners[i]
        (col_min, row_min) = up_left
        (col_max, row_max) = bottom_right
        col_min = max(col_min - pad, 0)
        col_max = min(col_max + pad, org.shape[1])
        row_min = max(row_min - pad, 0)
        row_max = min(row_max + pad, org.shape[0])

        # if component type already exists, index increase by 1, otherwise add this type
        compo_path = pjoin(output_root, compo)
        if compo_classes[i] not in compo_index:
            compo_index[compo_classes[i]] = 0
            if not os.path.exists(compo_path):
                os.mkdir(compo_path)
        else:
            compo_index[compo_classes[i]] += 1
        clip = org[row_min:row_max, col_min:col_max]
        cv2.imwrite(pjoin(compo_path, str(
            compo_index[compo_classes[i]]) + '.png'), clip)


def build_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory
