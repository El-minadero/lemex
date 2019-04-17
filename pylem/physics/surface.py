'''
Created on Oct 4, 2018

@author: kevinmendoza
'''
import numpy as np
from scipy import interpolate

from pylem.physics.base import GeoFunction, GeoMatrix
from pylem.physics.landscape import _LandscapeMatrix

class FromFileElevation():
    
    def __init__(self,**kwargs):
        pass
    
    def get_elevation(self,coordinates):
        pass

class RandomElevation():
    required_keys = ['seed','Cell Width','X Dimension Extent',
                     'Y Dimension Extent','divisions','mean','weight']
    def __init__(self,**kwargs):
        if all(name in kwargs.keys() for name in self.required_keys):
            self.activate = True
            self.define_interp_target(**kwargs)
            self.define_value_source(**kwargs)
        else:
            self.activate = False
    
    def define_interp_target(self,**kwargs):
        dxy = float(kwargs['Cell Width'])
        self.xy  = np.asarray([float(kwargs['X Dimension Extent']),
                               float(kwargs['Y Dimension Extent'])],dtype=np.float64)
        self.x_vals = np.arange(0,self.xy[0]+dxy,dxy)
        self.y_vals = np.arange(0,self.xy[1]+dxy,dxy)
        
    def define_value_source(self,**kwargs):
        x_points = np.linspace(0,self.xy[0],num=int(kwargs['divisions'])+1)
        y_points = np.linspace(0,self.xy[1],num=int(kwargs['divisions'])+1)
        xx, yy = np.meshgrid(x_points,y_points)
        np.random.seed(seed=int(kwargs['seed']))
        z = np.random.uniform(size=xx.shape,high=float(kwargs['weight'])) + float(kwargs['mean'])

        if z.shape[0]==2:
            k = 1
        elif z.shape[0]==3:
            k = 2
        else:
            k = 3
        self.function = interpolate.RectBivariateSpline(x_points,y_points,z,kx=k,ky=k)
    
    def get_elevation(self,coordinates):
        if not self.activate:
            return 0
        x = coordinates[0]
        y = coordinates[1]
        return self.function.ev(x,y)
    
class GaussianElevation():
    
    def __init__(self,**kwargs):
        pass
    
    def get_elevation(self,*args,**kwargs):
        return 0

class GeoForcing(GeoFunction):

    def __init__(self,**kwargs):
        super().__init__()
        self.init_defaults()
        self.required_keys=['X Center','Y Center','Azimuth','Rate']
        self.create_variables(**kwargs)

    def init_defaults(self):
        c, s = np.cos(0),np.sin(0)
        self.vector_op_dict = {
            'slope' : np.asarray([-1,1]),
            'adjust': np.asarray([3,3]),
            'R'     : np.array(((c,-s),(s,c)))
        }

    def create_variables(self,**kwargs):
        if self.required_keys_exist():
            radians = np.radians(kwargs['Azimuth'])
            c, s = np.cos(radians), np.sin(radians)
            self.vector_op_dict = {
                'slope' : np.asarray([[-1],[1]]),
                'adjust': np.asarray([ kwargs['X Center'], kwargs['Y Center'] ]),
                'R'     : np.asarray(((c,-s),(s,c)))
            }
            self.rate = kwargs['Rate']

    def simulate(self, ix: int, iy: int, matrix :GeoMatrix,x=0,y=0,**kwargs):
        vec = np.asarray([x,y])
        recenter = vec - self.vector_op_dict['adjust']
        align    = self.vector_op_dict['R'].dot(recenter)
        final    = align.dot(self.vector_op_dict['slope'])

        if final < 0:
            matrix.add_elevation(ix,iy,self.rate)


class InitialSurface(GeoFunction):
    
    def __init__(self,kwargs):
        super().__init__()
        self.required_keys.append('type')
        self.activate = False
        if self.required_keys_exist(**kwargs):
            key = kwargs['type']
            self.load_type(key,**kwargs)
            self.activate = True
        
    def load_type(self,key,**kwargs):
        if key=='random':
            self.elevation_map = RandomElevation(**kwargs)
        elif key=='gaussian':
            self.elevation_map = GaussianElevation(**kwargs)
        else:
            self.elevation_map = FromFileElevation(**kwargs)
        
    def simulate(self, ix, iy, matrix: GeoMatrix, x=0, y=0):
        if self.activate:
            z = self.elevation_map.get_elevation(np.asarray([x,y]))
            matrix.set_elevation(ix, iy, z)
