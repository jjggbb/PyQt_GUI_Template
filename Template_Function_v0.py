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
    Create dummy objects/methods to stand in for Powerworld calls
    Created a demonstration function to show how I generally implement
        powerflow study automation.
    Import general functions from "General_Functions.py"
    Import Powerworld functions from "Powerworld_functions.py"
            
    Worker 2 runs a simple dummy function
    
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


'''****************************************************************************
*******************************************************************************
****                                                                       ****
****                                                                       ****
****                         Basic Functions                               ****
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


#'''*************************************************************************'''
#def ctname():
#    # Get the Qt name of the current thread.
#    return QtCore.QThread.currentThread().objectName()


'''*************************************************************************'''
def get_preload_dict(preload_file):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    # Formats floating point elements in the passed list to the passed precision
    
    try:
        logger.log(logging.DEBUG, f'Starting {extra["qThreadName"]}.', extra = extra)
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
def is_number(text):
    # Identify whether the passed data is a number
    try:
        if text == None or text =='None':
            return False
        float(text)
        return True
    except ValueError:
        return False


'''*************************************************************************'''
def format_float_in_list(target, precision):  # Note: recursive for lists in lists
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    # Formats floating point elements in the passed list to the passed precision
    
    try:
        if type(target) == list or type(target) == tuple:
            string_list = ''
            for item in target:
                item2 = str(item)
                if type(item) == list or type(item) == tuple:
                    # execute this function recursively
                     string_list += ', ' + format_float_in_list(item, precision)
                elif item == True or item == False:
                    # Boolean gives some trouble if not captured
                    string_list = f'{string_list}, {item}'
                elif is_number(item2):
                    if '.' in item2 or 'e' in item2: # float string
                        string_list = f'{string_list}, {float(item2):.{precision}f}'
                    else: # integer, should be good
                        string_list = f'{string_list}, {item}'
                elif type(item) == str:
                    string_list = f"{string_list}, '{item}'"
                else:
                    string_list = f'{string_list}, {item}'
            return '[' + string_list[2:] + ']'
        elif target == True or target == False:
            # Boolean gives some trouble if not captured
            return str(target)
        elif is_number(target):
            item2 = str(target)
            if '.' in item2 or 'e' in item2: # float string
                return f'{float(item2):.{precision}f}'
            else:
                # integer, format to text and return
                return f'{item2}'
        elif type(target) == str:
            return f"'{target}'"
        else:
            return f'{target}'
    
        return 'unexpected return from def "format_float_in_list"'
        
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return ''


'''*************************************************************************'''
def adjust_file_path(file_data, working_dir):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    # Turn filepath/name data into full file/path.  Replace "./" or ".\" with working_dir
    
    try:
        enlist = False
        if type(file_data) != list:
            file_data = [file_data]
            enlist = True
        if len(file_data) > 0:
            if type(file_data[0]) == str:
                file_data = [fpath.replace('\\','/') for fpath in file_data]
                file_data = [f'{working_dir}{fpath}'.replace('./', '') if ((fpath[0:2] == './') or ('/' not in fpath)) else fpath for fpath in file_data]
            if enlist == True:
                file_data = file_data[0]
        
        return file_data
            
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}/n file_data = {file_data}/nworking_dir = {working_dir}'
#        err = f'Exception (loading adjust_file_path) = {e}/n file_data = {file_data}/nworking_dir = {working_dir}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action]


'''*************************************************************************'''
def format_borders(xl_range_obj, weight, XlBordersIndex = 'none', color = 0):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    # Wrapper for formatting the borders of cells in Excel
    #documentation for borders object:
    #https://docs.microsoft.com/en-us/office/vba/api/excel.borders
    
    #documentation for border object:
    #https://docs.microsoft.com/en-us/office/vba/api/excel.border(object)
    
    # enumeration for xlbordersindex object:
    # https://docs.microsoft.com/en-us/office/vba/api/excel.xlbordersindex
    
    # enumeration for xlborderweight object
    #https://docs.microsoft.com/en-us/office/vba/api/excel.xlborderweight
    
    try:
        border_dict = {'xlEdgeLeftAll'      : 1,    # Left edge of each cell in range, not in enumeration docs
                       'xlEdgeRightAll'     : 2,    # Right edge of each cell in range, not in enumeration docs
                       'xlEdgeTopAll'       : 3,    # Top edge of each cell in range, not in enumeration docs
                       'xlEdgeBottomAll'    : 4,    # Bottom edge of each cell in range, not in enumeration docs
                       'xlDiagonalDown'     : 5,    # Border running from the upper-left corner to the lower-right of each cell in the range.
                       'xlDiagonalUp'       : 6,    # Border running from the lower-left corner to the upper-right of each cell in the range.
                       'xlEdgeLeft'         : 7,    # Border at the left edge of the range.
                       'xlEdgeTop'          : 8,    # Border at the top of the range.
                       'xlEdgeBottom'       : 9,    # Border at the bottom of the range.
                       'xlEdgeRight'        : 10,   # Border at the right edge of the range.
                       'xlInsideVertical'   : 11,   # Vertical borders for all the cells in the range except borders on the outside of the range.
                       'xlInsideHorizontal' : 12}   # Horizontal borders for all cells in the range except borders on the outside of the range.
        
        if XlBordersIndex == 'xlCrossoutAll':  # Custom function to "cross out" all cells in the range
            xl_range_obj.api.Borders(5).Weight = weight
            xl_range_obj.api.Borders(5).Color = color
            xl_range_obj.api.Borders(6).Weight = weight
            xl_range_obj.api.Borders(6).Color = color
            return ''
        elif XlBordersIndex == 'xlBottomRightAll': # Custom function to format the bottom and right edges for all cells in the range
            xl_range_obj.api.Borders(2).Weight = weight
            xl_range_obj.api.Borders(2).Color = color
            xl_range_obj.api.Borders(4).Weight = weight
            xl_range_obj.api.Borders(4).Color = color
            return ''
        else:
            edge = border_dict.get(XlBordersIndex, 0)
            if edge:
                xl_range_obj.api.Borders(edge).Weight = weight
                xl_range_obj.api.Borders(edge).Color = color
                return ''
            else:
                xl_range_obj.api.Borders.Weight = weight
                xl_range_obj.api.Borders.Color = color
                if XlBordersIndex != 'none':
                    return f'XlBordersIndex = "{XlBordersIndex}" not found.  Formatted all edges.'
                else:
                    return ''

    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action]


'''*************************************************************************'''
def starbox_msg(msg, num_stars, num_spaces, num_space_lines):
    if type(msg) == str:
        # Make the passed message into a list of strings for each line of text
        # If there are '\n' only lines, they will be a blank string in the list ('')
        msg = msg.split('\n')
    elif type(msg) ==  list:
        # If it is already a list, convert each element to a string
        msg = [str(__e) for __e in msg]
    else:
        # If it is something other than a string, convert it to a string
        msg = str(msg)
    # Identify the longest string in the list of strings
    max_len = max([len(__e) for __e in msg])
    # Initialize and empty string
    mult_msg = ''
    for text in msg:
        # For each line, identify any exra spaces needed to fill out the "Starbox"
        # For for an odd difference, the extra space will go on the end
        # For the longest line, extra_spaces and orphan_space should both be zero
        xtra_spaces, orphan_space = divmod(max_len - len(text), 2)
        # Build the new line for the starboxed message and concatinate it to 'mult_msg'
        mult_msg += num_stars * '*' + num_spaces * ' ' + xtra_spaces * ' ' + text
        mult_msg += num_spaces * ' ' + xtra_spaces * ' ' + orphan_space * ' ' + num_stars * '*' + '\n'
    # Build the border lines (all stars)
    sborder = ('*' * (max_len + num_spaces*2 + num_stars*2) + '\n') * num_stars
    # Build the lines above and below the message lines that contain empty space
    space_lines = (num_stars * '*' + ' ' * (max_len + num_spaces*2) + num_stars * '*' + '\n') * num_space_lines
    # return the Starboxed message
    return ('\n' + sborder + space_lines + mult_msg + space_lines + sborder)



'''
****************************************************************************************
Post2Excel
# this section posts the data passed into Excel in the proper tab
rethink this: post as table or array
****************************************************************************************
'''
def Post2Excel(tab_name, obj, Excel_headers, obj_data, fmt_lst, wb):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    
    try:
        logger.log(logging.DEBUG, f'Starting {extra["qThreadName"]}.', extra = extra)
        
        import xlwings as xw
        
        if len(tab_name) > 31:
            logger.log(logging.WARNING, f'Warning:  Worksheet name is too long for Excel\n Changing {tab_name} to {tab_name[0:31]}', extra = extra)
            tab_name = tab_name[0:31]
            
        logger.log(logging.INFO, f'Posting:  {tab_name}', extra = extra)
        
        #look for an existing sheet.  If not present, create it
        if tab_name in [xw.sheets[i].name for i in wb.sheets]:
            sht = xw.sheets[[i.name for i in wb.sheets].index(tab_name)]  #sets the active sheet to tab_name if the sheet name exists
        else:
            sht = wb.sheets.add(tab_name) #adds a sheet named tab_name if the sheet does not already exist
        sht.activate()
        sht.clear_contents()
        
        # Post title
        sht.range(1, 1).value = obj
        # Post column headers
        sht.range(2, 1).value = Excel_headers
        
        endrow = len(obj_data)
        endcol = len(obj_data[0])
#        
#        # Make column headers two lines if required
#        sht.range((2,1), (2, endcol)).api.RowHeight = 45
#        sht.range((2,1), (2, endcol)).api.WrapText = True
        
        # Post the object data
        sht.range((3,1), (endrow + 2, endcol)).value = obj_data
        
        # Set any special formatting
        for fmt_rng, fmt_dec in fmt_lst:
            sht.range(fmt_rng).number_format = fmt_dec
        
        # Autofit the column width
        sht.range((2,1), (endrow + 2, endcol)).columns.autofit()
        
        return ['', '', sht]

    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action, '']
        
    
'''****************************************************************************
*******************************************************************************
****                                                                       ****
****                                                                       ****
****                     General Powerworld Functions                      ****
****                                                                       ****
****                                                                       ****
*******************************************************************************
****************************************************************************'''
def create_filters(filters_data, pw_com_object):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    # Create multiple filters in the active case using the passed list
    try:
        logger.log(logging.DEBUG, f'Starting {extra["qThreadName"]}.', extra = extra)
        
        results = []
        # Enter EDIT mode
        for filter_data in filters_data:
            resultx01 = create_filter(filter_data, pw_com_object)
            results.append(resultx01)
        
        if True in [result[0:2] != ['', ''] for result in results]:
            err = f'Failed to create one or more advanced filters.'
            action = 'Error'
        else:
            err = ''
            action = ''
            
        return [err, action, results]
        
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action, []]


'''*************************************************************************'''
def create_filter(filter_data, pw_com_object):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    # Create single filter in the active case using the passed list
    
    try:
        logger.log(logging.DEBUG, f'Starting {extra["qThreadName"]}.', extra = extra)
        
        import pythoncom
        pythoncom.CoInitialize()
        
        f_type = filter_data[0].split(',')[0].replace(' ','').replace('"','')
        f_name = filter_data[0].replace(' ,',',').replace(', ',',').split(',')[1]
#        result = pw_com_object.RunScriptCommand('EnterMode(EDIT);')
#        if result != '':
#            return_data = [[f'Could not enter EDIT mode. Result = {result[0]}','']]
        resultx02 = pw_com_object.RunScriptCommand(f'CreateData(Filter, [ObjectType,FilterName,FilterLogic,Number,FilterPre,Enabled], [{filter_data[0]}]);')
        if resultx02[0] != '':
            err = f'Error creating {f_name} filter: {resultx02[0]}'
            action = 'Error'
            logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
            return [err, action]
        
        for idx, condition in enumerate(filter_data[1]):
        # Add Bus-Selection filter conditions
            resultx03 = pw_com_object.RunScriptCommand(f'CreateData(Condition, [ObjectType,FilterName,ConditionNumber,VariableName,ConditionType,ConditionValue, ConditionValue:1,ConditionCaseAbs], [{condition}]);') # conditon1 =
            if resultx03[0] != '':
                err = f'Error adding {f_name} condition {idx+1}:  condition = {condition}, result = {resultx03[0]}'
                action = 'Error'
                logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                return [err, action]
        
        # Check filter creation
        resultx04 = pw_com_object.GetParametersSingleElement('Filter', ['ObjectType', 'FilterName', 'NumElements'], [f_type, f_name.replace('"',''), 0])
        if resultx04[0] != '':
            err = f'Error checking {f_name} filter: {resultx04[0]}.'
            action = 'Error'
            logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
            return [err, action]
        elif int(float(resultx04[1][2])) != len(filter_data[1]):
            err = f'Error, incorrect quantity of conditions for {f_name} filter.  Should be {len(filter_data[1])}, actual = {resultx04[1][2]}'
            action = 'Error'
            logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
            return [err, action]
        
        return['','']
        
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action]


'''*************************************************************************'''
def change_filter_conditionvalue(filter_data, pw_com_object):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    # Change an existing filter condition according to the passed filter data
    
    try:
        import pythoncom
        pythoncom.CoInitialize()
        object_type, filter_name, condition_num, condition_value = filter_data
    
        result = pw_com_object.ChangeParametersSingleElement('Condition', ['ObjectType', 'FilterName', 'ConditionNumber', 'ConditionValue'], filter_data)
        return result
        
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action]


'''*************************************************************************'''
def solve_twice(calling_thread, pw_com_object):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    
    try:
        # Solve the case twice
        result = pw_com_object.RunScriptCommand('SolvePowerFlow(RECTNEWT);')
        if result[0] != '':
            err = f'Error solving first Powerflow. Called by {calling_thread}. Result = {result[0]}'
            action = 'Skipped'
            logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action]
            
        result = pw_com_object.RunScriptCommand('SolvePowerFlow(RECTNEWT);')
        if result[0] != '':
            err = f'Error solving second Powerflow. Called by {calling_thread}. Result = {result[0]}'
            action = 'Skipped'
            logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action]
        
#        # DEBUG: Gather and report object data for troubleshooting
#        object_type = ['Interface', 'InjectionGroup']
#        element_data_vars = [['FGName', 'FGMW', 'CustomString:1', 'CustomString:2'], ['InjGrpName', 'CustomString', 'CustomString:1', 'CustomString:4']]
#        element_data = [['PDCI', '', '', ''], ['ZZ NA -- MOD Alg 01', '', '', '']]
#        for element in list(zip(object_type, element_data_vars, element_data)):
#            result = pw_com_object.GetParametersSingleElement(element[0], element[1], element[2])
#            if result[0] != '':
#                err = f'Cannot gather data from case. Result = {result[0]}'
#                action = 'Waning Only'
#                logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
#            else:
##                logger.log(logging.SUBINFO, f'DataElement: Variables = {element_data_vars}, element_data = {format_float_in_list(result[1], 1)}', extra = extra)
#                post_data = format_float_in_list(result[1], 1)
#                logger.log(logging.INFO, f'Debug data check = {post_data}', extra = extra)
            
        return['','']

    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action]


'''*************************************************************************'''
def adjust_inj_grp_mw(inj_grp, adj_mw, pw_com_object, enforce_limits = True, reset_target = False, limit_min_to_zero = False, enforce_AGC = False):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    
    try:
        logger.log(logging.DEBUG, f'Starting {extra["qThreadName"]}', extra = extra)
        
        # Get current injection group MW level, GenMWMin, and GenMWMin
        logger.log(logging.DEBUG, f'Gathering {inj_grp} levels: MW, GenMWMin, and GenMWMax ', extra = extra)
        result = pw_com_object.GetParametersSingleElement('InjectionGroup', ['Name','MW', 'GenMWMin', 'GenMWMax'], [inj_grp, '', '', ''])
        # Error handling for pw call
        if result[0] != '':
            err = f'Could not get data for {inj_grp}. \n result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
        inj_grp_mw = float(result[1][1])
        inj_grp__min_mw = float(result[1][2])
        inj_grp__max_mw = float(result[1][3])
        logger.log(logging.DATA, f'inj_grp_mw = {inj_grp_mw:.1f}, inj_grp__min_mw = {inj_grp__min_mw:.1f}, inj_grp__max_mw = {inj_grp__max_mw:.1f}', extra = extra)
        
        # Check against both limits
        for limit in [[inj_grp__max_mw, 'max', 1], [inj_grp__min_mw, 'min', -1]]:
            limit_mw, limit_txt, limit_sgn = limit
            # Check if adj_mw is outside this limit
            if (limit_sgn * adj_mw > 0) and (limit_sgn * (limit_mw - inj_grp_mw) < .1):
                err = f'Injection group alread at {limit_txt} MW.'
                action = 'Warning'
                logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
                return[err, action, [inj_grp_mw, inj_grp__min_mw, inj_grp__max_mw]]
    
        # Add Current MW level to model_data[model_data_idx_list[7]]
        desired_mw = inj_grp_mw + adj_mw
        logger.log(logging.DATA, f'adjust_inj_grp: start_mw = {inj_grp_mw:.1f}, desired_mw = {desired_mw:.1f}', extra = extra)
        
        # Call set_inj_grp with new MW levels
        result = scale_inj_grp_mw(inj_grp, desired_mw, pw_com_object, enforce_limits = enforce_limits, reset_target = reset_target, limit_min_to_zero = limit_min_to_zero, enforce_AGC = enforce_AGC)
        # Error handling for set_inj_grp call
        if result[0:2]!= ['','']:
            # Log that an error was returned for debug, but return results
            logger.log(logging.DEBUG, f'Error returned from "scale_inj_grp_mw"', extra = extra)
            return result
        
        return ['', ''] + result[2:]
        
        
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return[err, action, [None, None, None, None]]


'''*************************************************************************'''
def scale_inj_grp_mw(inj_grp, level, pw_com_object, enforce_limits = True, reset_target = False, limit_min_to_zero = False, enforce_AGC = False):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    
    try:
        logger.log(logging.DEBUG, f'Starting {extra["qThreadName"]}', extra = extra)
        
        global G_prefix
        
        if enforce_limits:
            enforce_limits_txt = 'YES'
        else:
            enforce_limits_txt = 'NO'
        
        # Limit level to zero if required
        if limit_min_to_zero:
            level = max(0, level)
        
        # set all injection groups BGScale parameter to "NO"
        logger.log(logging.DEBUG, f'Setting all BGScale to "NO"', extra = extra)
        result = pw_com_object.RunScriptCommand('SetData(InjectionGroup, ["BGScale"], ["NO"], ALL);')
        if result[0] != "":
            err = f'Error setting BGSCALE = "NO" for all injection groups. Result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
        
        # set the inj_grp BGScale parameter to "YES"
        logger.log(logging.DEBUG, f'Setting BGScale to "YES", inj_grp = {inj_grp}', extra = extra)
        result = pw_com_object.ChangeParametersSingleElement('InjectionGroup', ['InjGrpName', 'EnforceGenMWLimits', 'PVCEnforcePosLoad', 'BGScale', 'BGScale:1'], [inj_grp, enforce_limits_txt, 'YES', 'YES', 'YES'])
        if result[0] != "":
            err = f'Error setting BGSCALE = "YES" for injection group {inj_grp}. Result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
        
        # Set scale options?
        pass
        
        # Get current injection group MW level, GenMWMin, GenMWMin, and target
        logger.log(logging.DEBUG, f'Gathering {inj_grp} levels: MW, GenMWMin, and GenMWMax ', extra = extra)
        result = pw_com_object.GetParametersSingleElement('InjectionGroup', ['Name','MW', 'GenMWMin', 'GenMWMax'], [inj_grp, '', '', ''])
        # Error handling for pw call
        if result[0] != '':
            err = f'Could not get data for {inj_grp}. \n result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
        intial_inj_grp_mw = float(result[1][1])
        inj_grp__min_mw = float(result[1][2])
        inj_grp__max_mw = float(result[1][3])
        logger.log(logging.DATA, f'intial_inj_grp_mw = {intial_inj_grp_mw:.1f}, inj_grp__min_mw = {inj_grp__min_mw:.1f}, inj_grp__max_mw = {inj_grp__max_mw:.1f}', extra = extra)
        
        # Set Filter partpt filter for this injgrp
        filter_data = ['PartPointGen', f'{G_prefix}_NA_filter_Inj_Grp_Gens', '1', inj_grp]
        result = change_filter_conditionvalue(filter_data, pw_com_object)
        if result[0] != '':
            err = f'Failed to change injection group filter.  Result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
            
        # Get data for gens in inj_grp
        result = pw_com_object.GetParametersMultipleElementRect('PartPointGen', ['BusNum', 'GenID', 'GenMW', 'GenMWMax', 'Status'], f'{G_prefix}_NA_filter_Inj_Grp_Gens')
        if result[0] != '':
            err = f'Could not get generator list from {inj_grp}.  Result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
        # figure out if any of the operating gens are low
        operating_gens = [[__e[0], __e[1], float(__e[2]), float(__e[3]), __e[4]] for __e in result[1] if (__e[4] == 'Closed')]
        low_gens = [__e for __e in operating_gens if abs(__e[2]) < .05 * abs(__e[3])]
        
        #if current MW is less than 10 or there are low gens, set all gens to max MW
        if intial_inj_grp_mw < 10 or len(low_gens)>0:            
            # Set all gens in Injection Group to GenMaxMW
            logger.log(logging.DEBUG, f'Setting gens in {inj_grp} to GenMWMax', extra = extra)
            result = pw_com_object.RunScriptCommand('SetData(Gen, [GenMW], [@GenMWMax], "<DEVICE>InjectionGroup ' + f"'{inj_grp}'" + '");')
            if result[0] != "":
                err = f'Error setting current gen MW level for injection group {inj_grp} to @GenMaxMW. Result = {result[0]}'
                action = 'Error'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                return[err, action, [None, None, None, None]]
        
        # Scale the inj_grp MW to target value
        logger.log(logging.DEBUG, f'Scaling {inj_grp} to {level:.1f}MW', extra = extra)
#        result = pw_com_object.RunScriptCommand(f'Scale(INJECTIONGROUP, MW, [{level:.1f}], "<DEVICE>InjectionGroup ' + f"'{inj_grp}'" + '");')
        result = pw_com_object.RunScriptCommand(f'Scale(INJECTIONGROUP, MW, [{level}]);')
        if result[0] != '':
            err = f'Error scaling {inj_grp} to target level. Result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
        
        # Set the scale flag back to "NO"
        result = pw_com_object.RunScriptCommand(f'SetData(InjectionGroup, [InjGrpName, BGScale], ["{inj_grp}", "NO"]);')
        # error handling for pw call
        if result[0] != '':
            err = f'Failure setting BGScale flag.  Result = {result[0]}'
            action = 'Error'
            logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
            
        # DEBUG: Check the resulting level
        result = pw_com_object.GetParametersSingleElement('InjectionGroup', ['Name','MW', 'CustomFloat:1'], [inj_grp, '', '', '', ''])
        if result[0] != "":
            err = f'Error gathering current gen MW level for injection group {inj_grp}. Result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return[err, action, [None, None, None, None]]
        end_mw = float(result[1][1])
        if is_number(result[1][4]):
            target_mw = float(result[1][4])
        else:
            target_mw = None
        logger.log(logging.DEBUG, f'Check: {inj_grp} levels: start_mw = {intial_inj_grp_mw:.1f}, desired_mw = {level:.1f}, end_mw = {end_mw:.1f}', extra = extra)
            
        # Check if level at/beyond either limit
        for limit in [[inj_grp__max_mw, 'max', 1], [inj_grp__min_mw, 'min', -1]]:
            limit_mw, limit_txt, limit_sgn = limit
            # Check if adj_mw is outside this limit
            if (limit_sgn * (limit_mw - end_mw)) < .1:
                err = f'Injection group alread at {limit_txt} MW.'
                action = 'Warning'
                logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
                return[err, action, [end_mw, inj_grp__min_mw, inj_grp__max_mw, target_mw]]
        
        return['', '', [end_mw, inj_grp__min_mw, inj_grp__max_mw, target_mw]]
        
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return[err, action, [None, None, None, None]]


'''*************************************************************************'''
def scale_area_load_mw(area_num, new_load, pw_com_object, enforce_agc = False):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}
    
    try:
        logger.log(logging.DEBUG, f'Starting {extra["qThreadName"]}', extra = extra)
        
        global G_prefix
        
        if enforce_agc:
            enforce_agc_txt = 'YES'
        else:
            enforce_agc_txt = 'NO'
        
        # Set all Area BGScale to "NO"
        logger.log(logging.DEBUG, f'Setting all BGScale to "NO"', extra = extra)
        result = pw_com_object.RunScriptCommand('SetData(Area, ["BGScale"], ["NO"], ALL);')
        if result[0] != "":
            err = f'Error setting BGSCALE = "NO" for all injection groups. Result = {result[0]}'
            action = 'Study Stopped'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return [err, action]
        
        # set Area BGScale to "YES"
        logger.log(logging.DEBUG, f'Setting Area {area_num} BGScale to "YES"', extra = extra)
        result = pw_com_object.ChangeParametersSingleElement('Area', ['Number', 'Scale'], [area_num, 'YES'])
        if result[0] != "":
            err = f'Error setting BGSCALE = "YES" for Area {area_num}. Result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return [err, action]
        
        # Set "Scale Only AGCable Generation and Loads" to "YES"
        result = pw_com_object.ChangeParametersSingleElement('Scale_Options_Value', ['VariableName','ValueField'], ['EnforceAGC', enforce_agc_txt])
        if result[0] != "":
            err = f'Error setting EnforceAGC = "{enforce_agc_txt}". Result = {result[0]}'
            action = 'Study Stopped'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return [err, action]
        
        # Scale loads
        # Note: Using "MW" seems safer than using "FACTOR" in the script command
        #       Also make checking the result manually easier
        logger.log(logging.DEBUG, f'Scaling Area load to {new_load:.1f}', extra = extra)
#        result = pw_com_object.RunScriptCommand(f'Scale(INJECTIONGROUP, MW, [{level:.1f}], "<DEVICE>InjectionGroup ' + f"'{inj_grp}'" + '");')
        result = pw_com_object.RunScriptCommand(f'Scale(LOAD, MW, [{new_load}]);')
        if result[0] != '':
            err = f'Error scaling Area load to target level. Result = {result[0]}'
            action = 'Error'
            logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
            return [err, action]
        
        return['', '']
        
    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action]


'''*************************************************************************'''
def save_pw_case(dir_name, save_name, pw_com_object):
    extra = {"qThreadName": 'def ' + cf().f_code.co_name}

    try:
        # Save the case
        dir_name = dir_name.replace('/', '\\')
        
        import os
        
        # Check for a directory, create if needed
        if os.path.exists(f'{dir_name}'):
            logger.log(logging.DEBUG, f'Directory for case files already exists; good.', extra = extra)
        else:
            logger.log(logging.INFO, f'Creating directory in working directory for case files: {dir_name}', extra = extra)
            os.mkdir(f'{dir_name}')

        # Save the case
        logger.log(logging.INFO, f'Saving Powerworld Case as: {dir_name}{save_name}', extra = extra)
        result = pw_com_object.RunScriptCommand(f'SaveCase("{dir_name}{save_name}", PWB);')
        logger.log(logging.DEBUG, f'Case Saved', extra = extra)
        if result[0] != '':
            logger.log(logging.ERROR, f'Save case failed: Result = {result[0]}', extra = extra)

        # return from def
        return result

    except Exception as e:
        err = f'Exception ({extra["qThreadName"]}) = {e}, {print_exception()}'
        action = 'Exception'
        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
        return [err, action, []]

def worker1_function(worker1_data_dict):
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
    
    print(f'\n\n{" "*0}********* Loading Libraries ************')
    import pythoncom
    #import glob as gl
    import os
    from sys import exit as s_exit
    import xlwings as xw  # Loads a suite of functions to contol Excel from Python
    #import math
    #from operator import itemgetter  #Reference:  https://wiki.python.org/moin/HowTo/Sorting
    #import sys
    import logging
    import pandas as pd
    #from copy import deepcopy
    pythoncom.CoInitialize()
    #import csv
    
    global logging
    global logger
    logger = worker1_data_dict['logger']
    import win32com.client # loads a suite of tools access to windows routines
    try:  # 'try', 'except', and 'finally' are an iteration structure for error handling
        pw_com_object = win32com.client.Dispatch('pwrworld.SimulatorAuto') # win32com.client.dispatch is a function that returns a Powerworld case object
    except Exception as e:
        err = f'Exception (Loading Libraries) = {e}, {print_exception()}'
        action = f'Exception'
        logger.log(logging.CRITICAL, f'{err}\n{" "*0}*********** {action} ***********', extra = extra)
        # End the program here
#        s_exit("Cannot establish pw_com_object.  Exiting program")
        #(f'{err}\n{" "*16}*********** {action} ***********')
        # Signal main thread that the code is done
#       self.progress_report.emit(['Exception', 'none', '0 of 0', 0, 'none', '0 of 0', 0])
#       self.finished.emit()
#       return
    
    pd.set_option('display.max_columns', 25) # sets the max number of columns to display
    pd.set_option('display.width', 1000) # sets the max number of chars per line
    
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
    
        # I import user data as a dict.  The user data can come from the 
        # "main()" function, below, or from the GUI.
        cwd = worker1_data_dict['working_directory']
        summer_case = worker1_data_dict['summer_case']
        winter_case = worker1_data_dict['winter_case']
        spring_case = worker1_data_dict['spring_case']
        initial_cases = [summer_case, winter_case, spring_case]
        save_casenames = worker1_data_dict['save_casenames']
        summer_to_spring_pct = worker1_data_dict['summer_to_spring_pct']
        case_load_levels = worker1_data_dict['case_load_levels']
        max_slack_deviation = worker1_data_dict['max_slack_deviation']
#        quit_excel = worker1_data_dict['quit_excel']
        saved_scaled_cases = worker1_data_dict['saved_scaled_cases']
#        gui_active = worker1_data_dict['gui_active']
#        use_multi_proc = worker1_data_dict['use_multi_proc']
#        debug_options = worker1_data_dict['debug_options']
        
        python_dir = os.getcwd()
        
        # sets the current working directory to the level above the current working directory
        os.chdir(os.path.dirname(python_dir))
        
        if cwd[0:2] == './':
            cwd = cwd.replace('./', os.getcwd())
        logger.log(logging.DATA, f'Current working directory:\n{cwd}', extra = extra)
        
        # In some funtions, I have been known to set the current working directory
        #   to cwd
#        os.chdir(cwd)
        
        # Adjust the file path as required
        initial_cases = []
        for case in [summer_case, winter_case, spring_case]:
            if '/' not in case and '\\' not in case:
                initial_cases += [f'{cwd}\\Starting_Cases\\{case}'.replace('/', '\\')]
            elif './' in case[0:2]:
                initial_cases += [case.replace('./', cwd + '\\').replace('/', '\\')]
            else:
                initial_cases += [case.replace('/', '\\')]
        summer_case = initial_cases[0] # Update summer case with new path
        spring_case = initial_cases[2] # Update spring case with new path
        
        # Turn percent into fraction
        summer_to_spring_pct = summer_to_spring_pct/100.0
        
        # Develop case_load_named list.
        # Example: case_load_named = ['_500MW','_400MW','_300MW','_200MW','_100MW','_Base','_Minus_100MW','_Minus_200MW','_Minus_300MW','_Minus_400MW','_Minus_500MW']
        case_load_names = [f'_Minus_{-(__e)}MW' if __e < 0 else '_Base' if __e == 0 else f'_{__e}MW' for __e in case_load_levels]
        case_inputs = list(zip(case_load_levels, case_load_names))
        
        # Filter definition lists for "create_filters" function
        global G_prefix
        G_prefix = 'ZZ_LF'
        
        # This variable contains data necessary to create filter objects within Powerworld
        # After a Powerworld case is opened, I generally create some filters
        #   using my "create_filters" function.  The actual filtering is performed
        #   by Powerworld when some calls are made to Powerworld by the autmation.
        # The data shown here is an example of a set of filters.  It won't be used
        #   in this demo.
        filters_data = [[f'"Bus", "{G_prefix}_Bus_Owner_Area_02_Bus", "OR", 1, "NO ", "YES"',
                           [f'"Bus", "{G_prefix}_Bus_Owner_Area_02_Bus", 1, "OwnerNumber", "inrange", "101, 102, 103, 104", "", "NO"']],
                        [f'"AreaTieLine", "{G_prefix}_Tielines_Area_02", "OR", 1, "NO ", "YES"',
                           [f'"AreaTieLine", "{G_prefix}_Tielines_Area_02", 1, "AreaNumNear", "=", "02", "", "NO"',
                            f'"AreaTieLine", "{G_prefix}_Tielines_Area_02", 2, "AreaNumFar", "=", "02", "", "NO"']],
                        [f'"Area", "{G_prefix}_Area_01", "AND", "1", "NO", "YES"',
                           [f'"Area", "{G_prefix}_Area_01", 1, "Number", "=", "01", "", "NO"']],
                        [f'"Area", "{G_prefix}_Area_02", "AND", "1", "NO", "YES"',
                           [f'"Area", "{G_prefix}_Area_02", 1, "Number", "=", "02", "", "NO"']],
                        [f'"Area", "{G_prefix}_Area_01_or_02", "OR", "1", "NO", "YES"',
                           [f'"Area", "{G_prefix}_Area_01_or_02", 1, "Number", "=", "01", "", "NO"',
                            f'"Area", "{G_prefix}_Area_01_or_02", 2, "Number", "=", "02", "", "NO"']],
                        [f'"Shunt", "{G_prefix}_Shunts_Reactors_Active_Area_02", "AND", "1", "NO", "YES"',
                           [f'"Shunt", "{G_prefix}_Shunts_Reactors_Active_Area_02", 1, "MvarNom", "<", "0", "", "NO"' ,
                            f'"Shunt", "{G_prefix}_Shunts_Reactors_Active_Area_02", 2, "AreaNumber", "=", "02", "", "NO"',
                            f'"Shunt", "{G_prefix}_Shunts_Reactors_Active_Area_02", 3, "Mvar", "<", "0", "", "NO"']],
                        [f'"Branch", "{G_prefix}_Branches_Owners_List", "AND", "1", "NO", "YES"',
                           [f'"Branch", "{G_prefix}_Branches_Owners_List", 1, "OwnerNum1", "inrange", "101, 102, 103, 104", "", "NO"']],
                        [f'"StudyMWTransactions", "{G_prefix}_Area_01_MW_Transactions", "OR", 1, "NO", "YES"',
                           [f'"StudyMWTransactions", "{G_prefix}_Area_01_MW_Transactions", 1, "NumberImport", "=", "01", "", "NO"',
                            f'"StudyMWTransactions", "{G_prefix}_Area_01_MW_Transactions", 2, "NumberExport", "=", "01", "", "NO"']],
                        [f'"PartPointGen", "{G_prefix}_NA_filter_Inj_Grp_Gens", "AND", "1", "NO", "YES"',
                           [f'"PartPointGen", "{G_prefix}_NA_filter_Inj_Grp_Gens", 1, "GroupName", "=", "Inj_Grp_Name", "", "NO"',
                            f'"PartPointGen", "{G_prefix}_NA_filter_Inj_Grp_Gens", 2, "Status", "=", "Closed", "", "NO"']]]
        
        #Set the directory name to save the full AC results
        Study_Results_dir = cwd + '\\Results\\'
        
        # Close any orphan cases
        # This is a call to Powerworld to close the current open case.
        # If for some reason there is an open case (due to, say, and unexpected exit
        #   from the previous run), this will close it.  Open cases are akin to
        #   a memory leak.
        pw_com_object.CloseCase()
        
        '''
        ***********************************************************************************************************************************************
        Find/Create LSP Starting Case
        ***********************************************************************************************************************************************
        '''
        extra = {'qThreadName': 'Find/Create LSP Starting Case'}
        logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
        
        # check if the LSP case already exists.  If not then:
        if os.path.isfile(spring_case):
            logger.log(logging.INFO, f'Spring case has been found:\n{" "*21}Case: {spring_case}', extra = extra)
        else:
            logger.log(logging.INFO, f'Spring case not found:\n{" "*21}Case: {spring_case}\n{" "*21}Creating case from {summer_case}.', extra = extra)
            # Load HS case
            logger.log(logging.DEBUG, f'Loading {spring_case}', extra = extra)
            if os.path.isfile(spring_case):
                result = pw_com_object.OpenCase(spring_case)
                if result[0] != '':
                    err = f'Error loading Summer case. Result = {result[0]}'
                    action = 'Study Stopped'
                    logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                    pw_com_object.CloseCase()
                    return[err, action]
#                    s_exit(err)
            else:
                err = f'File not found: {spring_case}'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # Add the injection group participation point filter
            logger.log(logging.DEBUG, f'Creating PartPointGen filter', extra = extra)
            result = create_filter(filters_data[-1], pw_com_object) # in this case, the last filter definition in filters_data
            if result[0:2] != ['', '']:
                err = f'Failed to create PartPointGen filter.'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # May need to load a dummy slack to store change in level
            pass
            
            # Set Area 01 IG Slack to "Censored"
            slack_inj_grp = 'Censored Total Gen'
            # Set area 01 AGC response to injection group slack
            result = pw_com_object.ChangeParametersSingleElement('Area', ['Number','SlackInjectionGroup', 'AGC'], [1, slack_inj_grp, 'IG Slack'])
            # Script alternative
    #        result = pw_com_object.RunScriptCommand(r'SetData(Area, [Number,SlackInjectionGroup, AGC], [01, "Censored Total Gen", "IG Slack"]);')
            if result[0] != '':
                err = f'Error setting area AGC and IG Slack data. Result = {result[0]}'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
        
            # get initial slack level and area load level
            result = pw_com_object.GetParametersSingleElement('Area', ['Number', 'SlacIGMW', 'LoadMW'], [1, '', ''])
            if result[0] != '':
                err = f'Error getting area slack initial target. Result = {result[0]}'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
    #            return[err, action]
                pw_com_object.CloseCase()
                s_exit(err)
            initial_slack_mw = float(result[1][1])
            initial_load_mw = float(result[1][2])
            logger.log(logging.DATA, f'initial_slack_mw = {initial_slack_mw:.1f}, initial_load_mw = {initial_load_mw:.1f}', extra = extra)
            
            # Scale Area Load to XX% of area initial value by lowering "AGCable" loads:
            # Calculate desired load level
            new_load = summer_to_spring_pct * initial_load_mw
            
            # Begin scale_area_load_mw(area, new_load, pw_com_object, enforce_agc = False)
            area_num = 1        
            new_load = summer_to_spring_pct * initial_load_mw
            result = scale_area_load_mw(area_num, new_load, pw_com_object, enforce_agc = True)
            if result[0:2] != ['', '']:
                err = f'Error in scale_area_load_mw. Result = {result[0]}'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # Solve twice
            logger.log(logging.INFO, f'Solving Powerflow', extra = extra)
            result = solve_twice(extra, pw_com_object)
            if result[0:2] != ['', '']:
                err = f'Error in solve_twice.'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # Get New slack level and area load level
            result = pw_com_object.GetParametersSingleElement('Area', ['Number', 'SlacIGMW', 'LoadMW'], [1, '', ''])
            if result[0] != '':
                err = f'Error getting area slack initial target. Result = {result[0]}'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
    #            return[err, action]
                pw_com_object.CloseCase()
                s_exit(err)
            current_slack_mw = float(result[1][1])
            current_load_mw = float(result[1][2])
            load_change = current_load_mw - initial_load_mw
            logger.log(logging.DATA, f'current_slack_mw = {current_slack_mw:.1f}, current_load_mw = {current_load_mw:.1f}, load_change = {load_change:.1f}', extra = extra)
            
            # Check deviation from expected load level
            deviation_from_expected = current_load_mw - new_load
            if abs(deviation_from_expected) > .1:
                err = f'Larger than expected deviation from desired load:\nExpected load: {new_load}, Scaled load = {current_load_mw}, Deviation: {deviation_from_expected}'
                action = 'Warning Only'
                logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
            
            # calculate slack error
            slack_error = current_slack_mw - initial_slack_mw
            logger.log(logging.DATA, f'slack_error = {slack_error:.1f}', extra = extra)
        
            # Have Powerworld load an .aux file
            aux_file = f'{cwd}\\Aux_Files\\An_Aux_File.aux'
            logger.log(logging.INFO, f'Loading Aux file: {aux_file}', extra = extra)
            result = pw_com_object.RunScriptCommand(r'LoadAux("'+ aux_file +'" ,YES);')
            if result[0] != '':
                err = f'Error loading aux file. Result = {result[0]}'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
        
            # Adjust injection groups until either min gen or slack is balanced
            balance_inj_grps = ["Inj_Grp_1", "Inj_Grp_2"]
            iteration = 0
            max_iterations = 5
            balance_inj_grp_idx = 0
            lim_txt = ''
            # while max_iteration not exceeded
            while iteration < max_iterations:
                # increment counter
                iteration += 0
                balance_inj_grp = balance_inj_grps[balance_inj_grp_idx]
                
                # reduce (or increase) injection group by slack error (but respect MW limits), and do not go below zero
                result = adjust_inj_grp_mw(balance_inj_grp, slack_error, pw_com_object, limit_min_to_zero = True)
                if result[1] in ['Error', 'Exception']:
                    err = f'Error adjusting {balance_inj_grp}.'
                    action = 'Study Stopped'
                    logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
    #                return [err, action, None, None]
                    pw_com_object.CloseCase()
                    s_exit(err)
                elif result[1] in ['Warning']:
                    if 'max' in result[0]:
                        lim_txt = 'max'
                    elif 'min' in result[0]:
                        lim_txt = 'min'
            
                # Solve twice
                logger.log(logging.INFO, f'Solving Powerflow', extra = extra)
                result = solve_twice(extra, pw_com_object)
                if result[0:2] != ['', '']:
                    err = f'Error in solve_twice.'
                    action = 'Study Stopped'
                    logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                    pw_com_object.CloseCase()
                    return[err, action]
#                    s_exit(err)
                
                # Check current slack level, min gen level
                logger.log(logging.INFO, f'Checking {slack_inj_grp} MW level, Min MW', extra = extra)
                result = pw_com_object.GetParametersSingleElement('InjectionGroup', ['Name','MW', 'GenMWMin'], [slack_inj_grp, 0.0, 0.0])
                if result[0] != '':
                    err = f'Error gathering slack data. Result = {result[0]}'
                    action = 'Study Stopped'
                    logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                    pw_com_object.CloseCase()
                    return[err, action]
#                    s_exit(err)
                
                current_slack_mw = float(result[1][1])
                current_slack_min_mw = float(result[1][1])
                logger.log(logging.DATA, f'current_slack_mw = {current_slack_mw:.1f}, current_slack_min_mw = {current_slack_min_mw:.1f}', extra = extra)
            
                # Calculate slack error
                slack_error = current_slack_mw - initial_slack_mw
                logger.log(logging.DATA, f'slack_error = {slack_error:.1f}, max_slack_deviation = {max_slack_deviation:.1f}', extra = extra)
                if abs(slack_error) <= max_slack_deviation:
                    # If slack is close, exit loop
                    logger.log(logging.DEBUG, f'Exiting slack balance loop on "Slack balanced"', extra = extra)
                    break
                
                # Check current balance_inj_grp level, min gen level
                if lim_txt == 'max' or lim_txt == 'min':
                    if lim_txt == 'max':
                        lim_sgn = -1
                    else:
                        lim_sgn = 1
                    balance_inj_grp_idx += lim_sgn
                    if (balance_inj_grp_idx >= len(balance_inj_grps)) or (balance_inj_grp_idx < 0):
                        # if there are no more balance injection groups, exit loop
                        logger.log(logging.DEBUG, f'Exiting slack balance loop on "All injection groups at {lim_txt} gen"', extra = extra)
                        break
            # End of slack balancing while loop
            else:
                # This will only execute if the while loop exits on iteration overflow
                err = f'Failed to balance slack after {max_iterations} iterations.'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                
                # save current case as "{cwd}\\Starting_Cases\\Error_case_{spring_case}.pwb"
                dir_name = f'{cwd}\\Starting_Cases'
                save_name = f'\\Error_case_{spring_case}'
                logger.log(logging.DEBUG, f'Calling save_pw_case.', extra = extra)
                result = save_pw_case(dir_name, save_name, pw_com_object)
                # flag user to balance the slack manually
                message = f'WARNING:  Case would not balance!\nOpen error case in the "Starting_Cases" folder,\nbalance manually,\n save the case as "{spring_case}",\nthen restart this tool.'
                logger.log(logging.ERROR, starbox_msg(message, 2,2,2) , extra = extra)
                # exit program on "err"
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
                
            if current_slack_mw < current_slack_min_mw:
                err = f'Final Injection Group Slack level below InjGrp MinGen.  current_slack_mw = {current_slack_mw}, current_slack_min_mw = {current_slack_min_mw}'
                action = 'Warning Only'
                logger.log(logging.WARNING, f'{err} \n *********** {action} ***********', extra = extra)
            else:
                logger.log(logging.INFO, f'Final {slack_inj_grp} MW level: {current_slack_mw}', extra = extra)
        
            # save the case as "{cwd}\\Starting_Cases\\{spring_case}.pwb"
            logger.log(logging.DEBUG, f'Calling save_pw_case.', extra = extra)
            dir_name = f'{cwd}\\Starting_Cases'
            save_name = f'\\{spring_case}'
            result = save_pw_case(dir_name, save_name, pw_com_object)
            if result[0] != '':
                err = f'Failed to save spring base case.  Result = result[0]'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
        
        # Debug exit
        if False:
            err = f'Debug exit active.'
            action = 'Study Stopped'
            logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
            pw_com_object.CloseCase()
            return[err, action]
#            s_exit(err)
        
        
        extra = {'qThreadName': f'Run Cases'}
        debug_ctr = 0
        for case, initial_case in list(zip(save_casenames, initial_cases)):
            '''
            ***********************************************************************************************************************************************
            Develop base case from starting case
            ***********************************************************************************************************************************************
            '''
            # Debug break after x runs
            if False:
                logger.log(logging.WARNING, f'Debug break active', extra = extra)
                debug_ctr += 1
                if debug_ctr > 1:
                    break
            
            extra = {'qThreadName': f'Develop base case from starting case'}
            logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
            
            # Create a directory for the study, if it already exists, then use it
            if os.path.exists(f'{case}'):
                logger.log(logging.DEBUG, f'Directory for case files already exists; good.', extra = extra)
            else:
                logger.log(logging.INFO, f'Creating directory in working directory for case files: {case}', extra = extra)
                os.mkdir(f'{case}')
                
            study_dir = cwd + '\\' + case
            study_file = f'{study_dir}\\{case}_Base.pwb'
            
            # Load the Powerworld case file
            logger.log(logging.DATA, f'case = {case}', extra = extra)
            logger.log(logging.INFO, f'Opening: {initial_case}', extra = extra)
            result = pw_com_object.OpenCase(initial_case)
            if result[0] != '':
                err = f'Error loading starting case {initial_case}. result = {result[0]}.'
                action = 'Case Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                continue
#                s_exit(err)
            
            # Create filters
            result = create_filters(filters_data, pw_com_object)
            if result[0:2] != ['', '']:
                err = f'Failed to create one or more advanced filters. Result = {result[2]}'
                action = 'Case Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                continue
#                s_exit(err)
        
            # Some Dummy Powerworld calls
            #  Use a script command to create an area abject within the case
            logger.log(logging.INFO, f'Dummy Powerworld call #1.', extra = extra)
            result = pw_com_object.RunScriptCommand(r'CreateData(Area, [Number, Name], ["02", "Another Area"]);')
            if result[0] != '':
                err = f'Error creating area 02. result = {result[0]}.'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                continue
#                s_exit(err)
        
            # Use "GetParametersMultipleElement" to get some "Branch" object data from the case
            logger.log(logging.INFO, f'Dummy Powerworld call #2.', extra = extra)
            TerminalBus_ParamList = ["BusNumFrom", "BusNumTo"]
            result = pw_com_object.GetParametersMultipleElement('Branch', TerminalBus_ParamList, f'{G_prefix}_Branches_filter_1')
            if result[0] != '':
                err = f'Error gathering bus data for elements in "Branches_filter_1". result = {result[0]}.'
                action = 'Case Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                continue
            Terminal_Bus = result[1]
            
            # Create Bus_List from contents of Terminal_Bus
            Bus_List = [bus for buses in Terminal_Bus for bus in buses]
            
    #        Bus_List = []
    #        for x in range(len(Terminal_Bus[0])):
    #            Bus_List.append(Terminal_Bus[0][x])
    #            Bus_List.append(Terminal_Bus[1][x])
                
            logger.log(logging.DATA, f'len(Bus_List) = {len(Bus_List)}', extra = extra)
            Bus_List = list(set(Bus_List)) # remove duplicates in Bus_list
            logger.log(logging.DATA, f'len(Bus_List) = {len(Bus_List)}', extra = extra)
            
            # Move all buses in Bus_List to area 02 in case
            logger.log(logging.INFO, f'Adding buses to area 02.', extra = extra)
            Bus_List = [[__e,'02'] for __e in Bus_List]
            WriteBusAreaNum_ParamList = ["Number", "AreaNumber"]
            result = pw_com_object.ChangeParametersMultipleElementRect("Bus", WriteBusAreaNum_ParamList, Bus_List)
            if result[0] != '':
                err = f'Error moving buses to area 02. result = {result[0]}.'
                action = 'Study Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # make Area Gen injection groups for Area 01 and 02
            # Another example of calling a script command
            #  I sometimes create loops like this when running a similar algorithm
            area_data = [1, "{G_prefix}_Area_01_Gens"],[2, "{G_prefix}_Area_02_Gens"]
            for area_num, inj_grp_name in area_data:
                logger.log(logging.INFO, f'Making area {area_num} gen injection group', extra = extra)
                script_str = f'InjectionGroupCreate("{inj_grp_name}", GEN, MAX GEN MW, <DEVICE> Area "{area_num}",NO);'
                result = pw_com_object.RunScriptCommand(script_str)
                if result[0] != '':
                    err = f'Error creating Gen Inj Grp for Area {area_num}. Result = {result[0]}.'
                    action = 'Case Stopped'
                    logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                    pw_com_object.CloseCase()
                    return[err, action]
#                    s_exit(err)
            
            # Save case as base in study directory
            # DEBUG: Consider using save_case function
            # I sometimes use a "DEBUG:" comment when there is something to improve or fix.
            study_file = f'{study_dir}\\{case}_Base.pwb'
            logger.log(logging.INFO, f'Saving case to {study_file}', extra = extra)
            result = pw_com_object.RunScriptCommand('SaveCase("' + study_file + '");')
            if result[0] != '':
                err = f'Error saving base case: {study_file}.  Result = {result[0]}.'
                action = 'Case Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # Debug save case
            if False:
                logger.log(logging.DEBUG, f'Saving pre ACE correction case.', extra = extra)
                dir_name = f'{cwd}\\Error_Cases'
                save_name = f'\\pre_ACE_correction_case_{case}_Base.pwb'
                logger.log(logging.DEBUG, f'Calling save_pw_case.', extra = extra)
                result = save_pw_case(dir_name, save_name, pw_com_object)
                                    
            logger.log(logging.INFO, f'Performing "Clear transaction table and auto-insert tieline transactions".', extra = extra)
            result = pw_com_object.RunScriptCommand('AutoInsertTieLineTransactions;')
            if result[0] != '':
                err = f'Error resetting area transactions. Result = {result[0]}.'
                action = 'Case Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # Debug save case
            if False:
                logger.log(logging.DEBUG, f'Saving post ACE correction case.', extra = extra)
                dir_name = f'{cwd}\\Error_Cases'
                save_name = f'\\post_ACE_correction_case_{case}_Base.pwb'
                logger.log(logging.DEBUG, f'Calling save_pw_case.', extra = extra)
                result = save_pw_case(dir_name, save_name, pw_com_object)
            
            # Debug exit
            if False:
                err = f'Debug exit active.'
                action = 'Case Stopped'
                logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # Powerworld can make a copy of its current state in case something goes wrong
            # Set a reference case
            logger.log(logging.DEBUG, f'Saving reference state.', extra = extra)
            result = pw_com_object.SaveState()
            if result[0] != '':
                err = f'Cannot save reference state. error = {result[0]}'
                action = f'Warning only'
                logger.log(logging.CRITICAL, f'{err}\n{" "*21}*********** {action} ***********', extra = extra)
            
            # Solve case twice
            # This is typically where things go wrong
            logger.log(logging.INFO, f'Solving Powerflow', extra = extra)
            result = solve_twice(extra, pw_com_object)
            if result[0:2] != ['', '']:
                err = f'Error in solve_twice.'
                action = 'Case Skipped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                # Restore reference case
                logger.log(logging.DEBUG, f'Restoring reference state.', extra = extra)
                result = pw_com_object.LoadState()
                if result[0] != '':
                    err = f'Cannot restore saved case state. error = {result[0]}'
                    action = f'Case Stopped'
                    logger.log(logging.CRITICAL, f'{err}\n{" "*21}*********** {action} ***********', extra = extra)
                else:
                    # Save an error case
                    dir_name = f'{cwd}\\Error_Cases'
                    save_name = f'\\Error_case_{case}_Base.pwb'
                    logger.log(logging.DEBUG, f'Calling save_pw_case.', extra = extra)
                    result = save_pw_case(dir_name, save_name, pw_com_object)
                continue
            
            '''
            #save case as base in study directory
            study_file = f'{study_dir}\\{case}_Base.pwb'
            '''
            logger.log(logging.INFO, f'Saving case to ' + study_file, extra = extra)
            result = pw_com_object.RunScriptCommand('SaveCase("' + study_file + '");')
            if result[0] != '':
                err = f'Error saving base case: {study_file}. Result = {result[0]}.'
                action = 'Case Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            
            # Gather Area Load MW for areas 01 and 02 in a single call to GetParametersMultipleElementRect
            AreaLoad_ParamList = ['Number', 'LoadMW']
            result = pw_com_object.GetParametersMultipleElementRect('Area', AreaLoad_ParamList, f'{G_prefix}_Area_01_or_02')
            if result[0] != '':
                logger.log(logging.ERROR, f'Error gathering Area load.  Skipping study')
                err = f'Error gathering Area 01 load.  Result = {result[0]}.'
                action = 'Case Stopped'
                logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            Area_loads = result[1]
            Area_01_load = [float(__e[1]) for __e in Area_loads if '01' in __e[0]][0]
            Area_02_load = [float(__e[1]) for __e in Area_loads if '02' in __e[0]][0]
            logger.log(logging.DATA, f'Area_01_load = {Area_01_load:.1f}, Area_02_load = {Area_02_load:.1f}', extra = extra)
            
            logger.log(logging.INFO, f'Close Powerworld case', extra = extra)
            pw_com_object.CloseCase()
            
            # Debug exit
            # Sometimes I want to break or continue.                    
            if False:
                if False:
                    # Debug Continue
                    err = f'Debug continue active.'
                    action = 'Case Stopped'
                    logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                    continue
                if False:
                    # Debug Break
                    err = f'Debug break active.'
                    action = 'Case Loop Stopped'
                    logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                    break
                err = f'Debug exit active.'
                action = 'Study Stopped'
                logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
    #            return [err, action, None, None]
                pw_com_object.CloseCase()
                s_exit(err)
            
            '''
            ***********************************************************************************************************************************************
            Prepare results directory and excel file
            ***********************************************************************************************************************************************
            '''
            extra = {'qThreadName': f'Prepare results directory and excel file'}
            logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
            
            # Create a directory for the study, if it already exists, then use it
            if os.path.exists(f'{Study_Results_dir}'):
                logger.log(logging.DEBUG, f'Directory for results files already exists; good.', extra = extra)
            else:
                logger.log(logging.INFO, f'Creating directory in working directory for results files: {Study_Results_dir}', extra = extra)
                os.mkdir(f'{Study_Results_dir}')
            
            # Set the file name for the current Study results excel file
            Study_Results = f'{Study_Results_dir}{case}_Study_Results.xlsx'
            logger.log(logging.DATA, f'Study_Results = {Study_Results}', extra = extra)
            # look for an existing excel file.  If it exists open it, otherwise create it
            if os.path.isfile(Study_Results):
                #open it
                wb = xw.Book(Study_Results)
                logger.log(logging.DEBUG, f'opened', extra = extra)
            else:
                # create a new workbook, delete the extra sheet, and rename the first sheet to the current study, then save it
                wb = xw.Book()
                wb.sheets[0].name = 'Curve'
                wb.save(Study_Results)
                logger.log(logging.DEBUG, f'Results worksheet created.', extra = extra)
            wb.activate()
            
            # Debug exit
            if False:
                if False:
                    # Debug Continue
                    err = f'Debug continue active.'
                    action = 'Case Stopped'
                    logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                    continue
                if False:
                    # Debug Break
                    err = f'Debug break active.'
                    action = 'Case Stopped'
                    logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                    break
                err = f'Debug exit active.'
                action = 'Study Stopped'
                logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                pw_com_object.CloseCase()
                return[err, action]
#                s_exit(err)
            #load each load level including base case level
            
            '''
            ***********************************************************************************************************************************************
            Scale base case and solve powerflow
            ***********************************************************************************************************************************************
            '''
            for load_level, case_load_name in case_inputs:
                extra = {'qThreadName': f'Scale base case and solve powerflow.  Case: "{case_load_name}"'}
                logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
                        
                #Load the Powerworld case file
                logger.log(logging.INFO, f'Opening: {study_file}', extra = extra)
                result = pw_com_object.OpenCase(study_file)    #open case
                if result[0] != '':
                    err = f'Error loading case. {study_file}. result = {result[0]}.'
                    action = 'Case Stopped'
                    logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                    pw_com_object.CloseCase()
                    return[err, action]
#                    s_exit(err)
                
                result = create_filters(filters_data, pw_com_object)
                if result[0:2] != ['', '']:
                    err = f'Failed to create one or more advanced filters. Result = {result[2]}'
                    action = 'Case Stopped'
                    logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                    pw_com_object.CloseCase()
                    return[err, action]
#                    s_exit(err)
                
                #scale load in areas
                areas_data = [[1, Area_01_load], [2, Area_02_load]]
                for area_num, area_load in areas_data:
                    
                    # Calculate new Area Load MW
                    new_load = area_load + load_level
                    
                    # Call scale_area_load_mw
                    logger.log(logging.INFO, f'Scaling Area {area_num} load from {area_load:.1f} to {new_load:.1f}', extra = extra)
                    result = scale_area_load_mw(area_num, new_load, pw_com_object, enforce_agc = True)
                    if result[0:2] != ['', '']:
                        err = f'Error in scale_area_load_mw. Result = {result[0]}'
                        action = 'Study Stopped'
                        logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                        pw_com_object.CloseCase()
                        return[err, action]
#                        s_exit(err)
                
                    logger.log(logging.INFO, f'Solving Powerflow', extra = extra)
                    result = solve_twice(extra, pw_com_object)
                    if result[0:2] != ['', '']:
                        err = f'Error in solve_twice.'
                        action = 'Case Stopped'
                        logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                        pw_com_object.CloseCase()
                        return[err, action]
#                        s_exit(err)
                
                if (saved_scaled_cases == True):
                    result = pw_com_object.RunScriptCommand(r'SaveCase("' + study_dir + '\\' + case + case_load_name + '.pwb", PWB);')
                if result[0] != '':
                    logger.log(logging.ERROR, f'Error saving scaled case: ' + study_dir + '\\' + case + case_load_name + '.pwb')
                
                '''
                ***********************************************************************************************************************************************
                Post Data for scaled case
                ***********************************************************************************************************************************************
                '''
                extra = {'qThreadName': 'Post Data for scaled case'}
                logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
                
                #set Excel header names for Full AC ATC results
                Shunt_xl_hdr = ["Number of Bus", "Name of Bus", "ID", "Reg Bus Num", "Reg Bus Name", "Status", "Control Mode", "Regulates", "Nominal Mvar", "Actual Mvar", "Owner Number  1"]
                Branch_xl_hdr = ["From Number", "From Name", "From Area Name", "From Nom kV", "To Number", "To Name", "To Nom kV", "Circuit", "Status", "Xfrmr", "MW From", "MW To", "MW Loss", "Owner Name  1", "Owner Number  1", "Value", "Final Losses"]
                AreaTieLine_xl_hdr = ["Tie Type", "Near Area Name", "Near Number", "Near Name", "Far Area Name", "Far Number", "Far Name", "Ckt", "Meter MW", "Imports", "Exports"]
                Areas_xl_hdr = ["Area Num", "Area Name", "AGC Status", "Inj Grp Slack Name", "Gen MW", "Load MW", "Shunt MW", "Tot Sched MW","Int MW","ACE MW","Lambda","Loss MW"]
                    
                Shunt_ParamList = ["BusNum", "BusName", "ID", "RegBusNum", "RegName", "Status", "ShuntMode", "RegulationType", "MvarNom", "Mvar", "OwnerNum1"]
                Branch_ParamList = ["BusNumFrom", "BusNameFrom", "AreaNameFrom", "NomkVFrom", "BusNumTo", "BusNameTo", "NomkVTo", "Circuit", "Status", "IsXF", "MWFrom", "MWTo", "LossMW", "OwnerName1", "OwnerNum1"]
                AreaTieLine_ParamList = ["TieType", "AreaNameNear", "BusNumNear", "BusNameNear", "AreaNameFar", "BusNumFar", "BusNameFar", "Circuit", "MWMeter"]
                Areas_ParamList = ["Number","Name", "AGC", "SlackInjectionGroup", "GenMW", "LoadMW", "ShuntMW", "ExportMWSched", "ExportMW", "ACE", "EconDispLambda", "LossMW"]
                
                obj_calcs_dict = {
                        'Shunt': [],
                        'Branch': ['=Censored Excel Calculation String',
                                   '=P{row}*M{row}'],
                        'AreaTieLine': ['=Censored Excel Calculation String', 
                                        '=Censored Excel Calculation String'],
                        'Area': []
                        }
                
                
                pw_call_data = [['Shunt', Shunt_ParamList, f'{G_prefix}_Shunts_Reactors_Active_Area_02', '_Reactors', Shunt_xl_hdr, [['I:J', '0']]], 
                                ['Branch', Branch_ParamList, f'{G_prefix}_Branches_Owners_List', '_Losses', Branch_xl_hdr, [['K:L', '0'], ['M:M', '0.00'], ['Q:Q', '0.00']]], 
                                ['AreaTieLine', AreaTieLine_ParamList, f'{G_prefix}_Tielines_Area_02', '_AreaTieLine', AreaTieLine_xl_hdr, [['I:K', '0']]], 
                                ['Area', Areas_ParamList, f'{G_prefix}_Area_02', '_Area', Areas_xl_hdr, [['E:J', '0'], ['L:L', '0']]]]
                
                # Get/post object data loop
                for obj, params, pw_filt, sht_txt, xl_hdr, fmt_lst in pw_call_data:
                    # Gather the object data
                    logger.log(logging.INFO, f'Gathering {obj.lower()} data.', extra = extra)
                    result = pw_com_object.GetParametersMultipleElementRect(obj, params, pw_filt)
                    if result[0] != '':
                        err = f'Error reading {obj.lower()} data. {initial_case}. result = {result[0]}.'
                        action = 'Case Stopped'
                        logger.log(logging.ERROR, f'{err} \n *********** {action} ***********', extra = extra)
                        pw_com_object.CloseCase()
                        continue
                    # translate result[1] from tuple of tuples into list of lists
                    obj_data = [[__e for __e in __f] for __f in result[1]]
                    
                    if obj_calcs_dict[obj] != []:
                        # Create Excel calculation strings for each data element
                        calc_rows = []
                        for row in range(len(obj_data)):
                            calc_row = []
                            for calc in obj_calcs_dict[obj]:
                                calc_row += [calc.replace('{row}', f'{row + 3}')]
                            calc_rows += [calc_row]
                    
                        # Add required calcs for each data element
                        obj_data = [__e + calc_rows[__i] for __i, __e in enumerate(obj_data)]
                    
                    # Develop tab name
                    tab_name = f'{case}{case_load_name}{sht_txt}'[0:31]
                    
                    # Post data table to Excel
                    result2 = Post2Excel(tab_name, sht_txt, xl_hdr, obj_data, fmt_lst, wb)
                    if result2[0:2] != ['', '']:
                        err = result[0]
                        pw_com_object.CloseCase()
                        return[err, action]
#                        s_exit(err)
    #            wb.save()
                # Debug exit
                if False:
                    if False:
                        # Debug Continue
                        err = f'Debug continue active.'
                        action = 'Case Stopped'
                        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                        continue
                    if False:
                        # Debug Break
                        err = f'Debug break active.'
                        action = 'Case Stopped'
                        logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                        break
                    err = f'Debug exit active.'
                    action = 'Study Stopped'
                    logger.log(logging.CRITICAL, f'{err} \n *********** {action} ***********', extra = extra)
                    pw_com_object.CloseCase()
                    return[err, action]
#                    s_exit(err)
            
            '''
            ***********************************************************************************************************************************************
            Prepare HS-Curve worksheet
            ***********************************************************************************************************************************************
            '''
            extra = {'qThreadName': 'Prepare HS-Curve worksheet.'}
            logger.log(logging.INFO, f'\n\n{" "*0}********* {extra["qThreadName"]} ************', extra = extra)
            
            #find or create the HS-Curve worksheet
            if 'Curve' in [xw.sheets[i].name for i in wb.sheets]:
                sht = xw.sheets[[i.name for i in wb.sheets].index('Curve')]  #sets the active sheet to tab_name if the sheet name exists
                logger.log(logging.INFO, f'Found Curve Sheet', extra = extra)
            else:
                sht = wb.sheets.add('Curve') #adds a sheet named tab_name if the sheet does not already exist
                logger.log(logging.INFO, f'Added Curve Sheet', extra = extra)
            
            #move Curve sheet to first sheet in workbook
            sht.api.Move(Before = xw.sheets[0].api)
            
            # fill Curve formulas
            debug_ctr = 0
            sht.range(1, 1).value = ['','stuff','Losses','','%']
            for idx, case_load_name in enumerate(case_load_names):
                
                sht.range(12-idx, 1).value = [case_load_name,
                                                   "=Censored calcs",
                                                   "=Censored calcs",
                                                   '',
                                                   f'=C{12-idx}/B{12-idx}']
        
            sht.range(14, 1).value = ['','','','Average','=AVERAGE(E2:E11)']
            sht.range('B:D').number_format = '0.00'
            sht.range('E:E').number_format = '0.00%'
            sht.range('A:A').api.ColumnWidth = 16.0
            sht.range('B:E').api.ColumnWidth = 9.0
            
            #save the workbook for this study
            wb.save()
        '''
        #wb.close()
        wb.app.quit
        '''
        
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
        pw_com_object.CloseCase()
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
    worker1_data_dict = {
                        'working_directory' : './', # Where the function will save data and look for additional files
                        'summer_case' : '26HS.pwb', # Can be a path to anywhere, but 'working_directory\Starting_Cases\' is the assumed starting path
                        'winter_case' : '26HW.pwb', # Can be a path to anywhere, but 'working_directory\Starting_Cases\' is the assumed starting path
                        'spring_case' : '26LSP.pwb', # Can be a path to anywhere, but 'working_directory\Starting_Cases\' is the assumed starting path
                        'save_casenames' : ['26HS_LF', '26HW_LF', '26LSP_LF'], # folder names and saved case names
                        'summer_to_spring_pct' : 64.0, # Summer load will be scaled by this amount to create the spring case, if it does not already exist
                        'case_load_levels' : [500, 400, 300, 200, 100, 0, -100, -200, -300, -400, -500], # MW deviations from the base case used in the study
                        'max_slack_deviation' : 5, # Allowed slack deviation when balancing load changes during spring case creation
                        'quit_excel' : False, # When true, closes Excel when study is finished
                        'saved_scaled_cases' : True, # When true, saves all of the load deviation cases used in the study
                        'gui_active' : True, # True when the function is called from a GUI (enables progress reporting emits)
                        'use_multi_proc' : False, # When true, and the option is programmed, the function will use a multiprocessing pool to complete studies faster
                        'debug_options' : [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],  # Debug option flags potentially used in the case.
                        'logger' : logger
                        }
    
    python_dir = os.getcwd()
    result = get_preload_dict(f'{python_dir}/Preloads_Template.txt')
    if result[0:2] != ['', '']:
        return None
    preload_dict = result[2]
    
    for key in preload_dict.keys():
        if key in worker1_data_dict.keys():
            worker1_data_dict[key] = preload_dict[key]
    
    if is_number(preload_dict.get('summer_to_spring_pct', '64.0')):
        worker1_data_dict['summer_to_spring_pct'] = float(preload_dict['summer_to_spring_pct'])
    else:
        worker1_data_dict['summer_to_spring_pct'] = 64.0
            
    if 'true' in preload_dict.get('saved_scaled_cases', 'False').lower():
        worker1_data_dict['saved_scaled_cases'] = True
    else:
        worker1_data_dict['saved_scaled_cases'] = False
    
    # Call the worker function
    worker1_function(worker1_data_dict)
    
    return None

from inspect import currentframe as cf #, getframeinfo as gfi # Used to identify the current function -- avoids some copy-paste issues when making new defs
if __name__ == '__main__':      
    
    # creating a dummy variable ("m") to accept the 
    # object returned from "main" will prevent problems
    # with the kernal dying while running under Spyder.
    m = main()