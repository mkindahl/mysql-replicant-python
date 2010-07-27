# Copyright (c) 2010, Mats Kindahl, Charles Bell, and Lars Thalmann
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials
#       provided with the distribution.
#
#     * Neither the name of Sun Microsystems nor the names of its
#       contributors may be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL SUN
# MICROSYSTEMS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""
Module holding common definitions
"""

class Position:
    """Class to represent a binlog position for a specific server."""
    def __init__(self, file='', pos=0):
        self.file = file
        self.pos = pos

    def __cmp__(self, other):
        """Compare two positions lexicographically.  If the positions
        are from different servers, a ValueError exception will be
        raised.
        """
        return cmp((self.file, self.pos), (other.file, other.pos))

    def __repr__(self):
        "Give a printable and parsable representation of a binlog position"
        if self.pos == 0 or self.file == '':
            args = ''
        else:
            args = ', '.join(["'" + self.file + "'", str(self.pos)])
        return "Position(" + args + ")"
            

class User(object):
    """A MySQL server user"""
    def __init__(self, name, passwd = ""):
        self.name = name
        self.passwd = passwd

    def __repr__(self):
        return "User('%s','%s')" % (self.name, self.passwd)
