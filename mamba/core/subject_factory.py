################################################################################################
##
##  Copyright (c) Mamba Developers. All rights reserved.
##  Licensed under the MIT License. See License.txt in the project root for license information.
##
################################################################################################

""" The Mamba implementation of a RxPy Reactive Factory """

from typing import Dict

from rx.subject import Subject


class SubjectFactory:
    """ The Subject Factory object lets you handle subjects by a string name
    """
    def __init__(self) -> None:
        self._factory: Dict[str, Subject] = {}

    def __getitem__(self, key: str) -> Subject:
        """ Registers a given subject by id.
            Note: It creates an empty one if it does not exists
        Args:
            key: Subject identifier.
        """
        if key not in self._factory:
            self._factory[key] = Subject()

        return self._factory[key]
