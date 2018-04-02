#!/usr/bin/python

#import api keys
import config

import tweepy
import wget
import pathlib

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
from PIL import Image

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("models/research")
from object_detection.utils import ops as utils_ops

if tf.__version__ < '1.4.0':
  raise ImportError('Please upgrade your tensorflow installation to v1.4.* or later!')

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
#this needs to be done after the utils import above to avoid some backend error
from matplotlib import pyplot as plt

def tweet(eggcount,hencount,imagepath,status_id):

  if eggcount==1:
    eggs = "Egg"
  else:
    eggs = "Eggs"

  if hencount==1:
    hens = "Hen"
  else:
    hens = "Hens"

  if eggcount==0 and hencount==0:
    return
  else:
    api.update_with_media(imagepath,status="@{} {} {} and {} {}".format(config.twitter_user,eggcount,eggs,hencount,hens),in_reply_to_status_id=status_id)
  return

auth = tweepy.OAuthHandler(config.consumer_key,config.consumer_secret)
auth.set_access_token(config.access_token,config.access_secret)

api = tweepy.API(auth)

tweets = api.user_timeline(screen_name=config.twitter_user,
                           count=1, include_rts=False,
                           exclude_replies=True)

outdir = "image/"


# What model to use.
MODEL_NAME = 'coop_graph'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'labels.pbtxt')

NUM_CLASSES = 2

#load the frozen tensorflow model into memory
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
		serialized_graph = fid.read()
		od_graph_def.ParseFromString(serialized_graph)
		tf.import_graph_def(od_graph_def, name='')

#load the map file
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

#load the image
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)

def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.Session() as sess:
            # Get handles to input and output tensors
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in ['num_detections', 'detection_boxes', 'detection_scores',
                    'detection_classes', 'detection_masks']:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                    tensor_name)
            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
					detection_masks, detection_boxes, image.shape[0], image.shape[1])
                detection_masks_reframed = tf.cast(tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
            # Run inference
            output_dict = sess.run(tensor_dict,feed_dict={image_tensor: np.expand_dims(image, 0)})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict

statusid = ''
for status in tweets:
    
    media = status.entities.get('media',[])
    
    if ("EggCheck_image_" in status.text) and (len(media)>0):
        mediaurl = media[0]['media_url']
        wget.download(mediaurl,out=outdir)
    else:
        print("No eggcheck image")
        continue

    imagename = mediaurl.split('/')[-1]
    filepath = str(outdir+imagename)

    with open("id_file",'r') as fh:
        last_id = fh.readlines()[0]
        
        if str(last_id) == str(status.id):
            print "same as last image"
            os.system("rm image/*")
            exit()

    image_path = "{}{}".format(outdir,imagename)

    image = Image.open(image_path)
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    output_dict = run_inference_for_single_image(image_np, detection_graph)
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
      image_np,
      output_dict['detection_boxes'],
      output_dict['detection_classes'],
      output_dict['detection_scores'],
      category_index,
      instance_masks=output_dict.get('detection_masks'),
      use_normalized_coordinates=True,
      line_thickness=2)
    plt.figure(figsize=IMAGE_SIZE)
    plt.imshow(image_np)
    plt.imsave("{}test.png".format(outdir),image_np)

    i =0
    hencount=0
    eggcount=0
    for score in output_dict['detection_scores']:
      if score>=0.5:
        index = i
        classification = output_dict['detection_classes'][index]
        if classification==1:
            eggcount+=1
        if classification==2:
            hencount+=1
      i+=1

    print "\n{} eggs and {} hens".format(eggcount,hencount)

    tweet(eggcount,hencount,"{}test.png".format(outdir),status.id)

    with open("id_file",'w') as outf:
      outf.write(str(status.id))

    os.system("rm image/*")
