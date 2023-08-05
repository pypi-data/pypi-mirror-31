#!/bin/bash

export PSI_DEBUG="INFO"
export PSI_NAMESPACE="rpc_lesson2"
export FIB_ITERATIONS="3"

yaml1= 
yaml2= 

# ----------------Your Commands------------------- #
case $1 in
    "" | -p | --python )
	echo "Running Python"
	yaml1='server_python.yml'
	yaml2='client_python.yml'
	;;
    -m | --matlab )
	echo "Running Matlab"
	yaml1='server_python.yml'
	yaml2='client_matlab.yml'
	;;
    -c | --gcc )
	echo "Running C"
	yaml1='server_python.yml'
	yaml2='client_c.yml'
	;;
    --cpp | --g++ )
	echo "Running C++"
	yaml1='server_python.yml'
	yaml2='client_cpp.yml'
	;;
esac

cisrun $yaml1 $yaml2

outfile1="${TMPDIR}client_output1.txt"
outfile2="${TMPDIR}client_output2.txt"
cat $outfile1
cat $outfile2
