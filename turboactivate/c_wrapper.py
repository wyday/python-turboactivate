# -*- coding: utf-8 -*-
#
# Copyright 2013, 2014 Develer S.r.l. (https://www.develer.com/)
# Copyright 2021 wyDay, LLC (https://wyday.com/)
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

import sys
from os import path as ospath
from ctypes import (
    cdll,
    c_uint,
    c_uint32,
    c_void_p,
    c_char_p,
    c_wchar_p,
    Structure,
    create_string_buffer,
    create_unicode_buffer,
    CFUNCTYPE
)

# Utilities

# python 2.7 string.encode('utf-8') returns an str class
# python 3.6 string.encode('utf-8') returns a bytes class

is_win = sys.platform == "win32"

wbuf = create_unicode_buffer if is_win else create_string_buffer

wstr_type = c_wchar_p if is_win else c_char_p


class wstr(wstr_type):
    def __init__(self, string):
        if sys.version_info > (3, 0) and isinstance(string, str):
            super(wstr, self).__init__(string.encode('utf-8') if not is_win else string)
        else:
            super(wstr, self).__init__(string)


# Wrapper

TA_OK = 0x00000000
TA_FAIL = 0x00000001
TA_E_PKEY = 0x00000002
TA_E_ACTIVATE = 0x00000003
TA_E_INET = 0x00000004
TA_E_INUSE = 0x00000005
TA_E_REVOKED = 0x00000006
TA_E_GUID = 0x00000007
TA_E_PDETS = 0x00000008
TA_E_TRIAL = 0x00000009
TA_E_TRIAL_EUSED = 0x0000000C
TA_E_TRIAL_EEXP = 0x0000000D
TA_E_EXPIRED = 0x0000000D
TA_E_REACTIVATE = 0x0000000A
TA_E_COM = 0x0000000B
TA_E_INSUFFICIENT_BUFFER = 0x0000000E
TA_E_PERMISSION = 0x0000000F
TA_E_INVALID_FLAGS = 0x00000010
TA_E_IN_VM = 0x00000011
TA_E_EDATA_LONG = 0x00000012
TA_E_INVALID_ARGS = 0x00000013
TA_E_KEY_FOR_TURBOFLOAT = 0x00000014
TA_E_INET_DELAYED = 0x00000015
TA_E_FEATURES_CHANGED = 0x00000016
TA_E_ANDROID_NOT_INIT = 0x00000017
TA_E_NO_MORE_DEACTIVATIONS = 0x00000018
TA_E_ACCOUNT_CANCELED = 0x00000019
TA_E_ALREADY_ACTIVATED = 0x0000001A
TA_E_INVALID_HANDLE = 0x0000001B
TA_E_ENABLE_NETWORK_ADAPTERS = 0x0000001C
TA_E_ALREADY_VERIFIED_TRIAL = 0x0000001D
TA_E_TRIAL_EXPIRED = 0x0000001E
TA_E_MUST_SPECIFY_TRIAL_TYPE = 0x0000001F
TA_E_MUST_USE_TRIAL = 0x00000020
TA_E_NO_MORE_TRIALS_ALLOWED = 0x00000021
TA_E_BROKEN_WMI = 0x00000022
TA_E_INET_TIMEOUT = 0x00000023
TA_E_INET_TLS = 0x00000024

# Flags for the UseTrial() and CheckAndSavePKey() functions.

TA_SYSTEM = 0x00000001
TA_USER = 0x00000002

# Flags for the IsGeninueEx() function.

"""
If the user activated using offline activation
(ActivateRequestToFile(), ActivateFromFile() ), then with this
flag IsGenuineEx() will still try to validate with the LimeLM
servers, however instead of returning TA_E_INET (when within the
grace period) or TA_FAIL (when past the grace period) it will
instead only return TA_OK (if IsActivated()).

If you still want to get the TA_E_INET error code, without
deactivating after the grace period has expired, then use
this flag in tandem with TA_OFFLINE_SHOW_INET_ERR.

If the user activated using online activation then this flag
is ignored.
"""
TA_SKIP_OFFLINE = 0x00000001

