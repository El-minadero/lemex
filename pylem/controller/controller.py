
class MainController():

    def __init__(self,model,app):
        self.app=app
        self.model = model
        self.simulation_params= Params(always_enabled=True)
        self.surface_params   = Params(always_enabled=True)
        self.geology_params   = Params()
        self.waterbot_params  = Params()
        self.hillslope_params = Params()
        self.unit_convert     = UnitConvert()
        self.unit_convert.add_controller(self)
        self.time_update_list = []
        self.space_update_list= []

    def start_simulation(self):
        print('starting simulation')
        self.model.start_simulation(self)

    def initialize(self):
        self.update_map()
        self.model.update_surface(self)

    ### plot affecting updates  ###

    def _update_surface(self,*args,**kwargs):
        pass

    def _update_fault(self,*args,**kwargs):
        pass

    def _update_map(self,*args,**kwargs):
        pass


    def update(self):
        self.app.processEvents()

    def update_map(self):
        self._update_map(self)
        self.update()

    def update_fault(self):
        self._update_fault(self)
        self.update()
        
    def update_surface(self, matrix):
        self._update_surface(matrix)
        self.update()
        
    def update_iterations(self,iterations,year):
        self._update_iterations(iterations,year)
        self.update()
    
    def update_total_iterations(self,iterations,year):
        self._update_total_iterations(iterations,year)
        self.update()

    def add_space_unit(self,function):
        self.space_update_list.append(function)

    def add_time_unit(self,function):
        self.time_update_list.append(function)

    def update_time(self,multiplier,**kwargs):
        for function in self.time_update_list:
            function(multiplier,**kwargs)

        self.update()

    def update_space(self,multiplier,**kwargs):
        for function in self.space_update_list:
            function(multiplier,**kwargs)

        self.update_map()
        self.model.update_surface(self)

    ###  geology/physics/process enabled checks ###

    def simulation_params_enabled(self):
        return self.simulation_params.is_enabled()
    
    def surface_params_enabled(self):
        return self.surface_params.is_enabled()
    
    def geology_params_enabled(self):
        return self.geology_params.is_enabled()

    def waterbot_params_enabled(self):
        return self.waterbot_params.is_enabled()

    def hillslope_params_enable(self):
        return self.hillslope_params.is_enabled()

    # change enabled state
    def change_enable_simulation(self):
        self.simulation_params.change_enable()

    def change_enable_surface(self):
        self.surface_params.change_enable()

    def change_enable_geology(self):
        self.geology_params.change_enable()
        self._update_fault(self)

    def change_enable_waterbot(self):
        self.waterbot_params.change_enable()

    def change_enable_hillslope(self):
        self.hillslope_params.change_enable()

    ### Parameter access  ###

    # set parameters
    def set_spacetime_params(self,key,value):
        self.unit_convert.assign_value(key,value)

    def set_surface_params(self, dictionary,update_controller=True,**kwargs):
        self.surface_params.clear()
        for key, value in dictionary.items():
            self.surface_params.assign_value(key, value,**kwargs)

        if update_controller:
            self.update_map()
            self.model.update_surface(self)
    
    def set_waterbot_params(self,key,value,**kwargs):
        self.waterbot_params.assign_value(key,value,**kwargs)

    def set_hillslope_params(self,key,value,**kwargs):
        self.hillslope_params.assign_value(key,value,**kwargs)
        
    def set_simulation_params(self,key,value,update_controller=True,**kwargs):
        self.simulation_params.assign_value(key,value,**kwargs)
        if update_controller:
            self.update_map()
            self.model.update_surface(self)
        
    def set_geology_params(self,key,value,update_controller=True,**kwargs):
        self.geology_params.assign_value(key, value,**kwargs)
        if update_controller:
            self.update_fault()

    # get parameters
    def get_simulation_params(self):
        return self.simulation_params.get_params()
    
    def get_waterbot_params(self):
        return self.waterbot_params.get_params()
    
    def get_hillslope_params(self):
        return self.hillslope_params.get_params()
    
    def get_geology_params(self):
        return self.geology_params.get_params()
    
    def get_surface_params(self):
        return self.surface_params.get_params()
    


class UnitConvert():
    time_basis = {
        '1 day'       : 1.0,
        '1 month'     : 30.0,
        '1 year'    : 365.0,
        '10 years'  : 3650.0,
        '100 years' : 36500.0,
        '1 kyr'     : 365000.0,
        '10 kyr'    : 3650000.0,
        '100 kyr'   : 36500000.0
    }
    space_basis = {
        '1 m' : 1.0,
        '1 km': 1000.0,
        '1 ft': 0.3048,
        '1 yard':0.9144,
        '1 mile': 1609.34
    }
    def __init__(self):
        self.first_time = True
        self.first_space= True

    def assign_value(self,key,value,**kwargs):
        if key=='time':
            self.time_assign(value)

        else:
            self.space_assign(value)

    def space_assign(self, value):
        if self.first_space:
            self.space = value
            self.first_space = False
        else:
            multiplier = self.adjust_multiplier(self.space, value, self.space_basis)
            self.space = value
            self.update_space(multiplier,units={'space':self.space })

    def time_assign(self, value):
        if self.first_time:
            self.time = value
            self.first_time = False

        else:
            multiplier = self.adjust_multiplier(self.time, value, self.time_basis)
            self.time = value
            self.update_time(multiplier,units={'time':self.time})
            print(multiplier)

    def adjust_multiplier(self,old_value,new_value,working_dict):
        multiplier = working_dict[old_value]/working_dict[new_value]
        return multiplier

    def add_controller(self,controller: MainController):
        self.update_space = controller.update_space
        self.update_time  = controller.update_time

    def update_time(self,multiplier,**kwargs):
        pass

    def update_space(self,multiplier,**kwargs):
        pass


# Param container class
class Params():
    
    def __init__(self,enable=False,always_enabled=False):
        self.enabled = enable
        self.always_enabled=always_enabled
        self.__params__ = {}
        
    def change_enable(self):
        if not self.always_enabled:
            self.enabled = not self.enabled
        
    def assign_value(self,key,value,**kwargs):
        if value is not None and value is not '' and key is not 'enable':
            try:
                self.__params__[key]=float(value)
            except ValueError:
                self.__params__[key]=value
        elif key is 'enable':
            self.change_enable()

    def get_params(self):
        return {**self.__params__}
        
    def clear(self):
        self.__params__.clear()
        
    def is_enabled(self):
        return self.enabled

# lighter weight param class without checking
class BriefParams():

    def __init__(self):
        self.param = {}
        self.enabled= False
        self.controller = None


    def set_controller_update(self,controller: MainController):
        self.controller=controller

    def change_enable(self):
        self.enabled = not self.enabled
        self.controller('enable',self.enabled)

    def update(self):
        pass

    def change_param(self, key, value, update_controller=True):
        self.param[key]=value
        if self.controller:
            for key, value in self.param.items():
                self.controller(key,value,update_controller=False)

        if update_controller:
            self.update()

    def get_param(self):
        return self.param
        
