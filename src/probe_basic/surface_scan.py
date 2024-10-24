import math
import os


import linuxcnc

from qtpyvcp.hal import getComponent
from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.settings import getSetting, setSetting
 

INIFILE = linuxcnc.ini(os.getenv("INI_FILE_NAME"))

class SurfaceScan:
    """Surface Scan class for the ProbeBasic VCP."""
    def __init__(self, parent):
        self.gcode_properties = getPlugin("gcode_properties")
        self.subroutine_combobox = parent.surface_scan_subroutine_combobox
        self.scan_execute = parent.surface_scan_execute
        self.interpolation_method = parent.surface_scan_interpolation
        self.initialize_combobox()

        self.s = linuxcnc.stat()
        self.c = linuxcnc.command()
        self.comp = getComponent("qtpyvcp")
        
        self.comp.addPin("compensation_enable.interp-method", "s32", "out")
        self.comp.getPin("compensation_enable.interp-method").value = 1
        self.comp.addParam("extent-x-min", "float", "rw")
        self.comp.addParam("extent-x-max", "float", "rw")
        self.comp.addParam("extent-x-spacing", "float", "rw")
        self.comp.addParam("extent-y-min", "float", "rw")
        self.comp.addParam("extent-y-max", "float", "rw")
        self.comp.addParam("extent-y-spacing", "float", "rw")
        self.comp.addParam("end-pos-roundup", "float", "rw")
        self.comp.addParam("z_safety_pos", "float", "rw")
        self.comp.addParam("z_probe_min_pos", "float", "rw")
        self.comp.addParam("probe_z_fast_feedrate", "float", "rw")
        self.comp.addParam("probe_z_slow_feedrate", "float", "rw")
        self.comp.addParam("probe_xy_traverse_feedrate", "float", "rw")
        self.comp.addParam("probe_z_retract_feedrate", "float", "rw")
        self.comp.addParam("compensation_fade_height", "float", "rw")

        parent.surface_scan_x_start_pos_3050.textChanged.connect(self.update_extent_x_min)
        parent.surface_scan_x_end_pos_3051.textChanged.connect(self.update_extent_x_max)
        parent.surface_scan_x_point_spacing_3052.textChanged.connect(self.update_extent_x_spacing)
        parent.surface_scan_y_start_pos_3053.textChanged.connect(self.update_extent_y_min)
        parent.surface_scan_y_end_pos_3054.textChanged.connect(self.update_extent_y_max)
        parent.surface_scan_y_point_spacing_3055.textChanged.connect(self.update_extent_y_spacing)
        parent.surface_scan_end_pos_roundup_3056.clicked.connect(self.update_end_pos_roundup)
        parent.surface_scan_z_safety_pos_3057.textChanged.connect(self.update_z_safety_pos)
        parent.surface_scan_z_probe_min_pos_3058.textChanged.connect(self.update_z_probe_min_pos)
        parent.surface_scan_probe_z_fast_feedrate_3059.textChanged.connect(self.update_probe_z_fast_feedrate)
        parent.surface_scan_probe_z_slow_feedrate_3060.textChanged.connect(self.update_probe_z_slow_feedrate)
        parent.surface_scan_probe_xy_traverse_feedrate_3061.textChanged.connect(self.update_probe_xy_traverse_feedrate)
        parent.surface_scan_probe_z_retract_feedrate_3062.textChanged.connect(self.update_probe_z_retract_feedrate)
        parent.surface_scan_compensation_fade_height_3064.textChanged.connect(self.update_compensation_fade_height)
        
    def update_extent_x_min(self, value):
        self.comp.getParam("extent-x-min").value = value

    def update_extent_x_max(self, value):
        self.comp.getParam("extent-x-max").value = value

    def update_extent_x_spacing(self, value):
        self.comp.getParam("extent-x-spacing").value = value

    def update_extent_y_min(self, value):
        self.comp.getParam("extent-y-min").value = value

    def update_extent_y_max(self, value):
        self.comp.getParam("extent-y-max").value = value

    def update_extent_y_spacing(self, value):
        self.comp.getParam("extent-y-spacing").value = value

    def update_end_pos_roundup(self, value):
        self.comp.getParam("end-pos-roundup").value = value

    def update_z_safety_pos(self, value):
        self.comp.getParam("z_safety_pos").value = value
        
    def update_z_probe_min_pos(self, value):
        self.comp.getParam("z_probe_min_pos").value = value
        
    def update_probe_z_fast_feedrate(self, value):
        self.comp.getParam("probe_z_fast_feedrate").value = value
        
    def update_probe_z_slow_feedrate(self, value):
        self.comp.getParam("probe_z_slow_feedrate").value = value
        
    def update_probe_xy_traverse_feedrate(self, value):
        self.comp.getParam("probe_xy_traverse_feedrate").value = value
        
    def update_probe_z_retract_feedrate(self, value):
        self.comp.getParam("probe_z_retract_feedrate").value = value
        
    def update_compensation_fade_height(self, value):
        self.comp.getParam("compensation_fade_height").value = value

    def initialize_combobox(self):
        """Populate combobox and connect the signal for when the selected index changes."""
        # Add items to combobox
        self.subroutine_combobox.addItem("SMARTPROBE COMPENSATION", {'probe_ngc': "smartprobe_compensation.ngc"})
        self.subroutine_combobox.addItem("SURFACE SCAN", {'probe_ngc': "surface_scan.ngc"})
        self.subroutine_combobox.addItem("TEST PROBE",{'probe_ngc':"test_probe.ngc"})
        # Connect the combobox's index changed signal to a method
        self.subroutine_combobox.currentIndexChanged.connect(self.update_probing_subroutine)

        self.interpolation_method.addItem("BICUBIC",{'interpolation':0})
        self.interpolation_method.addItem("BILINEAR",{'interpolation':1})
        self.interpolation_method.addItem("NEAREST",{'interpolation':2})
        self.interpolation_method.currentIndexChanged.connect(self.update_interpolation_method)

    def ok_for_mdi(self):
        self.s.poll()
        return not self.s.estop and self.s.enabled and self.s.homed and (self.s.interp_state == linuxcnc.INTERP_IDLE)

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

        self.comp.getParam('extent-x-min').value = grid_x0
        self.comp.getParam('extent-x-max').value = grid_y0
        self.comp.getParam('extent-y-min').value = (grid_x0+grid_xdist)
        self.comp.getParam('extent-y-max').value = (grid_y0+grid_ydist)
        #self.comp.getParam("test_value").value = 123

        if self.ok_for_mdi():
            self.c.mode(linuxcnc.MODE_MDI)
            self.c.wait_complete() # wait until mode switch executed
            self.c.mdi("o<surface_scan_param_update> call")
        
        #somehow call o<surface_scan_param_update> sub here to update parameters in sim.var and we good

    def update_probing_subroutine(self, index):
        """Method to handle combobox selection changes."""
        print(f"Selected index: {index}, Subroutine: {self.subroutine_combobox.itemText(index)} ngc file: {self.subroutine_combobox.itemData(index)['probe_ngc']}")
        # Add more logic here if needed
        self.scan_execute.setProperty("text",f"RUN {self.subroutine_combobox.itemText(index)}")
        self.scan_execute.setProperty("filename",self.subroutine_combobox.itemData(index)['probe_ngc'])

    def update_interpolation_method(self, index):
        """Method to handle combobox selection changes."""
        print(f"Selected index: {index}, interpolation method: {self.interpolation_method.itemText(index)}")
        # Add more logic here if needed
        self.comp.getPin("compensation_enable.interp-method").value = index
        
