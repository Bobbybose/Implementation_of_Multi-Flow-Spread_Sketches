import sys
import random
import math

def main():
    
    # Checking that the correct number of arguments was passed in
    if len(sys.argv) != 2:
        print("Invalid number of arguments")
        print("Program should be run in form 'python ./bSkt_HLL.py input_file'")
        return
    
    # Setting input parameters
    input_file = open(sys.argv[1], "r")

    # First line of input file is number of flows
    num_flows = int(input_file.readline())

    # Creating list for flows
    flows = [] 

    # Obtaining flows from input file
    for flow in range(num_flows):
        # Reading in a new line and extracting flow id and number of elements
        curr_line = input_file.readline()

        # Flow id
        flow_id = curr_line.split('\t')[0]

        # Number of elements in flow
        num_elements = int(curr_line.split('\t')[-1].split('\n')[0])

        # Flow id without .'s
        flows_id_parts = flow_id.split('.')
        flow_id_concat_parts = int(flows_id_parts[0] + flows_id_parts[1] + flows_id_parts[2] + flows_id_parts[3])

        # Each flow is recorded in list as tuple of (flow id, flow spread, flow id without .'s)
        flows.append((flow_id, num_elements, flow_id_concat_parts))


    num_HLL_estimators = 4000
    num_registers_per_estimator = 128
    num_hashes = 3

    # bloom sketch consisting of a number of HLL estimators, each with a number of 5-bit registers
    bSketch = []

    # Adding HLL estimators to bSketch
    for i in range(num_HLL_estimators):
        bSketch.append([0] * num_registers_per_estimator)

    # Creating hashes
    hashes = []
    for hash in range(num_hashes):
        hashes.append(random.randrange(1000000000))

    record_flows(flows, bSketch, hashes)

    estimated_spreads = query_flows(flows, bSketch, hashes)

    for flow_index in range(len(flows)):
        print("Actual flow spread: " + str(flows[flow_index][1]) + "        Estimated spread: " + str(estimated_spreads[flow_index]))

    # Refining flow information for output
    flow_information = []
    for index in range(num_flows):
        flow_information.append((flows[index][0], flows[index][1], estimated_spreads[index]))

    # Sorting by estimated size
    flow_information.sort(reverse = True)

    # Printing 25 largest estimated flow spreads:
    for index in range(25):
        print("Flow id: " + str(flow_information[index][0]) + "      Estimated Size: " + str(flow_information[index][2]) + "      Actual Size: " + str(flow_information[index][1]))



# Inputs: List of all flows, physical bitmap, virtual bitmaps
# Returns: None
# Description: Generates elements for each flow based on given spread, and inserts them into the flow's virtual bitmap and overall physical bitmap
def record_flows(flows, bSketch, hashes):
    # Recording each flow
    for flow_index in range(len(flows)):
        # Creating element ids for the flow
        elements = []

        # Number of unique elements equal to flow spread
        for i in range(int(flows[flow_index][1])):
            element_id = random.randrange(1000000000)
            elements.append(element_id)
        
        # Recording each element
        for element in elements:
            for hash in hashes:
                # Hash to an estimator using value: flow_id ^ current_hash
                estimator_hashed_to = hash_function(flows[flow_index][2] ^ hash, 4, len(bSketch))

                # Hash to a register using element id
                register_hashed_to = hash_function(element, 6, len(bSketch[0]))

                # Getting the geometric hash using the element's hashed value
                geo_hash_value = geometric_hash(element)

                # Recording element spread
                # Number stored in register is maximum between currently stored value, and result of this element's geometric hash
                bSketch[estimator_hashed_to][register_hashed_to] = max(bSketch[estimator_hashed_to][register_hashed_to], geo_hash_value)

                # Register to hash size in
                #register_to_hash_size = random.randrange(1000000000) % len(bSketch[0])

                # Geometric hash of the register hashing size to
                #size_geo_hash_value = geometric_hash(register_to_hash_size)

                # Recording packet size
                #bSketch[estimator_hashed_to][register_to_hash_size] = max(bSketch[estimator_hashed_to][register_to_hash_size], size_geo_hash_value)
# record_flows()


def query_flows(flows, bSketch, hashes):
    num_registers = len(bSketch[0])
    
    alpha = 0.7213/(1 + 1.079/num_registers)

    # Estimated spreads of all flows
    estimated_spreads = []

    # For each flow
    for flow_index in range(len(flows)):
        # Estimates for this flow from each hashed to estimator
        flow_estimates = []

        # Going hash by hash
        for hash in hashes:
            # Hash to an estimator using value: flow_id ^ current_hash
            estimator_hashed_to = hash_function(flows[flow_index][2] ^ hash, 4, len(bSketch))

            # Harmonic mean of flow in estimator
            current_estimator_estimate = 0
            for register_num in range(num_registers):
                current_estimator_estimate += 2**(-bSketch[estimator_hashed_to][register_num])
            current_estimator_estimate = current_estimator_estimate ** -1

            # Estimating flow spread
            flow_estimate_for_estimator = alpha * (num_registers**2) * current_estimator_estimate
            flow_estimates.append(flow_estimate_for_estimator)

        # Using minimum estimated flow spread
        estimated_spread_for_flow = min(flow_estimates)
        estimated_spreads.append(estimated_spread_for_flow)

    return estimated_spreads

# Inputs: Id of element to hash, what size parts to split id into, length of bitmap
# Returns: Index in bitmap where element hashed to
# Description: Folding hash function implementation based from https://www.herevego.com/hashing-python/
#   Split id into a number of parts based on given step size and then add them together
#   Hash function changes depending on step size
def hash_function(element_id, step_size, size):
    # If id is too short than error will occur; fixing here
    if element_id < 10**(step_size):
        element_id += 10**(step_size)

    # Pointer to current position of number
    int_pos = 0
    # Total sum of the split id
    split_id_sum = 0
    # Creating parts until there's no number left
    while int_pos < len(str(element_id)):
        # Making sure index isn't out of bounds
        if int_pos + step_size < len(str(element_id)):
            split_id_part = str(element_id)[int_pos:int_pos + step_size]
        else:
            split_id_part = str(element_id)[int_pos:]
        
        # Incrementing number position pointer
        int_pos = int_pos + step_size
        split_id_sum += int(split_id_part)

    return split_id_sum % size
# hash_function()


# Inputs: Hash value
# Returns: Geometric hash of input
# Description: Calculates the geometric hash of the input value by calculating how many leading 0s are in the binary form of the number
#              Maximum number of bits is 7 for l = 128
def geometric_hash(element):
    # Performing uniform hash for element
    hash_value = hash_function(element, 5, 2**8)

    # Obtaining binary form of hash value and removing prefix
    binary_form = bin(hash_value)[2:]
    
    # Calculating how many leading 0s are present
    g = 8 - len(binary_form)
    
    #Returning geometric hash value
    return g
# geometric_hash()


main()