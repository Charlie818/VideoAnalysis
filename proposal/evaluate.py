#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charlie on 18-4-3

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle
from data_provider.THUMOS14 import THUMOS14

def cal_iou(period1,period2):
    if period1[1] < period2[0] or period2[1] < period1[0]:
        return 0.0
    else:
        intersection = min(period1[1], period2[1]) - max(period1[0], period2[0])
        union = max(period1[1], period2[1]) - min(period1[0], period2[0])
        return intersection / union

def cal_recall(predicts,groundtruth,tiou=0.5,num_proposals=100):
    """
        Implement according to ActivityNet Challenge
        predicts:
        {
        "video_id":{

        "duration":
        "proposals":[
            {'start': , 'end': },
            ....
            ]
        }
        }
    """
    assert len(predicts)==len(groundtruth)
    total_videos=len(predicts)
    total_submission_num_proposals=sum([len(predicts[video]['proposals'])for video in predicts])
    avg_submission_num_proposals=total_submission_num_proposals/total_videos
    ratio=num_proposals/avg_submission_num_proposals
    total_proposals=sum([len(groundtruth[video]['proposals'])for video in groundtruth])
    count_all=0
    count=0
    for vid,info in predicts.iteritems():
        end_idx=int(min(len(info['proposals'])*ratio,len(info['proposals'])))
        predict_proposals=[[proposal['start'],proposal['end']] for proposal in info['proposals'][:end_idx]]
        groundtruth_proposals = [[proposal['start'], proposal['end']] for proposal in groundtruth[vid]['proposals']]

        for gt in groundtruth_proposals:
            count_all+=1
            for pred in predict_proposals:
                if cal_iou(gt,pred)>tiou:
                    count+=1
                    break
    return count/total_proposals

def cal_average_recall(predicts,groundtruth,num_proposals=100):
    print("Total predict proposals",sum([len(predicts[vid]['proposals']) for vid in predicts]))
    print("Total groundtruth proposals", sum([len(groundtruth[vid]['proposals']) for vid in groundtruth]))
    tious=np.arange(0.5,1,0.05)
    ret=[cal_recall(predicts,groundtruth,tiou=t,num_proposals=num_proposals)for t in tious ]
    # print([(t,ret[idx]) for idx,t in enumerate(np.arange(0.5,1,0.05))])
    return sum(ret)/len(ret)

def cal_total_average_recall(predicts,groundtruth,num_proposals=10000):
    # print("Total predict proposals",sum([len(predicts[vid]['proposals']) for vid in predicts]))
    # print("Total groundtruth proposals", sum([len(groundtruth[vid]['proposals']) for vid in groundtruth]))
    tious=np.arange(0.5,1,0.05)
    ret=[cal_recall(predicts,groundtruth,tiou=t,num_proposals=num_proposals)for t in tious ]
    # print([(t,ret[idx]) for idx,t in enumerate(np.arange(0.5,1,0.05))])
    return sum(ret)/len(ret)

def cal_high_quality_average_recall(predicts,groundtruth,num_proposals=100):
    # print("Total predict proposals",sum([len(predicts[vid]['proposals']) for vid in predicts]))
    # print("Total groundtruth proposals", sum([len(groundtruth[vid]['proposals']) for vid in groundtruth]))
    tious=np.arange(0.7,1,0.05)
    ret=[cal_recall(predicts,groundtruth,tiou=t,num_proposals=num_proposals)for t in tious ]
    return sum(ret)/len(ret)


def cal_result(predicts, groundtruth, num_proposals=100):
    print("Total predict proposals", sum([len(predicts[vid]['proposals']) for vid in predicts]))
    print("Total groundtruth proposals", sum([len(groundtruth[vid]['proposals']) for vid in groundtruth]))
    tious = np.arange(0, 1.05, 0.05)
    ret = [cal_recall(predicts, groundtruth, tiou=t, num_proposals=num_proposals) for t in tious]
    return tious,ret

