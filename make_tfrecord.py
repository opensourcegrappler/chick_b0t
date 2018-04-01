import tensorflow as tf
import os
import xml.etree.cElementTree as ET

import sys

#required so python can find the utils
sys.path.append('models/research')
from object_detection.utils import dataset_util

#setup arguments
flags = tf.app.flags
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
FLAGS = flags.FLAGS

#dictionary of class labels
LABEL_DICT =  {
    "egg" : 1,
    "hen" : 2
    }

#build an example ready for writing to .record file
def create_tf_example(example):
    #parse the xml tree for this example
    tree = ET.ElementTree(file=os.path.join('data/train',example))

    #get heigh, width, filename 
    for elem in tree.iterfind('size/width'):
        width = long(elem.text)
    for elem in tree.iterfind('size/height'):
        height = long(elem.text)
    for elem in tree.iterfind('filename'):
        filename = elem.text

    #encode the image data
    with tf.gfile.GFile(os.path.join('data/train',filename), 'rb') as fid:
        encoded_image = fid.read()
    encoded_image_data = encoded_image # Encoded image bytes

    #set image format
    image_format = b'jpeg' # b'jpeg' or b'png'

    xmins = [] # List of normalized left x coordinates in bounding box (1 per box)
    xmaxs = [] # List of normalized right x coordinates in bounding box
             # (1 per box)
    ymins = [] # List of normalized top y coordinates in bounding box (1 per box)
    ymaxs = [] # List of normalized bottom y coordinates in bounding box
             # (1 per box)
    classes_text = [] # List of string class name of bounding box (1 per box)
    classes = [] # List of integer class id of bounding box (1 per box)

    #find and append normalised coordinates of boxes
    for xmin in tree.iter('xmin'):
        xmins.append(float(xmin.text)/width)

    for ymin in tree.iter('ymin'):
        ymins.append(float(ymin.text)/height)

    for xmax in tree.iter('xmax'):
        xmaxs.append(float(xmax.text)/width)

    for ymax in tree.iter('ymax'):
        ymaxs.append(float(ymax.text)/height)

    #set class and associated text name
    for child in tree.iter('name'):
        if child.text=='egg':
            classes.append(1)
        else:
            classes.append(2)
        classes_text.append(child.text)

    #add to the tf example
    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_image_data),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))

    return tf_example


def main(_):
    #declare the record writer
    writer = tf.python_io.TFRecordWriter(FLAGS.output_path)

    #find all xml files
    files = os.listdir('data/train')

    #loop through the images
    for xml in files:
        if not xml.endswith('.xml'): continue # if not xml file move on
        tf_example = create_tf_example(xml) # encode example
        writer.write(tf_example.SerializeToString()) # write to file

    #close the writer
    writer.close()

#run
if __name__ == '__main__':
  tf.app.run()

