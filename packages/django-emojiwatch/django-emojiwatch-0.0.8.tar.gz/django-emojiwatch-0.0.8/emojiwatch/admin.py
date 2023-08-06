# -*- encoding: utf-8 -*-

# ========================================================================
"""
Copyright and other protections apply. Please see the accompanying
:doc:`LICENSE <LICENSE>` and :doc:`CREDITS <CREDITS>` file(s) for rights
and restrictions governing use of this software. All rights not expressly
waived or licensed are reserved. If those files are missing or appear to
be modified from their originals, then please contact the author before
viewing or using this software in any capacity.
"""
# ========================================================================

from __future__ import absolute_import, division, print_function

TYPE_CHECKING = False  # from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import typing  # noqa: F401 # pylint: disable=import-error,unused-import,useless-suppression

from builtins import *  # noqa: F401,F403 # pylint: disable=redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import
from future.builtins.disabled import *  # noqa: F401,F403 # pylint: disable=no-name-in-module,redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import

# ---- Imports -----------------------------------------------------------

import django.forms as d_forms
import django.contrib.admin as d_c_admin

from .models import SlackWorkspaceEmojiWatcher

# ---- Data --------------------------------------------------------------

__all__ = ()

# ---- Classes -----------------------------------------------------------

# ========================================================================
class VersionedAdminForm(d_forms.ModelForm):

    # ---- Constructor ---------------------------------------------------

    def __init__(self, *args, **kw):
        # type: (...) -> None
        super().__init__(*args, **kw)  # type: ignore # py2
        # Hack to hide the _version field from the user, but still submit
        # its value with the form
        self.fields['_version'].widget = d_c_admin.widgets.AdminTextInputWidget(attrs={'type': 'hidden'})

# ========================================================================
class VersionedAdmin(d_c_admin.ModelAdmin):

    # ---- Data ----------------------------------------------------------

    form = VersionedAdminForm

# ---- Initialization ----------------------------------------------------

d_c_admin.site.register(SlackWorkspaceEmojiWatcher, VersionedAdmin)
