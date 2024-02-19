# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 00:05:24 2024

@author: Jeff Barton
         Electrical Engineer
         Transmission Long Term Planning
         Bonneville Power Administration
         jgbarton@bpa.gov

Change log:
v0:
    Adapted from "Loss_Factor_Study_v1.py"
    
    Worker 1 will call "Template_Function" which will:
        Create dummy objects/methods to stand in for Powerworld calls
        Created a demonstration function to show how I generally implement
            powerflow study automation.
            
    Worker 2 runs a simple dummy function
"""
'''****************************************************************************
*******************************************************************************
****                                                                       ****
****                                                                       ****
****                           Import Block                                ****
****                                                                       ****
****                                                                       ****
*******************************************************************************
****************************************************************************'''
import sys
import os
import logging
from inspect import currentframe as cf # Used to identify the current function -- avoids some copy-paste issues when making new defs
#import csv
#from datetime import datetime # date and time functions
#import win32com.client # loads a suite of tools access to windows routines

from PyQt5  import (
    QtCore, # Core routines
    #QtGui, # Not sure
    uic, # contains translator for .ui files
    #QtWidgets  # contains all widget descriptors
)
from PyQt5.QtCore import (
        #Qt, 
        QObject, 
        QThread, 
        #pyqtSignal
)

from PyQt5.QtWidgets import (
    QApplication,
    #QLabel,
    QMainWindow,
    #QPushButton,
    #QVBoxLayout,
    #QWidget,
    #QPlainTextEdit,
    QFileDialog
)

# shortcut declarations to make programming simpler
Signal = QtCore.pyqtSignal
Slot = QtCore.pyqtSlot

global logger

'''****************************************************************************
*******************************************************************************
****                                                                       ****
****                                                                       ****
****                    Setup Tasks and Functions                          ****
****                                                                       ****
****                                                                       ****
*******************************************************************************
****************************************************************************'''
def print_exception():
    # Return line number data from the last exception
    from linecache import getline, checkcache
    from sys import exc_info
    exc_type, exc_obj, tb = exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    checkcache(filename)
    line = getline(filename, lineno, f.f_globals)
    return[f'LINE {lineno} "{line.strip()}"']

'''******************************* Load GUI ********************************'''
#qtCreatorFile = r'C:/(your path here)/logging_display2.ui'
# use "./(filename)" to point to the same directory as the Python code
qtCreatorFile = r'./Template_GUI_v1.ui'

# This activates a translator that converts the .ui file
# into a Class with name "Ui_My_App_Window" that contains
# all the pyQt5 descriptors for the designed GUI.  You dont
# get to see the code here, but it gets loaded into memeory
Ui_My_App_Window, QtBaseClass = uic.loadUiType(qtCreatorFile)

'''**************************** Setup Logging ******************************'''
def addLoggingLevel(levelName, levelNum, methodName=None):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       #raise AttributeError('{} already defined in logging module'.format(levelName))
       logger.log(logging.WARNING, f'{levelName} already assigned.', extra = extra)
       return
    if hasattr(logging, methodName):
       #raise AttributeError('{} already defined in logging module'.format(methodName))
       logger.log(logging.WARNING, f'{methodName} already assigned.', extra = extra)
       return
    if hasattr(logging.getLoggerClass(), methodName):
       #raise AttributeError('{} already defined in logger class'.format(methodName))
       logger.log(logging.WARNING, f'{methodName} already assigned.', extra = extra)
       return

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


'''*********************** Create new logging levels ***********************'''
def subinfo(self, message, *args, **kws):
    # This function gets called when the logger sees a message with priority "SUBINFO"
    # "SUBINFO" has a priority between INFO and DEBUG"
    # Intended to report intermediate results
    if self.isEnabledFor(LOGLV_SUBINFO):
        # Yes, logger takes its '*args' as 'args'.
        self.log(LOGLV_SUBINFO, message, args, **kws) 
        
LOGLV_SUBINFO = 15 
logging.addLevelName(LOGLV_SUBINFO, "SUBINFO")
addLoggingLevel("SUBINFO", 15)
logging.Logger.subinfo = subinfo
        
def data(self, message, *args, **kws):
    # This function gets called when the logger sees a message with priority "DATA"
    # "DATA" has a priority between DEBUG and SUBDATA.
    # Intended to report important variables for troubleshooting
    if self.isEnabledFor(LOGLV_DATA):
        # Yes, logger takes its '*args' as 'args'.
        self.log(LOGLV_DATA, message, args, **kws)
        
LOGLV_DATA = 6 
logging.addLevelName(LOGLV_DATA, "DATA")
addLoggingLevel("DATA", 6)
logging.Logger.data = data
        
def subdata(self, message, *args, **kws):
    # This function gets called when the logger sees a message with priority "SUBDATA"
    # "SUBDATA" has a priority lower than "DATA"
    # Intended to report variables that may not be critical for troubleshooting at the moment that can be removed to reduce log clutter
    if self.isEnabledFor(LOGLV_SUBDATA):
        # Yes, logger takes its '*args' as 'args'.
        self.log(LOGLV_SUBDATA, message, args, **kws)
        
LOGLV_SUBDATA = 5 
logging.addLevelName(LOGLV_SUBDATA, "SUBDATA")
addLoggingLevel("SUBDATA", 5)
logging.Logger.subdata = subdata

#set the initial logging level
# Can be: DEBUG, INFO, WARNING, ERROR, or CRITICAL, by default
initial_log_level = logging.DATA

# Calls the basic config routine to initilize default config settings.
# Enter desired values for the default logger here.
# If this is not the first call to basicConfig,
# nothing will be changed.
logging.basicConfig() 

# identifies the current loggery
logger = logging.getLogger(__name__)
# Sets the logging level for the default logger
# Can be: DEBUG, INFO, WARNING, ERROR, or CRITICAL, by default
logger.setLevel(initial_log_level)


'''****************************************************************************
*******************************************************************************
****                                                                       ****
****                                                                       ****
****                          Class Definitions                            ****
****                                                                       ****
****                                                                       ****
*******************************************************************************
****************************************************************************'''
###############################################################################
#
# Signals need to be contained in a QObject or subclass in order to be correctly
# initialized.
#
class Signaller(QtCore.QObject):
    # creates a signal named "log event" with the type as shown
    log_event = Signal(str, logging.LogRecord)
    

###############################################################################
#
# Output to a Qt GUI is only supposed to happen on the main thread. So, this
# handler is designed to take a slot function which is set up to run in the main
# thread. In this example, the function takes a string argument which is a
# formatted log message, and the log record which generated it. The formatted
# string is just a convenience - you could format a string for output any way
# you like in the slot function itself.
#
# You specify the slot function to do whatever GUI updates you want. The handler
# doesn't know or care about specific UI elements.
#
class QtHandler(QObject, logging.Handler):
    def __init__(self, slotfunc, *args, **kwargs):
        super(QtHandler, self).__init__(*args, **kwargs)
        # Get available signals from "Signaller" class
        self.signaller = Signaller()
        # Connect the specific signal named "log_event"
        # to a function designated by the caller
        self.signaller.log_event.connect(slotfunc)

    # When a new log event happens, send the event
    # out via the named signal
    def emit(self, record):
        s = self.format(record)
        self.signaller.log_event.emit(s, record)


'''*************************************************************************'''
def ctname():
    # Get the Qt name of the current thread.
    return QtCore.QThread.currentThread().objectName()

'''*************************************************************************'''
def is_number(text):
    # Identify whether the passed data is a number
    try:
        if text == None or text =='None':
            return False
        float(text)
        return True
    except ValueError:
        return False
        return ''

    
'''****************************************************************************
*******************************************************************************
****                                                                       ****
****                                                                       ****
****                          Worker Functions                             ****
****                                                                       ****
****                                                                       ****
*******************************************************************************
****************************************************************************'''
class Worker(QObject):
    # Nothing to initialize in this example.  One might
    # Want to initialize using some GUI information to
    # pass data to the worker.
    
    # with the proper initialization, these signals
    # Could be added to the Signaller class, above
    finished = Signal()
    progress_report = Signal(list)
    
    # init the worker with the case_file_dat variable passed from the main event loop
    def __init__(self, worker_data_dict = {}, parent=None):
        QThread.__init__(self, parent)
        self.worker_data_dict = worker_data_dict
    
    # This is the definition of the task worker will 
    # perform.  You can have more than one task for work.
    # Other workers will be defs within this class
    # with different names performing different tasks.
    
    
    '''************************************************************************
    ***************************************************************************
    ****                                                                   ****
    ****                                                                   ****
    ****                             Worker 1                              ****
    ****                                                                   ****
    ****                                                                   ****
    ***************************************************************************
    ************************************************************************'''
    def worker1(self):
        extra = {"qThreadName": QtCore.QThread.currentThread().objectName() }
        # Subroutine to create tables used for creating cases
        # Loads the TSR file and the Build Instruction file
        # For each case in the Build Instruction file, 
        # The TSR file will be filtered according to the instructions
        # for the case in the Build Instruction file
        try:
                logger.log(logging.DEBUG, f'Started {extra["qThreadName"]}', extra=extra)
                
                from Template_Function_v0 import worker1_function
                
                # Call the worker function
                result = worker1_function(self.worker_data_dict)
                
                logger.log(logging.DEBUG, f'Completed: worker1_function.  Result: {result}', extra=extra)
                
                # Signal main thread that the code is done
                emit_txt = 'Finished'
                self.progress_report.emit([emit_txt, 'none', '0 of 0', 0, 'none', '0 of 0', 0])
                self.finished.emit()
                return
                
        except Exception as e:
                err = f'Exception (load create_tables) = {e}, {print_exception()}'
                action = 'Exception'
                logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                # Signal main thread that the code is done
                self.progress_report.emit(['Exception', 'none', '0 of 0', 0, 'none', '0 of 0', 0])
                self.finished.emit()
                return
    
    
    '''************************************************************************
    ***************************************************************************
    ****                                                                   ****
    ****                                                                   ****
    ****                             Worker 2                              ****
    ****                                                                   ****
    ****                                                                   ****
    ***************************************************************************
    ************************************************************************'''
    def worker2(self):
        extra = {"qThreadName": QtCore.QThread.currentThread().objectName() }
        # Subroutine to create cases for cases
        # Loads the case tables and the Build Instruction file
        # A starting case is loaded and the case is adjusted
        # according to the instructions in the Build Instruction file
        # and the TSR table for the case.
        
        try:
                
            from Template_Multiprocess_Function_v0 import worker2_function
                
            # Call the worker function
            result = worker2_function(self.worker_data_dict)
                
            logger.log(logging.DEBUG, f'Completed: worker1_function.  Result: {result}', extra=extra)
                
            # Signal main thread that the code is done
            self.progress_report.emit(['Finished', 'none', '0 of 0', 0, 'none', '0 of 0', 0])
            self.finished.emit()
        
        except Exception as e:
            err = f'Exception (create_cases worker) = {e}, {print_exception()}'
            action = 'Exception'
            logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
            self.progress_report.emit(['Exception', 'none', '0 of 0', 0, 'none', '0 of 0', 0])
            self.finished.emit()
    
    
'''****************************************************************************
*******************************************************************************
****                                                                       ****
****                                                                       ****
****                            GUI Application                            ****
****                                                                       ****
****                                                                       ****
*******************************************************************************
****************************************************************************'''
# This is the main application loop
# it references the widget "QMainWindow
# and the GUI code implemented by
# the uic.loadUiType call, above
class My_Application(QMainWindow, Ui_My_App_Window):
    # Initial state mod tftft
    debug_options = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
    COLORS = {
        logging.SUBDATA: 'grey',
        logging.DATA: 'green',
        logging.DEBUG: 'black',
        logging.SUBINFO: 'cyan',
        logging.INFO: 'blue',
        logging.WARNING: 'brown',
        logging.ERROR: 'red',
        logging.CRITICAL: 'purple'
    }
    LOG_LEVELS = {
        'SUBDATA': logging.SUBDATA,
        'DATA': logging.DATA,
        'SUBINFO': logging.SUBINFO,
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    INITIAL_LOG_LEVELS_IDX = {
        logging.SUBDATA : 7,
        logging.DATA : 6,
        logging.DEBUG : 5,
        logging.SUBINFO : 4,
        logging.INFO : 3,
        logging.WARNING : 2,
        logging.ERROR : 1,
        logging.CRITICAL : 0
    }
    worker1_data_dict = {'working_directory' : './',
                        'summer_case' : '26HS.pwb',
                        'winter_case' : '26HW.pwb',
                        'spring_case' : '26LSP.pwb',
                        'save_casenames' : ['26HS_LF', '26HW_LF', '26LSP_LF'],
                        'summer_to_spring_pct' : 64.0,
                        'case_load_levels' : [500, 400, 300, 200, 100, 0, -100, -200, -300, -400, -500],
                        'max_slack_deviation' : 5,
                        'quit_excel' : False,
                        'saved_scaled_cases' : True,
                        'gui_active' : True,
                        'use_multi_proc' : False,
                        'debug_options' : [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
                        'logger' : None
                        }
    
    worker2_data_dict = {
                        'start_level' : 100000000,
                        'number_cases' : 10,
                        'use_multi_proc' : False, # When true, and the option is programmed, the function will use a multiprocessing pool to complete studies faster
                        'debug_options' : [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],  # Debug option flags potentially used in the case.
                        'logger' : None
                        }
    extra = {"qThreadName": ctname() }
    
    # the next lines set the current working directory to the directory above the current working directory.
    python_dir = os.getcwd().replace('\\', '/')  # gets the current working directory
#    os.chdir(os.path.dirname(python_dir)) # sets the current working directory to the level above the current working directory
#    cwd = os.getcwd().replace('\\', '/') + '/'
    # sets the variable 'cwd' to the path above the current working directory
    cwd = os.path.dirname(python_dir)
    last_dir = cwd
    
    def __init__(self):
        try:
#            logger_done = False
            # Run the QMainWindow initialization routine
            QMainWindow.__init__(self)
            # initialize the Ui
            # the name should be "Ui_(object_name_of_top-level_object_in_ui_file)
            # This makes the setupUi routine, below, callable
            Ui_My_App_Window.__init__(self)
            # this runs the setupUi code insided the Ui class that was loaded with
            # the call to uic.loadUiType, above.  No Ui variables will be
            # accessable until the setupUi routine is run.
            self.setupUi(self)
            
            #routine to set up the logger
            self.setup_logger()
#            logger_done = True
            self.worker1_data_dict['logger'] = logger
            self.worker2_data_dict['logger'] = logger
            
            # a status indicator for the loop
            self.statuss = 0
        except Exception as e:
            self.log_text.appendHtml(f"<div style='color: purple;'> CRITICAL Exception in Application init = {e} </div>")
            
        try:    
            # Widgets for the GUI were created with "Qt Designer"
            # so there is no need to set up the GUI using code.
            # The widgets do need to be connected to the event loop:
            
            import os
            if os.path.isfile(f'{self.python_dir}/Preloads_Loss_Factor.txt'):
#            if False:  # Debug skip
                raw_file = open(f'{self.python_dir}/Preloads_Loss_Factor.txt','r')
                preload_raw_text = raw_file.readlines()
                raw_file.close()
                
#                preload_raw_text = []  # Debug code
                logger.log(logging.DATA, f'preload_raw_text = {preload_raw_text}', extra = self.extra)
#                
                preload_data = []
                for line2 in preload_raw_text:
                    line = line2[:-1]  # Eliminate carriage return at end of line
                    while ' =' in line or '= ' in line: # or '\n' in line:
                        line = line.replace(' =','=').replace('= ', '=')
                        print(line)
                    while line[0] == ' ':
                        line = line[1:]
                        print(line)
                    while line[-1] == ' ':
                        line = line[0:-1]
                        print(line)
                    preload_data += [line.split('=')]
                    
                logger.log(logging.DATA, f'preload_data = {preload_data}', extra = self.extra)
                preload_dict = dict(preload_data)
            else:
                logger.log(logging.DEBUG, f'No preload file found', extra = self.extra)
                preload_dict = {'': ''}
            
            logger.log(logging.DATA, f'preload_dict = {preload_dict}', extra = self.extra)
            
            worker_data_dicts = [self.worker1_data_dict, self.worker2_data_dict]
            for key in preload_dict.keys():
                for idx, worker_data_dict in enumerate(worker_data_dicts):
                    if key in worker_data_dict.keys():
                        worker_data_dicts[idx][key] = preload_dict[key]
            # is this step required?  Sometimes it is not clear how Python works internally
            self.worker1_data_dict, self.worker2_data_dict = worker_data_dicts
            pct = preload_dict.get('summer_to_spring_pct', '64.0')
            if is_number(pct):
                self.worker1_data_dict['summer_to_spring_pct'] = float(pct)
            else:
                self.worker1_data_dict['summer_to_spring_pct'] = 64.0
            
            if 'true' in preload_dict.get('saved_scaled_cases', 'False').lower():
                self.worker1_data_dict['saved_scaled_cases'] = True
            else:
                self.worker1_data_dict['saved_scaled_cases'] = False
                
            logger.log(logging.DATA, f'worker1_data_dict = {self.worker1_data_dict}', extra = self.extra)
            logger.log(logging.DATA, f'worker2_data_dict = {self.worker2_data_dict}', extra = self.extra)
            
            # Widgets for the GUI were created with "Qt Designer"
            # so there is no need to set up the GUI using code.
            # The widgets do need to be connected to the event loop:
            #identify working directory in log
#            self.worker1_data_dict['working_directory'] = preload_dict.get('working_directory', f'{self.cwd}')
            self.working_directory.setText(self.worker1_data_dict['working_directory']) # preload the cwd
            logger.log(logging.DEBUG, f'"Current working directory" set to:\n{" "*33}{self.worker1_data_dict["working_directory"]}', extra = self.extra)
#            self.worker1_data_dict['summer_case'] = preload_dict.get('summer_case', '')
            self.top_file.setText(self.worker1_data_dict['summer_case']) # preload the input file
            logger.log(logging.DEBUG, f'"Summer Case" set to:\n{" "*33}{self.worker1_data_dict["summer_case"]}', extra = self.extra)
#            self.worker1_data_dict['winter_case'] = preload_dict.get('winter_case', '')
            self.middle_file.setText(self.worker1_data_dict['winter_case']) # preload the input file
            logger.log(logging.DEBUG, f'"Winter Case" set to:\n{" "*33}{self.worker1_data_dict["winter_case"]}', extra = self.extra)
#            self.worker1_data_dict['spring_case'] = preload_dict.get('spring_case', '')
            self.bottom_file.setText(self.worker1_data_dict['spring_case']) # preload the input file
            logger.log(logging.DEBUG, f'"Spring Case" set to:\n{" "*33}{self.worker1_data_dict["spring_case"]}', extra = self.extra)
            
            # Placeholder until GUI is updated
#            self.worker1_data_dict['save_casenames'] = preload_dict.get('save_casenames', ['26HS_LF', '26HW_LF', '26LSP_LF'])
#            self.text_input.setText(self.worker1_data_dict['save_casenames'])
            logger.log(logging.DEBUG, f'"Save Casenames" set to:\n{" "*21}{self.worker1_data_dict["save_casenames"]}', extra = self.extra)
            
#            self.worker1_data_dict['summer_to_spring_pct'] = preload_dict['summer_to_spring_pct']
            self.percent.setValue(self.worker1_data_dict['summer_to_spring_pct'])
            logger.log(logging.DEBUG, f'"Summer to Spring Scale Percent" set to:\n{" "*33}{self.worker1_data_dict["summer_to_spring_pct"]}', extra = self.extra)
            
            # Placeholder until GUI is updated
#            self.worker1_data_dict['case_load_levels'] = preload_dict.get('case_load_levels', [500, 400, 300, 200, 100, 0, -100, -200, -300, -400, -500])
#            self.percent.setValue(self.worker1_data_dict['case_load_levels'])
            logger.log(logging.DEBUG, f'"Case Load Levels" set to:\n{" "*33}{self.worker1_data_dict["case_load_levels"]}', extra = self.extra)
#            self.worker1_data_dict['max_slack_deviation'] = preload_dict.get('max_slack_deviation', 5)
#            self.percent.setValue(self.worker1_data_dict['max_slack_deviation'])
            logger.log(logging.DEBUG, f'"Max Slack Deviation" set to:\n{" "*33}{self.worker1_data_dict["max_slack_deviation"]}', extra = self.extra)
            
            
#            self.worker1_data_dict['quit_excel'] = preload_dict.get('quit_excel', False)
            self.checkbox1.setChecked(self.worker1_data_dict['quit_excel'])
            logger.log(logging.DEBUG, f'"Quit Excel after file creation" set to:\n{" "*33}{self.worker1_data_dict["quit_excel"]}', extra = self.extra)
#            self.worker1_data_dict['saved_scaled_cases'] = preload_dict.get('saved_scaled_cases', True)
            self.checkbox2.setChecked(self.worker1_data_dict['saved_scaled_cases'])
            logger.log(logging.DEBUG, f'"Saved Scaled Cases" set to:\n{" "*33}{self.worker1_data_dict["saved_scaled_cases"]}', extra = self.extra)
            
            # This tells the called worker that a GUI is active
            self.worker1_data_dict['gui_active'] = True
            # This tells the called worker that multiprocessing is disabled
            self.worker1_data_dict['use_multi_proc'] = False
            # Debugging options
            self.worker1_data_dict['debug_options'] = self.debug_options
            
            logger.log(logging.DATA, f'Preload done, starting connects', extra = self.extra)
            
            #This section is telling Python which line of code to go to when each button is clicked in the GUI 
            self.working_directory_button.clicked.connect(self.set_working_directory)
            self.working_directory.textChanged.connect(self.capture_working_directory_text)
            self.top_file_button.clicked.connect(self.set_top_file)
            self.top_file.textChanged.connect(self.capture_top_file_text)
            self.middle_file_button.clicked.connect(self.set_middle_file) 
            self.middle_file.textChanged.connect(self.capture_middle_file_text)
            self.bottom_file_button.clicked.connect(self.set_bottom_file) 
            self.bottom_file.textChanged.connect(self.capture_bottom_file_text)
            self.checkbox1.stateChanged.connect(self.checkbox1_changed)
            self.logging_level_select.setCurrentIndex(self.INITIAL_LOG_LEVELS_IDX.get(initial_log_level))
            self.logging_level_select.currentTextChanged.connect(self.change_logging_level)
            self.worker1_button.clicked.connect(self.run_worker1)
            self.checkbox2.stateChanged.connect(self.checkbox2_changed)
            self.worker2_button.clicked.connect(self.run_worker2)
            self.exit_button.clicked.connect(self.run_exit)
            self.percent.valueChanged.connect(self.percent_changed)
            
            self.worker1_button.setEnabled(True)
            self.worker2_button.setEnabled(True)
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in GUI init = {e}, {print_exception()}', extra = self.extra)
            
        try:
            logger.log(logging.DATA, f'Setting options', extra = self.extra)
            # Set initial start for debug checkboxes
            # I don't know how to make this a loop
            self.option01.setChecked(self.debug_options[0])
            self.option02.setChecked(self.debug_options[1])
            self.option03.setChecked(self.debug_options[2])
            self.option04.setChecked(self.debug_options[3])
            self.option05.setChecked(self.debug_options[4])
            self.option06.setChecked(self.debug_options[5])
            self.option07.setChecked(self.debug_options[6])
            self.option08.setChecked(self.debug_options[7])
            self.option09.setChecked(self.debug_options[8])
            self.option10.setChecked(self.debug_options[9])
            self.option11.setChecked(self.debug_options[10])
            self.option12.setChecked(self.debug_options[11])
            self.option13.setChecked(self.debug_options[12])
            self.option14.setChecked(self.debug_options[13])
            self.option15.setChecked(self.debug_options[14])
            self.option01.stateChanged.connect(lambda:self.change_debug_options(self.option01.isChecked(), 0))
            self.option02.stateChanged.connect(lambda:self.change_debug_options(self.option02.isChecked(), 1))
            self.option03.stateChanged.connect(lambda:self.change_debug_options(self.option03.isChecked(), 2))
            self.option04.stateChanged.connect(lambda:self.change_debug_options(self.option04.isChecked(), 3))
            self.option05.stateChanged.connect(lambda:self.change_debug_options(self.option05.isChecked(), 4))
            self.option06.stateChanged.connect(lambda:self.change_debug_options(self.option06.isChecked(), 5))
            self.option07.stateChanged.connect(lambda:self.change_debug_options(self.option07.isChecked(), 6))
            self.option08.stateChanged.connect(lambda:self.change_debug_options(self.option08.isChecked(), 7))
            self.option09.stateChanged.connect(lambda:self.change_debug_options(self.option09.isChecked(), 8))
            self.option10.stateChanged.connect(lambda:self.change_debug_options(self.option10.isChecked(), 9))
            self.option11.stateChanged.connect(lambda:self.change_debug_options(self.option11.isChecked(), 10))
            self.option12.stateChanged.connect(lambda:self.change_debug_options(self.option12.isChecked(), 11))
            self.option13.stateChanged.connect(lambda:self.change_debug_options(self.option13.isChecked(), 12))
            self.option14.stateChanged.connect(lambda:self.change_debug_options(self.option14.isChecked(), 13))
            self.option15.stateChanged.connect(lambda:self.change_debug_options(self.option15.isChecked(), 14))
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in Debug Options init = {e}, {print_exception()}', extra = self.extra)
        
        logger.log(logging.DEBUG, f'End intialization', extra = self.extra)
        
        
        
    # This routine is called once by the "My_Application"
    # class to set up the log handler
    def setup_logger(self):
        try:
            # Set up the logging handler, in this case "QtHandler"
            # defined above.  Remember to use qThreadName rather 
            # than threadName in the format string.
            
            # This line connects the handler to "QtHandler" and
            # points the handler to the slot function "QtHander"
            # is expection for the emit signal.  THis sends the
            # signal to the routine "update_status" defined below.
            self.handler = QtHandler(self.update_status)
            
            # fs is a string containing format information
            #
            # %(pathname)s Full pathname of the source file where the logging call was issued(if available).
            # %(filename)s Filename portion of pathname.
            # %(module)s Module (name portion of filename).
            # %(funcName)s Name of function containing the logging call.
            # %(lineno)d Source line number where the logging call was issued (if available).
            # %(asctime)s time of log event
            #Trying diffferent formatters, below        
            #fs = '%(asctime)s %(qThreadName)-12s %(levelname)-8s %(message)s'
            fs = '(line %(lineno)d) %(qThreadName)-12s %(levelname)-8s %(message)s'
            
            # formatter calls the logging formatter with the format
            # string and takes a return reference for the desired 
            # format.
            formatter = logging.Formatter(fs)
            
            # sets the formatter for "QtHandler"
            self.handler.setFormatter(formatter)
            
            # Adds QtHandler to the current logger identified above
            # at the very beginning of the program
            logger.addHandler(self.handler)
            
            # Can I add a second handler to send log messages to the console?
            
        except Exception as e:
            # Since logging is not working, add this to log text
            self.log_text.appendHtml(f"<div style='color: purple;'> CRITICAL Exception in setup_logger = {e} </div>")
            
            
    # When data is emitted in the "progress_report" signal, this routine
    # will be called, and the value of the "progress_report" signal will
    # be passed into "progress_report" and the text labels and progress bars
        
    def report_progress(self, progress_report):
        try:
            extra = {"qThreadName": ctname() }
            logger.log(logging.DEBUG, 'Starting report_progress_bar ', extra = extra)
            logger.log(logging.DEBUG, f'progress_report = {progress_report}', extra = extra)
            self.last_update.setText(progress_report[0])
            self.case_name.setText(progress_report[1])
            self.case_num.setText(progress_report[2])
            self.case_progressBar.setValue(progress_report[3])
            self.model_name.setText(progress_report[4])
            self.model_num.setText(progress_report[5])
            self.model_progressBar.setValue(progress_report[6])
        except Exception as e:
            logger.log(logging.ERROR, 'Exception = ' + str(e), extra = extra)
        logger.log(logging.DEBUG, 'report_progress finished', extra = extra)

    
    def change_logging_level(self, level):
        try:
            #level = self.logging_level_select.currentText
            log_level = self.LOG_LEVELS.get(level, logging.INFO)
            message = f'change_logging_level to {level}, {log_level},  handler = {self.handler}'
            message = message.replace("<", "_").replace(">", "_")
            logger.log(logging.DEBUG, message, extra = {"qThreadName": ctname() })
            self.handler.setLevel(level)
            message = f'handler now = ' + str(self.handler)
            message = message.replace("<", "_").replace(">", "_")
            logger.log(logging.DEBUG, message, extra = {"qThreadName": ctname() })
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in change_logging_level = {e}, {print_exception()}', extra = self.extra)

    # this is for log updates. writes the log event to the log_text window
    def update_status(self, status, record):
        try:
            color = self.COLORS.get(record.levelno, 'black')
            s = '<pre><font color="%s">%s</font></pre>' % (color, status)
            self.log_text.appendHtml(s)
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in update_status = {e}, {print_exception()}', extra = self.extra)
    
    #This section sets the working directory based on button click
    def set_working_directory(self):
        try:
            logger.log(logging.DEBUG, 'Executing: set_working_directory', extra = self.extra)
            file = QFileDialog.getExistingDirectory(
                    parent = self,
                    caption = 'Select a Directory',
                    directory = self.last_dir,
                    ) + '/' # returns a tuple of the path/filename and the filetype
            self.working_directory.setText(file)
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in set_working_directory = {e}, {print_exception()}', extra = self.extra)
    
    # This section sets the working directory based on direct text input.
    # There was a request to be able to manipulate this text box directly
    # rather than use the file dialog.
    def capture_working_directory_text(self):
        try:
            logger.log(logging.DEBUG, 'Executing: capture_working_directory_text', extra = self.extra)
            file = self.working_directory.toPlainText()
            if '\\' in file:
                file = str(file).replace(os.path.sep, '/')
                self.working_directory.setText(file)
                # check for '/' at end of filename
            elif file[-1] != '/':
                file += '/'
                self.working_directory.setText(file)
            else:
                self.last_dir = file
                self.worker1_data_dict['working_directory'] = file
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in capture_working_directory_text = {e}, {print_exception()}', extra = self.extra)
     
    #This sets the Top File/path
    def set_top_file(self):
        try:
            logger.log(logging.DEBUG, 'Executing: set_top_file', extra = self.extra)
            file_filter = 'Powerworld File (*.pwb)'
            file = QFileDialog.getOpenFileName(
                    parent=self,
                    caption='Enter filenamee',
                    directory=self.last_dir,
                    filter=file_filter,
                    )
            if type(file[0]) == str:
                self.top_file.setText(file[0])
            else:
                self.top_file.setText('')
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in set_top_file = {e}, {print_exception()}', extra = self.extra)
    
    #This section sets the top_file based on direct text input
    def capture_top_file_text(self):
        try:
            logger.log(logging.DEBUG, 'Executing: capture_top_file_text', extra = self.extra)
            file = self.top_file.toPlainText()
            if '\\' in file:
                file = str(file).replace(os.path.sep, '/')
                self.top_file.setText(file)
            else:
                self.last_dir = '/'.join(file.split('/')[0:-1])
                self.worker1_data_dict['summer_case'] = file
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in capture_top_file_text = {e}, {print_exception()}', extra = self.extra)
    
    # This sets the build_ibnstruction_file/path
    def set_middle_file(self):
        try:
            logger.log(logging.DEBUG, 'Executing: set_middle_file', extra = self.extra)
            file_filter = 'Powerworld File (*.pwb)'
            file = QFileDialog.getSaveFileName(
                        parent=self,
                        caption='Enter filenamee',
                        directory=self.last_dir,
                        filter=file_filter,
                        )
            if type(file[0]) == str:
                self.middle_file.setText(file[0])
            else:
                self.middle_file.setText('')
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in set_middle_file = {e}, {print_exception()}', extra = self.extra)
    
    #This section sets the working directory based on direct text input
    def capture_middle_file_text(self):
        try:
            logger.log(logging.DEBUG, 'Executing: capture_middle_file_text', extra = self.extra)
            file = self.middle_file.toPlainText()
            if '\\' in file:
                file = str(file).replace(os.path.sep, '/')
                self.middle_file.setText(file)
            else:
                self.last_dir = '/'.join(file.split('/')[0:-1])
                self.worker1_data_dict['winter_case'] = file
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in capture_middle_file_text = {e}, {print_exception()}', extra = self.extra)
    
# This sets the build_ibnstruction_file/path
    def set_bottom_file(self):
        try:
            logger.log(logging.DEBUG, 'Executing: set_bottom_file', extra = self.extra)
            file_filter = 'Powerworld File (*.pwb)'
            file = QFileDialog.getOpenFileName(
                        parent=self,
                        caption='Enter filenamee',
                        directory=self.last_dir,
                        filter=file_filter,
                        )
            if type(file[0]) == str:
                self.bottom_file.setText(file[0])
            else:
                self.bottom_file.setText('')
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in set_bottom_file = {e}, {print_exception()}', extra = self.extra)
    
    # This section sets the bottom file based on direct text input
    # There was a request to be able to manipulate this text box directly
    # rather than use the file dialogs.
    def capture_bottom_file_text(self):
        try:
            logger.log(logging.DEBUG, 'Executing: capture_bottom_file_text', extra = self.extra)
            file = self.bottom_file.toPlainText()
            if '\\' in file:
                file = str(file).replace(os.path.sep, '/')
                self.bottom_file.setText(file)
            else:
                self.last_dir = '/'.join(file.split('/')[0:-1])
                self.worker1_data_dict['spring_case'] = file
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in capture_bottom_file_text = {e}, {print_exception()}', extra = self.extra)
            
    def percent_changed(self, state):
        try:
            self.worker1_data_dict['summer_to_spring_pct'] = state
            message = f'summer_to_spring_pct now = {self.worker1_data_dict["summer_to_spring_pct"]}'
            logger.log(logging.DEBUG, message, extra = self.extra)
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in quit_excel_after_changed = {e}, {print_exception()}', extra = self.extra)
            
    def checkbox1_changed(self, state):
        try:
            self.worker1_data_dict['quit_excel'] = (state>0)
            message = f'quit_excel_after_file_creation now = {self.worker1_data_dict["quit_excel"]}'
            logger.log(logging.DEBUG, message, extra = self.extra)
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in quit_excel_after_changed = {e}, {print_exception()}', extra = self.extra)
    
    def checkbox2_changed(self, state):
        try:
            self.worker1_data_dict['saved_scaled_cases'] = (state>0)
            message = f'Saved Scaled Cases now = {self.worker1_data_dict["saved_scaled_cases"]}'
            logger.log(logging.DEBUG, message, extra = self.extra)
            
        except Exception as e:
            logger.log(logging.CRITICAL, f'Exception in quit_excel_after_changed = {e}, {print_exception()}', extra = self.extra)
    
    def change_debug_options(self, state, idx):
        try:
            logger.log(logging.DEBUG, f'state = {state}   idx = {idx}', extra = self.extra)
            self.debug_options[idx] = bool(state)
            message = f'debug_options now = {self.debug_options}'
            logger.log(logging.DEBUG, message, extra = self.extra)
            self.worker1_data_dict['debug_options'] = self.debug_options
            
        except Exception as e:
            logger.log(logging.ERROR, f'Exception in change_debug_options = {e}, {print_exception()}', extra = self.extra)
    
    def run_worker1(self):
        try:
            logger.log(logging.DEBUG, 'Starting "run_worker1"', extra = self.extra)
            # Create a QThread object
            self.thread = QThread()
            # Give the thread a name
            self.thread.setObjectName('Loss_Factor_Study')
            # Create a worker object by calling the "Worker" class defined above
            self.worker = Worker(self.worker1_data_dict)
            # Move worker to the thread just created
            self.worker.moveToThread(self.thread)
            
            # Connect signals and slots:
            # This connects the thread start troutine to the
            # name of the routine defined under the "Worker" class, above
            self.thread.started.connect(self.worker.worker1)
            
            # this connects the "finished' signal to three routines
            # to end the thread when the worker is finished.
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            # this connects the "progress_report" signal defined in
            # in the "Worker" class
            self.worker.progress_report.connect(self.report_progress)
            
            #  Start the thread
            self.thread.start()
            
            # Final resets
            
            # Disables the "worker_start" button when the
            # thread is launched.  Leaving the button enabled
            # will mean that the task can be re-launched multiple
            # times which may or may not be a problem.
            self.worker1_button.setEnabled(False)
            self.worker2_button.setEnabled(False)
            
            # re-enables the "treate_tables" and "create cases" buttons disabled above when
            # when the thread has finished
            self.thread.finished.connect(lambda: self.worker1_button.setEnabled(True))
            self.thread.finished.connect(lambda: self.worker2_button.setEnabled(True))
            # sets the stepLabel text when the thread has finished
            #self.thread.finished.connect(lambda: self.stepLabel.setText("Long-Running Step: 0"))
            
        except Exception as e:
            logger.log(logging.ERROR, f'Exception in run_worker1 = {e}, {print_exception()}', extra = self.extra)
    
    def run_worker2(self):
        try:
            logger.log(logging.DEBUG, 'Starting "run_worker2"', extra = self.extra)
            # Create a QThread object
            self.thread = QThread()
            # Give the thread a name
            self.thread.setObjectName('Create_Cases_Thread')
            # Create a worker object by calling the "Worker" class defined above
            self.worker = Worker(self.worker2_data_dict)
            # Move worker to the thread just created
            self.worker.moveToThread(self.thread)
            
            # Connect signals and slots:
            # This connects the thread start troutine to the
            # name of the routine defined under the "Worker" class, above
            self.thread.started.connect(self.worker.worker2)
            
            # this connects the "finished' signal to three routines
            # to end the thread when the worker is finished.
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            
            # this connects the "progress_report" signal defined in
            # in the "Worker" class
            self.worker.progress_report.connect(self.report_progress)
            
            #  Start the thread
            self.thread.start()
            
            # Final resets
            
            # Disables the "worker_start" button when the
            # thread is launched.  Leaving the button enabled
            # will mean that the task can be re-launched multiple
            # times which may or may not be a problem.
            self.worker1_button.setEnabled(False)
            self.worker2_button.setEnabled(False)
            
            # re-enables the "Work Start" button disabled above when
            # when the thread has finished
            self.thread.finished.connect(lambda: self.worker1_button.setEnabled(True))
            self.thread.finished.connect(lambda: self.worker2_button.setEnabled(True))
            # sets the stepLabel text when the thread has finished
            #self.thread.finished.connect(lambda: self.stepLabel.setText("Long-Running Step: 0"))
                
        except Exception as e:
            logger.log(logging.ERROR, f'Exception in run_worker2 = {e}, {print_exception()}', extra = self.extra)
        
    # Quits the event loop and closes the window when the Exit
    # button is pressed.
    def run_exit(self):
        try:
            self.close()
            return
                
        except Exception as e:
            logger.log(logging.ERROR, f'Exception in run_exit = {e}, {print_exception()}', extra = self.extra)
        
    def force_quit(self):
        try:
            pass
            # For use when the window is closed
            #if self.worker_thread.isRunning():
                #self.kill_thread()
                
        except Exception as e:
            logger.log(logging.ERROR, f'Exception in force_quit = {e}, {print_exception()}', extra = self.extra)



    
    
'''****************************************************************************
*******************************************************************************
****                                                                       ****
****                                                                       ****
****                                 Main                                  ****
****                                                                       ****
****                                                                       ****
*******************************************************************************
****************************************************************************'''
######################################################################
# The code below  resolves the need to kill the kernal after closing
# when executing the code from Spyder
# Discussion: https://stackoverflow.com/questions/57408620/cant-kill-pyqt-window-after-closing-it-which-requires-me-to-restart-the-kernal/58537032#58537032

def main():
    # sets the name of the current thread in QThread
    QtCore.QThread.currentThread().setObjectName('MainThread')
    
    # If the application is not already runnng, launch it,
    # otherwise enter the exitsting instance.
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        print('already running')
        app = QApplication.instance()
    # Closes app
    app.setQuitOnLastWindowClosed(True)    
    # launch main window
    main = My_Application()
    # show he main window
    main.show()
    # put the main window at the top of the desktop
    main.raise_()
    sys.exit(app.exec_())

    

    # returning main to the global coller will avoid
    # problems with Spyder kernal terminating when
    # the application is launched under Sypder
    return main

if __name__ == '__main__':      
    
    # creating a dummy variable ("m") to accept the 
    # object returned from "main" will prevent problems
    # with the kernal dying while running under Spyder.
    m = main()
    

######################################################################
# The code below allows running the software by double clicking from 
# File Explorer

#if __name__ == "__main__":
#    app = 0
#    app = QApplication(sys.argv)
#    window = My_Application()
#    window.show()
#    sys.exit(app.exec_())
