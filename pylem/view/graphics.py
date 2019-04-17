#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 13:27:12 2018

@author: kevinmendoza
"""
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QGridLayout
from pylem.view._view_ import FieldMonitor
from pylem.controller.controller import MainController
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np

class Surface(QGridLayout):
    
    
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.align_widgets()
        
    def add_controller(self,controller: MainController):
        controller._update_iterations       = self.update_iterations
        controller._update_total_iterations = self.update_total_iterations
        self.viewbox.add_controller(controller)
        
    def create_widgets(self):
        self.viewbox           = CustomPlot()
        self.simulation_readout= FieldMonitor(name="Iterations:",default_value='0')
        self.iteration_count   = FieldMonitor(name="Years:",default_value='0')
        
    def align_widgets(self):
        self.setColumnMinimumWidth(0,200)
        self.setColumnMinimumWidth(1,200)
        self.setRowMinimumHeight(0,400)
        self.setRowMinimumHeight(1,100)
        self.addWidget(self.viewbox,     0,0,1,3)
        self.addLayout(self.simulation_readout,1,0,1,1)
        self.addLayout(self.iteration_count,1,2,1,1)
        
    def update_iterations(self,iterations,year):
        str1 = str(iterations) + '/' + str(self.total_iterations)
        str2 = str(year)       + '/' + str(self.total_year)
        self.simulation_readout.update_field(str1)
        self.iteration_count.update_field(str2)
        
    def update_total_iterations(self,total_iterations,total_year):
        self.total_year       = total_year
        self.total_iterations = total_iterations
        
        
class CustomPlot(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        self.boundary_object = BoundaryObject()
        color_scale     = ColorScaleObject()
        #self.fault_trace     = Fault2Coordinates(boundary_object)
        self.surface         = SurfacePlot(color_scale,self.boundary_object)
        self.xygrid          = XYGrid(self.boundary_object)
        #self.addItem(self.fault_trace)
        self.addItem(self.surface)
        self.addItem(self.xygrid)
        
    def add_controller(self,controller):
        controller._update_map     = self.update_map
        controller._update_surface = self.update_surface
        controller._update_fault   = self.update_fault

    def update_map(self,controller):
        self.boundary_object.update(controller)
        self.xygrid.controller_update(controller)

    def update_fault(self,controller):
        pass

    def update_surface(self,matrix):
        self.surface.update_surface(matrix)



class BoundaryObject:

    corner_array = np.asarray([1,1])

    def __init__(self):
        self.upper = self.corner_array
        self.lower = self.corner_array * -1
        self.connected = False

    def update(self,controller: MainController):
        self.connected  = True
        extent_dict     = controller.get_simulation_params()
        extent          = np.asarray([extent_dict['X Dimension Extent'], extent_dict['Y Dimension Extent']])
        self.cells      = [extent[0]/extent_dict['Cell Width'],extent[1]/extent_dict['Cell Width']]
        ratio           = extent[0]/extent[1]

        if ratio < 1.0:
            self.upper      = [ratio ,  1]
            self.lower      = [-ratio, -1]
        else:
            self.upper      = [ 1,  1/ratio]
            self.lower      = [-1, -1/ratio]

    def create_xseries(self):
        return np.linspace(self.lower[0],self.upper[0],num=int(self.cells[0]))

    def create_yseries(self):
        return np.linspace(self.lower[1],self.upper[1],num=int(self.cells[1]))

    def scale_xy_grid(self,other: gl.GLGridItem):
        other.setSize(x=self.upper[0]-self.lower[0],y=self.upper[1]-self.lower[1],z=1)

class ColorScaleObject:

    CUTOFF = 1e-16
    def __init__(self):
        self.color_mapping = cm.ScalarMappable(cmap=plt.get_cmap('plasma') )

    def convert_to_colors(self,matrix):
        min = np.min(matrix)
        max = np.max(matrix)
        if min - max > self.CUTOFF:
            values = (matrix - min) / (max - min)
        else:
            values = matrix

        return self.color_mapping.to_rgba(values)


class SurfacePlot(gl.GLSurfacePlotItem):

    def __init__(self,color,boundary):
        super().__init__()
        self.color    = color
        self.boundary = boundary
        self.z_scale   = 1
        self.z_offset  = 0

    def update_surface(self,matrix):
        if self.boundary.connected:
            xs      = self.boundary.create_xseries()
            ys      = self.boundary.create_yseries()
            if xs.shape[0] > 0 and ys.shape[0] > 0:
                values  = (matrix - self.z_offset) * self.z_scale
                colors  = self.color.convert_to_colors(values)
                self.setData(x=ys, y=xs, z=values,colors=colors)

class XYGrid(gl.GLGridItem):

    def __init__(self,boundary_object):
        super().__init__()
        self.boundary_object = boundary_object

    def controller_update(self,controller: MainController):
        self.boundary_object.scale_xy_grid(self)



class Fault2Coordinates(gl.GLGridItem):

    def __init__(self,boundary_object):
        super().__init__()
        self.boundary_object=boundary_object

