"""Encapsulates datasets in a generic Dataset class, and in some more specific classes that inherit
from it

"""

import os
import json
import math
from multiprocessing import Pool

import cv2
from PIL import Image

import numpy as np

from deeposlandia import utils

class Dataset:
    """Generic class that describes the behavior of a Dataset object: it is initialized at least
    with an image size, its label are added always through the same manner, it can be serialized (save) and
    deserialized (load) from/to a `.json` file

    Attributes
    ----------
    image_size : int
        Size of considered images (height=width), raw images will be resized during the
    preprocessing

    """
    def __init__(self, image_size):
        self.image_size = image_size
        self.label_info = []
        self.image_info = []

    @property
    def label_ids(self):
        """Return the list of labels ids taken into account in the dataset

        They can be grouped.

        Returns
        -------
        list
            List of label ids
        """
        return [label_id for label_id, attr in enumerate(self.label_info)
                if attr['is_evaluate']]

    @property
    def labels(self):
        """Return the description of label that will be evaluated during the process
        """
        return [label for label in self.label_info if label["is_evaluate"]]

    def get_nb_labels(self, see_all=False):
        """Return the number of labels

        Parameters
        ----------
        see_all : boolean
            If True, consider all labels, otherwise consider only labels for which `is_evaluate` is
        True
        """
        if see_all:
            return len(self.label_info)
        else:
            return len(self.label_ids)

    def get_nb_images(self):
        """ `image_info` getter, return the size of `image_info`, i.e. the
        number of images in the dataset
        """
        return len(self.image_info)

    def get_label_popularity(self):
        """Return the label popularity in the current dataset, *i.e.* the proportion of images that
        contain corresponding object
        """
        labels = [img["labels"] for img in self.image_info]
        if self.get_nb_images() == 0:
            utils.logger.error("No images in the dataset.")
            return None
        else:
            return np.round(np.divide(sum(np.array([list(l.values()) for l in labels])),
                                      self.get_nb_images()), 3)


    def add_label(self, label_id, label_name, color, is_evaluate,
                  category=None, aggregate=None):
        """ Add a new label to the dataset with label id `label_id`

        Parameters
        ----------
        label_id : integer
            Id of the new label
        label_name : str
            String designing the new label name
        color : list
            List of three integers (between 0 and 255) that characterizes the
            label (useful for semantic segmentation result printing)
        is_evaluate : bool
        category : str
            String designing the category of the dataset label
        aggregate : list (optional)
            List of label ids aggregated by the current label_id
        """
        if label_id in self.label_info:
            utils.logger.error("Label {} already stored into the label set.".format(label_id))
            return None
        self.label_info.append({"name": label_name,
                                "id": label_id,
                                "category": category,
                                "is_evaluate": is_evaluate,
                                "aggregate": aggregate,
                                "color": color})

    def save(self, filename):
        """Save dataset in a json file indicated by `filename`

        Parameters
        ----------
        filename : str
            String designing the relative path where the dataset must be saved
        """
        with open(filename, 'w') as fp:
            json.dump({"image_size": self.image_size,
                       "labels": self.label_info,
                       "images": self.image_info}, fp)
        utils.logger.info("The dataset has been saved into {}".format(filename))

    def load(self, filename, nb_images=None):
        """Load a dataset from a json file indicated by `filename` ; use dict comprehension instead
        of direct assignments in order to convert dict keys to integers

        Parameters
        ----------
        filename : str
            String designing the relative path from where the dataset must be
        loaded
        nb_images : integer
            Number of images that must be loaded (if None, the whole dataset is loaded)
        """
        with open(filename) as fp:
            ds = json.load(fp)
        self.image_size = ds["image_size"]
        self.label_info = ds["labels"]
        if nb_images is None:
            self.image_info = ds["images"]
        else:
            self.image_info = ds["images"][:nb_images]
        utils.logger.info("The dataset has been loaded from {}".format(filename))

