# PyQt_GUI_Template
A PyQT template I use for my power system studies.  Includes the GUI, two "worker" functions, logging setup, and a log window.
I made this repository mostly to seek feedback to improve my coding.

I make projects to automate my transmission studies for productivity. I use a GUI template for convenience.  I have not figured 
out how to combine my PyQt GUI with multiprocessing.  For some studies, multiprocessing is important to shorten the completion
time.  Using multiprocessing can shorten some studies from 2 weeks to 3 days.

In the project, if a worker function is launched from the GUI, multiprocessing is automatically disabled.  Logging is directed
to the "log_text" text window.

If a worker function is launched from the "Multiprocess_Function" file, no GUI is initialized and the worker can have multiprocessing
enabled.

I use "Powerworld" to run powerflow studies, which can be controlled by Python.  A Powerworld "case" can be thought of as a large database
object that can be opened and manipulated by either Powerworld's GUI or by python calls.  In the project,  "Template_Function" shows
some typical calls to Powerworld to manipulate a case.  Powerworld calls always return a tuple in the form of:
('error message', ('return data string 1', 'return data string 2', ... , 'return data string n'))

Any error returned from Powerworld needs to be handled; more frequently than not, this means recording the error and ending the case.
Since I create a lot of bugs while I program, I use a lot of logging.  I generally only use Exceptions to identify when I have
a bug in my script.  I use Errors to identify problems in input data or a failed Powerworld call.  Other priorities are used
for helping me figure out where something went wrong in a case.

In the Template example, "Template_Function" contains worker1, which is an example of the kinds of manipulations made to a case in order to
get some simulation result. It will throw an error if you try to run it.

"Template_Multiprocessing_Function" contains worker2, which is a CPU-heavy calculation that takes about 10 seconds.  It returns how 
long the calculation took to execute.  It can be run with or without multiprocessing enabled.
