


3.1	lib_logger	
This library provides a set of tools to log messages to the standard output.
It allows six (6) logging levels: debug, info, warning, error, critical, and fatal.
The main module starts the logging mechanism.  Every module, including the main module, must initialize the logging by providing their “__name__”.

3.1.1	API Description:

3.1.1.1	logger_init
lib_logger.logger_init(
log_id=’log_’, 
log_file_level=’info’, 
log_file=’’,
log_file_append=True
)

This API initializes the logging mechanism by mainly providing the logging name prefix (log_id).
If log messages are also to be written to file then at a minimum the log file name (log_file) argument must be provided.
Arguments:
log_id	Prefix added to a module name as an logging identifier (default: log_)
log_file_level	Minimum level at which log messages get written into the log file
log_file	Name of the log file. By default, log messages are not written to file.
log_file_append	By default (True), if the file exists it will be appended. If False, a new file will be created.  If False, a new log file will be created.


3.1.1.2	logger_init_level
lib_logger.logger_init_level(
log_level_dict, 
level=’warning’ 
)

This API sets the default standard output logging level by and provides a dictionary of module ids (log_xxx) with potential non-default level.

Arguments:
Log_level_dict	dictionary of module ids with potential non-default level, i.e.: log_module_name=info
level		Default level: warning. Logging level at which log messages get displayed to the standard output


3.1.1.3	log_module_init
lib_logger.log_module_init (
module_name, 
multiprocess_flag=False 
)

This API overwrites the default standard output logging level for the particular module.

Arguments:
module_name	Name of the module (file name less extension)
multiprocess_flag	Default: False.  Require if module has multi-processing portion.  

3.1.2	Sample code
3.1.2.1	Main Module
import lib_logger
import module1
import module2
import module3

# Init logging.  MUST be called once only
# Logging module name: log_moduleID
#    i.e.: module.py ==> logging name: log_module

lib_logger.logger_init(log_id='log_', log_file_level='info', log_file_append=False)

#####################################################################

# Module Log Levels
test_dict[‘log_module_1’] = ‘info’
test_dict[‘log_module_2’] = ‘warning’
test_dict[‘log_module_3’] = ‘warning’

# Init module logging levels.  MUST be called once only
lib_logger.logger_init_level(test_dict)

#####################################################################

# Init module logging levels.  MUST be called once only
# Default level is "warning"
lib_logger.logger_init_level(test_dict)

#####################################################################
# Start logging for the main module

import os
main_name = os.path.splitext(os.path.basename(__file__))[0]
logger = lib_logger.log_module_init(main_name)
logger.info('starting main_module')

#####################################################################

if __name__ == '__main__':

task_dict = {
    #  ID           	function         	test_dict: dictionary of various test features)
    'task_A010': [module1.task_function_1,    [test_dict]],   # task_A010
    'task_A020': [module2.task_function_2,    [test_dict]],   # task_A020
    'task_A030': [module3.task_function_3,    [test_dict]],   # task_A030
}

3.1.2.2	Additional Module
# Module: module1

import lib_logger
logger = lib_logger.log_module_init(__name__)

def task_function_1(. . .):
. . .