class MapillaryDataset(Dataset):
    """Dataset structure that gathers all information related to the Mapillary images

    Attributes
    ----------
    image_size : int
        Size of considered images (height=width), raw images will be resized during the
    preprocessing
    glossary_filename : str
        Name of the Mapillary input glossary, that contains every information about Mapillary
    labels

    """

    def __init__(self, image_size, glossary_filename):
        """ Class constructor ; instanciates a MapillaryDataset as a standard Dataset which is
        completed by a glossary file that describes the dataset labels
        """
        super().__init__(image_size)
        self.build_glossary(glossary_filename)

    def build_glossary(self, config_filename):
        """Read the Mapillary glossary stored as a json file at the data
        repository root

        Parameters
        ----------
        config_filename : str
            String designing the relative path of the dataset glossary
        (based on Mapillary dataset)
        """
        with open(config_filename) as config_file:
            glossary = json.load(config_file)
        if "labels" not in glossary:
            utils.logger.error("There is no 'label' key in the provided glossary.")
            return None
        for lab_id, label in enumerate(glossary["labels"]):
            name_items = label["name"].split('--')
            category = '-'.join(name_items)
            self.add_label(lab_id, name_items, label["color"],
                           label['evaluate'], category, label.get('aggregate'))

    def group_image_label(self, image):
        """Group the labels

        If the label ids 4, 5 and 6 belong to the same group, they will be turned
        into the label id 4.

        Parameters
        ----------
        image : PIL.Image

        Returns
        -------
        PIL.Image
        """
        # turn all label ids into the lowest digits/label id according to its "group"
        # (manually built)
        a = np.array(image)
        for root_id, label in enumerate(self.label_info):
            for label_id, _ in label['aggregate']:
                mask = a == label_id
                a[mask] = root_id
        return Image.fromarray(a, mode=image.mode)

    def _preprocess(self, image_filename, output_dir, aggregate, labelling=True):
        """Resize/crop then save the training & label images

        Parameters
        ----------
        datadir : str
        image_filaname : str
        aggregate : boolean
        labelling : boolean

        Returns
        -------
        dict
            Key/values with the filenames and label ids
        """
        # open original images
        img_in = Image.open(image_filename)

        # resize images (self.image_size*larger_size or larger_size*self.image_size)
        img_in = utils.resize_image(img_in, self.image_size)

        # crop images to get self.image_size*self.image_size dimensions
        crop_pix = np.random.randint(0, 1 + max(img_in.size) - self.image_size)
        final_img_in = utils.mono_crop_image(img_in, crop_pix)

        # save final image
        new_in_filename = os.path.join(output_dir, 'images', image_filename.split('/')[-1])
        final_img_in.save(new_in_filename)

        # label_filename vs label image
        if labelling:
            label_filename = image_filename.replace("images/", "labels/")
            label_filename = label_filename.replace(".jpg", ".png")
            img_out = Image.open(label_filename)
            img_out = utils.resize_image(img_out, self.image_size)
            final_img_out = utils.mono_crop_image(img_out, crop_pix)
            # group some labels
            if aggregate:
                final_img_out = self.group_image_label(final_img_out)

            labels = utils.mapillary_label_building(final_img_out, self.label_ids)
            new_out_filename = os.path.join(output_dir, 'labels', label_filename.split('/')[-1])
            final_img_out.save(new_out_filename)
        else:
            new_out_filename = None
            labels = {i: 0 for i in range(self.get_nb_labels())}

        return {"raw_filename": image_filename,
                "image_filename": new_in_filename,
                "label_filename": new_out_filename,
                "labels": labels}

    def populate(self, output_dir, input_dir, nb_images=None, aggregate=False, labelling=True):
        """ Populate the dataset with images contained into `datadir` directory

        Parameters
        ----------
        output_dir : str
            Path of the directory where the preprocessed image must be saved
        input_dir : str
            Path of the directory that contains input images
        nb_images : integer
            Number of images to be considered in the dataset; if None, consider the whole
        repository
        aggregate : bool
            Aggregate some labels into more generic ones, e.g. cars and bus into the vehicle label
        labelling: boolean
            If True labels are recovered from dataset, otherwise dummy label are generated
        """
        image_list = os.listdir(os.path.join(input_dir, "images"))[:nb_images]
        image_list_longname = [os.path.join(input_dir, "images", l) for l in image_list]
        with Pool() as p:
            self.image_info = p.starmap(self._preprocess, [(x, output_dir, aggregate, labelling)
                                                  for x in image_list_longname])

