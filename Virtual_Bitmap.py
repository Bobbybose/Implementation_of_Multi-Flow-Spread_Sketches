import sys
import random
import math
import matplotlib.pyplot as plt

def main():
    
    # Checking that the correct number of arguments was passed in
    if len(sys.argv) != 2:
        print("Invalid number of arguments")
        print("Program should be run in form 'python ./Virtual_Bitmap.py input_file'")
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
        flow_id = curr_line.split('\t')[0]
        num_elements = int(curr_line.split('\t')[-1].split('\n')[0])
        flows.append((flow_id, num_elements))

    # Bitmap size parameters
    physical_bitmap_size = 500000
    virtual_bitmap_size = 500

    # Creating physical and virtual bitmaps
    bitmap = [0] * physical_bitmap_size
    #virtual_bitmaps = []
    
    # Creating hashes
    hashes = []
    for hash in range(virtual_bitmap_size):
        hashes.append(random.randrange(100000000000))

    # Creating hash map for each flow's virtual bitmap to map each virtual bitmap bit to a bit in the physical bitmap
    virtual_bitmap_mappings = []
    for flow_index in range(num_flows):
        # Mapping for the flow
        mapping_for_flow = []
        for virtual_bitmap_index in range(virtual_bitmap_size):
            # Creating one int form of flow id
            id_parts = str(flows[flow_index][0]).split('.')
            flow_id_whole = int(id_parts[0] + id_parts[1] + id_parts[2] + id_parts[3])

            # Hashing from virtual bitmap spot to a place in physical bitmap
            mapping_for_flow.append(hash_function(flow_id_whole ^ hashes[virtual_bitmap_index], 6, physical_bitmap_size))
        
        # Adding to total virtual bitmaps
        virtual_bitmap_mappings.append(mapping_for_flow)

    # Recording all flows
    record_flows(flows, bitmap, virtual_bitmap_mappings)

    # Estimated the spread of all flows
    estimated_flow_spreads = query_flows(flows, bitmap, virtual_bitmap_mappings)

    # Printing flow spreads
    #for flow_index in range(len(flows)):
    #    print("Flow id: " + str(flows[flow_index][0]) + "        True spread: " + str(flows[flow_index][1]) + "        Estimated Spread: " + str(estimated_flow_spreads[flow_index]))

    # Plot the actual flow spread vs the estimated flow spread
    plot_flow_spreads(flows, estimated_flow_spreads)


# Inputs: List of all flows, physical bitmap, virtual bitmap mappings
# Returns: None
# Description: Generates elements for each flow based on given spread, and inserts them into bitmap based on flow's virtual bitmap mapping
def record_flows(flows, bitmap, virtual_bitmap_mappings):
    # Recording each flow
    for flow_index in range(len(flows)):
        # Creating element ids for the flow
        elements = []
        # Number of unique elements equal to flow spread
        for i in range(int(flows[flow_index][1])):
            element_id = random.randrange(1000000000)
            elements.append(element_id)
        
        # Inserting each element into the bitmaps
        for element in elements:
            # Index in virtual bitmap for flow that element hashes to
            virtual_bitmap_hash_index = hash_function(element, 3, len(virtual_bitmap_mappings[0]))

            # Index in physical bitmap that virtual bitmap bit hashes to
            physical_bitmap_index = virtual_bitmap_mappings[flow_index][virtual_bitmap_hash_index]

            # Inserting into bitmap
            bitmap[physical_bitmap_index] = 1
# record_flows()


# Inputs: List of all flows, physical bitmap, virtual bitmap mappings
# Returns: The estimated spread of each flow
# Description: Estimates the spread of each flow using formula:
#   n_f = l*ln(V_b) - l*ln(V_f)
#       l = Virtual bitmap length
#       V_b and V_f = percent of zeros in physical and virtual bitmap respectively
def query_flows(flows, bitmap, virtual_bitmap_mappings):
    # Calculating percent of zeros in physical bitmap
    virtual_bitmap_length = len(virtual_bitmap_mappings[0])
    physical_bitmap_percent_zeroes = bitmap.count(0) / len(bitmap)
    
    # Estimated spread of all flows
    estimated_flow_spreads = []
    
    # Estimating spread of each flow
    for flow_index in range(len(flows)):
        # Construct virtual bitmap
        virtual_bitmap = []
        for map_index in virtual_bitmap_mappings[flow_index]:
            virtual_bitmap.append(bitmap[map_index])

        # Find percent of zeroes in virtual bitmap for flow
        if virtual_bitmap.count(0) != 0:
            virtual_bitmap_percent_zeroes = virtual_bitmap.count(0) / virtual_bitmap_length
        # Correcting 0% which cause math error later
        else:
            virtual_bitmap_percent_zeroes = 1 / virtual_bitmap_length

        # Calculating the estimated flow spread using formula
        estimated_spread = virtual_bitmap_length * math.log(physical_bitmap_percent_zeroes) - virtual_bitmap_length * math.log(virtual_bitmap_percent_zeroes)
        estimated_flow_spreads.append(estimated_spread)

    # Retuning estimated spread of all flows
    return estimated_flow_spreads
# query_flows()


# Inputs: List of all flows, estimated flow spreads
# Returns: None
# Description: Plots actual flow spreads vs estimated flow spreads
def plot_flow_spreads(flows, estimated_flow_spreads):
    # Acquiring the actual flow spreads
    actual_spreads = []
    for flow in flows:
        actual_spreads.append(flow[1])

    # Plotting the spreads
    plt.scatter(actual_spreads, estimated_flow_spreads, color='blue', marker = '+', s = 20)
    
    # Setting axes parameters
    plt.xlim([0, 500])
    plt.ylim([0, 700])
    plt.xlabel("actual spread", fontsize=15)
    plt.ylabel("estimated spread", fontsize=15)

    # Saving the plot in the local folder
    plt.savefig("flow_spread.png")

    # Displaying the plot
    plt.show()
    

# Inputs: Id of element to hash, what size parts to split id into, length of bitmap
# Returns: Index in bitmap where element hashed to
# Description: Folding hash function implementation based from https://www.herevego.com/hashing-python/
#   Split id into a number of parts based on given step size and then add them together
#   Hash function changes depending on step size
def hash_function(element_id, step_size, bitmap_length):
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

    return split_id_sum % bitmap_length
# hash_function()


main()