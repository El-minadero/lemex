#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 14:27:10 2018

@author: kevinmendoza
"""
from PyQt5 import QtGui
from PyQt5.QtWidgets import QGridLayout, QCheckBox, QLabel, QLineEdit, QComboBox

def get_bold_font():
    font = QtGui.QFont()
    font.setPointSize(12)
    font.setBold(True)
    font.setWeight(75)
    return font
    
def get_mega_bold():
    font2 = QtGui.QFont()
    font2.setPointSize(18)
    font2.setBold(True)
    font2.setWeight(75)
    return font2

def parse_float(value: float):
    if value > 1000 or value < 0.1:
        value = '{0: 1.3e}'.format(value)
    elif value < 1.0e-16:
        value = '0'
    else:
        value = '{0:1.3g}'.format(value)

    return value

class FieldComboBox(QGridLayout):
    def __init__(self,name,keys,key,**kwargs):
        super().__init__()
        self.name = name
        self.controller = None
        self.data_key = key
        self.keys = keys
        self.create_widgets(name,keys,**kwargs)
        self.align_widgets()

    def create_widgets(self,name,keys,**kwargs):
        self.label      = QLabel(name)
        self.combo_box  = QComboBox()
        for key in keys:
            self.combo_box.addItem(key)

        self.combo_box.activated.connect(self.update)

    def align_widgets(self):
        self.addWidget(self.label, 0,0,1,1)
        self.addWidget(self.combo_box,0,1,1,1)

    def add_controller(self,controller):
        self.controller = controller
        self.update(self.combo_box.currentIndex())

    def update(self,text):
        key = self.keys[text]
        if self.controller:
            self.controller(self.data_key,key)

class FieldMonitor(QGridLayout):
    
    def __init__(self,*args,**kwargs):
        super().__init__()
        self.create_widgets(**kwargs)
        self.align_widgets()
        
    def create_widgets(self,name='',default_value=0,**kwargs):
        self.name    = name
        self.default = default_value
        self.label1 = QLabel(name)
        self.label2 = QLabel(str(self.default))
        
    def align_widgets(self):
        self.addWidget(self.label1, 0,0,1,1)
        self.addWidget(self.label2,0,1,1,1)
        
    def update_field(self,text):
        self.label2.setText(text)
        

class Field(QGridLayout):
    
    def __init__(self,*args,**kwargs):
        super().__init__()
        self.just_multiplied=False
        self.create_widgets(**kwargs)
        self.align_widgets()
        
    def create_widgets(self,name='',key=None,default_value=0,**kwargs):
        if key:
            self.key = key
        else:
            self.key = name
        self.name    = name
        self.default = default_value
        self.label = QLabel(name)
        self.entry = QLineEdit(str(default_value),)
        
    def setHidden(self,value):
        self.label.setHidden(value)
        self.entry.setHidden(value)
        
    def align_widgets(self):
        self.columnMinimumWidth(15)
        self.addWidget(self.label,0,0,1,1)
        self.addWidget(self.entry,0,1,1,1)
        
    def add_controller(self,controller):
        self.controller = controller
        self.entry.textChanged.connect(self.text_changed)
        self.text_changed(self.default)
        self.default_init()
        
    def text_changed(self,text,*args,**kwargs):
        if not self.just_multiplied:
            try:
                value = float(text)
                self.controller(self.key,value,update_controller=True)
            except ValueError:
                pass
        self.just_multiplied=False

    def default_init(self):
        self.controller(self.key,self.entry.text())

    def multiply_and_set_value(self,value):
        self.just_multiplied=True
        text=self.entry.text()
        value = float(text) *  value
        fstring = parse_float(value)
        self.entry.setText(fstring)
        self.controller(self.key,value,update_plot=False)

class UnitField(QGridLayout):

    def __init__(self,*args,unit_layout='m/s',**kwargs):
        super().__init__()
        self.just_multiplied=False
        self.unit_handler = UnitHandler(unit_layout)
        self.create_widgets(**kwargs)
        self.align_widgets()

    def create_widgets(self,name='',key=None,default_value=0,**kwargs):
        if key:
            self.key = key
        else:
            self.key = name
        self.name    = name
        self.default = default_value
        self.label = QLabel(name)
        self.units = QLabel('')
        self.entry = QLineEdit(str(default_value),)

    def setHidden(self,value):
        self.label.setHidden(value)
        self.units.setHidden(value)
        self.entry.setHidden(value)

    def align_widgets(self):
        self.columnMinimumWidth(15)
        self.addWidget(self.label,0,0,1,1)
        self.addWidget(self.units,0,1,1,1)
        self.addWidget(self.entry,0,2,1,1)

    def add_controller(self,controller):
        self.controller = controller
        self.entry.textChanged.connect(self.text_changed)
        self.text_changed(self.default)
        self.default_init()

    def text_changed(self,text,*args,**kwargs):
        if not self.just_multiplied:
            try:
                value = float(text)
                self.controller(self.key,value,update_controller=False)
            except ValueError:
                pass
        self.just_multiplied=False

    def default_init(self):
        self.controller(self.key,self.entry.text())

    def multiply_and_set_value(self,value,units={'space':'m','time':'year'}):
        self.just_multiplied=True
        text=self.entry.text()
        value = float(text) *  value
        fstring = parse_float(value)
        self.entry.setText(fstring)
        self.controller(self.key,value,update_controller=False)
        target_string = '('+self.unit_handler.update_units(units)+')'
        self.units.setText(target_string)


class UnitHandler:

    def __init__(self,unit_layout):
        self.breakout_units(unit_layout)

    def breakout_units(self, unit_layout):
        if '/' in unit_layout:
            self.top_units=self.create_divisor_unit_dict_upper(unit_layout)
            self.bottom_units=self.create_divisor_unit_dict_lower(unit_layout)
        else:
            self.top_units    = self.create_unit_dict(unit_layout)
            self.bottom_units = {}

    def create_divisor_unit_dict_upper(self,unit_layout):
        upper = unit_layout.split('/')[0]
        if upper =='1':
            return {}
        else:
            return self.create_unit_dict(upper)

    def create_divisor_unit_dict_lower(self,unit_layout):
        lower = unit_layout.split('/')[1]
        return self.create_unit_dict(lower)

    def create_unit_dict(self,string):
        new_dict = {}
        if 'space' in string:
            new_dict['space'] = 'm'
        if 'time' in string:
            new_dict['time'] = 's'
        return new_dict

    def update_dict(self,units,target_dict):
        for key in units.keys():
            if key in target_dict.keys():
                target_dict[key] = units[key]

    def get_dict_string(self,target):
        total = ''
        for entry in target.values():
            total = total + ' ' + entry
        return total

    def update_units(self,units={'space','time'}):
        #3 cases:
        self.update_dict(units,self.top_units)
        self.update_dict(units,self.bottom_units)

        if self.top_units and self.bottom_units:
            top = self.get_dict_string(self.top_units)
            bottom = self.get_dict_string(self.bottom_units)
            return top + '/' + bottom
        elif not self.top_units and self.bottom_units:
            bottom = self.get_dict_string(self.bottom_units)
            return '1/' + bottom

        else:
            top = self.get_dict_string(self.top_units)
            return top
        
        
class CheckBox(QGridLayout):
    
    def __init__(self,*args,**kwargs):
        super().__init__()
        self.create_widgets(**kwargs)
        self.align_widgets()
        
    def create_widgets(self,name='',**kwargs):
        self.label = QLabel(name)
        self.entry = QCheckBox()
        
    def align_widgets(self):
        self.addWidget(self.label,0,0,1,1)
        self.addWidget(self.entry,0,1,1,1)
        
    def add_controller(self,controller):
        self.controller = controller
        
    def checkbox_changed(self,text,*args,**kwargs):
        pass
