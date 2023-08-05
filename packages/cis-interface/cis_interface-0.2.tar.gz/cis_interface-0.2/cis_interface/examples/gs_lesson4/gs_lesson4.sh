#!/bin/bash

export PSI_DEBUG="INFO"
export PSI_NAMESPACE="gs_lesson4"

yaml= 

# ----------------Your Commands------------------- #
case $1 in
    "" | -p | --python )
	echo "Running Python"
	yaml='gs_lesson4_python.yml'
	;;
    -m | --matlab )
	echo "Running Matlab"
	yaml='gs_lesson4_matlab.yml'
	;;
    -c | --gcc )
	echo "Running C"
	yaml='gs_lesson4_c.yml'
	;;
    --cpp | --g++)
	echo "Running C++"
	yaml='gs_lesson4_cpp.yml'
	;;
esac

cisrun $yaml
