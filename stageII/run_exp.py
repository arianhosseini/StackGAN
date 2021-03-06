from __future__ import division
from __future__ import print_function

import os
import dateutil
import dateutil.tz
import datetime
import argparse
import pprint

from stageII.model import CondGAN
from stageII.trainer import CondGANTrainer
from misc.config import cfg, cfg_from_file
from misc.registry import datastore
from misc.utils import mkdir_p


def parse_args():
    parser = argparse.ArgumentParser(description='Train a GAN network')
    parser.add_argument('--cfg', dest='cfg_file',
                        help='optional config file',
                        default=None, type=str)
    parser.add_argument('--path', dest='data_path',
                        default='/data', type=str)
    parser.add_argument('--gpu', dest='gpu_id',
                        help='GPU device id to use [0]',
                        default=-1, type=int)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    if args.cfg_file is not None:
        cfg_from_file(args.cfg_file)

    if args.gpu_id != -1:
        cfg.GPU_ID = args.gpu_id

    print('Using config:')
    pprint.pprint(cfg)

    now = datetime.datetime.now(dateutil.tz.tzlocal())
    timestamp = now.strftime('%Y_%m_%d_%H_%M_%S')

    datadir = '%s/%s' % (args.data_path, cfg.DATASET_NAME)
    dataset = datastore.create(datadir, cfg)

    print('Using dataset:')
    print(dataset)

    dataset.test = dataset.get_data(os.path.join(datadir, 'test'))
    if cfg.TRAIN.FLAG:
        dataset.train = dataset.get_data(os.path.join(datadir, 'train'))
        ckt_logs_dir = "ckt_logs/%s/%s_%s" % \
            (cfg.DATASET_NAME, cfg.CONFIG_NAME, timestamp)
        mkdir_p(ckt_logs_dir)
    else:
        s_tmp = cfg.TRAIN.PRETRAINED_MODEL
        ckt_logs_dir = s_tmp[:s_tmp.find('.ckpt')]

    model = CondGAN(
        dataset.lr_imsize,
        dataset.hr_lr_ratio
    )

    algo = CondGANTrainer(
        model=model,
        dataset=dataset,
        ckt_logs_dir=ckt_logs_dir
    )

    if cfg.TRAIN.FLAG:
        algo.train()
    else:
        ''' For every input text embedding/sentence in the
        training and test datasets, generate cfg.TRAIN.NUM_COPY
        images with randomness from noise z and conditioning augmentation.'''
        algo.evaluate()
