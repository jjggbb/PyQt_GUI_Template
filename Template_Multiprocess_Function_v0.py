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
    Worker 2 runs a simple function that can run a sub-function
    on an array of dummy cases using either a single-processor method or a 
    multi-processing method.
    
'''*************************************************************************'''
"""

'''**************************** Print Exception ****************************'''
#def print_exception():
#    # Return line number data from the last exception
#    from linecache import getline, checkcache
#    from sys import exc_info
#    exc_type, exc_obj, tb = exc_info()
#    f = tb.tb_frame
#    lineno = tb.tb_lineno
#    filename = f.f_code.co_filename
#    checkcache(filename)
#    line = getline(filename, lineno, f.f_globals)
#    return[f'LINE {lineno} "{line.strip()}"']

#!/usr/bin/env python


'''*************************************************************************'''
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


'''**************************** Setup Logging ******************************'''
def addLoggingLevel(levelName, levelNum, methodName=None):
    extra = {'qThreadName' : 'def addLoggingLevel'}
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
        

def data(self, message, *args, **kws):
    # This function gets called when the logger sees a message with priority "DATA"
    # "DATA" has a priority between DEBUG and SUBDATA.
    # Intended to report important variables for troubleshooting
    if self.isEnabledFor(LOGLV_DATA):
        # Yes, logger takes its '*args' as 'args'.
        self.log(LOGLV_DATA, message, args, **kws)
        
def subdata(self, message, *args, **kws):
    # This function gets called when the logger sees a message with priority "SUBDATA"
    # "SUBDATA" has a priority lower than "DATA"
    # Intended to report variables that may not be critical for troubleshooting at the moment that can be removed to reduce log clutter
    if self.isEnabledFor(LOGLV_SUBDATA):
        # Yes, logger takes its '*args' as 'args'.
        self.log(LOGLV_SUBDATA, message, args, **kws)
        
        
'''*************************************************************************'''
def get_preload_dict(preload_file):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    # Formats floating point elements in the passed list to the passed precision
    
    try:
        import os
        
        if os.path.isfile(preload_file):
#            if False:  # Debug skip
            raw_file = open(preload_file,'r')
            preload_raw_text = raw_file.readlines()
            raw_file.close()
                    
#            preload_raw_text = []  # Debug code
            logger.log(logging.DATA, f'preload_raw_text = {preload_raw_text}', extra = extra)
#                    
            preload_data = []
            for line2 in preload_raw_text:
                line = line2[:-1]  # Eliminate carriage return at end of line
                while ' =' in line or '= ' in line: # or '\n' in line:
                    line = line.replace(' =','=').replace('= ', '=')
#                    print(line)
                while line[0] == ' ':
                    line = line[1:]
#                    print(line)
                while line[-1] == ' ':
                    line = line[0:-1]
#                    print(line)
                preload_data += [line.split('=')]
            
            logger.log(logging.DATA, f'preload_data = {preload_data}', extra = extra)
            preload_dict = dict(preload_data)
            return['', '', preload_dict]
                        
        else:
            logger.log(logging.DEBUG, f'No preload file found, using default values', extra = extra)
            err = f'No preload file found, using default values'
            action = 'Warning Only'
            logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
            return [err, action, {}]
                
        logger.log(logging.DATA, f'preload_dict = {preload_dict}', extra = extra)
        
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action, {}]
        

'''*************************************************************************'''
def sum_of_squares(number):
    # A simple placeholder function    
    total = 0
    for x in range(number):
        total += x**0.5
        

'''*************************************************************************'''
def run_cases(case):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}

    try:
        use_multi_proc = case[2]
        if not use_multi_proc:
            logger.log(logging.DEBUG, f'Starting {extra["qThreadName"]}', extra = extra)
            logger.log(logging.DATA, f'case = {case}', extra = extra)
        
        import timeit
        # For an input of 100000000, the function takes about 10 seconds
        start = timeit.default_timer()
        sum_of_squares(case[1])
        time = timeit.default_timer() - start
        
        # form some kind of result
        err = '' # no error
        action = '' # default action
        num_digits = len(f'{case[0]}')
        result = [f'{" "*(10 - num_digits)}Case {case[0]} time: {time:.3f}', time]
        
        # return from def
        return [err, action, result]

    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        if not use_multi_proc:
            logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action, []]
        

'''*************************************************************************'''
def worker2_function(worker2_data_dict):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    
    '''****************************************************************************
    *******************************************************************************
    ****                                                                       ****
    ****                                                                       ****
    ****                           Import Block                                ****
    ****                                                                       ****
    ****                                                                       ****
    *******************************************************************************
    ****************************************************************************'''
    
    from datetime import datetime  # date and time functions
    Starttime = datetime.now()
    
    import pythoncom
#    import glob as gl
#    import os
#    from sys import exit as s_exit
    import multiprocessing
#    import xlwings as xw  # Loads a suite of functions to contol Excel from Python
#    import math
#    from operator import itemgetter  #Reference:  https://wiki.python.org/moin/HowTo/Sorting
#    import sys
    import logging
#    import pandas as pd
#    from copy import deepcopy
    pythoncom.CoInitialize()
#    import csv
    import timeit
    
    global logging
    global logger
    logger = worker2_data_dict['logger']
#    import win32com.client # loads a suite of tools access to windows routines
#    try:  # 'try', 'except', and 'finally' are an iteration structure for error handling
#        pw_com_object = win32com.client.Dispatch('pwrworld.SimulatorAuto') # win32com.client.dispatch is a function that returns a Powerworld case object
#    except Exception as e:
#        err = f'Exception (Loading Libraries) = {e}, {print_exception()}'
#        action = f'Exception'
#        logger.log(logging.CRITICAL, f'{err}\n{" "*0}*********** {action} ***********', extra = extra)
        # End the program here
#        s_exit("Cannot establish pw_com_object.  Exiting program")
        #(f'{err}\n{" "*16}*********** {action} ***********')
        # Signal main thread that the code is done
#       self.progress_report.emit(['Exception', 'none', '0 of 0', 0, 'none', '0 of 0', 0])
#       self.finished.emit()
#       return
    
#    pd.set_option('display.max_columns', 25) # sets the max number of columns to display
#    pd.set_option('display.width', 1000) # sets the max number of chars per line

    '''
    ****************************************************************************************
    # A Powerflow study automation algorithm
    ****************************************************************************************
    '''
    try:
        ''' 
        *************************
        Settings block
        *************************
        '''
        extra = {'qThreadName': 'Settings Block'}
        logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
        
        
        start_level = worker2_data_dict['start_level']
        number_cases = worker2_data_dict['number_cases']
        use_multi_proc = worker2_data_dict['use_multi_proc']
#        debug_options = worker2_data_dict['debug_options']
        logger = worker2_data_dict['logger']
        
        '''
        ***********************************************************************************************************************************************
        Prepare Cases Array
        ***********************************************************************************************************************************************
        '''
        extra = {'qThreadName': 'Create Case Array'}
        logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
        
        # This is normally a complex operation before running cases.
        # It might involve gathering setup information from an Excel file
        # and/or doing some precalculationto generate 'cases_array'.
        # I generally use "__i" for index and "__e" for "element" in list comprehensions
        cases_array = [[__e, start_level + __e, use_multi_proc] for __e in range(number_cases)]
        logger.log(logging.DATA, f'cases_array = {cases_array}', extra = extra)
        
        
        
        # How do I determine how many processors are available automatically?
        # Generally, I set this manually for my machine, setting the value to
        #   two less than my total processor cores.
        start = timeit.default_timer()
        if use_multi_proc:
            '''
            ***********************************************************************************************************************************************
            Run cases using multiprocessing
            ***********************************************************************************************************************************************
            '''
            extra = {'qThreadName': f'Run cases using multiprocessing'}
            logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
            results = []
            # How do I get multiprocessing to work with my PyQT GIU?
            
            # It would be nice to be able to detect the number of cores available 
            # automatically.
            cores = 6 # 12 is faster on my machine, but some engineers have older machines
            pool = multiprocessing.Pool(cores)
            results_mp = pool.imap_unordered(run_cases, cases_array)
    
            # logs the results in the main process as soon as say are ready
            # but results are not in order!
            
            for result in results_mp:
                # I don't know why the logger doesn't work here
                logger.log(logging.DATA, f'result = {result}', extra = extra)
#                print(f'result = {result}')
                results += [result]
                
            # Join after printing all results
            pool.close()
            pool.join()
        
        else:
            '''
            ***********************************************************************************************************************************************
            Run cases in single process
            ***********************************************************************************************************************************************
            '''
            extra = {'qThreadName': f'Run cases in single process'}
            logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
            
            results = []
            for case in cases_array:
                result = run_cases(case)
                logger.log(logging.DATA, f'result = {result}', extra = extra)
                results += [result]
        elapsed_time = timeit.default_timer() - start
        # Generally, I do something with the results like save them to an excel file
        result_message = [f'{"*"*30}', 'Results:']
        result_sum = 0
        for result in results:
            if result[0:2] != ['', '']:
                result_message += ['exception']
            else:
                result_message += [result[2][0]]
                result_sum += result[2][1]
        result_message += ['']
        result_message += [f'Total Processor Time: {result_sum:.3f}']
        result_message += [f'{" "*8}Elapsed Time: {elapsed_time:.3f}']
        result_message += [f'{"*"*30}']
        result_message = '\n\n' + '\n'.join(result_message) + '\n\n'
        logger.log(logging.INFO, result_message, extra = extra)
        
        '''
        ***********************************************************************************************************************************************
        Report start and finish times
        ***********************************************************************************************************************************************
        '''
        extra = {'qThreadName': 'Report times'}
        logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
        
        Endtime = datetime.now()
        message =  f'\n\n**********************************************'
        message +=   f'\n*                                            *'
        message +=   f'\n*        program start and end times         *'
        message +=   f'\n*         start {Starttime.strftime("%d/%m/%Y %H:%M:%S")}          *'
        message +=   f'\n*           end {Endtime.strftime("%d/%m/%Y %H:%M:%S")}          *'
        message +=   f'\n*                                            *'
        message +=   f'\n******** All your base are become ours *******'
        message +=   f'\n*****************   Done!   ******************'
                       
        logger.log(logging.INFO, message, extra=extra)
    
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
#        pw_com_object.CloseCase()
        return[err, action]
#        s_exit(err)
    
def setup_logging():
    import logging
    '''****************************************************************************
    *******************************************************************************
    ****                                                                       ****
    ****                                                                       ****
    ****                          Logging Block                                ****
    ****                                                                       ****
    ****                                                                       ****
    *******************************************************************************
    ****************************************************************************'''
    #print(f'\n\n{" "*0}********* Setup Logging ************')
    #
    ############################## Basic Logging ################################### 
    #logging.basicConfig(format='%(levelname)-8s [%(lineno)d] %(message)s',
    #    datefmt='%Y-%m-%d:%H:%M:%S',
    #    level=logging.DEBUG)
    #
    #logger = logging.getLogger(__name__)
    ########################## Test Basic Logging ##################################
    #
    #logger.debug("This is a debug log")
    #logger.info("This is an info log")
    #logger.critical("This is critical")
    #logger.error("An error occurred")
    #
    #raise SystemExit
    ############################### Advanced Logging ##############################
            
    # Calls the basic config routine to initilize default config settings.
    # Enter desired values for the default logger here.
    # If this is not the first call to basicConfig,
    # nothing will be changed.
    #logging.basicConfig()
    
    # identifies the current logger
    global LOGLV_SUBINFO
    global LOGLV_DATA
    global LOGLV_SUBDATA
    logger = logging.getLogger(__name__)

    LOGLV_SUBINFO = 15 
    logging.addLevelName(LOGLV_SUBINFO, "SUBINFO")
    addLoggingLevel("SUBINFO", 15)
    logging.Logger.subinfo = subinfo
        
    LOGLV_DATA = 6 
    logging.addLevelName(LOGLV_DATA, "DATA")
    addLoggingLevel("DATA", 6)
    logging.Logger.data = data
        
    LOGLV_SUBDATA = 5 
    logging.addLevelName(LOGLV_SUBDATA, "SUBDATA")
    addLoggingLevel("SUBDATA", 5)
    logging.Logger.subdata = subdata

    #set the initial logging level
    # Can be: DEBUG, INFO, WARNING, ERROR, or CRITICAL, by default
    initial_log_level = logging.DATA

    # Sets the logging level for the default logger
    # Can be: DEBUG, INFO, WARNING, ERROR, or CRITICAL, by default
    logger.setLevel(initial_log_level)
    
    
    # check the quantity of handlers
    if len(logger.handlers) == 0:
        # only add these handlers if there are none present
        # to keep from adding a bunch of handlers on each execution from Sypder
    
        # if it is not already createdm create console handler ("ch")
        ch = logging.StreamHandler()
        # Set level to SUBDATA for the console handler "ch"
        ch.setLevel(initial_log_level)
    
        # fs is a string containing format information
        #
        # %(pathname)s Full pathname of the source file where the logging call was issued(if available).
        # %(filename)s Filename portion of pathname.
        # %(module)s Module (name portion of filename).
        # %(funcName)s Name of function containing the logging call.
        # %(lineno)d Source line number where the logging call was issued (if available).
        # %(asctime)s time of log event
        #Trying diffferent formatters, below:        
        #fs = '%(asctime)s %(qThreadName)-12s %(levelname)-8s %(message)s'
        #fs = '(line %(lineno)4d) %(levelname)-8s %(message)s  (thread: %(qThreadName)-12s) '
        fs = '(line %(lineno)4d) %(levelname)-8s %(message)s'
        #fs = '%(levelname)-8s %(message)s %(qThreadName)-12s'
        #fs = '%(levelname)s %(message)s'
    
    
        # "Formatter" calls the logging formatter with the format
        # string and takes a return reference for the desired 
        # format.
        # create formatter
        formatter = logging.Formatter(fs)
    
        # add formatter to the console handler "ch"
        ch.setFormatter(formatter)
        
        # add the console handler "ch" to logger
        logger.addHandler(ch)
    ####################### Test Advanced Logging #################################
    #extra = {'qThreadName': 'Setup Logging'}
    #
    ## Logging test messages
    #logger.log(logging.SUBDATA, "This is a subdata log", extra = extra)
    #logger.log(logging.DATA, "This is a data log", extra = extra)
    #logger.log(logging.DEBUG, "This is a debug log", extra = extra)
    #logger.log(logging.SUBINFO, "This is a subinfo log", extra = extra)
    #logger.log(logging.INFO, "This is an info log", extra = extra)
    #logger.log(logging.WARNING, "This is warning", extra = extra)
    #logger.log(logging.ERROR, "An error occurred", extra = extra)
    #logger.log(logging.CRITICAL, "This is a critical log", extra = extra)
    #
    #logger.log(logging.CRITICAL, "Debug Exit", extra = extra)
    #raise SystemExit
    
    return logger
    
def main():
    import os
    import logging
    global logging
    '''****************************************************************************
    *******************************************************************************
    ****                                                                       ****
    ****                                                                       ****
    ****                            User Variables                             ****
    ****                                                                       ****
    ****                                                                       ****
    *******************************************************************************
    ****************************************************************************'''
    global logger
#    extra = 'main'
    # Call the logging setup function
    logger = setup_logging()
    
    # User entered data needed by case.
    worker2_data_dict = {
                        'start_level' : 100000000,
                        'number_cases' : 10,
                        'use_multi_proc' : True, # When true, and the option is programmed, the function will use a multiprocessing pool to complete studies faster
                        'debug_options' : [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],  # Debug option flags potentially used in the case.
                        'logger' : logger
                        }
    python_dir = os.getcwd()
    result = get_preload_dict(f'{python_dir}/Preloads_Template.txt')
    if result[0:2] != ['', '']:
        return None
    preload_dict = result[2]
    
    for key in preload_dict.keys():
        if key in worker2_data_dict.keys():
            worker2_data_dict[key] = preload_dict[key]
    
    # Call the loss factor function
    worker2_function(worker2_data_dict)
    
    return None

from inspect import currentframe as cf #, getframeinfo as gfi # Used to identify the current function -- avoids some copy-paste issues when making new defs
if __name__ == '__main__':      
    
    # creating a dummy variable ("m") to accept the 
    # object returned from "main" will prevent problems
    # with the kernal dying while running under Spyder.
    m = main()