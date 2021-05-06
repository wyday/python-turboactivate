# Change Log

All notable changes to this project are documented in this file.

## 4.4.4 - 2021-05-xx

* Remove unused "sandbox" flag and error code. Sandboxes are VMs.
* Add the ta.get_version() function to get the version of the TurboActivate library currently loaded.

## 4.0.3 - 2019-04-17

* Fix Github issue #10 (AttributeError: 'bytes' object has no attribute 'encode'). Thanks @cbenhagen
* Fix pip install failing, github issue #9
* Remove old deprecated file from previous maintainer (not used).


## 4.0.2 - 2018-09-11

* Works with latest version of TurboActivate (4.0.x) and newer.
* Add support for Python 3.x+.
* Completely re-vamp the example app to be more "copy-paste" ready for existing Python apps.
* Handle an incorrect VersionGUID immediately in the TurboActivate constructor.
* Remove redundant "GenuineOptions" class (nearly identical structure to GENUINE_OPTIONS).
* `turboactivate.is_genuine` is split into 2 separate functions (for good reason --
  they should be used in completely separate contexts)
* `is_genuine` and `is_genuine_ex` now return an IsGenuineResult instead of raising exceptions.
* Remove useless helper function, and put it in the TurboActivate constructor.
* Make the Python TurboActivate class match other object-oriented examples.
* Remove unused imports in the example and in the TurboActivate class.
* Change the default for `ta.deactivate()` to *not* delete the product key.
* Split `ta.activate()` in 2 separate functions (online and offline activation).
* Add ability to pass [extra data](https://wyday.com/limelm/help/extra-data/) to `ta.activate()` and `ta.use_trial`
* Modify `ta.is_activated()` to raise errors when it needs to.
* Modify `ta.is_date_valid()` to require a passed in date/time value.
* Fix Linux support in Python 3.3+ (no longer uses the "linux2" identifier --
  now uses "linux"). Also, add support for BSD, etc. and remove old cruft.
* Make a first class language integration with LimeLM (meaning supported with
  the help of wyDay).
* Changed the version scheme to match that of the TurboActivate API (it will now match, or slightly trail the TurboActivate API).
* Add new error codes and remove unused error codes.
* Load the native library files and TurboActivate.dat file from the location of the executing python script (or compiled executable) rather than the current working directory (CWD).


## 4.0.0 / 4.0.1 - 2018-01-31

* Changes from Develer (some of which are in our 4.x branch). Unfortunately our 4.x branch has breaking changes from their 4.x branch.


## 1.0.4 - 2016-01-27

### Changed

* Let `TurboActivateConnectionDelayedError` and `TurboActivateConnectionError` bubble up. (Thanks
  to @cbenhagen).


## 1.0.3 - 2014-11-04

### Changed

* `TurboActivate.activate()` throws an exception if activation fails


## 1.0.2 - 2014-11-03

### Changed

* Calling `SetCustomActDataPath` under Linux will raise a runtime exception since the method is not
  available on that platform.


## 1.0.1 - 2014-09-29

### Added

* `TurboActivate.is_date_valid()` now accepts an optional `date` parameter, which must be a
  string.


### Fixed

* We use the correct buffer allocation scheme when using `GetFeatureValue`.'
* Solved a packaging problem (README.rst was not included in the distribution).


## 1.0.0 - 2014-08-12

First public version
