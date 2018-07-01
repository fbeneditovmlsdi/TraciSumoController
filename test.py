from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
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

def run_simulation():
    # step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()  # Run a simulation step

    traci.close()
    sys.stdout.flush()

# this is the main entry point of this script
if __name__ == "__main__":
    sumoBinary = checkBinary('sumo-gui')

    curr_datetime = datetime.datetime.now()

    output_file_name = "ufmaTracer"+curr_datetime.strftime("%Y-%m-%d %H:%M:%S")+".xml"

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                             "--tripinfo-output", "tripinfo.xml",
                             "--fcd-output", output_file_name])
    run_simutaion()
