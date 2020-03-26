from xml.etree import ElementTree
from time import perf_counter
import pandas as pd
import json
import os


def get_tree_item(parent, tag, file_path, find_all=False):
    """
    Get item from xml tree element.
    Args:
        parent: Parent in xml element tree
        tag: tag to look for.
        file_path: Current xml file being handled.
        find_all: If True, all elements found will be returned.

    Return:
        Tag item.
    """
    target = parent.find(tag)
    if find_all:
        target = parent.findall(tag)
    if target is None:
        raise ValueError(f'Could not find "{tag}" in {file_path}')
    return target


def parse_voc_file(file_path, voc_conf):
    """
    Parse voc annotation from xml file.
    Args:
        file_path: Path to xml file.
        voc_conf: voc configuration file.

    Return:
        A list of image annotations.
    """
    image_data = []
    with open(voc_conf) as json_data:
        tags = json.load(json_data)
    tree = ElementTree.parse(file_path)
    image_path = get_tree_item(tree, tags['Tree']['Path'], file_path).text
    size_item = get_tree_item(tree, tags['Size']['Size Tag'], file_path)
    image_width = get_tree_item(size_item, tags['Size']['Width'], file_path).text
    image_height = get_tree_item(size_item, tags['Size']['Height'], file_path).text
    for item in get_tree_item(tree, tags['Object']['Object Tag'], file_path, True):
        name = get_tree_item(item, tags['Object']['Object Name'], file_path).text
        box_item = get_tree_item(item, tags['Object']['Object Box']['Object Box Tag'], file_path)
        x0 = get_tree_item(box_item, tags['Object']['Object Box']['X0'], file_path).text
        y0 = get_tree_item(box_item, tags['Object']['Object Box']['Y0'], file_path).text
        x1 = get_tree_item(box_item, tags['Object']['Object Box']['X1'], file_path).text
        y1 = get_tree_item(box_item, tags['Object']['Object Box']['Y1'], file_path).text
        image_data.append([image_path, image_width, image_height, name, x0, y0, x1, y1])
    return image_data


def parse_voc_folder(folder_path, voc_conf, cache_file='data_set_labels.csv'):
    """
    Parse a folder containing voc xml annotation files.
    Args:
        folder_path: Folder containing voc xml annotation files.
        voc_conf: voc configuration file.
        cache_file: csv file name containing current session labels.

    Return:
        pandas DataFrame with the annotations.
    """
    cache_path = os.path.join('Caches', cache_file)
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)
    image_data = []
    frame_columns = ['Image Path', 'Image Width', 'Image Height', 'Object Name', 'X_min', 'Y_min', 'X_max', 'Y_max']
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xml'):
            annotation_path = os.path.join(folder_path, file_name)
            image_labels = parse_voc_file(annotation_path, voc_conf)
            image_data.extend(image_labels)
    frame = pd.DataFrame(image_data, columns=frame_columns)
    frame.to_csv(cache_path, index=False)
    return frame


if __name__ == '__main__':
    t1 = perf_counter()
    pd.set_option('display.max_columns', 500)
    xx = parse_voc_folder('../../beverly_hills_gcp/lbl', 'Config/voc_conf.json')
    print(xx)
    print(f'{perf_counter() - t1} seconds')