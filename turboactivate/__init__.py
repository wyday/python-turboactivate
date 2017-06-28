# -*- coding: utf-8 -*-
#
# Copyright 2013, 2014 Develer S.r.l. (http://www.develer.com/)
#
# Author: Lorenzo Villani <lvillani@develer.com>
# Author: Riccardo Ferrazzo <rferrazz@develer.com>
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

import sys

from datetime import datetime

from ctypes import pointer, sizeof, c_uint32

from turboactivate.c_wrapper import *

#
# Object oriented interface
#


class GenuineOptions(object):

    """A set of options to use with is_genuine()"""

    FLAG_SKIP_OFFLINE = 0x00000001
    FLAG_OFFLINE_SHOW_INET_ERR = 0x00000002

    def __init__(self, flags=0, grace_days=0, days_between_checks=0):
        self._flags = flags
        self._grace_days = grace_days
        self._days_between_checks = days_between_checks

    def get_pointer(self):
        options = GENUINE_OPTIONS(sizeof(GENUINE_OPTIONS()),
                                  self._flags,
                                  self._days_between_checks,
                                  self._grace_days)
        return pointer(options)

    def flags(self, flags):
        self._flags = flags

    def grace_days(self, days):
        """
        If the call fails because of an internet error,
        how long, in days, should the grace period last (before
        returning deactivating and returning TA_FAIL).

        14 days is recommended.
        """
        self._grace_days = days

    def days_between_checks(self, days):
        """How often to contact the LimeLM servers for validation. 90 days recommended."""
        self._days_between_checks = days


