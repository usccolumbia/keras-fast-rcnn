#!/usr/bin/env python

# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick
# --------------------------------------------------------

"""Train a Fast R-CNN network on a region of interest database."""

import _init_paths
#from fast_rcnn.train import get_training_roidb, train_net
from fast_rcnn.config import cfg, cfg_from_file, cfg_from_list, get_output_dir
from datasets.factory import get_imdb
#import caffe
import argparse
import pprint
import numpy as np
import sys
# ------------
import roi_data_layer.roidb as rdl_roidb
from keras_model import prepare_data 


def get_training_roidb(imdb):
    """Returns a roidb (Region of Interest database) for use in training."""
    if cfg.TRAIN.USE_FLIPPED:
        print 'Appending horizontally-flipped training examples...'
        imdb.append_flipped_images()
        print 'done'

    print 'Preparing training data...'
    rdl_roidb.prepare_roidb(imdb)
    print 'done'

    return imdb.roidb



def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Train a Fast R-CNN network')
    parser.add_argument('--gpu', dest='gpu_id',
                        help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--solver', dest='solver',
                        help='solver prototxt',
                        default=None, type=str)
    parser.add_argument('--iters', dest='max_iters',
                        help='number of iterations to train',
                        default=40000, type=int)
    #parser.add_argument('--weights', dest='pretrained_model',
    #                    help='initialize with pretrained model weights',
    #                    default=None, type=str)
    parser.add_argument('--cfg', dest='cfg_file',
                        help='optional config file',
                        default=None, type=str)
    parser.add_argument('--imdb', dest='imdb_name',
                        help='dataset to train on',
                        default='voc_2007_trainval', type=str)
    #parser.add_argument('--rand', dest='randomize',
    #                    help='randomize (do not use a fixed seed)',
    #                    action='store_true')
    parser.add_argument('--set', dest='set_cfgs',
                        help='set config keys', default=None,
                        nargs=argparse.REMAINDER)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    print('Called with args:')
    print(args)

    if args.cfg_file is not None:
        cfg_from_file(args.cfg_file)
    if args.set_cfgs is not None:
        cfg_from_list(args.set_cfgs)

    print('Using config:')
    pprint.pprint(cfg)
    '''
    if not args.randomize:
        # fix the random seeds (numpy and caffe) for reproducibility
        np.random.seed(cfg.RNG_SEED)
        caffe.set_random_seed(cfg.RNG_SEED)
    '''
    # set up caffe
    #caffe.set_mode_gpu()
    #if args.gpu_id is not None:
    #    caffe.set_device(args.gpu_id)

    #  gpu_id not is necessary after setting up CUDA_VISIBLE_DEVICES ??

    imdb = get_imdb(args.imdb_name)
    print 'Loaded dataset `{:s}` for training'.format(imdb.name)
    roidb = get_training_roidb(imdb)

    output_dir = get_output_dir(imdb, None)
    print 'Output will be saved to `{:s}`'.format(output_dir)

    print 'Computing bounding-box regression targets...'
    # bbox_means, bbox_stds haven't been used so far
    bbox_means, bbox_stds = rdl_roidb.add_bbox_regression_targets(roidb)
    print 'done'
    
    print 'loading images ...'
    prepare_data.add_image_data(roidb)
    
    print 'Computing normalized roi boxes coordinates ...'
    prepare_data.add_normalized_bbox(roidb)
    print 'done'

    #train_net(args.solver, roidb, output_dir,
    #          pretrained_model=args.pretrained_model,
    #          max_iters=args.max_iters)
