#!/usr/bin/env python3

# Copyright © 2018 Broadcom. All Rights Reserved. The term “Broadcom” refers to
# Broadcom Inc. and/or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may also obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

:mod:`extension_tunnel_create` - PyFOS util for creating a tunnel.
********************************************************************************
The :mod:`extension_tunnel_create` provides tunnel creation functionality.

This module is a stand-alone script that can be used to create an extension
tunnel.

extension_tunnel_create.py: Usage

* Infrastructure options:
    * -i,--ipaddr=IPADDR: IP address of FOS switch.
    * -L,--login=LOGIN: Login name.
    * -P,--password=PASSWORD: Password.
    * -f,--vfid=VFID: VFID to which the request is directed.
    * -s,--secured=MODE: HTTPS mode "self" or "CA"[Optional].
    * -v,--verbose: Verbose mode[Optional].

* Util scripts options:
    * -n,--name=NAME: Set name.
    * -l,--load-level=VALUE: Set load-level.
    * -f,--fast-write-enabled=VALUE: Set fast-write-enabled.
    * -c,--compression-tunnel=VALUE: Set compression-tunnel.
    * -a,--admin-enabled=VALUE: Set admin-enabled.
    *    --ipsec-policy=VALUE: Set ipsec-policy.
    *    --user-friendly-name=VALUE: Set user-friendly-name.
    *    --fc-compression=VALUE: Set fc-compression.
    *    --ip-compression=VALUE: Set ip-compression.
    *    --ip-extension=VALUE: Set ip-extension.

* Outputs:
    * Python dictionary content with RESTCONF response data.

.. function:: extension_tunnel_create.create_extension_tunnel(session, name)

    *Create extension tunnel*

        Example usage of the method::

                ret = extension_tunnel_create.create_extension_tunnel(session,
                name)
                print (ret)

        Details::

            tunnel = {
                            "name": name,
                      }
            result = extension_tunnel_create._create_extension_tunnel(session,
            tunnel)

        * Inputs:
            :param session: Session returned by login.
            :param name: VE port name expressed as slot/port.

        * Outputs:
            :rtype: dictionary of return status matching rest response.

        *Use cases*

         Create a new extension tunnel.
"""


import pyfos.pyfos_auth as pyfos_auth
import pyfos.pyfos_util as pyfos_util
from pyfos.pyfos_brocade_extension_tunnel import extension_tunnel
import sys
import pyfos.utils.brcd_util as brcd_util

isHttps = "0"


def _create_extension_tunnel(session, tnlobject):
    result = tnlobject.post(session)
    return result


def create_extension_tunnel(session, name):
    value_dict = {'name': name}
    tnlobject = extension_tunnel(value_dict)
    result = _create_extension_tunnel(session, tnlobject)
    return result


def validate(tnlobject):
    if tnlobject.peek_name() is None:
            return 1
    return 0


def main(argv):
    # myinput=str("-i 10.17.3.70  --name 4/19")
    # argv = myinput.split()
    filters = ['name', 'user_friendly_name', 'ipsec_policy', 'load_level',
               'ip_extension', 'fast_write_enabled', 'compression_tunnel',
               'compression_protocol_ip_compression',
               'compression_protocol_fc_compression', 'admin_enabled']
    inputs = brcd_util.parse(argv, extension_tunnel, filters, validate)
    tnlobject = inputs['utilobject']
    session = brcd_util.getsession(inputs)
    result = _create_extension_tunnel(session, tnlobject)
    pyfos_util.response_print(result)
    pyfos_auth.logout(session)


if __name__ == "__main__":
    main(sys.argv[1:])