class TurboActivate(object):

    def __init__(self, dat_file, guid, library_folder="", mode=TA_USER):
        self._lib = load_library(library_folder)
        self._set_restype()

        self.set_current_product(dat_file, guid, mode=mode)

    #
    # Public
    #

    # Product management

    def use_trial(self, verified=True):

        flags = TA_VERIFIED_TRIAL | self._mode if verified else TA_UNVERIFIED_TRIAL | self._mode

        self._lib.TA_UseTrial(self._handle, flags, None)

    def set_current_product(self, dat_file, guid, mode=TA_USER):
        """
        This functions allows you to use licensing for multiple products within
        the same running process.
        """
        self._mode = mode
        self._dat_file = wstr(dat_file)

        try:
            self._lib.PDetsFromPath(self._dat_file)
        except TurboActivateFailError:
            # The dat file is already loaded
            pass

        self._handle = self._lib.TA_GetHandle(wstr(guid))

    # Product key

    def product_key(self):
        """
        Gets the stored product key. NOTE: if you want to check if a product key is valid
        simply call is_product_key_valid().
        """
        buf_size = 128
        buf = wbuf(buf_size)

        try:
            self._lib.TA_GetPKey(self._handle, buf, buf_size)

            return buf.value
        except TurboActivateProductKeyError as e:
            return None

    def set_product_key(self, product_key):
        """Checks and saves the product key."""
        self._lib.TA_CheckAndSavePKey(self._handle, wstr(product_key), self._mode)

    def is_product_key_valid(self):
        """
        Checks if the product key installed for this product is valid. This does NOT check if
        the product key is activated or genuine. Use is_activated() and is_genuine() instead.
        """
        try:
            self._lib.TA_IsProductKeyValid(self._handle)

            return True
        except TurboActivateError:
            return False

    # Activation status

    def deactivate(self, erase_p_key=True, deactivation_request_file=""):
        """
        Deactivates the product on this computer. Set erase_p_key to True to erase the stored
        product key, False to keep the product key around. If you're using deactivate to let
        a user move between computers it's almost always best to *not* erase the product
        key. This way you can just use activate() when the user wants to reactivate
        instead of forcing the user to re-enter their product key over-and-over again.
        If deactivation_request_file is specified, then it gets the "deactivation request"
        file for offline deactivation.
        """
        e = 1 if erase_p_key else 0
        fn = self._lib.TA_DeactivationRequestToFile if deactivation_request_file else self._lib.TA_Deactivate
        args = [wstr(deactivation_request_file)] if deactivation_request_file else []

        args.append(e)

        try:
            fn(self._handle, *args)
        except TurboActivateNotActivatedError:
            return

    def activate(self, activation_request_file=""):
        """
        Activates the product on this computer. You must call set_product_key()
        with a valid product key or have used the TurboActivate wizard sometime
        before calling this function.
        If activation_request_file is specified, then it gets the "activation request"
        file for offline activation.
        """
        if self.is_activated():
            return False

        fn = self._lib.TA_ActivationRequestToFile if activation_request_file else self._lib.TA_Activate
        args = [wstr(activation_request_file)] if activation_request_file else []

        args.append(None)

        try:
            fn(self._handle, *args)

            return True
        except TurboActivateError as e:
            if not activation_request_file:
                self.deactivate(True)

            raise e

    def activate_from_file(self, filename):
        """Activate from the "activation response" file for offline activation."""
        self._lib.ActivateFromFile(self._handle, wstr(filename))

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
        try:
            self._lib.TA_IsActivated(self._handle)

            return True
        except TurboActivateError:
            return False

    # Features

    def has_feature(self, name):
        return len(self.get_feature_value(name)) > 0

    def get_feature_value(self, name):
        """Gets the value of a feature."""
        buf_size = self._lib.GetFeatureValue(wstr(name), 0, 0)
        buf = wbuf(buf_size)

        self._lib.GetFeatureValue(wstr(name), buf, buf_size)

        return buf.value

    # Genuine

    def is_genuine(self, options=None):
        """
        Checks whether the computer is genuinely activated by verifying with the LimeLM servers.
        If reactivation is needed then it will do this as well.
        Optionally you can pass a GenuineOptions object to specify more details
        """
        fn = self._lib.TA_IsGenuine
        args = [self._handle]

        if options:
            fn = self._lib.TA_IsGenuineEx

            args.append(options.get_pointer())

        try:
            fn(*args)

            return True
        except TurboActivateFeaturesChangedError:
            return True

    # Trial

    def trial_days_remaining(self, verified=True):
        """
        Get the number of trial days remaining.
        0 days if the trial has expired or has been tampered with
        (1 day means *at most* 1 day, that is it could be 30 seconds)

        You must have called "use_trial" o use this function
        """
        flags = TA_VERIFIED_TRIAL | self._mode if verified else TA_UNVERIFIED_TRIAL | self._mode
        days = c_uint32(0)

        self._lib.TA_TrialDaysRemaining(self._handle, flags, pointer(days))

        return days.value

    def extend_trial(self, extension_code):
        """Extends the trial using a trial extension created in LimeLM."""
        self._lib.TA_ExtendTrial(self._handle, self._mode, wstr(extension_code))

    # Utils

    def is_date_valid(self, date=None):
        """
        Check if the date is valid
        """
        if not date:
            to_check = datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")
        else:
            to_check = date

        try:
            self._lib.TA_IsDateValid(self._handle, wstr(to_check), TA_HAS_NOT_EXPIRED)

            return True
        except TurboActivateFlagsError as e:
            raise e
        except TurboActivateError:
            return False

    def set_custom_path(self, path):
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

        On linux it is not available
        """
        if sys.platform.startswith('linux'):
            raise RuntimeError("set_custom_path is not available under linux")

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
        self._lib.SetCustomProxy(wstr(address))

    def _set_restype(self):
        self._lib.PDetsFromPath.restype = validate_result
        self._lib.TA_UseTrial.restype = validate_result
        self._lib.TA_GetPKey.restype = validate_result
        self._lib.TA_CheckAndSavePKey.restype = validate_result
        self._lib.TA_IsProductKeyValid.restype = validate_result
        self._lib.TA_DeactivationRequestToFile.restype = validate_result
        self._lib.TA_Deactivate.restype = validate_result
        self._lib.TA_Activate.restype = validate_result
        self._lib.TA_ActivationRequestToFile.restype = validate_result
        self._lib.TA_ActivateFromFile.restype = validate_result
        self._lib.TA_GetExtraData.restype = validate_result
        self._lib.TA_IsActivated.restype = validate_result
        self._lib.TA_IsGenuine.restype = validate_result
        self._lib.TA_IsGenuineEx.restype = validate_result
        self._lib.TA_TrialDaysRemaining.restype = validate_result
        self._lib.TA_ExtendTrial.restype = validate_result
        self._lib.TA_IsDateValid.restype = validate_result
        self._lib.SetCustomProxy.restype = validate_result

        # SetCustomActDataPath is not defined under linux
        if not sys.platform.startswith('linux'):
            self._lib.TA_SetCustomActDataPath.restype = validate_result