"""
If the user activated using offline activation, and you're
using this flag in tandem with TA_SKIP_OFFLINE, then IsGenuineEx()
will return TA_E_INET on internet failure instead of TA_OK.

If the user activated using online activation then this flag
is ignored.
"""
TA_OFFLINE_SHOW_INET_ERR = 0x00000002

"""
Use the TA_DISALLOW_VM in UseTrial() to disallow trials in virtual machines.
If you use this flag in UseTrial() and the customer's machine is a Virtual
Machine, then UseTrial() will return TA_E_IN_VM.
"""
TA_DISALLOW_VM = 0x00000004

"""
Use this flag in TA_UseTrial() to tell TurboActivate to use client-side
unverified trials. For more information about verified vs. unverified trials,
see here: https://wyday.com/limelm/help/trials/
Note: unverified trials are unsecured and can be reset by malicious customers.
"""
TA_UNVERIFIED_TRIAL = 0x00000010

"""
Use the TA_VERIFIED_TRIAL flag to use verified trials instead
of unverified trials. This means the trial is locked to a particular computer.
The customer can't reset the trial.
"""
TA_VERIFIED_TRIAL = 0x00000020


# Flags for the is_date_valid() Function

TA_HAS_NOT_EXPIRED = 0x00000001


# Possible callback statuses from the TrialCallbackType function:

'''
Callback-status value used when the trial has expired.
'''
TA_CB_EXPIRED = 0x00000000

'''
Callback-status value used when the trial has expired due to date/time fraud.
'''
TA_CB_EXPIRED_FRAUD = 0x00000001


class GENUINE_OPTIONS(Structure):
    _fields_ = [
        ("nLength", c_uint),
        ("flags", c_uint),
        ("nDaysBetweenChecks", c_uint),
        ("nGraceDaysOnInetErr", c_uint),
    ]


class ACTIVATE_OPTIONS(Structure):
    _fields_ = [
        ("nLength", c_uint),
        ("sExtraData", wstr),
    ]


TrialCallback = CFUNCTYPE(None, c_uint32, c_void_p)

def load_library(path):

    if sys.platform == 'win32' or sys.platform == 'cygwin':
        return cdll.LoadLibrary(ospath.join(path, 'TurboActivate.dll'))
    elif sys.platform == 'darwin':
        return cdll.LoadLibrary(ospath.join(path, 'libTurboActivate.dylib'))

    # else: linux, bsd, etc.
    return cdll.LoadLibrary(ospath.join(path, 'libTurboActivate.so'))


