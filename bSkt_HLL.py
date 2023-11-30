import sys
import random

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

    # Bloom sketch parameters
    num_HLL_estimators = 4000
    num_registers_per_estimator = 128
    num_hashes = 3

    # Bloom sketch consisting of a number of HLL estimators, each with a number of 5-bit registers
    bSketch = []

    # Adding HLL estimators to bSketch
    for i in range(num_HLL_estimators):
        bSketch.append([0] * num_registers_per_estimator)

    # Creating hashes
    hashes = []
    for hash in range(num_hashes):
        hashes.append(random.randrange(1000000000))

    # Recording all flows in bloom sketch
    record_flows(flows, bSketch, hashes)

    # Estimating flow spreads in bloom sketch
    estimated_spreads = query_flows(flows, bSketch, hashes)

    #for flow_index in range(len(flows)):
    #    print("Flow id: " + flows[flow_index][0] + "      Actual flow spread: " + str(flows[flow_index][1]) + "        Estimated spread: " + str(estimated_spreads[flow_index]))

    #test_flow_information = []
    #for index in range(num_flows):
    #    test_flow_information.append((flows[index][1], estimated_spreads[index], flows[index][0]))
    #test_flow_information.sort(reverse = True)
    #for index in range(25):
    #    print("aFlow id: " + str(test_flow_information[index][2]) + "      Estimated Size: " + str(test_flow_information[index][1]) + "      Actual Size: " + str(test_flow_information[index][0]))

    # Refining flow information for output
    flow_information = []
    for index in range(num_flows):
        flow_information.append((estimated_spreads[index], flows[index][0], flows[index][1]))

    # Sorting by estimated size
    flow_information.sort(reverse = True)

    # Printing 25 largest estimated flow spreads:
    for index in range(25):
        print("Flow id: " + str(flow_information[index][1]) + "      Estimated Size: " + str(flow_information[index][0]))
# main()


# Inputs: List of all flows, bloom sketch, hashes
# Returns: None
# Description: Generates elements for each flow based on given spread, and records them into given number of HLL estimators in bloom sketch
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
            # Register hashed to in each HLL estimator for this element based on it's id
            register_hashed_to = hash_function(element, 4, len(bSketch[0]))

            # Getting the geometric hash for this element (0-31)
            geo_hash_value = geometric_hash(element)

            # Hashing to a given number of HLL estimators
            for hash in hashes:
                # Hash to an estimator using value: flow_id ^ hash
                estimator_hashed_to = hash_function(flows[flow_index][2] ^ hash, 5, len(bSketch))

                # Recording element spread
                # Number stored in register is maximum between currently stored value, and result of this element's geometric hash
                bSketch[estimator_hashed_to][register_hashed_to] = max(bSketch[estimator_hashed_to][register_hashed_to], geo_hash_value)
# record_flows()


# Inputs: List of all flows, bloom sketch, hashes
# Returns: None
# Description: Finds the estimated flow spread for each given flow
def query_flows(flows, bSketch, hashes):
    # Variables to calculate spread
    num_registers = len(bSketch[0])
    alpha = 0.7213/(1 + 1.079/num_registers)

    # Estimated spreads of all flows
    estimated_spreads = []

    # For each flow
    for flow_index in range(len(flows)):
        # Estimates for this flow from each hashed to HLL estimator
        flow_estimates = []

        # Going hash by hash
        for hash in hashes:
            # Hash to an estimator using value: flow_id ^ current_hash
            estimator_hashed_to = hash_function(flows[flow_index][2] ^ hash, 5, len(bSketch))

            # Harmonic mean of flow in estimator
            current_estimator_estimate = 0
            for register_num in range(num_registers):
                current_estimator_estimate += 2**(-1*bSketch[estimator_hashed_to][register_num])
            current_estimator_estimate = 1/current_estimator_estimate

            # Estimating flow spread
            flow_estimate_for_estimator = alpha * (num_registers**2) * current_estimator_estimate
            flow_estimates.append(flow_estimate_for_estimator)

        # Using minimum estimated flow spread
        estimated_spreads.append(min(flow_estimates))

    # Returning all estimated flow spreads
    return estimated_spreads
# query_flows()


# Inputs: key to hash, what size parts to split key into, size of hash table
# Returns: Index in hash table to hash key to
# Description: Folding hash function implementation based from https://www.herevego.com/hashing-python/
#   Split key into a number of parts based on given step size and then add them together
#   Hash function changes depending on step size
def hash_function(key, step_size, size):
    # If key is too short than error will occur; fixing here
    if key < 10**(step_size):
        key += 10**(step_size)

    # Pointer to current position of number
    int_pos = 0
    # Total sum of the split key
    split_id_sum = 0
    # Creating parts until there's no number left
    while int_pos < len(str(key)):
        # Making sure index isn't out of bounds
        if int_pos + step_size < len(str(key)):
            split_id_part = str(key)[int_pos:int_pos + step_size]
        else:
            split_id_part = str(key)[int_pos:]
        
        # Incrementing number position pointer
        int_pos = int_pos + step_size
        split_id_sum += int(split_id_part)
    
    # Returning position key hashes to in hash table
    return split_id_sum % size
# hash_function()


# Inputs: Key to hash, size of table hashing into
# Returns: Hash value
# Description: Uniform prime hashing method
def hash_function2(key, table_size):
    # Hash and return value
    return (key * 13) % table_size
    


# Inputs: Element to get geometric hash of
# Returns: Geometric hash of input
# Description: Calculates the geometric hash of given element by doing a uniform hash and then checking number of leading 0s
def geometric_hash(element):
    # Performing uniform hash for element 
    hash_value = hash_function2(element**2, 2**32)

    # Obtaining binary form of hash value and removing prefix
    binary_form = bin(hash_value)[2:]
    
    # Calculating how many leading 0s are present
    g = 32 - len(binary_form) + 1
    
    # Returning geometric hash value
    return g
# geometric_hash()


main()