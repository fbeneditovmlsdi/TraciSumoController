from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import math
import subprocess
import random
import time
import datetime

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci

t_type = {"PATH":0, "PUNCTUALITY":1, "SPEED_MOV":2, "SPEED_STILL":3, "DISTANCE":4,}
timestamp = {"NOW":long(round(time.time() * 1000)), "4:00":1530601200000, "8:00":1530615600000, "10:46":1530625560000}


def distance(x1,y1, x2,y2):
    dist = ((x1-x2)**2)+((y1-y2)**2)
    return math.sqrt(dist)


def run_simutaion(test_type = 0):
    step = 0
    prev_car_li = []
    if test_type == t_type["PATH"]:
        with open("[PATH]ConstBreakLog.txt", "w") as breakLog:
            # write the current time to the log
            breakLog.write(str(timestamp["NOW"])+"\n")

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()  # Run a simulation step
            car_li = traci.edge.getLastStepVehicleIDs("327676501#0")  # get the cars at the edge

            if isinstance(car_li, (list,)):
                new_car_li = set(car_li) - set(prev_car_li)
            if len(new_car_li) > 0:  # if there is a new car
                prev_car_li = car_li
                change_route = str(raw_input('Type Y to change route: ')) # ask if the route should be changed
                if change_route == 'Y':
                    print('step: '+str(step))
                    with open("[PATH]ConstBreakLog.txt", "a") as breakLog:
                        breakLog.write(str(step) + "\n")
                    for vehicle_id in new_car_li:
                        traci.vehicle.setRouteID(str(vehicle_id), "routeshuttleDeviate1")
            step += 1
    if test_type == t_type["SPEED_MOV"]:
        threshold = 13.89
        car_li = set([])
        with open("[SPEED_MOV]ConstBreakLog.txt", "w") as breakLog:
            # write the current time to the log
            breakLog.write(str(timestamp["8:00"])+"\n")
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            # traci._vehicle.VehicleDomain.getDrivingDistance() # try to use to get distance between vehicle and edge
            for car in traci.simulation.getDepartedIDList():
                car_li.add(car)
            car_li = car_li - set(traci.simulation.getArrivedIDList())
            for car in car_li:
                speed = round(traci.vehicle.getSpeed(car), 2)
                if speed > threshold:
                    with open("[SPEED_MOV]ConstBreakLog.txt", "a") as breakLog:
                        breakLog.write("v_id: "+str(car)+", speed: "+str(speed)+", step: "+str(step) + "\n")
            step += 1

    if test_type == t_type["PUNCTUALITY"]:
        logfile_name = "[PUNCTUALITY]"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"ConstBreakLog.txt"
        with open(logfile_name, "w") as breakLog:
            # write the current time to the log
            breakLog.write(str(timestamp["8:00"])+"\n")
        edges = ["327676501#0", "327676501#1", "327676501#2", "433033617#0", "433033617#1", "433033617#2",
                 "433033617#3", "343294482#3", "343294482#4", "343294482#5", "327676481#3", "327676481#4", "327676512#0"]
        car_li = [list()] * len(edges)
        prev_car_li = [list()] * len(edges)
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()  # Run a simulation step
            for i in range(0, len(edges)):
                car_li[i] = traci.edge.getLastStepVehicleIDs(edges[i])  # get the cars at the edge
                new_car_li = set(car_li[i]) - set(prev_car_li[i])
                if len(new_car_li) > 0:  # if there is a new car
                    prev_car_li[i] = car_li[i]
                    for vehicle_id in new_car_li:
                        with open(logfile_name, "a") as breakLog:
                            breakLog.write("v_id: " + str(vehicle_id) + ", edge_id: " + str(edges[i]) + ", step: "
                                           + str(step) + "\n")
            step += 1

    if test_type == t_type["DISTANCE"]:
        logfile_name = "[DISTANCE]"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"ConstBreakLog.txt"
        with open(logfile_name, "w") as breakLog:
            # write the current time to the log
            breakLog.write(str(timestamp["8:00"])+"\n")
        edges = ["327676501#0", "327676501#1", "327676501#2", "433033617#0", "433033617#1", "433033617#2",
                 "433033617#3", "343294482#3", "343294482#4", "343294482#5", "327676481#3", "327676481#4", "327676512#0"]
        car_set = set([])

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()  # Run a simulation step
            car_set.update(traci.edge.getLastStepVehicleIDs(edges[0])) # get the cars at the edge

            car_li = list(car_set)
            print(car_li)
            for i in range(0, len(car_li)):
                x1, y1 = traci.vehicle.getPosition(car_li[i])
                for j in range(i, len(list)):
                    x2, y2 = traci.vehicle.getPosition(car_li[j])
                    dist = distance(x1, y1, x2, y2)
                    dist_string = "v_id1: " + str(car_li[i]) + ", v_id2: " + str(car_li[j]) + ", distance: " + str(dist)
                    print(dist_string)
                    with open(logfile_name, "a") as breakLog:
                        breakLog.write(dist_string + "\n")
            step += 1

    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    test_type = t_type["DISTANCE"]

    curr_datetime = datetime.datetime.now()

    output_file_name = "ufmaTracer"+curr_datetime.strftime("%Y-%m-%d %H:%M:%S")+".xml"

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    if test_type == t_type["PATH"]:
        traci.start([sumoBinary, "-c", "ufma.sumocfg"])
    if test_type == t_type["PUNCTUALITY"]:
        traci.start([sumoBinary, "-c", "ufma_punctuality.sumocfg"])
    if test_type == t_type["SPEED_MOV"]:
        traci.start([sumoBinary, "-c", "ufma_speed.sumocfg"])
    if test_type == t_type["SPEED_STILL"]:
        traci.start([sumoBinary, "-c", "ufma_not_still.sumocfg"])
    if test_type == t_type["DISTANCE"]:
        traci.start([sumoBinary, "-c", "ufma.sumocfg"])
    run_simutaion(test_type)

"""
# Get all new cars
            for car in traci.simulation.getDepartedIDList():
                car_li.add(car)
            car_li = car_li - set(traci.simulation.getArrivedIDList())
            new_car_li = set(car_li) - set(prev_car_li)
            if len(new_car_li) > 0:  # if there is a new car
                prev_car_li = car_li
                print('*-------------- New Car Detected --------------*')
                print('CarsList: '+str(car_li)+"\nNewCarsList"+str(new_car_li))
                print('*-------------- New Car Detected --------------*\n')
"""