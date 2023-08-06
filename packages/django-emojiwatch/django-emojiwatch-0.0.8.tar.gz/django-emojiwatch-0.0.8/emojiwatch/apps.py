# -*- encoding: utf-8 -*-
# ======================================================================
"""
Copyright and other protections apply. Please see the accompanying
:doc:`LICENSE <LICENSE>` and :doc:`CREDITS <CREDITS>` file(s) for rights
and restrictions governing use of this software. All rights not
expressly waived or licensed are reserved. If those files are missing or
appear to be modified from their originals, then please contact the
author before viewing or using this software in any capacity.
"""
# ======================================================================

from __future__ import absolute_import, division, print_function

TYPE_CHECKING = False  # from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import typing  # noqa: F401 # pylint: disable=import-error,unused-import,useless-suppression

from builtins import *  # noqa: F401,F403 # pylint: disable=redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import
from future.builtins.disabled import *  # noqa: F401,F403 # pylint: disable=no-name-in-module,redefined-builtin,unused-wildcard-import,useless-suppression,wildcard-import
from future.standard_library import install_aliases
install_aliases()

# ---- Imports ---------------------------------------------------------

from gettext import gettext

import django.apps as d_apps

from . import (
    LOGGER,
    SLACK_VERIFICATION_TOKEN,
)

# ---- Classes ---------------------------------------------------------

# ======================================================================
class EmojiwatchConfig(d_apps.AppConfig):

    # ---- Data --------------------------------------------------------

    name = 'emojiwatch'
    verbose_name = gettext('Emojiwatch')

    # ---- Overrides ---------------------------------------------------

    def ready(self):
        # type: (...) -> None
        super().ready()  # type: ignore # py2

        if not SLACK_VERIFICATION_TOKEN:
            LOGGER.critical("EMOJIWATCH['slack_verification_token'] setting is missing")