def validate_result(return_code):
    # All ok, no need to perform error handling.
    if return_code == TA_OK:
        return

    # Raise an exception type appropriate for the kind of error
    if return_code == TA_FAIL:
        raise TurboActivateFailError()
    elif return_code == TA_E_PDETS:
        raise TurboActivateDatFileError()
    elif return_code == TA_E_EDATA_LONG:
        raise TurboActivateExtraDataLongError()
    elif return_code == TA_E_PKEY:
        raise TurboActivateProductKeyError()
    elif return_code == TA_E_INUSE:
        raise TurboActivateInUseError()
    elif return_code == TA_E_REVOKED:
        raise TurboActivateRevokedError()
    elif return_code == TA_E_GUID:
        raise TurboActivateGuidError()
    elif return_code == TA_E_TRIAL:
        raise TurboActivateTrialCorruptedError()
    elif return_code == TA_E_TRIAL_EUSED:
        raise TurboActivateTrialUsedError()
    elif return_code == TA_E_TRIAL_EEXP:
        raise TurboActivateTrialExpiredError()
    elif return_code == TA_E_ACTIVATE:
        raise TurboActivateNotActivatedError()
    elif return_code == TA_E_INVALID_FLAGS:
        raise TurboActivateFlagsError()
    elif return_code == TA_E_COM:
        raise TurboActivateComError()
    elif return_code == TA_E_INET:
        raise TurboActivateInetError()
    elif return_code == TA_E_PERMISSION:
        raise TurboActivatePermissionError()
    elif return_code == TA_E_NO_MORE_DEACTIVATIONS:
        raise TurboActivateNoMoreDeactivationsError()
    elif return_code == TA_E_ACCOUNT_CANCELED:
        raise TurboActivateAccountCanceledError()
    elif return_code == TA_E_INVALID_HANDLE:
        raise TurboActivateInvalidHandleError()
    elif return_code == TA_E_ALREADY_ACTIVATED:
        raise TurboActivateAlreadyActivatedError()
    elif return_code == TA_E_ENABLE_NETWORK_ADAPTERS:
        raise TurboActivateEnableNetworkAdaptersError()
    elif return_code == TA_E_ALREADY_VERIFIED_TRIAL:
        raise TurboActivateAlreadyVerifiedTrialError()
    elif return_code == TA_E_TRIAL_EXPIRED:
        raise TurboActivateTrialExpiredError()
    elif return_code == TA_E_MUST_SPECIFY_TRIAL_TYPE:
        raise TurboActivateMustSpecifyTrialTypeError()
    elif return_code == TA_E_MUST_USE_TRIAL:
        raise TurboActivateMustUseTrialError()
    elif return_code == TA_E_NO_MORE_TRIALS_ALLOWED:
        raise TurboActivateNoMoreTrialsError()
    elif return_code == TA_E_INVALID_ARGS:
        raise TurboActivateInvalidArgsError()
    elif return_code == TA_E_BROKEN_WMI:
        raise TurboActivateBrokenWMIError()
    elif return_code == TA_E_INET_TIMEOUT:
        raise TurboActivateInetTimeoutError()
    elif return_code == TA_E_INET_TLS:
        raise TurboActivateInetTLSError()

    # Otherwise bail out and raise a generic exception
    raise TurboActivateError(return_code)


#
# Exception types
#

class TurboActivateError(Exception):

    """Generic TurboActivate error"""
    pass


class TurboActivateFailError(TurboActivateError):

    """Fail error"""
    pass


class TurboActivateProductKeyError(TurboActivateError):

    """Invalid product key"""
    pass


class TurboActivateNotActivatedError(TurboActivateError):

    """The product needs to be activated."""
    pass


class TurboActivateInetError(TurboActivateError):

    """Connection to the server failed."""
    pass


class TurboActivateInetTimeoutError(TurboActivateInetError):

    """The connection to the server timed out because a long period of time
    elapsed since the last data was sent or received."""
    pass


class TurboActivateInetTLSError(TurboActivateInetError):

    """The secure connection to the activation servers failed due to a TLS or
    certificate error. More information here: https://wyday.com/limelm/help/faq/#internet-error"""
    pass


class TurboActivateInUseError(TurboActivateError):

    """The product key has already been activated with the maximum number of computers."""
    pass


class TurboActivateRevokedError(TurboActivateError):

    """The product key has been revoked."""
    pass


class TurboActivateGuidError(TurboActivateError):

    """The version GUID doesn't match that of the product details file."""
    pass


class TurboActivateTrialCorruptedError(TurboActivateError):

    """The trial data has been corrupted, using the oldest date possible."""
    pass


class TurboActivateTrialUsedError(TurboActivateError):

    """The trial extension has already been used."""
    pass


class TurboActivateTrialExpiredError(TurboActivateError):

    """
    The activation has expired or the system time has been tampered
    with. Ensure your time, timezone, and date settings are correct.
    """
    pass


class TurboActivateComError(TurboActivateError):

    """
    The hardware id couldn't be generated due to an error in the COM setup.
    Re-enable Windows Management Instrumentation (WMI) in your group policy
    editor or reset the local group policy to the default values. Contact
    your system admin for more information.

    This error is Windows only.

    This error can also be caused by the user (or another program) disabling
    the "Windows Management Instrumentation" service. Make sure the "Startup type"
    is set to Automatic and then start the service.


    To further debug WMI problems open the "Computer Management" (compmgmt.msc),
    expand the "Services and Applications", right click "WMI Control" click
    "Properties" and view the status of the WMI.
    """
    pass


