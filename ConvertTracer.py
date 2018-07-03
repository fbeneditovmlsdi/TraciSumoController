from __future__ import print_function

import xml.etree.ElementTree as ET

import time


class StrToInt:  # Code a string to int
    def __init__(self):
        self.strSet = []

    def get_int(self, buffer):
        if self.strSet.count(buffer) > 0:
            return (self.strSet.index(buffer) + 1) * 100
        else:
            self.strSet.append(buffer)
            return (self.strSet.index(buffer) + 1) * 100


MUID_CONTAINS_STRING = True

try:
    with open("ConstBreakLog.txt", "r") as breakLog:
        breakLog_lines = breakLog.readlines
        now = long(breakLog_lines[0])
except IOError:
    now = long(round(time.time() * 1000))

tree = ET.parse('ufmaTrace.xml')
root = tree.getroot()
i=0
lines_arr = []
str_to_int = StrToInt()  # This will code the string parts of vehicle.id to int

for timestep in root:
    timestamp = str(now + int(float(timestep.get('time'))*500))
    for vehicle in timestep:
        if MUID_CONTAINS_STRING:
            id_parts = str(vehicle.get('id')).split('.')
            muID = id_parts[0]
            muID = str(str_to_int.get_int(muID))
            muID = muID + id_parts[1]
        else:
            muID = str(vehicle.get('id'))

        x = str(vehicle.get('x'))

        y = str(vehicle.get('y'))
        kindOfMU = str(vehicle.get('type'))
        speedf = round(float(vehicle.get('speed'))*3.6, 3)
        speed = str(speedf)
        lines_arr.append(muID+','+x+','+y+','+speed+','+timestamp+','+kindOfMU+'\n')

fo = open("ufmaTrace.txt", "w")
fo.writelines(lines_arr)

print(lines_arr[:20])

