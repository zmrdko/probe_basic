import os
import sys

from probe_basic.probe_basic import ProbeBasic
from qtpyvcp.plugins import getPlugin
from qtpyvcp.actions import program_actions
from qtpyvcp.widgets.input_widgets.file_system import FileSystemTable
from qtpyvcp.widgets.button_widgets.mdi_button import MDIButton
from qtpyvcp.widgets.button_widgets.subcall_button import SubCallButton
from qtpyvcp.widgets.button_widgets.dialog_button import DialogButton
from qtpyvcp.widgets.input_widgets.setting_slider import VCPSettingsLineEdit, VCPSettingsPushButton, VCPSettingsSlider
from qtpyvcp.widgets.hal_widgets.hal_led import HalLedIndicator
from qtpyvcp.utilities.info import Info
from PyQt5 import QtCore, QtGui, QtWidgets
from linuxcnc import ini
from qtpyvcp.plugins import getPlugin

class CustomProbeBasic(ProbeBasic):
    """Main window class for the ProbeBasic VCP.


    save this file as `custom_probebasic.py` in you config directory
    then your custom_config.yml add the `provider:` line below to the `mainwidow: section`

    ```
    windows:
      mainwindow:
        provider: custom_probebasic:CustomProbeBasic
    ```       

    """

    INI_FILE = os.environ.get("INI_FILE_NAME")
    CONFIG_DIR = os.environ.get('CONFIG_DIR')

    def __init__(self, *args, **kwargs):
        super(CustomProbeBasic, self).__init__(*args, **kwargs)
        _translate = QtCore.QCoreApplication.translate
        self.status = getPlugin('status')

        if self.INI_FILE is None:
            self.INI_FILE = ini_file or '/dev/null'
            os.environ['INI_FILE_NAME'] = self.INI_FILE

        if self.CONFIG_DIR is None:
            self.CONFIG_DIR = os.path.dirname(self.INI_FILE)
            os.environ['CONFIG_DIR'] = self.CONFIG_DIR

        self.ini = ini(self.INI_FILE)
        self.pin = self.ini.find('DISPLAY', 'PIN') or "1234"

        # Set Default tab
        self.tabWidget.setCurrentIndex(0)

        # rename the Flood button
        self.flood_button.setText("Vaccum")

        # rename the Mist button
        self.mist_button.setText("ISOALCOHOL")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.vtk_model_button = VCPSettingsPushButton(self.sb_page_3)
        sizePolicy.setHeightForWidth(self.vtk_model_button.sizePolicy().hasHeightForWidth())
        self.vtk_model_button.setSizePolicy(sizePolicy)
        self.vtk_model_button.setMinimumSize(QtCore.QSize(0, 40))
        self.vtk_model_button.setMaximumSize(QtCore.QSize(16777215, 30))
        self.vtk_model_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.vtk_model_button.setObjectName("vtk_model_button")
        #self.vtk_control_buttons.addWidget(self.vtk_model_button)
        #self.vtk_control_buttons.insertWidget(self.verticalLayout_40.indexOf(self.settings_pushbutton), self.vtk_model_button)
        self.vtk_model_button.setText(_translate("Form", "MCH MODEL"))
        self.vtk_model_button.setProperty("settingName", _translate("Form", "backplot.show-machine-model"))
