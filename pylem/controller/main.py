
from pylem.controller.controller import MainController
from pylem.model.model import MainModel
from pylem.view.param_view import OptionalPhysicsView
from pylem.view.simulate_view import SimulationParams
from pylem.view.graphics import Surface
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout


class Main():
    def __init__(self,app):
        self.main_view = MainView()
        self.main_view.show()
        self.main_model      = MainModel()
        self.main_controller = MainController(self.main_model,app)
        self.main_view.add_controller(self.main_controller)
        self.main_controller.initialize()
        
    def exit(self):
        #Exit the program, for now, no confirmation
        QApplication.quit()
        
        
class MainView(QWidget):
    
    def __init__(self):
        super().__init__()
        self._define_self()
        self._create_widgets()
        self._align_widgets()

    def _define_self(self):
        self.layout = QGridLayout(self)
        self.setGeometry(700, 500, 720, 520)
        self.setWindowTitle('Erosion Simulator')
        self.setLayout(self.layout)
        
    def _create_widgets(self):
        self.erosion_params    = OptionalPhysicsView()
        self.simulation_params = SimulationParams()
        self.main_graphics     = Surface()
        
    def _align_widgets(self):
        self.layout.setColumnMinimumWidth(0,400)
        self.layout.setColumnMinimumWidth(1,500)
        self.layout.setRowMinimumHeight(0,200)
        self.layout.setRowMinimumHeight(1,400)
        self.layout.addLayout(self.erosion_params,0,0,1,1)
        self.layout.addLayout(self.simulation_params,1,0,1,1)
        self.layout.addLayout(self.main_graphics,0,1,2,1)
        
    def add_controller(self,controller):
        self.erosion_params.add_controller(controller)
        self.simulation_params.add_controller(controller)
        self.main_graphics.add_controller(controller)
