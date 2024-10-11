
import os


import linuxcnc

from qtpyvcp.hal import getComponent
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.settings import getSetting, setSetting


INIFILE = linuxcnc.ini(os.getenv("INI_FILE_NAME"))

class SurfaceScan:


    def __init__(self, subroutine_combobox,scan_execute,interpolation_method):
        self.gcode_properties = getPlugin("gcode_properties")
        # I dont know how to handle this: self.surface_scan_subroutine_combobox.currentIndexChanged.connect(self.function)
        self.subroutine_combobox = subroutine_combobox
        self.scan_execute = scan_execute
        self.interpolation_method = interpolation_method
        self.initialize_combobox()

    def initialize_combobox(self):
        """Populate combobox and connect the signal for when the selected index changes."""
        # Add items to combobox
        self.subroutine_combobox.addItem("smartprobe_compensation.ngc", {'probe_ngc': "smartprobe_compensation.ngc"})
        self.subroutine_combobox.addItem("simple_probe.ngc", {'probe_ngc': "simple_probe.ngc"})
        self.subroutine_combobox.addItem("test_probe.ngc",{'probe_ngc':"test_probe.ngc"})
        # Connect the combobox's index changed signal to a method
        self.subroutine_combobox.currentIndexChanged.connect(self.update_probing_subroutine)

        self.interpolation_method.addItem("bicubic",{'interpolation':0})
        self.interpolation_method.addItem("bilinear",{'interpolation':1})
        self.interpolation_method.addItem("nearest",{'interpolation':2})
        self.interpolation_method.currentIndexChanged.connect(self.update_interpolation_method)

        self.comp = getComponent("qtpyvcp")

    def get_extents(self):
        xmin = self.gcode_properties.x_min_extents()
        ymin = self.gcode_properties.y_min_extents()
        xmax = self.gcode_properties.x_max_extents()
        ymax = self.gcode_properties.y_max_extents()
        xdist = self.gcode_properties.x_extents_size()
        ydist = self.gcode_properties.y_extents_size()

        if getSetting('surface-scan.end-pos-roundup').getValue():
            x_point_spacing = getSetting('surface-scan.x-point-spacing').getValue()
            y_point_spacing = getSetting('surface-scan.y-point-spacing').getValue()
            grid_xdist = math.ceil(xdist/x_point_spacing)*x_point_spacing
            grid_ydist = math.ceil(ydist/y_point_spacing)*y_point_spacing
        else:
            grid_xdist = xdist
            grid_ydist = ydist
        grid_x0 = xmin-(grid_xdist-xdist)/2
        grid_y0 = ymin-(grid_ydist-ydist)/2
        setSetting('surface-scan.x-start-pos', grid_x0)
        setSetting('surface-scan.y-start-pos', grid_y0)
        setSetting('surface-scan.x-end-pos', (grid_x0+grid_xdist))
        setSetting('surface-scan.y-end-pos', (grid_y0+grid_ydist))

    def update_probing_subroutine(self, index):
        """Method to handle combobox selection changes."""
        print(f"Selected index: {index}, Subroutine: {self.subroutine_combobox.itemText(index)}")
        # Add more logic here if needed
        self.scan_execute.setProperty("text",f"RUN {self.subroutine_combobox.itemText(index)}")
        self.scan_execute.setProperty("filename",self.subroutine_combobox.itemText(index))

    def update_interpolation_method(self, index):
        """Method to handle combobox selection changes."""
        print(f"Selected index: {index}, interpolation method: {self.interpolation_method.itemText(index)}")
        # Add more logic here if needed
        self.comp.getPin("compensation_enable.interp-method").value = index
        