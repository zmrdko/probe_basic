#!/usr/bin/env python

# import sys;sys.path.append(r'~/.p2/pool/plugins/org.python.pydev.core_8.3.0.202104101217/pysrc')
# import pydevd;pydevd.settrace()

import os
import sys
import importlib.util
import math

import linuxcnc

from qtpy.QtCore import Slot, QRegExp, Qt
from qtpy.QtGui import QFontDatabase, QRegExpValidator
from qtpy.QtWidgets import QAbstractButton

from qtpyvcp import actions
from qtpyvcp.utilities import logger
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.utilities.settings import getSetting, setSetting
from qtpyvcp.plugins import getPlugin

sys.path.insert(0,'/usr/lib/python3/dist-packages/probe_basic')
import probe_basic_rc

LOG = logger.getLogger('QtPyVCP.' + __name__)
VCP_DIR = os.path.abspath(os.path.dirname(__file__))
INIFILE = linuxcnc.ini(os.getenv("INI_FILE_NAME"))

# Add custom fonts
QFontDatabase.addApplicationFont(os.path.join(VCP_DIR, 'fonts/BebasKai.ttf'))

# Constant array for reading parameter values from file into probe_basic settings
const_setting_parameter = {
    "tool-setter-probe.fast-probe-fr": 3004,
    "tool-setter-probe.slow-probe-fr": 3005,
    "tool-setter-probe.traverse-fr": 3006,
    "tool-setter-probe.z-max-travel": 3007,
    "tool-setter-probe.xy-max-travel": 3008,
    "tool-setter-probe.retract-distance": 3009,
    "tool-setter-probe.spindle-nose-height": 3010,
    "probe-parameters.probe-tool-number": 3014,
    "probe-parameters.probe-slow-fr": 3015,
    "probe-parameters.probe-fast-fr": 3016,
    "probe-parameters.probe-traverse-fr": 3017,
    "probe-parameters.max-xy-distance": 3018,
    "probe-parameters.xy-clearance": 3019,
    "probe-parameters.max-z-distance": 3020,
    "probe-parameters.z-clearance": 3021,
    "probe-parameters.extra-probe-depth": 3022,
    "probe-parameters.step-off-width": 3023,
    "surface-scan.x-start-pos": 3050,
    "surface-scan.x-end-pos": 3051,
    "surface-scan.x-point-spacing": 3052,
    "surface-scan.y-start-pos": 3053,
    "surface-scan.y-end-pos": 3054,
    "surface-scan.y-point-spacing": 3055,
    "surface-scan.end-pos-roundup": 3056,
    "surface-scan.z-safety-pos": 3057,
    "surface-scan.z-probe-min-pos": 3058,
    "surface-scan.probe-z-fast-feedrate": 3059,
    "surface-scan.probe-z-slow-feedrate": 3060,
    "surface-scan.probe-xy-traverse-feedrate": 3061,
    "surface-scan.probe-z-retract-feedrate": 3062
}

