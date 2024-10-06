
import os


import linuxcnc

from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.settings import getSetting, setSetting


INIFILE = linuxcnc.ini(os.getenv("INI_FILE_NAME"))

class SurfaceScan:


    def __init__(self):
        self.gcode_properties = getPlugin("gcode_properties")
        # I dont know how to handle this: self.surface_scan_subroutine_combobox.currentIndexChanged.connect(self.function)

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

    def update_probing_procedure(self):
        # magic
        return