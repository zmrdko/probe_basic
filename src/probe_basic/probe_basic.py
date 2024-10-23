#!/usr/bin/env python


import os
import sys
import importlib.util
import math

import linuxcnc

from qtpy.QtCore import Slot, QRegExp, Qt
from qtpy.QtGui import QFontDatabase, QRegExpValidator
from qtpy.QtWidgets import QAbstractButton

from qtpyvcp import actions
from qtpyvcp.hal import getComponent
from qtpyvcp.utilities import logger
from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow
from qtpyvcp.utilities.settings import getSetting, setSetting
from qtpyvcp.plugins import getPlugin
from probe_basic.surface_scan import SurfaceScan

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
    "tool-setter-probe.diameter-probe": 3011,
    "tool-setter-probe.diameter-offset": 3012,
    "tool-setter-probe.setter-offset-direction": 3013,
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
        self.filesystemtable.sortByColumn(3, Qt.DescendingOrder)
        self.filesystemtable_2.sortByColumn(3, Qt.DescendingOrder)
        self.run_from_line_Num.setValidator(QRegExpValidator(QRegExp("[0-9]*")))
        self.btnMdiBksp.clicked.connect(self.mdiBackSpace_clicked)
        self.btnMdiSpace.clicked.connect(self.mdiSpace_clicked)
        self.surface_scan = SurfaceScan(self.surface_scan_subroutine_combobox,self.surface_scan_execute,self.surface_scan_interpolation)

        self.stat = getPlugin('status')
        self.surface_scan_load_extents.clicked.connect(self.surface_scan.get_extents)
        self.surface_scan_opacity_slider.valueChanged.connect(self.change_suface_mesh_transparency)
        
        self.surface_scan_x_start_pos_3050.textChanged.connect(self.update_extent_x_min)
        self.surface_scan_x_end_pos_3051.textChanged.connect(self.update_extent_x_max)
        self.surface_scan_y_start_pos_3053.textChanged.connect(self.update_extent_y_min)
        self.surface_scan_y_end_pos_3054.textChanged.connect(self.update_extent_y_max)

        self.comp = getComponent("qtpyvcp")
        self.comp.addPin("compensation_enable.interp-method", "s32", "out")
        self.comp.getPin("compensation_enable.interp-method").value = 1
        self.comp.addParam("extent-x-min", "float", "rw")
        self.comp.addParam("extent-x-max", "float", "rw")
        self.comp.addParam("extent-y-min", "float", "rw")
        self.comp.addParam("extent-y-max", "float", "rw")

        if (0 == int(INIFILE.find("ATC", "POCKETS") or 0)):
            atc_tab_index = self.tabWidget.indexOf(self.atc_tab)
            self.tabWidget.setTabVisible(atc_tab_index, False)
            self.tabWidget.removeTab(atc_tab_index)
            
        self.vtk.setViewMachine()

        if (getSetting("spindle-rpm-display.calculated-rpm").getValue()):
            self.spindle_rpm_source_widget.setCurrentIndex(self.spindle_calculated_rpm_button.property('page'))
        
        else:
            self.spindle_rpm_source_widget.setCurrentIndex(self.spindle_encoder_rpm_button.property('page'))
    
        self.load_user_tabs()
        
        self.load_user_buttons()
        self.load_var_file()

    def update_extent_x_min(self, value):
        self.comp.getParam("extent-x-min").value = value

    def update_extent_x_max(self, value):
        self.comp.getParam("extent-x-max").value = value
        
    def update_extent_y_min(self, value):
        self.comp.getParam("extent-y-min").value = value

    def update_extent_y_max(self, value):
        self.comp.getParam("extent-y-max").value = value

    def load_user_buttons(self):
        self.user_button_modules = {}
        self.user_buttons = {}
        
        user_buttons_paths = INIFILE.findall("DISPLAY", "USER_BUTTONS_PATH")

        for user_buttons_path in user_buttons_paths:
            user_button_path = os.path.expanduser(user_buttons_path)
            user_button_folders = os.listdir(user_buttons_path)
            for user_button in user_button_folders:
                if not os.path.isdir(os.path.join(user_buttons_path, user_button)):
                    continue
                module_name = "user_buttons." + os.path.basename(user_buttons_path) + "." + user_buttons_path
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(os.path.dirname(user_buttons_path), user_button, user_button + ".py"))
                self.user_button_modules[module_name] = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = self.user_button_modules[module_name]
                spec.loader.exec_module(self.user_button_modules[module_name])
                
                self.user_buttons[module_name] = self.user_button_modules[module_name].UserButton()
                
                self.user_buttons_layout.addWidget( self.user_buttons[module_name])
               
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
                            if matching_key == 'tool-setter-probe.setter-offset-direction':
                                match file_value:
                                    case 0:
                                         setSetting('tool-setter-probe.setter-offset-direction-left', 1)
                                    case 1:
                                         setSetting('tool-setter-probe.setter-offset-direction-right', 1)
                                    case 2:
                                         setSetting('tool-setter-probe.setter-offset-direction-front', 1)
                                    case 3:
                                         setSetting('tool-setter-probe.setter-offset-direction-back', 1)
                            else:
                                setSetting(matching_key, file_value)
                        else:
                            print(f"Code '{file_code_as_int}' not found in const_setting_parameter, skipping...")
                    else:
                        print(f"Unexpected format in line: {line.strip()}")
        except Exception as e:
            print(f"Failed to load var file {var_filename}: {e}")
            return

    def load_user_tabs(self):
        self.user_tab_modules = {}
        self.user_tabs = {}
        sidebar_loaded = False
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

    def change_suface_mesh_transparency(self):
        level = self.surface_scan_opacity_slider.value()
        setSetting('backplot.surface-map-transparency', level)
        print(f"backplot map transparency set to {level}")

    @Slot(QAbstractButton)
    def on_probetabGroup_buttonClicked(self, button):
        self.probe_tab_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_settertabGroup_buttonClicked(self, button):
        self.setter_tab_widget.setCurrentIndex(button.property('page'))

    @Slot(QAbstractButton)
    def on_surfacemaptabGroup_buttonClicked(self, button):
        self.digitizing_tab_widget.setCurrentIndex(button.property('page'))

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
