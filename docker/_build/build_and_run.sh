set -e

print_usage () {
    echo ""
    echo "------------------USAGE------------------------"
    echo "COMMAND:"
    echo "./build_and_run.sh mode"
    echo ""
    echo "PARAMS:"
    echo "mode: 0=minimize, 1=full_funtion"
    echo "------------------USAGE------------------------"
    exit -1
}

if [ $# -lt 1 ]; then
    print_usage
fi

if [ ${1} -eq 0 ]
then
    cd minimize
    docker build -t tieba_sign_min:latest .
    check_results=`docker run -it -d --name tieba_sign_min tieba_sign_min:latest`
    docker logs -f $check_results
elif [ ${1} -eq 1 ]
then
    cd fullFunction
    docker build -t tieba_sign_full:latest .
    docker run -it --name tieba_sign_full tieba_sign_full:latest /bin/sh
else
    echo "invalid mode: ${1}"
    exit -1
fi
