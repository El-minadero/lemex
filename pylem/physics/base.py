'''
Created on Oct 4, 2018

@author: kevinmendoza
'''

class GeoMatrix:

    def __init__(self,**kwargs):
        pass

    def set_elevation(self,ix,iy,z):
        raise NotImplementedError('please implement the \'set elevation\' method')

    def add_elevation(self,ix,iy,z):
        raise NotImplementedError('please implement the \'add elevation\' method')

    def set_sediment(self,ix,iy,**kwargs):
        raise NotImplementedError('please implement the \'set sediment\' method')

    def add_sediment(self,ix,iy,**kwargs):
        raise NotImplementedError('please implement the \'add sediment\' method')

    def get_sediment(self,ix,iy,**kwargs):
        raise NotImplementedError('please implement the \'get sediment\' method')

    def get_elevation(self,ix,iy):
        raise NotImplementedError('please implement the \'get elevation\' method')

    def get_elevation_matrix(self):
        raise NotImplementedError('please implement the \'get elevation matrix\' method')

    def get_bedrock_matrix(self):
        raise NotImplementedError('please implement the \'get bedrock matrix\' method')

    def get_sediment_matrix(self):
        raise NotImplementedError('please implement the \'get sediment matrix\' method')

    def get_steepest_cell_neighbor(self,x,y,return_gradient=False,**kwargs):
        raise NotImplementedError('please implement the \'get steepest cell neighbor\' method')

class GeoSetting:

    def __init__(self,**kwargs):
        self.required_keys = []

    def required_keys_exist(self,**kwargs):
         exists = all(name in kwargs.keys() for name in self.required_keys)
         return exists

class GeoFunction(GeoSetting):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.required_keys = []
    
    def simulate(self, ix: int, iy: int, matrix :GeoMatrix,x=0,y=0,**kwargs):
        pass

