# -*- coding: utf-8 -*-
#
# Copyright 2013, 2014 Develer S.r.l. (https://www.develer.com/)
# Copyright 2018 wyDay, LLC (https://wyday.com/)
#
# Current Author / maintainer:
#
#   Author: wyDay, LLC <support@wyday.com>
#
#
# Previous authors (and based on their fantastic work):
#
#   Author: Lorenzo Villani <lvillani@develer.com>
#   Author: Riccardo Ferrazzo <rferrazz@develer.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from ctypes import pointer, sizeof, c_uint32, c_void_p

from turboactivate.c_wrapper import *

import os
import sys

#
# Object oriented interface
#

class IsGenuineResult:
    Genuine, GenuineFeaturesChanged, NotGenuine, NotGenuineInVM, InternetError = range(5)


class TurboActivate(object):

    def __init__(self, guid, flags = TA_USER, dat_file_loc = "", library_folder = ""):

        # load the executing file's location
        if getattr(sys, 'frozen', False):
            # running in a bundle
            execFileLoc = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # running live
            execFileLoc = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))

        if not library_folder:
            library_folder = execFileLoc

        # form the full, absolute path to the TurboActivate.dat file
        if not dat_file_loc:
            dat_file_loc = os.path.join(execFileLoc, "TurboActivate.dat")

        self._lib = load_library(library_folder)
        self._set_restype()

        self._flags = flags

        try:
            self._lib.TA_PDetsFromPath(wstr(dat_file_loc))
        except TurboActivateFailError:
            # The dat file is already loaded
            pass

        self._handle = self._lib.TA_GetHandle(wstr(guid))

        # if the handle is still unset then immediately throw an exception
        # telling the user that they need to actually load the correct
        # TurboActivate.dat and/or use the correct GUID for the TurboActivate.dat
        if self._handle == 0:
            raise TurboActivateDatFileError()

    #
    # Public
    #

    # Product key

    def check_and_save_pkey(self, product_key):
        """Checks and saves the product key."""
        ret = self._lib.TA_CheckAndSavePKey(self._handle, wstr(product_key), self._flags)

        if ret == TA_OK:
            return True
        elif ret == TA_FAIL:
            return False

        validate_result(ret)

    def is_product_key_valid(self):
        """
        Checks if the product key installed for this product is valid. This does NOT check if
        the product key is activated or genuine. Use is_activated() and is_genuine_ex() instead.
        """
        try:
            self._lib.TA_IsProductKeyValid(self._handle)

            return True
        except TurboActivateError:
            return False

    def get_pkey(self):
        """
        Gets the stored product key. NOTE: if you want to check if a product key is valid
        simply call is_product_key_valid().
        """
        buf_size = 35
        buf = wbuf(buf_size)

        try:
            self._lib.TA_GetPKey(self._handle, buf, buf_size)

            return buf.value
        except TurboActivateProductKeyError:
            return None


    # Activation status

    def deactivate(self, erase_p_key=False):
        """
        Deactivates the product on this computer. Set erasePkey to 1 to erase the stored
        product key, 0 to keep the product key around. If you're using deactivate to let
        a user move between computers it's almost always best to *not* erase the product
        key. This way you can just use TA_Activate() when the user wants to reactivate
        instead of forcing the user to re-enter their product key over-and-over again.
        """

        args = 1 if erase_p_key else 0

        self._lib.TA_Deactivate(self._handle, args)

    def deactivation_request_to_file(self, filename, erase_p_key=False):
        """
        Get the "deactivation request" file for offline deactivation. Set erase_p_key to
        True to erase the stored product key, False to keep the product key around. If
        you're using deactivate to let a user move between computers it's almost always
        best to *not* erase the product key. This way you can just use
        activation_request_to_file() when the user wants to reactivate instead of forcing
        the user to re-enter their product key over-and-over again.
        """

        args = [wstr(filename)]

        if erase_p_key is True:
            args.append(1)
        else:
            args.append(0)

        self._lib.TA_DeactivationRequestToFile(self._handle, *args)

    def activate(self, extra_data=""):
        """
        Activates the product on this computer. You must call set_product_key()
        with a valid product key or have used the TurboActivate wizard sometime
        before calling this function.
        """

        if extra_data:
            options = ACTIVATE_OPTIONS(sizeof(ACTIVATE_OPTIONS()),
                                      wstr(extra_data))

            args = pointer(options)
        else:
            args = None

        self._lib.TA_Activate(self._handle, args)

    def activation_request_to_file(self, filename, extra_data=""):
        """
        Get the "activation request" file for offline activation. You must call
        set_product_key() with a valid product key or have used the TurboActivate
        Wizard sometime before calling this function.
        """
        args = [wstr(filename)]

        if extra_data:
            options = ACTIVATE_OPTIONS(sizeof(ACTIVATE_OPTIONS()),
                                      wstr(extra_data))

            args.append(pointer(options))
        else:
            args.append(None)

        self._lib.TA_ActivationRequestToFile(self._handle, *args)

    def activate_from_file(self, filename):
        """Activate from the "activation response" file for offline activation."""

        self._lib.TA_ActivateFromFile(self._handle, wstr(filename))

    def get_extra_data(self):
        """Gets the extra data you passed in using activate()"""
        buf_size = 255
        buf = wbuf(buf_size)

        try:
            self._lib.TA_GetExtraData(self._handle, buf, buf_size)

            return buf.value
        except TurboActivateFailError:
            return ""

    def is_activated(self):
        """ Checks whether the computer has been activated."""

        ret = self._lib.TA_IsActivated(self._handle)

        if ret == TA_OK:
            return True
        elif ret == TA_FAIL:
            return False

        # raise an error on all other return codes
        validate_result(ret)

    # Features

    def has_feature(self, name):
        return len(self.get_feature_value(name)) > 0

    def get_feature_value(self, name):
        """Gets the value of a feature."""
        buf_size = self._lib.TA_GetFeatureValue(self._handle, wstr(name), 0, 0)
        buf = wbuf(buf_size)

        self._lib.TA_GetFeatureValue(self._handle, wstr(name), buf, buf_size)

        return buf.value

    # Genuine

    def is_genuine(self):
        """
        Checks whether the computer is genuinely activated by verifying with the LimeLM servers.
        If reactivation is needed then it will do this as well.
        """
        ret = self._lib.TA_IsGenuine(self._handle)

        if ret == TA_OK:
            return IsGenuineResult.Genuine
        elif ret in {TA_FAIL, TA_E_REVOKED, TA_E_ACTIVATE}:
            return IsGenuineResult.NotGenuine
        elif ret == TA_E_INET:
            return IsGenuineResult.InternetError
        elif ret == TA_E_IN_VM:
            return IsGenuineResult.NotGenuineInVM
        elif ret == TA_E_FEATURES_CHANGED:
            return IsGenuineResult.GenuineFeaturesChanged

        validate_result(ret)

    # IsGenuineEx

    def is_genuine_ex(self, days_between_checks, grace_days_on_inet_err, skip_offline = False, offline_show_inet_err = False):
        """
        Checks whether the computer is genuinely activated by verifying with the LimeLM servers.
        If reactivation is needed then it will do this as well.
        """
        flags = 0

        if skip_offline:
            flags = TA_SKIP_OFFLINE

        if offline_show_inet_err:
            flags = flags | TA_OFFLINE_SHOW_INET_ERR

        options = GENUINE_OPTIONS(sizeof(GENUINE_OPTIONS()),
                                  flags,
                                  days_between_checks,
                                  grace_days_on_inet_err)

        ret = self._lib.TA_IsGenuineEx(self._handle, pointer(options))

        if ret == TA_OK:
            return IsGenuineResult.Genuine
        elif ret in {TA_FAIL, TA_E_REVOKED, TA_E_ACTIVATE}:
            return IsGenuineResult.NotGenuine
        elif ret in {TA_E_INET, TA_E_INET_DELAYED}:
            return IsGenuineResult.InternetError
        elif ret == TA_E_IN_VM:
            return IsGenuineResult.NotGenuineInVM
        elif ret == TA_E_FEATURES_CHANGED:
            return IsGenuineResult.GenuineFeaturesChanged

        validate_result(ret)

    # Trial

    def use_trial(self, verified=True, extra_data="", callback = None):
        """
        Begins the trial the first time it's called. Calling it again will validate the trial
        data hasn't been tampered with.
        """
        flags = TA_VERIFIED_TRIAL | self._flags if verified else TA_UNVERIFIED_TRIAL | self._flags

        args = [flags]

        if extra_data:
            args.append(wstr(extra_data))
        else:
            args.append(None)

        # Set the trial callback
        if callback is not None:
            # "cast" the native python function to TrialCallback type
            # save it locally so that it acutally works when it's called
            # back
            self._callback = TrialCallback(callback)
            self._lib.TA_SetTrialCallback(self._handle, self._callback, c_void_p(0))

        self._lib.TA_UseTrial(self._handle, *args)

    def trial_days_remaining(self, verified=True):
        """
        Get the number of trial days remaining.
        0 days if the trial has expired or has been tampered with
        (1 day means *at most* 1 day, that is it could be 30 seconds)

        You must have called "use_trial" o use this function
        """
        flags = TA_VERIFIED_TRIAL | self._flags if verified else TA_UNVERIFIED_TRIAL | self._flags
        days = c_uint32(0)

        self._lib.TA_TrialDaysRemaining(self._handle, flags, pointer(days))

        return days.value

    def extend_trial(self, extension_code, verified=True):
        """Extends the trial using a trial extension created in LimeLM."""

        flags = TA_VERIFIED_TRIAL | self._flags if verified else TA_UNVERIFIED_TRIAL | self._flags

        self._lib.TA_ExtendTrial(self._handle, flags, wstr(extension_code))

    # Utils

    def is_date_valid(self, date):
        """
        Check if the date is valid
        """

        try:
            self._lib.TA_IsDateValid(self._handle, wstr(date), TA_HAS_NOT_EXPIRED)

            return True
        except TurboActivateFlagsError as e:
            raise e
        except TurboActivateError:
            return False

    def set_custom_act_data_path(self, path):
        """
        This function allows you to set a custom folder to store the activation
        data files. For normal use we do not recommend you use this function.

        Only use this function if you absolutely must store data into a separate
        folder. For example if your application runs on a USB drive and can't write
        any files to the main disk, then you can use this function to save the activation
        data files to a directory on the USB disk.

        If you are using this function (which we only recommend for very special use-cases)
        then you must call this function on every start of your program at the very top of
        your app before any other functions are called.

        The directory you pass in must already exist. And the process using TurboActivate
        must have permission to create, write, and delete files in that directory.
        """

        self._lib.TA_SetCustomActDataPath(wstr(path))

    def set_custom_proxy(self, address):
        """
        Sets the custom proxy to be used by functions that connect to the internet.

        Proxy address in the form: http://username:password@host:port/

        Example 1 (just a host): http://127.0.0.1/
        Example 2 (host and port): http://127.0.0.1:8080/
        Example 3 (all 3): http://user:pass@127.0.0.1:8080/

        If the port is not specified, TurboActivate will default to using port 1080 for proxies.
        """
        self._lib.TA_SetCustomProxy(wstr(address))

    def get_version(self):
        """
        Gets the version number of the currently used TurboActivate library.
        This is a useful alternative for platforms which don't support file meta-data
        (like Linux, FreeBSD, and other unix variants).

        The version format is:  Major.Minor.Build.Revision
        """
        major = c_uint32(0)
        minor = c_uint32(0)
        build = c_uint32(0)
        rev = c_uint32(0)

        self._lib.TA_GetVersion(pointer(major), pointer(minor), pointer(build), pointer(rev))

        return major.value, minor.value, build.value, rev.value

    def _set_restype(self):
        self._lib.TA_PDetsFromPath.restype = validate_result
        self._lib.TA_UseTrial.restype = validate_result
        self._lib.TA_GetPKey.restype = validate_result
        self._lib.TA_IsProductKeyValid.restype = validate_result
        self._lib.TA_DeactivationRequestToFile.restype = validate_result
        self._lib.TA_Deactivate.restype = validate_result
        self._lib.TA_Activate.restype = validate_result
        self._lib.TA_ActivationRequestToFile.restype = validate_result
        self._lib.TA_ActivateFromFile.restype = validate_result
        self._lib.TA_GetExtraData.restype = validate_result
        self._lib.TA_TrialDaysRemaining.restype = validate_result
        self._lib.TA_ExtendTrial.restype = validate_result
        self._lib.TA_IsDateValid.restype = validate_result
        self._lib.TA_SetCustomProxy.restype = validate_result
        self._lib.TA_SetCustomActDataPath.restype = validate_result
        self._lib.TA_SetTrialCallback.restype = validate_result
