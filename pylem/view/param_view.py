#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 11:26:38 2018

@author: kevinmendoza
"""
from PyQt5.QtWidgets import QCheckBox, QGridLayout, QLabel, QComboBox, QWidget
from pylem.view._view_ import Field, UnitField
from pylem.controller.controller import MainController, BriefParams
import pylem.view._view_ as v

class AbstractPhysicsView(QGridLayout):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.widgets={}
        self.show = False
        self.params = BriefParams()
        self.create_widgets()
        self.align_widgets()
        self.hide()

    def create_widgets(self):
        pass

    def align_widgets(self):
        pass

    def add_widget(self,name,widget):
        self.widgets[name]=widget

    def add_custom_widget(self,widget):
        self.widgets[widget.name]=widget

    def set_change_enable_widget(self,name):
        self.get_widget(name).stateChanged.connect(self.params.change_enable)

    def get_widget(self,name):
        return self.widgets[name]

    def _align(self,name,*args):
        test_object = self.widgets[name]
        if isinstance(test_object,QWidget):
            self.addWidget(test_object,*args)
        else:
            self.addLayout(test_object,*args)

    def hide(self):
        for widget in self.widgets.values():
            widget.setHidden(self.show)

    def flipstate(self):
        self.show = not self.show
        self.hide()

    def get_params(self):
        return self.params.get_param()

    def get_state(self):
        return self.show

    def update_time(self,multiplier,**kwargs):
        pass

    def update_space(self,multiplier,**kwargs):
        pass

    def add_controller(self,controller: MainController):
        controller.add_space_unit(self.update_space)
        controller.add_time_unit(self.update_time)
        self._add_controller(controller)

    def _add_controller(self,controller: MainController):
        pass

    def connect_params_to_MainController(self, controller):
        self._add_controller_en_masse(self.params.change_param)
        self.params.set_controller_update(controller)

    def _add_controller_en_masse(self,controller):
        for widget in self.widgets.values():
            try:
                widget.add_controller(controller)
            except AttributeError:
                pass

    def default_init(self):
        for widget in self.widgets.values():
            try:
                widget.default_init()
            except AttributeError:
                pass

class OptionalPhysicsView(QGridLayout):

    keys=[
        'Geology',
        'Hillslope Creep',
        'Waterbot Automata'
        ]

    def __init__(self):
        super().__init__()
        self.current_layout='Geology'
        self.create_widgets()
        self.align_widgets()

    def create_widgets(self):
        self.label = QLabel('Optional Physical Processes')
        self.label.setFont(v.get_mega_bold())
        self.layouts = {
            'Geology'          : GeologicForcingParams(),
            'Hillslope Creep'  : HillslopeCreepParams(),
            'Waterbot Automata': WaterBotParams()
            }

        self.comboBox = QComboBox()
        for initial_type in self.keys:
            self.comboBox.addItem(initial_type)

        self.comboBox.activated.connect(self.change_type)

    def align_widgets(self):
        self.addWidget(self.label,0,0)
        self.addWidget(self.comboBox,0,1)
        for entry in self.layouts.values():
            self.addLayout(entry,1,0,2,2)
        for entry in self.layouts.values():
            entry.flipstate()

    def change_type(self,text):
        key = self.keys[text]
        self.layouts[self.current_layout].flipstate()
        self.layouts[key].flipstate()
        self.current_layout=key
        self.controller.update()

    def init_default_state(self):
        self.layouts[self.current_layout].flipstate()
        self.controller.update()

    def add_controller(self,controller: MainController):
        self.controller = controller
        for layout in self.layouts.values():
            layout.add_controller(controller)
        self.init_default_state()


class WaterBotParams(AbstractPhysicsView):
    def __init__(self):
        super().__init__()

    def create_widgets(self):
        title = QLabel("Waterbot Erosion")
        title.setFont(v.get_bold_font())
        checkbox = QCheckBox()
        gradient_constant=  UnitField(self,name='Gradient Constant',default_value=1.0,unit_layout='space/time')
        exponent         =  Field(self,name='Exponential Law',default_value=1.0)
        gradient_offset  =  UnitField(self,name='Gradient Offset',default_value=0.0,unit_layout='space/time')
        base_load        =  UnitField(self,name='Base Offset',default_value=0.0,unit_layout='space')
        sediment_discharge= UnitField(self,name='Sediment Discharge %',default_value=10.0)
        self.add_widget('Title',title)
        self.add_widget('Checkbox',checkbox)
        self.add_custom_widget(gradient_constant)
        self.add_custom_widget(gradient_offset)
        self.add_custom_widget(exponent)
        self.add_custom_widget(base_load)
        self.add_custom_widget(sediment_discharge)
        self.set_change_enable_widget('Checkbox')

    def align_widgets(self):
        self.columnMinimumWidth(60)
        self._align("Title",   0, 0, 1, 1)
        self._align("Checkbox",0, 2, 1, 1)
        self._align("Gradient Constant",1, 0, 1, 3)
        self._align("Exponential Law",  2, 0, 1, 3)
        self._align("Gradient Offset",  1, 4, 1, 3)
        self._align("Base Offset",      2, 4, 1, 3)
        self._align("Sediment Discharge %",    3, 0, 1, 3)

    def _add_controller(self,controller: MainController):
        self.connect_params_to_MainController(controller.set_waterbot_params)
        self.default_init()

    def update_time(self,multiplier,**kwargs):
        self.get_widget('Gradient Offset').multiply_and_set_value(1/multiplier,**kwargs)
        self.get_widget('Gradient Constant').multiply_and_set_value(1/multiplier,**kwargs)

    def update_space(self,multiplier,**kwargs):
        self.get_widget('Base Offset').multiply_and_set_value(multiplier,**kwargs)
        self.get_widget('Gradient Constant').multiply_and_set_value(multiplier,**kwargs)
        self.get_widget('Base Offset').multiply_and_set_value(multiplier,**kwargs)
        self.get_widget('Gradient Offset').multiply_and_set_value(multiplier,**kwargs)

class HillslopeCreepParams(AbstractPhysicsView):
    def __init__(self):
        super().__init__()
        
    def create_widgets(self):
        title = QLabel("Hillslope Creep")
        title.setFont(v.get_bold_font())
        checkbox = QCheckBox()
        gradient_constant= UnitField(self,name='Gradient Constant',default_value=1.0,unit_layout='space/time')
        self.add_widget('Title',title)
        self.add_widget('Checkbox',checkbox)
        self.add_custom_widget(gradient_constant)
        self.set_change_enable_widget('Checkbox')

    def align_widgets(self):
        self._align('Title',             0, 0, 1, 1)
        self._align('Checkbox',          0, 1)
        self._align('Gradient Constant', 1, 0, 1, 1)

    def _add_controller(self,controller: MainController):
        self.connect_params_to_MainController(controller.set_hillslope_params)
        self.default_init()

    def update_time(self,multiplier,**kwargs):
        self.get_widget('Gradient Constant').multiply_and_set_value(multiplier,**kwargs)

    def update_space(self,multiplier,**kwargs):
        self.get_widget('Gradient Constant').multiply_and_set_value(multiplier,**kwargs)

class GeologicForcingParams(AbstractPhysicsView):

    cmyr   = 0.1
    az     = 0
    x      = 10
    y      = 10


    def __init__(self):
        super().__init__()


    def create_widgets(self):
        label   = QLabel('Geologic Fault Forcing')
        label.setFont(v.get_bold_font())
        checkbox = QCheckBox()
        rate    = UnitField(name='Uplift Rate',key='Rate',default_value=self.cmyr,unit_layout='space/time')
        az      = Field(name='Azimuth',default_value=0)
        x_center= UnitField(name='X Origin',key='X Center',default_value=self.x,unit_layout='space')
        y_center= UnitField(name='Y Origin',key='Y Center',default_value=self.y,unit_layout='space')

        self.add_widget('Geologic Fault Forcing',label)
        self.add_widget('Checkbox',checkbox)
        self.add_custom_widget(rate)
        self.add_custom_widget(az)
        self.add_custom_widget(x_center)
        self.add_custom_widget(y_center)
        self.set_change_enable_widget('Checkbox')

    def align_widgets(self):
        self._align('Geologic Fault Forcing',0,0,1,2)
        self._align('Checkbox',0,3,1,2)
        self._align('Uplift Rate',1,0,1,2)
        self._align('Azimuth',1,3,1,2)
        self._align('X Origin',2,0,1,2)
        self._align('Y Origin',2,3,1,2)

    def _add_controller(self,controller: MainController):
        self.connect_params_to_MainController(controller.set_geology_params)
        self.default_init()

    def update_time(self,multiplier,**kwargs):
        self.get_widget('Uplift Rate').multiply_and_set_value(1/multiplier,**kwargs)


    def update_space(self,multiplier,**kwargs):
        self.get_widget('Uplift Rate').multiply_and_set_value(multiplier,**kwargs)
        self.get_widget('X Origin').multiply_and_set_value(multiplier,**kwargs)
        self.get_widget('Y Origin').multiply_and_set_value(multiplier,**kwargs)

