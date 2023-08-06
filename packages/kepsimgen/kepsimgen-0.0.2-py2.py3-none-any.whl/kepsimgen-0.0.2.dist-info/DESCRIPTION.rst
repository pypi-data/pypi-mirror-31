kep-simgen
========

CLI tool for converting Kepware project files so that they use simulation
devices instead of real device types.

# Overview

kep-simgen uses the library [KEP.py](https://github.com/jmbeach/KEP.py) to
parse Kepware JSON files. Then it changes the devices in the project to be
simulated devices and uses appropriate addresses so that you can easily
simulate a real project with the same tag names.

# Install

`pip install kep-simgen`

# Usage

`$> kep-simgen my-kepware-project.json`

Use `kep-simgen -?` for more detailed instructions


