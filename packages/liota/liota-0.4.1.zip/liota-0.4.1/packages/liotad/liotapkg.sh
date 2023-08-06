#!/usr/bin/env sh
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------#
#  Copyright © 2015-2016 VMware, Inc. All Rights Reserved.                    #
#                                                                             #
#  Licensed under the BSD 2-Clause License (the “License”); you may not use   #
#  this file except in compliance with the License.                           #
#                                                                             #
#  The BSD 2-Clause License                                                   #
#                                                                             #
#  Redistribution and use in source and binary forms, with or without         #
#  modification, are permitted provided that the following conditions are met:#
#                                                                             #
#  - Redistributions of source code must retain the above copyright notice,   #
#      this list of conditions and the following disclaimer.                  #
#                                                                             #
#  - Redistributions in binary form must reproduce the above copyright        #
#      notice, this list of conditions and the following disclaimer in the    #
#      documentation and/or other materials provided with the distribution.   #
#                                                                             #
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"#
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE  #
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE #
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE  #
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR        #
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF       #
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS   #
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN    #
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)    #
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF     #
#  THE POSSIBILITY OF SUCH DAMAGE.                                            #
# ----------------------------------------------------------------------------#

liota_config="/etc/liota/liota.conf"
package_messenger_pipe=""

if ! [ `ps -ef | grep "liotad.py" | grep -v grep | wc -l` -gt 0 ]
then
        echo "Liota package manager is not running. Please run it first!"
        exit -1
fi

if [ ! -f "$liota_config" ]
then
    echo "ERROR: Configuration file not found" >&2
    echo "You made need to copy the distributed configuration file from /usr/lib/liota/config/liota.conf to /etc/liota/liota.conf" >&2
    exit -2
fi

while read line # Read configurations from file
do
    varname=$(echo "$line" | sed "s/^\(..*\)\s*\=\s*..*$/\1/")
    if [ "$varname" = "pkg_msg_pipe " ]
    then
        value=$(echo "$line" | sed "s/^..*\s*\=\s*\(..*\)$/\1/")
        package_messenger_pipe=$value
        break
    fi
done < $liota_config

if [ "$package_messenger_pipe" = "" ]
then
    echo "ERROR: Pipe path not found in configuration file" >&2
    exit -3
fi

if [ ! -p "$package_messenger_pipe" ]
then
    echo "ERROR: Pipe path is not a named pipe" >&2
    exit -4
fi

# Collect the supplied arguments and create a comma seperated string so that package manager can split using comma as
# delimeter. The package name supplied could contain space character.
comma_seperated_args="$1"
shift
for arg in "$@"; do
	comma_seperated_args="$comma_seperated_args,$arg"
done

# Echo to named pipe
echo "Pipe file: $package_messenger_pipe" >&2
echo -n "$comma_seperated_args" > $package_messenger_pipe
