#! /usr/bin/env python
# -*- coding: utf-8 -*-


def install(console):
    """Install the commands."""
    from Desc import Desc
    from Delete import Delete
    from Drop import Drop
    from Insert import Insert
    from Select import Select
    from Show import Show
    from Set import Set
    from Use import Use

    Delete().install(console)
    Desc().install(console)
    Drop().install(console)
    Insert().install(console)
    Select().install(console)
    Set().install(console)
    Show().install(console)
    Use().install(console)
