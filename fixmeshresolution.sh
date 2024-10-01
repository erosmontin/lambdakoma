#!/bin/bash

# Define the input and output files
input_file="/home/eros/Downloads/GMT_decoupled_shield_rad_10.246cm_wide_3.9cm_len_22cm_width_1cm_mesh_0.005.msh"
output_file="/home/eros/Downloads/GMT_decoupled_shield_rad_10.246cm_wide_3.9cm_len_22cm_width_1cm_mesh_0.005mm.msh"

# Define the line to start the multiplication
start_line=6

# Initialize line number
line_number=0

# Read the file line by line
while IFS= read -r line
do
    # Increment the line number
    line_number=$((line_number+1))

    # Check if the line number is greater than or equal to the start line
    if (( line_number >= start_line )); then
        # Split the line into an array
        IFS=' ' read -r -a array <<< "$line"

        # Multiply the values by 1000, except for the first index
        for index in "${!array[@]}"
        do
            if (( index != 0 )); then
                array[$index]=$(echo "${array[$index]} * 1000" | bc)
            fi
        done

        # Join the array into a string
        line=$(IFS=' '; echo "${array[*]}")
    fi

    # Print the line to the output file
    echo "$line" >> "$output_file"
done < "$input_file"
