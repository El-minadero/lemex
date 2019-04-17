"""
Created on Tue Sep 25 11:09:17 2018

@author: kevinmendoza
"""
import numpy as np

    
class HillslopeCreep():
    def __init__(self,**kwargs):
        self.c =float(kwargs['Gradient Constant'])
        
    def simulate(self,node):
        gradient =node.get_gradient()
        if gradient <= 0:
                new_node=node.get_lowest_node()
                sediment_to_move = np.abs(gradient)*self.c
                new_node.z+=sediment_to_move
                node.z-=sediment_to_move
        
    
class _WaterBot_():
    
    def __init__(self):
        self.sediment      =0
        
    def iterate(self):
        self.iterations+=1
        
    def should_terminate(self):
        return self.iterations > self.max_iterations
                    
class WaterBotSimulate():
    max_iterations = 100
    def __init__(self,*args,**kwargs):
        self.constants = {}
        for key in kwargs.keys():
            self.constants[key]=float(kwargs[key])
 
    def simulate(self,node,**kwargs):
        waterbot = _WaterBot_()
        kwargs['controller']=waterbot
        for iteration in range(0,self.max_iterations):
            kwargs['gradient']= node.get_gradient()
            if kwargs['gradient'] <= 0:
                self.river_running(node=node,**kwargs)
                node = node.get_lowest_node()
            else:
                self.lake_filling(node=node,**kwargs)
    
    def river_running(self,node=None,**kwargs):
        sedimentation_potential   = self.get_deposit_potential(**kwargs)
        elevation_change          = self.change_sediment(sedimentation_potential,**kwargs)
        node.z                   += elevation_change
                
    def lake_filling(self,node=None,**kwargs):
        d_sediment = kwargs['controller'].sediment*0.3
        if d_sediment > 1e-4:
            node.z+= d_sediment
            kwargs['controller'].sediment-=d_sediment
                
    def change_sediment(self,sedimentation_potential,waterbot=None,**kwargs):
        # if sedimentation potential is negative, it wants a lot of sediment
        # if sedimentation potential is positive, it needs to get rid of sediment
        sed_disch = self.constants['Sediment Discharge %'] / 100.0
        # dump all sediment
        if sedimentation_potential > waterbot.sediment:
            sediment = waterbot.sediment*sed_disch
            waterbot.sediment-=sediment
            return sediment
        #  dump an amount of sediment
        elif sedimentation_potential > 0:
            waterbot.sediment-= sedimentation_potential*sed_disch
            return sedimentation_potential*sed_disch
        # Erode to match sediment potential
        else:
            waterbot.sediment-=sedimentation_potential
            return sedimentation_potential
        
            
    def get_deposit_potential(self,waterbot=None,gradient=0,**kwargs):
        expected_load    = self.calculate_expected_load(gradient=gradient,**kwargs)
        dz               = waterbot.sediment - expected_load
        return dz
        
    def calculate_expected_load(self,gradient=0,**kwargs):
        grad_offset = self.constants['Gradient Offset']
        grad_const  = self.constants['Gradient Constant']
        exponent    = self.constants['Exponential Law']
        base_offset = self.constants['Base Offset']
        
        gradient = np.abs(gradient)+ grad_offset
        return grad_const * np.power(gradient,exponent) + base_offset
    
