# @chick_b0t

A Twitter bot for finding eggs and hens in your chicken coop.

## Getting Started

### Dependencies

Install the Tensorflow models repository inside the top level of this
project.
* [TensorFlow Models](https://github.com/tensorflow/models) - Follow the installation instructions for that project.

Other dependencies:
* Tweepy
* todo document the rest of the dependencies

### Configuration

The scripts in this project will require that you create you own
config.py for holding twitter api keys. Here is an example:

'''
consumer_key = YOUR_KEY
consumer_secret = YOUR_SECRET
access_token = YOUR_ACCESS_TOKEN
access_secret = YOUR_ACCESS_SECRET
twitter_user = TARGET_TWITTER_USER
'''

## Code

There are three python scripts in this project:

### get_images.py

This script downloads images from a given twitter feed. The images are
used in this project to for object detection of eggs and hens.

Todo: this script needs some tidy up.

#### Use:

'''
python get_images.py
'''

### make_tfrecord.py

Builds a tensorflow record file for use in training an object
detection model. Required are the images contained in data/train and
data/test and the associated xml files that denote the location of
bounding boxes for the eggs and hens.

#### Use:

'''
     python make_tfrecord.py --output_path=/path/to/outfile.record
'''

### tweet_it_od.py

Downloads most recent tweet from target twitter account, saves the
image from the tweet, passes the image to the trained model
(coop_graph), and tweets the resulting output as a reply to the
original tweet.

#### Use:

'''
python tweet_it_od.py
'''

## Data

There are two directories of images within the data directory of this
project - test and train. Each directory contains jpeg images and some
associated xml files describing the bounding boxes containing eggs and
hens.

## Contributing

Help with improving the dataset that @chick_b0t has been trained on is
very much appreciated. This can be done by labelling images with
bounding boxes containing eggs and hens.

Download the [labelImg](https://github.com/tzutalin/labelImg) tool and
mark up images in the train or test folder that have not yet had
bounding boxes drawn around the eggs and hens.

Please use the class labels "egg" and "hen".

Save the xml files in the same directory as the images.

You can also use the get_images.py script to download images from the
twitter account @chickenpi8 and label those new images.

Submit a pull request!