class TurboActivatePermissionError(TurboActivateError):

    """
    Insufficient system permission. Either start your process as an
    admin / elevated user or call the function again with the
    TA_USER flag instead of the TA_SYSTEM flag.
    """
    pass


class TurboActivateDatFileError(TurboActivateError):

    """The product details file "TurboActivate.dat" failed to load."""
    pass


class TurboActivateFlagsError(TurboActivateError):

    """
    The flags you passed to use_trial(...) were invalid (or missing).
    """
    pass


class TurboActivateExtraDataLongError(TurboActivateError):

    """
    The "extra data" was too long. You're limited to 255 UTF-8 characters.
    Or, on Windows, a Unicode string that will convert into 255 UTF-8
    characters or less.
    """
    pass


class TurboActivateNoMoreDeactivationsError(TurboActivateError):
    """
    This product key had a limited number of allowed deactivations.
    No more deactivations are allowed for the product key. This product
    is still activated on this computer.
    """
    pass


class TurboActivateAccountCanceledError(TurboActivateError):
    """
    Can't activate or start a verified trial because the LimeLM
    account is cancelled.
    """
    pass


class TurboActivateAlreadyActivatedError(TurboActivateError):
    """
    You can't use a product key because your app is already activated
    with a product key. To use a new product key, then first deactivate using
    either the TA_Deactivate() or TA_DeactivationRequestToFile().
    """
    pass


class TurboActivateInvalidHandleError(TurboActivateError):
    """
    The handle is not valid. To get a handle use TA_GetHandle().
    """
    pass


class TurboActivateEnableNetworkAdaptersError(TurboActivateError):
    """
    There are network adapters on the system that are disabled and
    TurboActivate couldn't read their hardware properties (even after trying
    and failing to enable the adapters automatically). Enable the network adapters,
    re-run the function, and TurboActivate will be able to "remember" the adapters
    even if the adapters are disabled in the future.

    Note:   The network adapters do not need an active Internet connections. They just
            need to not be disabled. Whether they are or are not connected to the
            internet/intranet is not important and does not affect this error code at all.


    On Linux you'll get this error if you don't have any real network adapters attached.
    For example if you have no "eth[x]", "wlan[x]", "en[x]", "wl[x]", "ww[x]", or "sl[x]"
    network interface devices.

    See: https://wyday.com/limelm/help/faq/#disabled-adapters
    """
    pass


class TurboActivateAlreadyVerifiedTrialError(TurboActivateError):
    """
    The trial is already a verified trial. You need to use the "TA_VERIFIED_TRIAL"
    flag. Can't "downgrade" a verified trial to an unverified trial.
    """
    pass


class TurboActivateMustSpecifyTrialTypeError(TurboActivateError):
    """
    You must specify the trial type (TA_UNVERIFIED_TRIAL or TA_VERIFIED_TRIAL).
    And you can't use both flags. Choose one or the other. We recommend TA_VERIFIED_TRIAL.
    """
    pass


class TurboActivateMustUseTrialError(TurboActivateError):
    """
    You must call TA_UseTrial() before you can get the number of trial days remaining.
    """
    pass


class TurboActivateNoMoreTrialsError(TurboActivateError):
    """
    In the LimeLM account either the trial days is set to 0, OR the account is set
    to not auto-upgrade and thus no more verified trials can be made.
    """
    pass


class TurboActivateBrokenWMIError(TurboActivateError):
    """
    The WMI repository on the computer is broken. To fix the WMI repository
    see the instructions here:

    https://wyday.com/limelm/help/faq/#fix-broken-wmi
    """
    pass


class TurboActivateInvalidArgsError(TurboActivateError):
    """
    The arguments passed to the function are invalid. Double check your logic.
    """
    pass
