# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Parts of this are based on or taken from Brady Johnston's MolecularNodes
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy

from . import ui

all_classes = (
    ui.CLASSES
)


def _test_register():
    try:
        register()
    except Exception:
        unregister()
        register()


def register():
    # register all of the import operators
    for op in all_classes:
        try:
            bpy.utils.register_class(op)
        except Exception:
            # print(e)
            pass


def unregister():
    for op in all_classes:
        try:
            bpy.utils.unregister_class(op)
        except Exception:
            # print(e)
            pass

