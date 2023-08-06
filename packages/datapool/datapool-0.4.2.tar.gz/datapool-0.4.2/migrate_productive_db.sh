#! /bin/sh
#
# migrate_productive_db.sh
# Copyright (C) 2018 Uwe Schmitt <uwe.schmitt@id.ethz.ch>
#
# Distributed under terms of the MIT license.
#


alembic -c alembic-productive.ini upgrade head
