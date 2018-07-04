from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
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

t_type = {"PATH":0, "PUNCTUALITY":1, "SPEED_MOV":2, "SPEED_STILL":3}
timestamp = {"NOW":long(round(time.time() * 1000)), "4:00":1530601200000, "8:00":1530615600000, "10:46":1530625560000}


def run_simutaion(test_type = 0):
    step = 0
    prev_car_li = []
    if test_type == t_type["PATH"]:
        with open("ConstBreakLog.txt", "w") as breakLog:
            # write the current time to the log
            breakLog.write(str(timestamp["NOW"])+"\n")

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()  # Run a simulation step
            car_li = traci.edge.getLastStepVehicleIDs("327676501#0")  # get the cars at the edge

            if isinstance(car_li, (list,)):
                new_car_li = set(car_li) - set(prev_car_li)
            if len(new_car_li) > 0:  # if there is a new car
                prev_car_li = car_li
                change_route = str(raw_input('Type Y to change route: ')) #ask if the route should be changed
                if change_route == 'Y':
                    print('step: '+str(step))
                    with open("ConstBreakLog.txt", "a") as breakLog:
                        breakLog.write(str(step) + "\n")
                    for vehicle_id in new_car_li:
                        traci.vehicle.setRouteID(str(vehicle_id), "routeshuttleDeviate1")
            step+=1
    if test_type == t_type["SPEED_MOV"]:
        car_li = set([])
        with open("ConstBreakLog.txt", "w") as breakLog:
            # write the current time to the log
            breakLog.write(str(timestamp["8:00"])+"\n")
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            # traci._vehicle.VehicleDomain.getDrivingDistance() # try to use to get distance between vehicle and edge
            for car in traci.simulation.getDepartedIDList():
                car_li.add(car)
            car_li = car_li - set(traci.simulation.getArrivedIDList())
            new_car_li = set(car_li) - set(prev_car_li)
            if len(new_car_li) > 0:  # if there is a new car
                prev_car_li = car_li
                print('*-------------- New Car Detected --------------*')
                print('CarsList: '+str(car_li)+"\nNewCarsList"+str(new_car_li))
                print('*-------------- New Car Detected --------------*\n')

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

    test_type = t_type["SPEED_MOV"]

    curr_datetime = datetime.datetime.now()

    output_file_name = "ufmaTracer"+curr_datetime.strftime("%Y-%m-%d %H:%M:%S")+".xml"

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    if test_type == t_type["PATH"]:
        traci.start([sumoBinary, "-c", "ufma.sumocfg"])
    if test_type == t_type["PUNCTUALITY"]:
        traci.start([sumoBinary, "-c", "ufma_slow.sumocfg"])
    if test_type == t_type["SPEED_MOV"]:
        traci.start([sumoBinary, "-c", "ufma_speed.sumocfg"])
    if test_type == t_type["SPEED_STILL"]:
        traci.start([sumoBinary, "-c", "ufma_not_still.sumocfg"])
    run_simutaion(test_type)
