#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 13:00:46 2018

@author: kevinmendoza
"""
from PyQt5.QtWidgets import QGridLayout, QPushButton, QLabel, QComboBox
from pylem.view._view_ import Field, FieldComboBox, UnitField
from pylem.controller.controller import MainController, BriefParams
import pylem.view._view_ as v


class SimulationParams(QGridLayout):
    
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.align_widgets()
        
    def create_widgets(self):
        self.title = QLabel("Simulation Parameters")
        self.title.setFont(v.get_mega_bold())
        self.buttons    = Buttons()
        self.surface_init  = SurfaceParamView()
        self.unit_params= UnitParameters()
        self.sim_params = SimParams()
        
    def align_widgets(self):
        self.addWidget(self.title,       0,0,1,1)
        self.addLayout(self.unit_params, 1,0,1,1)
        self.addLayout(self.buttons,     2,0,1,1)
        self.addLayout(self.surface_init,3,0,1,1)
        self.addLayout(self.sim_params  ,4,0,1,1)
        
    def add_controller(self,controller: MainController):
        self.buttons.add_controller(controller)
        self.surface_init.add_controller(controller)
        self.unit_params.add_controller(controller)
        self.sim_params.add_controller(controller)
        
        
class Buttons(QGridLayout):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.align_widgets()
        
    def create_widgets(self):
        self.button = QPushButton('Start Simulation')
        
    def align_widgets(self):
        self.addWidget(self.button, 0, 0, 1, 1)
        
    def add_controller(self,controller: MainController):
        self.button.clicked.connect(controller.start_simulation)

class SurfaceParamView(QGridLayout):
    keys=[
        'random',
        'gaussian',
        'from file'
        ]
    def __init__(self):
        super().__init__()
        self.current_layout='random'
        self.create_widgets()
        self.align_widgets()
    
    def create_widgets(self):
        self.label = QLabel('Surface Initial Conditions')
        self.label.setFont(v.get_bold_font())
        self.layouts = {
            'random'   : RandomGrid(),
            'gaussian' : Gaussian(),
            'from file': FromFile()
            }
        
        self.comboBox = QComboBox()
        for initial_type in self.keys:
            self.comboBox.addItem(initial_type)
            
        self.comboBox.activated.connect(self.change_type)
        
    def align_widgets(self):
        self.addWidget(self.label,0,0)
        self.addWidget(self.comboBox,0,2)
        for entry in self.layouts.values():
            self.addLayout(entry,1,0,2,2)
        for entry in self.layouts.values():
            entry.flipstate()
            entry.params.update = self.set_params
        
    def change_type(self,text):
        key = self.keys[text]
        self.layouts[self.current_layout].flipstate()
        self.layouts[key].flipstate()
        self.current_layout=key
        self.set_params()
        self.controller.update()

    def init_default_state(self):
        self.layouts[self.current_layout].flipstate()
        self.set_params()
        self.controller.update()
        
    def add_controller(self,controller: MainController):
        for layout in self.layouts.values():
            layout.add_controller(controller)
        self.controller = controller
        self.init_default_state()

    def set_params(self):
        parameters = {'type': self.current_layout }
        new_params = self.layouts[self.current_layout].get_params()
        parameters = {**parameters,**new_params}
        self.controller.set_surface_params(parameters)
        
class RandomGrid(QGridLayout):
    
    def __init__(self):
        super().__init__()
        self.show = False
        self.params = BriefParams()
        self.create_widgets()
        self.align_widgets()
        self.hide()
        
    def create_widgets(self):
        self.divisions = Field(name='divisions',default_value=1)
        self.seed      = Field(name='seed',default_value=1)
        self.weight    = UnitField(name='weight',default_value=1,unit_layout='space')
        self.mean      = UnitField(name='mean',default_value=0,unit_layout='space')
        
        self.divisions.add_controller(self.params.change_param)
        self.seed.add_controller(self.params.change_param)
        self.weight.add_controller(self.params.change_param)
        self.mean.add_controller(self.params.change_param)
        
    def align_widgets(self):
        self.addLayout(self.seed,0,0)
        self.addLayout(self.divisions,0,1)
        self.addLayout(self.weight,1,0)
        self.addLayout(self.mean,1,1)
        
    def hide(self):
        self.divisions.setHidden(self.show)
        self.seed.setHidden(self.show)
        self.weight.setHidden(self.show)
        self.mean.setHidden(self.show)
        
    def flipstate(self):
        self.show = not self.show
        self.hide()
        
    def get_params(self):
        return self.params.get_param()

    def get_state(self):
        return self.show

    def add_controller(self,controller):
        controller.add_space_unit(self.update_space)
        controller.add_time_unit(self.update_time)

    def update_time(self,multiplier,**kwargs):
        pass

    def update_space(self,multiplier,**kwargs):
        self.weight.multiply_and_set_value(multiplier,**kwargs)
        self.mean.multiply_and_set_value(multiplier,**kwargs)

class Gaussian(QGridLayout):
    
    def __init__(self):
        super().__init__()
        self.show = False
        self.params = BriefParams()
        self.create_widgets()
        self.align_widgets()
        self.hide()
        
    def create_widgets(self):
        self.label   = QLabel('f(x,y)= A*e ^ { -b ( c* x^2 + d*y^2 )}')
        self.weight  = UnitField(name='weight:(A)',default_value=1,unit_layout='space')
        self.xy_ratio= Field(name='xy_ratio:(c/d)',default_value=1)
        self.decay   = Field(name='decay:(b)',default_value=1)
        self.rot     = Field(name='xy rotation:(degrees)',default_value=0)
        
        self.weight.add_controller(self.params.change_param)
        self.xy_ratio.add_controller(self.params.change_param)
        self.decay.add_controller(self.params.change_param)
        self.rot.add_controller(self.params.change_param)
        
    def align_widgets(self):
        self.addWidget(self.label,0,0,1,2)
        self.addLayout(self.weight,1,0)
        self.addLayout(self.xy_ratio,1,1)
        self.addLayout(self.decay,2,0)
        self.addLayout(self.rot,2,1)
        
    def hide(self):
        self.label.setHidden(self.show)
        self.weight.setHidden(self.show)
        self.xy_ratio.setHidden(self.show)
        self.rot.setHidden(self.show)
        self.decay.setHidden(self.show)
        
    def flipstate(self):
        self.show = not self.show
        self.hide()
        
    def get_params(self):
        return self.params.get_param()

    def get_state(self):
        return self.show

    def add_controller(self,controller):
        controller.add_space_unit(self.update_space)
        controller.add_time_unit(self.update_time)

    def update_time(self,multiplier,**kwargs):
        pass

    def update_space(self,multiplier,**kwargs):
        self.weight.multiply_and_set_value(multiplier,**kwargs)
        
class FromFile(QGridLayout):
    
    def __init__(self):
        super().__init__()
        self.show = False
        self.params = BriefParams()
        self.create_widgets()
        self.align_widgets()
        self.hide()
        
    def create_widgets(self):
        self.label   = QLabel('test1')
        self.weight  = Field(name='test2',default_value=1)
        self.xy_ratio= Field(name='test3',default_value=1)
        self.decay   = Field(name='test4',default_value=1)
        
        self.weight.add_controller(self.params.change_param)
        self.xy_ratio.add_controller(self.params.change_param)
        self.decay.add_controller(self.params.change_param)
        
    def align_widgets(self):
        self.addWidget(self.label,0,0,1,2)
        self.addLayout(self.weight,1,0)
        self.addLayout(self.xy_ratio,1,1)
        self.addLayout(self.decay,2,0)
        
    def hide(self):
        self.label.setHidden(self.show)
        self.weight.setHidden(self.show)
        self.xy_ratio.setHidden(self.show)
        self.decay.setHidden(self.show)
        
    def flipstate(self):
        self.show = not self.show
        self.hide()
        
    def get_params(self):
        return self.params.get_param()

    def get_state(self):
        return self.show

    def add_controller(self,controller):
        controller.add_space_unit(self.update_space)
        controller.add_time_unit(self.update_time)

    def update_time(self,multiplier,**kwargs):
        pass

    def update_space(self,multiplier,**kwargs):
        pass

class SimParams(QGridLayout):
    default_years = 1
    default_dt    = 1.0
    default_x     = 100
    default_dx    = 10
    default_y     = 100
    default_dy    = 10
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.align_widgets()
        
    def create_widgets(self):
        self.label = QLabel('Simulation Dimensions')
        self.label.setFont(v.get_bold_font())
        
        self.time           = UnitField(self,name='Total Time',default_value=self.default_years,unit_layout='space')
        self.d_time         = UnitField(self,name='Iterations per Time',default_value=self.default_dt,unit_layout='/time')
        self.x_distance     = UnitField(self,name='X Dimension Extent',default_value=self.default_x,unit_layout='space')
        self.y_distance     = UnitField(self,name='Y Dimension Extent',default_value=self.default_y,unit_layout='space')
        self.dxy_distance   = UnitField(self,name='Cell Width',default_value=self.default_dx,unit_layout='space')
        
    def align_widgets(self):
        self.addWidget(self.label,0,0,1,1)
        self.addLayout(self.time,  1, 0, 1, 1)
        self.addLayout(self.d_time, 1, 1, 1, 1)
        self.addLayout(self.x_distance,  2, 0, 1, 1)
        self.addLayout(self.dxy_distance, 2, 1, 1, 1)
        self.addLayout(self.y_distance,  3, 0, 1, 1)
        
    def add_controller(self,controller: MainController):
        controller.set_simulation_params('Time',self.default_years)
        controller.set_simulation_params('Iterations/Time Interval',self.default_dt)
        controller.set_simulation_params('X Dimension Extent',self.default_x)
        controller.set_simulation_params('Cell Width',self.default_dx)
        controller.set_simulation_params('Y Dimension Extent',self.default_y)

        self.time.add_controller(controller.set_simulation_params)
        self.d_time.add_controller(controller.set_simulation_params)
        self.x_distance.add_controller(controller.set_simulation_params)
        self.y_distance.add_controller(controller.set_simulation_params)
        self.dxy_distance.add_controller(controller.set_simulation_params)

        controller.add_space_unit(self.update_space)
        controller.add_time_unit(self.update_time)

    def update_time(self,multiplier,**kwargs):
        self.time.multiply_and_set_value(multiplier,**kwargs)
        self.d_time.multiply_and_set_value(1/multiplier,**kwargs)

    def update_space(self,multiplier,**kwargs):
        self.x_distance.multiply_and_set_value(multiplier,**kwargs)
        self.y_distance.multiply_and_set_value(multiplier,**kwargs)
        self.dxy_distance.multiply_and_set_value(multiplier,**kwargs)

class UnitParameters(QGridLayout):
    lengths=[
        '1 km',
        '1 m',
        '1 ft',
        '1 yard',
        '1 mile'
        ]
    times = [
        '1 day','1 month','1 year', '10 years', '100 years', '1 kyr','10 kyr', '100 kyr'
    ]
    def __init__(self):
        super().__init__()
        self.current_length='km'
        self.current_time  ='day'
        self.create_widgets()
        self.align_widgets()

    def create_widgets(self):
        self.label = QLabel('Surface Initial Conditions')
        self.label.setFont(v.get_bold_font())
        self.space  = FieldComboBox('Length Units',self.lengths,'length')
        self.time   = FieldComboBox('Time Units',self.times,'time')

    def align_widgets(self):
        self.addWidget(self.label,0,0)
        self.addLayout(self.time,1,1)
        self.addLayout(self.space,1,2)

    def add_controller(self,controller: MainController):
        self.space.add_controller(controller.set_spacetime_params)
        self.time.add_controller(controller.set_spacetime_params)

