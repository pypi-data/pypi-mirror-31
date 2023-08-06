__author__ = 'nickdg'

import math
from collections import namedtuple

Position = namedtuple("Position", "x y z")
RotationEuler = namedtuple("RotationEuler", "x y z")
RotationQuaternion = namedtuple("RotationQuaternion", "x y z w")


def quaternion_to_euler(qx, qy, qz, qw):
    """Convert quaternion (qx, qy, qz, qw) angle to euclidean (x, y, z) angles, in degrees.
    Equation from http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/"""

    heading = math.atan2(2*qy*qw-2*qx*qz , 1 - 2*qy**2 - 2*qz**2)
    attitude = math.asin(2*qx*qy + 2*qz*qw)
    bank = math.atan2(2*qx*qw-2*qy*qz , 1 - 2*qx**2 - 2*qz**2)

    return [math.degrees(angle) for angle in [attitude, heading, bank]]  # TODO: May need to change some things to negative to deal with left-handed coordinate system.


class MarkerSet(object):

    def __init__(self, name='', id=None):
        self.name = name
        self.id = id
        self.markers = []


class Marker(object):

    def __init__(self, position=(0,0,0), name='', id=None, size=None):
        super(Marker, self).__init__()
        self.name = name
        self.id = id
        self.size = size
        self.position = Position(*position)

        # Optitrack-Provided attributes for labelled markers.
        self.occluded = None
        self.pc_solved = None
        self.model_solved = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Marker at [{:3.2f}, {:3.2f}, {:3.2f}]".format(self.position[0], self.position[1], self.position[2])


class RigidBody(object):

    def __init__(self, name='', markers=[], id=None, parent_id=None, offset=(0., 0., 0.)):
        super(RigidBody, self).__init__()
        self.name = name
        self.id, self.parent_id = id, parent_id
        self.markers = markers
        self.error = None  # Mean marker error
        self.seen = True  # Indicates that Tracking was successful this frame.
        self.offset = Position(*offset)
        self.__position, self.__rotation = None, None
        self.__rotation_to_var = None


    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = Position(*value)

    @property
    def rotation(self):
        return RotationEuler(*quaternion_to_euler(*self.__quaternion))

    # @rotation.setter
    # def rotation(self, value):
    #     coords = value if len(value)==3 else quaternion_to_euler(*value)
    #     self.__rotation = RotationEuler(*coords)

    @property
    def quaternion(self):
        return self.__quaternion

    @quaternion.setter
    def quaternion(self, coords):
        self.__quaternion = RotationQuaternion(*coords)
