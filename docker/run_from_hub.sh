set -e

print_usage () {
    echo ""
    echo "------------------USAGE------------------------"
    echo "COMMAND:"
    echo "./run_from_hub.sh mode"
    echo ""
    echo "PARAMS:"
    echo "mode: 0=minimize, 1=full_funtion"
    echo "------------------USAGE------------------------"
    # shellcheck disable=SC2242
    exit -1
}

if [ $# -lt 1 ]; then
    print_usage
fi

if [ ${1} -eq 0 ]
then
    check_results=$(docker run -it -d --name tieba_sign_min ck123pm/tieba_sign_min)
    docker logs -f "$check_results"
elif [ ${1} -eq 1 ]
then
    check_results=$(docker run -it --name tieba_sign_full ck123pm/tieba_sign_full)
    docker logs -f "$check_results"
else
    echo "invalid mode: ${1}"
    exit -1
fi
