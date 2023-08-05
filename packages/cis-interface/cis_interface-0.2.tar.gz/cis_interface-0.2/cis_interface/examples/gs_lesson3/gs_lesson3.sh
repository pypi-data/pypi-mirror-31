#!/bin/bash

export PSI_DEBUG="INFO"
export PSI_NAMESPACE="gs_lesson3"

yaml= 

# ----------------Your Commands------------------- #
case $1 in
    "" | -p | --python )
	echo "Running Python"
	yaml='gs_lesson3_python.yml'
	;;
    -m | --matlab )
	echo "Running Matlab"
	yaml='gs_lesson3_matlab.yml'
	;;
    -c | --gcc )
	echo "Running C"
	yaml='gs_lesson3_c.yml'
	;;
    --cpp | --g++)
	echo "Running C++"
	yaml='gs_lesson3_cpp.yml'
	;;
esac

cisrun $yaml
