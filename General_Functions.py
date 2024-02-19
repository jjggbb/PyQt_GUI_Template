# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 13:09:53 2024

@author: JGB1290
"""

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