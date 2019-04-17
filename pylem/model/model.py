#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 13:01:12 2018

@author: kevinmendoza
"""
import time
import threading
from pylem.controller.controller import MainController
from pylem.physics.landscape import Landscape
from pylem.physics.surface import InitialSurface, GeoForcing

class MainModel():
    
    def __init__(self):
        pass
    
    def update_surface(self,controller: MainController):
        print('updating plot')
        landscape       = self.generate_landscape(controller)
        initial_surface = self.create_initial_surface_operator(controller)
        geoForcing      = self.create_geoforcing_operator(controller)
        landscape.assign_elevations(initial_surface)
        controller.update_surface(landscape.get_update())

    def start_simulation(self,controller: MainController):
        landscape       = self.generate_landscape(controller)
        initial_surface = self.create_initial_surface_operator(controller)
        physics_list    = self.create_physics_list(controller)
        # update plot
        landscape.assign_elevations(initial_surface)
        controller.update_surface(landscape.get_update())

    def create_geoforcing_operator(self,controller: MainController):
        geoparams = controller.get_geology_params()

    def create_physics_list(self,controller: MainController):
        return None

    def generate_landscape(self,controller: MainController):
        simulation = controller.get_simulation_params()
        return Landscape(simulation)

    def create_initial_surface_operator(self,controller: MainController):
        surface = controller.get_surface_params()
        simulation = controller.get_simulation_params()
        return InitialSurface({**surface,**simulation})



            

