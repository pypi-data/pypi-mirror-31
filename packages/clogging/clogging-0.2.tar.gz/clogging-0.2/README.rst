#############
clogging
#############

clogging - Configurable Logging Boilerplate for the Autologging Module. 

About
************

Autologging (https://github.com/mzipay/Autologging) is awesome and is now my
go-to for automatic logging in Python; however, it's not completely boilerplate
free. This module, clogging, addresses tasks that I would otherwise need to
address per application I incorperate autologging into.

It features:

* Completely sets up a complex root Logger instance with one call
* Logging is configurable through a YAML configuration file or function
  with keyword arguments 
* Surpressed columns for higher level logging with more detailed output
  for lower logging levels
* Quick incorperation (one line) into projects for basic usage
* Writing log output to file with log rotation

A demo "Hello World" application using clogging/autologging is available here,
    https://github.com/RyanMillerC/DemoCloggingApp

*Technically clogging could be used to configure the standard Python
logging module, since this doesn't directly interact with autologging,
but it was specifically created to fill in gaps and save me time
building applications that use autologging.*

Installation
************
 
::

  pip install clogging


Documentation
*************

Import this module with:
::

  import clogging

These are the two functions which will start logging.

start_from_yaml
~~~~~~~~~~~~~~~

Usage:
::

  log = clogging.start_from_yaml('path/to/file.yaml')

Start logging based on entries in a YAML configuration file. This is
designed to work with an existing application settings.yaml file, but
does not have to have anything additional for your application inside
it. All clogging entries should be nested under 'clogging' at the root
of the YAML file. If this is unclear, look at the example provided under
conf/settings.yaml. This function returns a root Logger instance.

Your YAML file, at it's root level, should be structured like,
::

  clogging:
    file: log/test.log
    level: WARNING
    max_file_size: 5000
    max_retention: 5
    ...
  app:
    ...
  ...

All settings are optional. If you erase one or more of the settings in
the YAML file, default settings will be used. For a list of available
option, see the Options section below. start_from_yaml does require that
you have at least a "clogging" section in your YAML file. To use clogging
without a YAML file, use start_from_args.

start_from_args
~~~~~~~~~~~~~~~

Usage:
::

  log = clogging.start_from_args()


Start logging based on keyword arguments. This function will accept the
same options as start_from_yaml, but passed in to the function as
keyword arguments. This function returns a root Logger instance.

This example is the easiest way to add clogging into a project and start
INFO level logging to the console,
::

  log = clogging.start_from_args(level='INFO')

Or, example to start DEBUG level logging with file output,
::

  log = clogging.start_from_args(
          file='logs/app.log',
          level='INFO'
  )


Options
~~~~~~~

The following are available options and their descriptions. If any of
these options are not supplied, the default value will be used. These
option names can be set in either YAML format or as arguments to
start_from_args.

:file:
  Path to log file. If max_retention is set > 0, then rolled logs will
  be saved as log.1, log.2, ...etc., up to the value of max_retention.

  Default: None

:format:
  Logging format for all non-verbose levels. By default non-verbose is
  considered to be INFO and higher.

  Default: '%(asctime)22s:%(levelname)8s:%(name)20s:%(message)s'

:format_ext:
  Logging format for all verbose levels. By default this is considered
  DEBUG and TRACE levels. Additional levels can be added to
  verbose_levels
  
  Default: '%(asctime)22s:%(levelname)8s:%(name)20s:%(funcName)20s:%(message)s' 

:level:
  Logging level.

  Default: 'INFO'

:max_file_size:
  Maximum log file size in bytes before rollover. Setting to 0 will
  cause the log file to grow forever with no rollover. This option has
  no impact if file is set to None.

  Default: 5000

:max_retention:
  Maximum number of rolled over logs to keep. Logs will be saved as
  log.1, log.2, ...etc., until max_retention is reached. At that point
  the oldest of the rollover logs will be cleared. This option has no
  impact if file is set to None.

  Default: 5

:verbose_levels:
  Logging levels in this list are considered verbose levels and will use
  format_ext for formatting. This is typically done to follow low
  level logs which show funcName alongside name.
  
  Default: ['TRACE', 'DEBUG']

Author
************
* Ryan Miller - ryan@devopsmachine.com
