# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2010, 2013-2015, 2017-2018 Rocky Bernstein
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import cmdbreak as Mcmdbreak
from trepan.processor import complete as Mcomplete


class BreakCommand(Mbase_cmd.DebuggerCommand):
    """**break** [*location*] [if *condition*]]

Sets a breakpoint, i.e. stopping point just before the
execution of the instruction specified by *location*.

Without arguments or an empty *location*, the breakpoint is set at the
current stopped location.

See `help syntax location` for detailed information on a location.

If the word `if` is given after *location*, subsequent arguments given
Without arguments or an empty *location*, the breakpoint is set
the current stopped location.

Normally we only allow stopping at lines that we think are
stoppable. If the command has a `!` suffix, force the breakpoint anyway.

Examples:
---------

   break                # Break where we are current stopped at
   break if i < j       # Break at current line if i < j
   break 10             # Break on line 10 of the file we are
                        # currently stopped at
   break! 10            # Break where we are current stopped at, even if
                        # we don't think line 10 is stoppable
   break os.path.join() # Break in function os.path.join
   break x[i].fn()      # break in function specified by x[i].fn
   break x[i].fn() if x # break in function specified by x[i].fn
                        # if x is set
   break os.path:45     # Break on line 45 file holding module os.path
   break myfile.py:2    # Break on line 2 of myfile.py
   break myfile.py:2 if i < j # Same as above but only if i < j
   break "foo's.py":1"  # One way to specify path with a quote
   break 'c:\\foo.bat':1      # One way to specify a Windows file name,
   break '/My Docs/foo.py':1  # One way to specify path with blanks in it

See also:
---------

`tbreak`, `condition` and `help syntax location`."""

    aliases       = ('b', 'break!', 'b!')
    category      = 'breakpoints'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Set breakpoint at specified line or function'

    complete= Mcomplete.complete_break_linenumber

    def run(self, args):
        if args[0][-1] == '!':
            force = True
        else:
            force = False
        (func, filename, lineno,
         condition) = Mcmdbreak.parse_break_cmd(self.proc, args)
        if not (func == None and filename == None):
            Mcmdbreak.set_break(self, func, filename, lineno, condition,
                                False, args, force=force)
        return

# # Demo it
# if __name__ == '__main__':
#     import sys
#     from trepan import debugger as Mdebugger
#     d = Mdebugger.Debugger()
#     cmd = BreakCommand(d.core.processor)
#     cmd.proc.frame = sys._getframe()
#     cmd.proc.setup()

#     def foo():
#         return 'bar'

#     for c in (
#             ('break', 'os.path:10'),
#             ('break', 'os.path.join()'),
#             ('break', 'foo()', 'if', 'True'),
#             ('break', 'os.path:10', 'if', 'True'),
#             ('break',),
#             ('break', 'cmd.run()'),
#             ('break', '10'),
#             ('break', __file__ + ':10'),
#             ('break', 'foo()')):
#         cmd.proc.current_command = ' '.join(c)
#         cmd.run(c)
#     pass
