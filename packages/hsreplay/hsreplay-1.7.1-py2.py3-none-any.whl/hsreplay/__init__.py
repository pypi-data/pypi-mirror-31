import pkg_resources


__version__ = pkg_resources.require("hsreplay")[0].version

DTD_VERSION = "1.6"
SYSTEM_DTD = "https://hearthsim.info/hsreplay/dtd/hsreplay-%s.dtd" % (DTD_VERSION)
