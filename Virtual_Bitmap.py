import sys
import random

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
    virtual_bitmaps = []
    
    # Creating a virtual bitmap for each flow
    #   Each virtual bitmap is a tuple, with first entry as flow id, and second entry as the bitmap
    for i in range(num_flows):
        virtual_bitmaps.append((flows[i][0], [0] * virtual_bitmap_size))


def record_flows(flows, bitmaps, virtual_bitmaps):

    for flow_index in range(len(flows)):
        # Creating element ids for the flow
        elements = []
        for i in range(flows[flow_index][0]):
            element_id = random.randrange(1000000000)
            elements.append(element_id)

        # Inserting each element into the 
        for element in elements:
            hash_function


# Inputs: Id of flow to hash, hashes to use for multi-hashing, what size parts to split id into
# Returns: Index in each counter where flow should be recorded to
# Description: Folding hash function implementation based from https://www.herevego.com/hashing-python/
#   Split id into a number of parts based on given step size and then add them together
#   Hash function changes depending on step size
def hash_function(flow_id, hashes, step_size):
    # Creating one int form of  flow id to hash
    id_parts = str(flow_id[0]).split('.')
    flow_id_to_hash = int(id_parts[0] + id_parts[1] + id_parts[2] + id_parts[3])
    
    # Obtaining hash ids
    multi_hashing_flow_ids = []
    for hash in hashes:
        multi_hashing_flow_ids.append(flow_id_to_hash^hash)
    
    # Obtaining counter positions flow hashes to
    flow_hash_counters = []
    for current_id in multi_hashing_flow_ids:
        # If id is too short than error will occur; fixing here
        if current_id < 10**(step_size):
            current_id += 10**(step_size)

        # Pointer to current position of number
        int_pos = 0
        # Total sum of the split id
        split_id_sum = 0
        # Creating parts until there's no number left
        while int_pos < len(str(current_id)):
            # Making sure index isn't out of bounds
            if int_pos + step_size < len(str(current_id)):
                split_id_part = str(current_id)[int_pos:int_pos + step_size]
            else:
                split_id_part = str(current_id)[int_pos:]
            
            # Incrementing number position pointer
            int_pos = int_pos + step_size
            split_id_sum += int(split_id_part)

        flow_hash_counters.append(split_id_sum)

    return flow_hash_counters
# hash_function()

main()