def plot():
    dataset = THUMOS14()
    _, test = dataset.load_in_info()
    pairs = {}

    ret=pickle.load(open(os.path.join(THUMOS14.RES_DIR,'sliding_window_proposal'),'r'))
    tious,recall=cal_result(predicts=ret, groundtruth=test, num_proposals=200)
    print(cal_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_high_quality_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_total_average_recall(predicts=ret, groundtruth=test))
    pairs['Sliding Window']=np.array([tious,recall])

    ret=pickle.load(open(os.path.join(THUMOS14.RES_DIR,'even_proposal'),'r'))
    tious,recall=cal_result(predicts=ret, groundtruth=test, num_proposals=200)
    print(cal_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_high_quality_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_total_average_recall(predicts=ret, groundtruth=test))
    pairs['Even Segment']=np.array([tious,recall])

    ret=pickle.load(open(os.path.join(THUMOS14.RES_DIR,'random_proposal'),'r'))
    tious,recall=cal_result(predicts=ret, groundtruth=test, num_proposals=200)
    print(cal_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_high_quality_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_total_average_recall(predicts=ret, groundtruth=test))
    pairs['Random']=np.array([tious,recall])

    ret=pickle.load(open(os.path.join(THUMOS14.RES_DIR,'turn_proposal'),'r'))
    tious,recall=cal_result(predicts=ret, groundtruth=test, num_proposals=200)
    print(cal_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_high_quality_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_total_average_recall(predicts=ret, groundtruth=test))
    pairs['TURN']=np.array([tious,recall])

    ret=pickle.load(open(os.path.join(THUMOS14.RES_DIR,'tag_proposal'),'r'))
    tious,recall=cal_result(predicts=ret, groundtruth=test, num_proposals=200)
    print(cal_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_high_quality_average_recall(predicts=ret, groundtruth=test, num_proposals=200))
    print(cal_total_average_recall(predicts=ret, groundtruth=test))
    pairs['TAG']=np.array([tious,recall])

    method = {
            'Sliding Window': {'legend': 'DAPs-prop',
                       'color': np.array([102, 166, 30]) / 255.0,
                       'marker': None,
                       'linewidth': 6.5,
                       'linestyle': '-'},
              'Even Segment': {'legend': 'SCNN-prop',
                            'color': np.array([230, 171, 2]) / 255.0,
                            'marker': None,
                            'linewidth': 6.5,
                            'linestyle': '-'},
              'Random': {'legend': 'Sparse-prop',
                              'color': np.array([153, 78, 160]) / 255.0,
                              'marker': None,
                              'linewidth': 6.5,
                              'linestyle': '-'},
              'TAG': {'legend': 'Sliding Window',
                                 'color': np.array([205, 110, 51]) / 255.0,
                                 'marker': None,
                                 'linewidth': 6.5,
                                 'linestyle': '-'},
              'TURN': {'legend': 'Random',
                         'color': np.array([132, 132, 132]) / 255.0,
                         'marker': None,
                         'linewidth': 6.5,
                         'linestyle': '-'}
              }

    fn_size = 20
    legend_size = 20
    legends = ['Random', 'Sliding Window', 'TAG', 'TURN', 'Even Segment']

    plt.figure(num=None, figsize=(12, 10))
    for _key in legends:
        plt.plot(pairs[_key][0, :], pairs[_key][1, :],
                 label=method[_key]['legend'],
                 color=method[_key]['color'],
                 linewidth=method[_key]['linewidth'],
                 linestyle=str(method[_key]['linestyle']),
                 marker=str(method[_key]['marker']))

    plt.ylabel('Recall@AN=200', fontsize=fn_size)
    plt.xlabel('tIoU', fontsize=fn_size)
    plt.grid(b=True, which="both")
    plt.ylim([0, 1])
    plt.xlim([0, 1])
    plt.xticks(np.arange(0.0, 1.1, 0.2))
    plt.legend(legends, loc=3, prop={'size': legend_size})
    plt.setp(plt.axes().get_xticklabels(), fontsize=fn_size)
    plt.setp(plt.axes().get_yticklabels(), fontsize=fn_size)
    plt.savefig(os.path.join(THUMOS14.RES_DIR,'AR'), bbox_inches="tight")
    # plt.show()
if __name__ == '__main__':
    plot()