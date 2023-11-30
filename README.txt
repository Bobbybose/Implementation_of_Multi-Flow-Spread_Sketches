CS685 - Internet Data Streaming 
Project 5 - Implementation of Multi-Flow Spread Sketches
Author: Bobby Bose

Description
- This is an implementation of a Virtual Bitmap and bSkt (HLL)
- There are two Python scripts, one for structure
- An example output is given in two output (.out) files
- One of the hash functions used in the code was based off of the folding method from https://www.herevego.com/hashing-python/

Required Packages and Modules
- No external packages required 
- The only required modules are the sys, random, and math modules built into Python

Virtual Bitmap
- To run, do 'python ./Virtual_Bitmap.py input_file'
- Architecture Operation:
    - Physical bitmap has 500,000 bits
    - Each virtual bitmap has 500 bits
        - Each flow is given a virtual bitmap
        - Each entry in the virtual bitmap hashes to an entry in the physical bitmap
    - Elements are hashed to one entry in bitmap
    - When querying, estimate flow spread using formula n_f = l*ln(V_B) - l*ln(V_f)
        - l = number of bits in the virtual bitmap
        - V_B = percent of bits in physical bitmap set to 0
        - V_f = percent of bits in virtual bitmap set to 0
- Program Flow: 
    - Read in flows and flow spreads from input file
    - Create physical bitmap and a virtual bitmap mapping per flow
    - Record all flows into bitmap
        - Create elements (# elements = flow spread size)
        - Find virtual bitmap bit that element hashes to
        - Record element in physical bitmap bit that hashed virtual bitmap bit maps to
    - Query all flows to get estimated flow sizes
    - Plot actual vs estimated flow sizes
- Output
    - Plot of actual vs estimated bit sizes
        - x axis limit set to flow size = 500

bSkt (HLL)
- To run, do 'python ./bSkt_HLL.py input_file'
- Architecture Operation:
    - Bloom sketch has 4000 HLL estimators
        - Each HLL estimator has 128 5-bit registers
    - Flows are hashed to three HLL estimators
        - Elements are hashed to a register
    - Value in register is highest geometric mean of an element hashed to the register so far
    - When querying, estimate flow spread using formula n_f = alpha* l^2 * sum(2^-A[H_i(f)][j] from 0 <= j <= l-1)^-1
        - l = number of registers in each HLL estimator
        - alpha = 0.7213/(1 + 1.079/l)
        - H_i(f) = ith hash function for flow, with 0 < i <= 3
        - A = bloom sketch
            - A[H_i(f)] = ith HLL estimator flow f hashes and records elements to
            - A[H_i(f)][j] = jth register in HLL estimator A[H_i(f)]
- Program Flow: 
    - Read in flows and flow spreads from input file
    - Create bloom sketch
    - Create hashes for flow hashing
    - Record all flows in bloom sketch
        - Create elements (# elements = flow spread size)
        - Each element hashes to one register in each HLL estimator that flow hashes to
    - Query all flows to get estimated flow sizes
    - Print 25 highest estimated flow sizes with flow id
- Output
    - 25 highest estimated flow sizes, with associated flow id