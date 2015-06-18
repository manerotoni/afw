"""
channelname.py

Methods to validate channelnames

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("ChannelName", )

class ChannelName(object):
    """The convetion is that channel names constist of the string
    'channel' and underscore or space and an integer number e.g. 'Channel 1'

    This class provides an uniform methods to manipulate strings to follow
    the channel name convention.
    """

    @classmethod
    def splitFeatureName(cls, fname):
        return fname.split('-')

    @classmethod
    def abreviate(cls, name):

        if not name.lower().startswith("channel"):
            raise ValueError("Invalid channel name")

        if name.count(" ") == 1:
            ns = name.split(" ")
            if not ns[1].isdigit():
                raise ValueError("Invalid channel name")
            return "ch%s" %ns[1]

        elif name.count("_") == 1:
            ns = name.split(" ")
            if not ns[1].isdigit():
                raise ValueError("Invalid channel name")
            return "ch%s" %ns[1]

    @classmethod
    def number(cls, name):

        if name.lower().startswith("channel "):
            return int(name[8:])

        elif name.lower().startswith("channel_"):
            return int(name[8:])

        elif name[2:].isdigit():
            return int(name[2:])
        else:
            raise ValueError("Invalid channel name")

    @classmethod
    def from_abreviation(cls, name):

        if name.startswith("ch"):
            return "Channel %d" %int(name[2:])
        else:
            raise ValueError("Invalid channel name")

    @classmethod
    def validate(self, name):
        return name.replace(" ", "_")

    @classmethod
    def display(self, name):
        return name.replace("_", " ")
