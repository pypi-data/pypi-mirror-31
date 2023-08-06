# Demo Script to verify sanity of network

*** Settings ***
# Importing test libraries, resource files and variable files.
Library        ats.robot.pyATSRobot
Library        genie.libs.robot.GenieRobot


*** Variables ***
# Defining variables that can be used elsewhere in the test data. 
# Can also be driven as dash argument at runtime

# Define the pyATS testbed file to use for this run
${testbed}     virl.yaml 

# Genie Libraries to use
${trigger_datafile}     %{VIRTUAL_ENV}/genie_yamls/iosxe/trigger_datafile_iosxe.yaml
${verification_datafile}     %{VIRTUAL_ENV}/genie_yamls/iosxe/verification_datafile_iosxe.yaml


*** Test Cases ***
# Creating test cases from available keywords.

Initialize
    # Initializes the pyATS/Genie Testbed
    # pyATS Testbed can be used within pyATS/Genie
    use genie testbed "${testbed}"

    # Connect to both device
    connect to device "uut"
    connect to device "helper"

Ping uut
    run testcase     examples.genie.demo5_robot.pyats_loopback_reachability.NxosPingTestcase    device=uut
Ping helper
    run testcase     examples.genie.demo5_robot.pyats_loopback_reachability.PingTestcase    device=helper

# Verify Bgp Neighbors
Verify Bgp neighbors uut
    verify count "1" "bgp neighbors" on device "uut"
Verify Bgp neighbors helper
    verify count "1" "bgp neighbors" on device "helper"

# Verify Bgp Routes
# Tags can be used to control the behavior of the tests, noncritical tests which
# fail, will not cause the entire job to fail

Verify Bgp routes uut
    [Tags]    noncritical
    verify count "2" "bgp routes" on device "uut"
Verify Bgp routes helper
    [Tags]    noncritical
    verify count "2" "bgp routes" on device "helper"

# Verify OSPF neighbor counts
Verify Ospf neighbors uut
    verify count "2" "ospf neighbors" on device "uut"
Verify Ospf neighbors helper
    verify count "2" "ospf neighbors" on device "helper"

# Verify Interfaces
Verify Interace uut
    verify count "5" "interface up" on device "uut"
Verify Interace helper
    verify count "5" "interface up" on device "helper"
