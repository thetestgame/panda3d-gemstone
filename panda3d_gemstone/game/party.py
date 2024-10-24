"""
MIT License

Copyright (c) 2024 Jordan Maxwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from panda3d_gemstone.framework.internal_object import InternalObject

class PlayerGroup(InternalObject): 
    """
    Represents a player group in the Gemstone application
    """

    def __init__(self):
        InternalObject.__init__(self)

        self.__leader = None
        self.__regular_members = []

    @property
    def group_leader(self) -> object:
        """
        Current group leader
        """

        return self.__leader

    @property
    def group_members(self) -> list:
        """
        All members of the group
        """

        return self.get_members()

    @property
    def regular_members(self) -> list:
        """
        Regular members of the group
        """

        return self.__regular_members

    def empty(self) -> None:
        """
        Empties the group object
        """

        self.__leader = None
        self.__regular_members = []

    def destroy(self) -> None:
        """
        Destroys the group object
        """

        InternalObject.destroy(self)
        self.empty()

    def is_leader(self, member: object) -> bool:
        """
        Returns true if the member is the group leader
        """

        return member == self.__leader

    def is_member(self, member: object) -> bool:
        """
        Returns true if the member is in the group
        """

        return self.is_leader(member) or self.is_regular_member(member)

    def is_regular_member(self, member: object) -> bool:
        """
        Returns true if the member is a regular member of the group
        """

        return member in self.__regular_members

    def get_members(self) -> list:
        """
        Returns all members in the team
        """

        group = []
        if self.__leader:
            groups.append(self.__leader)

        group.extend(self.__regular_members)
        return group

    def get_leader(self) -> object:
        """
        Returns the group's leader
        """

        return self.__leader

    def has_leader(self) -> bool:
        """
        Returns true if the group has a leader
        """

        return self.get_leader() != None

    def remove(self, member: object) -> None:
        """
        Removes the member from the group
        """

        if member in self.__regular_members:
            self.__regular_members.remove(member)
        elif member == self.__leader:
            self.__leader = None
        else:
            self.notify.warning('Failed to remove member from group. %s is not a member of the group' % str(member))

    def add(self, member: object, leader: bool = False) -> None:
        """
        Adds the member to the group. Optionally as the party leader
        """

        if self.is_member(member):
            self.notify.warning('Failed to add member to group. %s is already a member of the group' % str(member))
            return

        if leader:
            if self.has_leader():
                self.notify.warning('Failed to add member to group as leader. Group already has a leader.')
            else:
                self.__leader = member
        else:
            self.__regular_members.append(member)
        