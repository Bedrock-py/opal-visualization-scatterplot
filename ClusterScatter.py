#****************************************************************
#
# Copyright (c) 2015, Georgia Tech Research Institute
# All rights reserved.
#
# This unpublished material is the property of the Georgia Tech
# Research Institute and is protected under copyright law.
# The methods and techniques described herein are considered
# trade secrets and/or confidential. Reproduction or distribution,
# in whole or in part, is forbidden except by the express written
# permission of the Georgia Tech Research Institute.
#****************************************************************/

from visualization.utils import *
import json, random
import vincent
import numpy as np
import pandas as pd
from visualization.colors import brews

class ClusterScatter(Visualization):
    def __init__(self):
        super(ClusterScatter, self).__init__()
        self.inputs = ['matrix.csv', 'assignments.csv']
        self.parameters = ['matrix','assignments']
        self.parameters_spec = [{ "name" : "X feature index", "attrname" : "x_feature", "value" : 0, "type" : "input"},
                                { "name" : "Y feature index", "attrname" : "y_feature", "value" : 1, "type" : "input"} ]
        self.name = 'Cluster Scatterplot'
        self.description = ''

    def initialize(self, inputs):
        # self.features = utils.load_features(inputs['features.txt'])
        self.matrix = load_dense_matrix(inputs['matrix.csv']['rootdir'] + 'matrix.csv')
        self.assignments = load_assignments(inputs['assignments.csv']['rootdir'] + 'assignments.csv')

    def create(self):
        red_mat = self.matrix.ix[:, [self.x_feature,self.y_feature]]
        print red_mat

        cluster_mat = {}
        clusters = map(int, self.assignments)
        if min(clusters) != 0:
            newClusters = []
            for each in clusters:
                newClusters.append(each-1)
            clusters = newClusters
        xData = self.matrix.ix[:,self.x_feature]
        yData = self.matrix.ix[:,self.y_feature]

        for cluster in np.unique(clusters):
            data = zip(xData, yData, clusters)
            clusterData = []
            for each in range(len(data)):
                if data[each][2] == cluster:
                    clusterData.append([data[each][0], data[each][1]])
            cluster_mat[`cluster`] = clusterData


        print cluster_mat
        #vincent portions

        vis = vincent.Chart(data=[1,2], width=600, height=400, iter_idx=0)
        min_x = []
        min_y = []
        max_x = []
        max_y = []

        for key, value in cluster_mat.items():
            print key, ':', len(value)
            data = pd.DataFrame(data=value, columns=['x','y'])
            min_all = np.min(data)
            min_x.append(min_all[0])
            min_y.append(min_all[1])
            max_all = np.max(data)
            max_x.append(max_all[0])
            max_y.append(max_all[1])

            temp = vincent.Chart(data=data, width=200, height=150, iter_idx='x').data[0]
            temp.name = key
            vis.data.append(temp)

        vis.data.pop(0)
        min_x = min(min_x)
        min_y = min(min_y)
        max_x = max(max_x)
        max_y = max(max_y)

        x_range = [min_x,max_x]
        y_range = [min_y,max_y]

        scales = zip(x_range, y_range)
        print scales
        data = pd.DataFrame(data=scales, columns=['x','y'])
        temp = vincent.Chart(data=data, width=200, height=150, iter_idx='x').data[0]
        temp.name ='scales'
        vis.data.append(temp)

        x_type = 'linear'
        vis.scales += [
                    vincent.Scale(name='x', type=x_type, range='width', zero=False,
                          domain=vincent.DataRef(data='scales', field="data.idx")),
                    vincent.Scale(name='y', range='height', nice=True, zero=False,
                          domain=vincent.DataRef(data='scales', field="data.val")),
                    vincent.Scale(name='color', range='category10', type='ordinal',
                          domain=cluster_mat.keys())

                ]
        vis.axes += [vincent.Axis(type='x', scale='x'),
                    vincent.Axis(type='y', scale='y')]

        ### iterate
        for key, value in cluster_mat.items():

            from_ = vincent.MarkRef(
                        data=key,
                        transform=[vincent.Transform(type='facet', keys=['data.col'])])
            
            enter_props = vincent.PropertySet(
                        x=vincent.ValueRef(scale='x', field="data.idx"),
                        y=vincent.ValueRef(scale='y', field="data.val"),
                        size=vincent.ValueRef(value=35),
                        fill=vincent.ValueRef(value=brews['Category10'][int(key)]),
                        opacity=vincent.ValueRef(value=.8))
            
            marks = [vincent.Mark(type='symbol',
                                  properties=vincent.MarkProperties(enter=enter_props))]
            mark_group = vincent.Mark(type='group', from_=from_, marks=marks)
            vis.marks.append(mark_group)

        vis.legend(title="Clusters")

        self.json = vis.to_json()


        vis_id = 'vis_' + get_new_id()

        script = '<script> spec =' + self.json + ';vg.parse.spec(spec, function(chart) { chart({el:"#' + vis_id + '"}).update(); });</script>'
        


        return {'data':script,'type':'default', 'id': vis_id, 'title': 'Scatterplot'}



