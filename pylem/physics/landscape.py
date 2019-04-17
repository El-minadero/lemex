#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 11:10:19 2018

@author: kevinmendoza
"""

import numpy as np
from pylem.physics.base import GeoSetting, GeoMatrix


def _reduce_nan_matrix(nan_matrix):
    shape      = nan_matrix.shape
    matrix    = nan_matrix[1:shape[0]-1,1:shape[1]-1]
    return matrix

class _LandscapeMatrix(GeoMatrix):
    _dxy_mask = np.asarray([[np.sqrt(2), 1 ,np.sqrt(2)],
                            [1,          0, 1         ],
                            [np.sqrt(2), 1, np.sqrt(2)]])

    _mask_3  = np.arange(0,3,1)

    _ones  = np.ones((1,2),dtype=np.int16)
    def __init__(self,shape=(100,100)):
        super().__init__()
        self._bedrock_map    = np.pad(np.zeros(shape), (1,1),'constant',constant_values=(np.nan,np.nan))
        self._sediment_map   = np.pad(np.zeros(shape), (1,1),'constant',constant_values=(np.nan,np.nan))

    def set_elevation(self,ix,iy,z):
        self._bedrock_map[ix+1,iy+1]=z

    def add_elevation(self,ix,iy,z):
        self._bedrock_map[ix+1,iy+1]=self._bedrock_map[ix+1,iy+1]+z

    def set_sediment(self,ix,iy,z=0,**kwargs):
        self._sediment_map[ix+1,iy+1]=z

    def add_sediment(self,ix,iy,z=0,**kwargs):
        self._sediment_map[ix+1,iy+1]=self._sediment_map[ix+1,iy+1]+z

    def _get_elevation(self):
        return self._bedrock_map + self._sediment_map

    def get_sediment(self,ix,iy,**kwargs):
        return self._sediment_map[ix + 1, iy + 1]

    def get_elevation(self,ix,iy):
        return self._get_elevation()[ix+1,iy+1]

    def get_elevation_matrix(self):
        nan_matrix = self._get_elevation()
        return _reduce_nan_matrix(nan_matrix)

    def get_bedrock_matrix(self):
        nan_matrix = self._bedrock_map
        return _reduce_nan_matrix(nan_matrix)

    def get_sediment_matrix(self):
        nan_matrix = self._sediment_map
        return _reduce_nan_matrix(nan_matrix)

    def get_steepest_cell_neighbor(self,x,y,return_gradient=False):
        elevation     = self._get_elevation()
        arx           = self._mask_3 + x
        ary           = self._mask_3 + y
        sub_elevation_matrix = elevation[np.ix_(arx,ary)]
        normalized_difference = np.divide(sub_elevation_matrix - sub_elevation_matrix[1,1],self._dxy_mask)
        indices       = np.unravel_index(np.nanargmin(normalized_difference),normalized_difference.shape)
        local_indices = np.asarray(indices)
        actual_indices= local_indices - self._ones + np.asarray([x,y])

        if return_gradient:
            gradient       = normalized_difference[local_indices[0],local_indices[1]]
            actual_indices = (actual_indices.ravel(),gradient)

        return actual_indices.ravel()
        
            
class Landscape(GeoSetting):
    default_dict = {
        'X Dimension Extent': 100,
        'Y Dimension Extent': 100,
        'Cell Width'  : 10,
    }

    def __init__(self,kwargs):
        super().__init__()
        self.required_keys=['X Dimension Extent', 'Y Dimension Extent',
                            'Cell Width']
        self.shape = self.__get_indice_dimensions__(**kwargs)
        self.matrix = _LandscapeMatrix(shape=self.shape)
        
    def __get_indice_dimensions__(self, **kwargs):
        if not self.required_keys_exist(**kwargs):
            kwargs = self.default_dict

        x_extent       = float(kwargs['X Dimension Extent'])
        y_extent       = float(kwargs['Y Dimension Extent'])
        self._dxy      = float(kwargs['Cell Width'])

        numx   = int(x_extent / self._dxy)
        numy   = int(y_extent / self._dxy)

        return numy, numx  # x is columns, y is rows

    def get_update(self):
        return self.matrix.get_elevation_matrix()

    def apply_to_nodes(self,function):
        x_index_shuffled = np.random.shuffle(list(range(0,self.shape[0])))
        y_index_shuffled = np.random.shuffle(list(range(0,self.shape[1])))
        for ix in x_index_shuffled:
            for iy in y_index_shuffled:
                function.simulate(ix,iy,self.matrix)
            
    def assign_elevations(self,function):
        dxy = self._dxy
        for ix in range(0,self.shape[0]):
            for iy in range(0,self.shape[1]):
                x=ix*dxy
                y=iy*dxy
                function.simulate(ix,iy,self.matrix,x=x,y=y)
            
            
