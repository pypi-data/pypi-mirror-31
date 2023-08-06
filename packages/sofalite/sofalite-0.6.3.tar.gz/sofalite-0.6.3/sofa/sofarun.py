#!/usr/bin/python3
import numpy as np
import csv
import json
import sys
import argparse
import multiprocessing as mp
import glob
import os
from functools import partial
from sofa.sofa_config import *
from sofa.sofa_print import * 
from sofa.sofa_record import * 
from sofa.sofa_preprocess import * 
from sofa.sofa_analyze import * 
from sofa.sofa_viz import * 

def main():
    logdir = './sofalog/'
    command = None
    usr_command = None
    sys.stdout.flush()

    
    if sys.version_info < (3,4) :
        print_error("Your Python version is %s.%s.%s" % sys.version_info[:3])
        print_error("But SOFA requires minimum version of Python 3.4.")
        quit()

    parser = argparse.ArgumentParser(description='SOFA')
    parser.add_argument(
        '--logdir',
        metavar='/path/to/logdir/',
        type=str,
        required=False,
        help='path to the directory of SOFA logged files')
    parser.add_argument(
        '--gpu_filters',
        metavar='"keyword1:color1,keyword2:color2"',
        type=str,
        required=False,
        help='A string of list of pairs of keyword and color')
    parser.add_argument(
        '--cpu_filters',
        metavar='"keyword1:color1,keyword2:color2"',
        type=str,
        required=False,
        help='A string of list of pairs of keyword and color')
    parser.add_argument('--cpu_top_k', metavar='N', type=int, required=False,
                        help='K functions of the highest overheads')
    parser.add_argument('--gpu_time_offset', metavar='N', type=int, required=False,
                        help='timestamp offset between CPU and GPU, +N or -N')
    parser.add_argument(
        '--plot_ratio',
        metavar='N',
        type=int,
        required=False,
        help='Down-sample ratio for points in scatter plot: 1, 10, 100, etc..')
    parser.add_argument(
        '--viz_port',
        metavar='N',
        type=int,
        required=False,
        help='Specify port of web server for browsing visualization results')
    parser.add_argument('--profile_all_cpus', dest='profile_all_cpus', action='store_true')
    parser.set_defaults(profile_all_cpus=False)
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.set_defaults(verbose=False)
    parser.add_argument(
        'command',
        type=str,
        nargs=1,
        metavar='<stat|record|report|preprocess|analyze|viz>')
    parser.add_argument(
        'usr_command',
        type=str,
        nargs='?',
        metavar='<PROFILED_COMMAND>')

    cfg = SOFA_Config()

    args = parser.parse_args()
    if args.logdir is not None:
        logdir = args.logdir + '/'

    if args.command is not None:
        command = args.command[0]
    if args.usr_command is not None:
        usr_command = args.usr_command

    if args.verbose is not None:
        cfg.verbose = args.verbose

    if args.plot_ratio is not None:
        cfg.plot_ratio = args.plot_ratio

    if args.gpu_time_offset is not None:
        cfg.gpu_time_offset = args.gpu_time_offset
    
    if args.viz_port is not None:
        cfg.viz_port = args.viz_port

    if args.profile_all_cpus is not None:
        cfg.profile_all_cpus = args.profile_all_cpus


    cfg.cpu_filters.append(Filter('nv_alloc_system_pages', 'red'))
    cfg.cpu_filters.append(Filter('bus', 'cornflowerblue'))
    if args.cpu_filters is not None:
        pairs = args.cpu_filters.split(',')
        for pair in pairs:
            cfg.cpu_filters.append(
                Filter(str(pair.split(':')[0]), str(pair.split(':')[1])))
    else:
        cfg.cpu_filters.append(Filter('idle', 'black'))

    cfg.gpu_filters.append(Filter('copyKind_1_', 'Red'))
    cfg.gpu_filters.append(Filter('copyKind_2_', 'Peru'))
    cfg.gpu_filters.append(Filter('copyKind_10_', 'Purple'))
    if args.gpu_filters is not None:
        pairs = args.gpu_filters.split(',')
        for pair in pairs:
            cfg.gpu_filters.append(
                Filter(str(pair.split(':')[0]), str(pair.split(':')[1])))
    else:
        cfg.gpu_filters.append(Filter('_fw_', 'yellow'))
        cfg.gpu_filters.append(Filter('_bw_', 'orange'))
        cfg.gpu_filters.append(Filter('AllReduceKernel', 'indigo'))

    print("Ratio of raw data points to plotting points : %d" % cfg.plot_ratio)
    for filter in cfg.cpu_filters:
        print_info("CPU filter = %s:%s" % (filter.keyword, filter.color))
    for filter in cfg.gpu_filters:
        print_info("GPU filter = %s:%s" % (filter.keyword, filter.color))

    print_info("logdir = %s" % logdir)

    if command == 'stat':
        sofa_record(usr_command, logdir, cfg)
        sofa_preprocess(logdir, cfg)
        sofa_analyze(logdir, cfg)
    elif command == 'record':
        sofa_record(usr_command, logdir, cfg)
    elif command == 'preprocess':
        sofa_preprocess(logdir, cfg)
    elif command == 'analyze':
        sofa_analyze(logdir, cfg)
    elif command == 'viz':
        sofa_viz(logdir, cfg)
    elif command == 'report':
        sofa_preprocess(logdir, cfg)
        sofa_analyze(logdir, cfg)
        sofa_viz(logdir, cfg)
    else:
        print_error("Cannot recognized SOFA-command [%s]" % command)
        quit()
    #sofa_analyze(logdir, cfg)