class ShapeDataset(Dataset):
    """Dataset structure that gathers all information related to a randomly-generated shape Dataset

    In such a dataset, a set of images is generated with either a square, or a circle or a
    triangle, or two of them, or all of them. A random background color is applied, and shape color
    itself is also randomly generated.

    Attributes
    ----------
    image_size : int
        Size of considered images (height=width), raw images will be resized during the
    preprocessing
    nb_labels : int
        Number of shape types that must be integrated into the dataset (only 1, 2 and 3 are supported)

    """

    SQUARE = 0
    SQUARE_COLOR = (0, 10, 10)
    CIRCLE = 1
    CIRCLE_COLOR = (200, 10, 50)
    TRIANGLE = 2
    TRIANGLE_COLOR = (200, 130, 130)
    BACKGROUND = 3
    BACKGROUND_COLOR = (255, 255, 255)

    def __init__(self, image_size):
        """ Class constructor
        """
        super().__init__(image_size)
        self.build_glossary()

    def build_glossary(self):
        """Read the shape glossary stored as a json file at the data
        repository root

        Parameters
        ----------
        nb_labels : integer
            Number of shape types (either 1, 2 or 3, warning if more)
        """
        self.add_label(self.SQUARE, "square", self.SQUARE_COLOR, True)
        self.add_label(self.CIRCLE, "circle", self.CIRCLE_COLOR, True)
        self.add_label(self.TRIANGLE, "triangle", self.TRIANGLE_COLOR, True)
        self.add_label(self.BACKGROUND, "background", self.BACKGROUND_COLOR, False)

    def generate_labels(self, nb_images):
        """ Generate random shape labels in order to prepare shape image
        generation; use numpy to generate random indices for each labels, these
        indices will be the positive examples; return a 2D-list

        Parameters
        ----------
        nb_images : integer
            Number of images to label in the dataset
        """
        raw_labels = [np.random.choice(np.arange(nb_images),
                                            int(nb_images/2),
                                            replace=False)
                      for i in range(self.get_nb_labels())]
        labels = np.zeros([nb_images, self.get_nb_labels()], dtype=int)
        for i in range(self.get_nb_labels()):
            labels[raw_labels[i], i] = 1
        return [dict([(i, int(j)) for i, j in enumerate(l)]) for l in labels]

    def populate(self, output_dir, input_dir=None, nb_images=10000, aggregate=False, labelling=True, buf=8):
        """ Populate the dataset with images contained into `datadir` directory

        Parameters
        ----------
        output_dir : str
            Path of the directory where the preprocessed image must be saved
        input_dir : str
            Path of the directory that contains input images
        nb_images: integer
            Number of images that must be added in the dataset
        aggregate: bool
            Aggregate some labels into more generic ones, e.g. cars and bus into the vehicle label
        labelling: boolean
            Dummy parameter: in this dataset, labels are always generated, as images are drawed with them
        buf: integer
            Minimal number of pixels between shape base point and image borders
        """
        shape_gen = self.generate_labels(nb_images)
        for i, image_label in enumerate(shape_gen):
            bg_color = np.random.randint(0, 255, 3).tolist()
            shape_specs = []
            for l in image_label.items():
                if l:
                    shape_color = np.random.randint(0, 255, 3).tolist()
                    x, y = np.random.randint(buf, self.image_size - buf - 1, 2).tolist()
                    shape_size = np.random.randint(buf, self.image_size // 4)
                    shape_specs.append([shape_color, x, y, shape_size])
                else:
                    shape_specs.append([None, None, None, None])
            self.add_image(i, bg_color, shape_specs, image_label)
            self.draw_image(i, output_dir)

    def add_image(self, image_id, background, specifications, labels):
        """ Add a new image to the dataset with image id `image_id`; an image
        in the dataset is represented by an id, a list of shape specifications,
        a background color and a list of 0-1 labels (1 if the i-th label is on
        the image, 0 otherwise)

        Parameters
        ----------
        image_id : integer
            Id of the new image
        background : list
            List of three integer between 0 and 255 that designs the image
        background color
        specifications : list
            Image specifications, as a list of shapes (color, coordinates and
        size)
        labels : list
            List of 0-1 values, the i-th value being 1 if the i-th label is on
        the new image, 0 otherwise; the label list length correspond to the
        number of labels in the dataset
        """
        if image_id in self.image_info:
            utils.logger.error("Image {} already stored into the label set.".format(image_id))
            return None
        self.image_info.append({"background": background,
                                "shape_specs": specifications,
                                "labels": labels})

    def draw_image(self, image_id, datapath):
        """Draws an image from the specifications of its shapes and saves it on
        the file system to `datapath`

        Save labels as mono-channel images on the file system by using the label ids

        Parameters
        ----------
        image_id : integer
            Image id
        datapath : str
            String that characterizes the repository in which images will be stored
        """
        image_info = self.image_info[image_id]

        image = np.ones([self.image_size, self.image_size, 3], dtype=np.uint8)
        image = image * np.array(image_info["background"], dtype=np.uint8)
        label = np.full([self.image_size, self.image_size], self.BACKGROUND, dtype=np.uint8)

        # Get the center x, y and the size s
        if image_info["labels"][self.SQUARE]:
            color, x, y, s = image_info["shape_specs"][self.SQUARE]
            color = tuple(map(int, color))
            image = cv2.rectangle(image, (x - s, y - s), (x + s, y + s), color, -1)
            label = cv2.rectangle(label, (x - s, y - s), (x + s, y + s), self.SQUARE, -1)
        if image_info["labels"][self.CIRCLE]:
            color, x, y, s = image_info["shape_specs"][self.CIRCLE]
            color = tuple(map(int, color))
            image = cv2.circle(image, (x, y), s, color, -1)
            label = cv2.circle(label, (x, y), s, self.CIRCLE, -1)
        if image_info["labels"][self.TRIANGLE]:
            color, x, y, s = image_info["shape_specs"][self.TRIANGLE]
            color = tuple(map(int, color))
            x, y, s = map(int, (x, y, s))
            points = np.array([[(x, y - s),
                                (x - s / math.sin(math.radians(60)), y + s),
                                (x + s / math.sin(math.radians(60)), y + s),]],
                              dtype=np.int32)
            image = cv2.fillPoly(image, points, color)
            label = cv2.fillPoly(label, points, self.TRIANGLE)
        image_filename = os.path.join(datapath, "images", "shape_{:05}.png".format(image_id))
        self.image_info[image_id]["image_filename"] = image_filename
        cv2.imwrite(image_filename, image)
        label_filename = os.path.join(datapath, "labels", "shape_{:05}.png".format(image_id))
        self.image_info[image_id]["label_filename"] = label_filename
        cv2.imwrite(label_filename, label)