class ProbeBasic(VCPMainWindow):
    """Main window class for the ProbeBasic VCP."""
    def __init__(self, *args, **kwargs):
        super(ProbeBasic, self).__init__(*args, **kwargs)
        self.filesystemtable.sortByColumn(3, Qt.DescendingOrder) # sorting via 'datemodified' header 3
        self.filesystemtable_2.sortByColumn(3, Qt.DescendingOrder) # sorting via 'datemodified' header 3
        self.run_from_line_Num.setValidator(QRegExpValidator(QRegExp("[0-9]*")))
        self.btnMdiBksp.clicked.connect(self.mdiBackSpace_clicked)
        self.btnMdiSpace.clicked.connect(self.mdiSpace_clicked)
        
        self.stat = getPlugin('status')
        self.gcode_properties = getPlugin("gcode_properties")
        self.actionbutton.clicked.connect(self.get_extents)

        if (0 == int(INIFILE.find("ATC", "POCKETS") or 0)):
            atc_tab_index = self.tabWidget.indexOf(self.atc_tab)
            self.tabWidget.setTabVisible(atc_tab_index, False)
            self.tabWidget.removeTab(atc_tab_index)
            
        self.vtk.setViewMachine()  # set view to machine at startup

        if (getSetting("spindle-rpm-display.calculated-rpm").getValue()):
            self.spindle_rpm_source_widget.setCurrentIndex(self.spindle_calculated_rpm_button.property('page'))
        
        else:
            self.spindle_rpm_source_widget.setCurrentIndex(self.spindle_encoder_rpm_button.property('page'))
    
        self.load_user_tabs()
        self.load_var_file()

    def load_var_file(self):

        var_filename = INIFILE.find("RS274NGC", "PARAMETER_FILE") # Get var file name from INI
        if not var_filename:
            print("No PARAMETER_FILE found in INI")
            return

        var_filename = os.path.expanduser(var_filename)  # Expand user directory if needed
        if not os.path.isfile(var_filename):
            print(f"File {var_filename} does not exist.")
            return

        try:
            with open(var_filename, 'r') as file:
                for line in file:
                    parsed_line = line.strip().split('\t') # Strip and split the line (assuming tab-separated)

                    if len(parsed_line) == 2:  # Expecting key-value pairs
                        file_code, file_value = parsed_line

                        try:
                            # Convert the code of parameter to an integer, as the constant dictionary values are integers
                            file_code_as_int = int(file_code)
                        except ValueError:
                            print(f"Parameter code '{file_code}' from var file is not a valid integer, skipping...")
                            continue

                        # Look for the parameter codes in the values of const_setting_parameter
                        matching_key = next((k for k, v in const_setting_parameter.items() if v == file_code_as_int), None)

                        if matching_key:
                            # Set Setting according to value from var file
                            print(f"setting variable {matching_key} to value {file_value}")
                            setSetting(matching_key, file_value)
                        else:
                            print(f"Code '{file_code_as_int}' not found in const_setting_parameter, skipping...")
                    else:
                        print(f"Unexpected format in line: {line.strip()}")
        except Exception as e:
            print(f"Failed to load var file {var_filename}: {e}")
            return

        return parsed_data  # Returning the dictionary for further use

    def get_extents(self, file_path):
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

    def load_user_tabs(self):
        self.user_tab_modules = {}
        self.user_tabs = {}
        sidebar_loaded = False;
        user_tabs_paths = INIFILE.findall("DISPLAY", "USER_TABS_PATH")

        for user_tabs_path in user_tabs_paths:
            user_tabs_path = os.path.expanduser(user_tabs_path)
            user_tab_folders = os.listdir(user_tabs_path)
            for user_tab in user_tab_folders:
                if not os.path.isdir(os.path.join(user_tabs_path, user_tab)):
                    continue

                module_name = "user_tab." + os.path.basename(user_tabs_path) + "." + user_tabs_path
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(os.path.dirname(user_tabs_path), user_tab, user_tab + ".py"))
                self.user_tab_modules[module_name] = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = self.user_tab_modules[module_name]
                spec.loader.exec_module(self.user_tab_modules[module_name])
                self.user_tabs[module_name] = self.user_tab_modules[module_name].UserTab()
                if self.user_tabs[module_name].property("sidebar"):
                    if sidebar_loaded == False:
                        sidebar_loaded = True
                        self.user_tabs[module_name].setParent(self.sb_page_4)
                        self.user_sb_tab.setText(self.user_tabs[module_name].objectName().replace("_", " "))
                    else:
                        # can not load more than one sidebar widget
                        pass
                else:
                    self.tabWidget.addTab(self.user_tabs[module_name], self.user_tabs[module_name].objectName().replace("_", " "))

        if sidebar_loaded == False:
            self.user_sb_tab.hide()
            self.plot_tab.setStyleSheet(self.user_sb_tab.styleSheet())

    @Slot(QAbstractButton)
    def on_probetabGroup_buttonClicked(self, button):
        self.probe_tab_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_settertabGroup_buttonClicked(self, button):
        self.setter_tab_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_sidebartabGroup_buttonClicked(self, button):
        self.sidebar_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_spindlerpmsourcebtnGroup_buttonClicked(self, button):
        self.spindle_rpm_source_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_gcodemdibtnGroup_buttonClicked(self, button):
        self.gcode_mdi.setCurrentIndex(button.property('page'))

    # Fwd/Back buttons off the stacked widget
    def on_probe_help_next_released(self):
        lastPage = 6
        currentIndex = self.probe_help_widget.currentIndex()
        if currentIndex == lastPage:
            self.probe_help_widget.setCurrentIndex(0)
        else:
            self.probe_help_widget.setCurrentIndex(currentIndex + 1)

    def on_probe_help_prev_released(self):
        lastPage = 6
        currentIndex = self.probe_help_widget.currentIndex()
        if currentIndex == 0:
            self.probe_help_widget.setCurrentIndex(lastPage)
        else:
            self.probe_help_widget.setCurrentIndex(currentIndex - 1)


    @Slot(QAbstractButton)
    def on_fileviewerbtnGroup_buttonClicked(self, button):
        self.file_viewer_widget.setCurrentIndex(button.property('page'))

    def on_run_from_line_Btn_clicked(self):
        try:
            lineNum = int(self.run_from_line_Num.text())
        except:
            return False

        actions.program_actions.run(lineNum)

    # MDI Panel
    @Slot(QAbstractButton)
    def on_btngrpMdi_buttonClicked(self, button):
        char = str(button.text())
        text = self.mdiEntry.text() or 'null'
        if text != 'null':
            text += char
        else:
            text = char
        self.mdiEntry.setText(text)

    def mdiBackSpace_clicked(parent):
        if len(parent.mdiEntry.text()) > 0:
            text = parent.mdiEntry.text()[:-1]
            parent.mdiEntry.setText(text)

    def mdiSpace_clicked(parent):
        text = parent.mdiEntry.text() or 'null'
        # if no text then do not add a space
        if text != 'null':
            text += ' '
            parent.mdiEntry.setText(text)


