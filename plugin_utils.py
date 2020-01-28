import os
import json
import logging
from dataloop_converter import convert_dataloop_to_coco

logger = logging.getLogger(__name__)
data_format = 'dataloop'


def get_dataset_obj():
    import dtlpy as dl
    with open("dataloop_configs.json") as f:
        dataloop_configs = json.load(f)
    project_name = dataloop_configs['project']
    dataset_name = dataloop_configs['dataset']
    project = dl.projects.get(project_name=project_name)
    dataset_obj = project.datasets.get(dataset_name)
    return dataset_obj


def maybe_download_data(dataset_obj):
    # check if data is downloaded if not then download

    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    path_to_put_data = os.path.join(parent_dir, 'data')
    if not os.path.exists(path_to_put_data):
        os.mkdir(path_to_put_data)

    if data_format == 'dataloop':
        dataset_name = dataset_obj.name
        path_to_dataset = os.path.join(path_to_put_data, dataset_name)
        if os.path.exists(os.path.join(path_to_dataset, dataset_name)):
            logger.info(dataset_name + ' already exists, no need to download')
        else:
            if not os.path.exists(path_to_dataset):
                os.mkdir(path_to_dataset)
            dataset_obj.items.download(local_path=path_to_dataset, to_items_folder=False)
            dataset_obj.download_annotations(local_path=path_to_dataset)
            # move annotations out of item folder becuz this feature doesnt exist in download annotations method
            for j in os.listdir(os.path.join(path_to_dataset, 'json', 'items')):
                os.rename(os.path.join(path_to_dataset, 'json', 'items', j), os.path.join(path_to_dataset, 'json', j))
            os.rmdir(os.path.join(path_to_dataset, 'json', 'items'))

            convert_dataloop_to_coco(path_to_data=path_to_dataset, name='train')
            convert_dataloop_to_coco(path_to_data=path_to_dataset, name='val')

    else:
        name = dataset_obj.directory_tree.dir_names[-2].strip('/')
        if os.path.exists(os.path.join(path_to_put_data, name)):
            logger.info(name + ' already exists, no need to download')
        else:
            dataset_obj.items.download(local_path=path_to_put_data, to_items_folder=False)

        logger.info('downloaded dataset to ' + path_to_put_data)
