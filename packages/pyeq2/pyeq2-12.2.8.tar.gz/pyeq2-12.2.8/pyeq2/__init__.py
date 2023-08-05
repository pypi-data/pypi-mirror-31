from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

#    pyeq2 is a collection of equations expressed as Python classes
#
#    Copyright (C) 2013 James R. Phillips
#    2548 Vera Cruz Drive
#    Birmingham, AL 35235 USA
#
#    email: zunzun@zunzun.com
#
#    License: BSD-style (see LICENSE.txt in main source directory)

import warnings
warnString = 'Python 2.X will end-of-life in the year 2020, please use pyeq3. See http://legacy.python.org/dev/peps/pep-0373/'
warnings.warn(warnString, category=FutureWarning)

from . import DataCache
from . import Services
from . import ExtendedVersionHandlers
from . import IModel
from . import Models_2D
from . import Models_3D

dataConvertorService = Services.DataConverterService.DataConverterService
solverService = Services.SolverService.SolverService
outputSourceCodeService = Services.OutputSourceCodeService.OutputSourceCodeService
dataCache = DataCache.DataCache.DataCache
