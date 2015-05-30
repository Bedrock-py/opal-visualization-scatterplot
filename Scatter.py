#****************************************************************
#  File: Scatter.py
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

from ..visualization import VisBase
import utils
import vincent, json


def get_classname():
    return 'Scatter'
    
class Scatter(VisBase):
    def __init__(self):
        super(Scatter, self).__init__()
        self.inputs = ['matrix.csv', 'features.txt']
        self.parameters = ['matrix','features']
        self.parameters_spec = []
        self.name = 'Scatterplot'
        self.description = ''

    def initialize(self, inputs):
        self.features = utils.load_features(inputs['features.txt']['rootdir'] + 'features.txt')
        self.matrix = utils.load_dense_matrix(inputs['matrix.csv']['rootdir'] + 'matrix.csv', names=self.features)

    def create(self):
        scatter = vincent.Scatter(self.matrix, iter_idx=0)
        scatter.colors(brew='Set1')
        scatter.axis_titles(x=self.features[0], y='')
        scatter.legend(title='Features')
        
        self.json = scatter.to_json()
        data = json.loads(self.json)
        dateAxis = False
        for idx, scale in enumerate(data['scales']):
            if scale['name'] == 'x':
                if dateAxis is True:
                    data['scales'][idx]['type'] = 'time'
                else:
                    data['scales'][idx]['zero'] = False
        self.json = json.dumps(data)

        vis_id = 'vis_' + utils.get_new_id()
        script = '<script> spec =' + self.json + ';vg.parse.spec(spec, function(chart) { chart({el:"#' + vis_id + '"}).update(); });</script>'
        
        return {'data':script,'type':'default', 'id': vis_id, 'title': 'Scatterplot'}
