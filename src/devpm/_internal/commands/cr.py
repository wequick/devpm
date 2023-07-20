# -*- coding:utf-8 -*-

# This file is part of devpm.
#
# Copyright (c) 2023 wequick
# This software is distributed under the MIT license.

# devpm cr - code review, same to pr

from devpm._internal.commands.pr import PrCommand


class CrCommand(PrCommand):
    def run(self, args=None):
        return super().run(args)
