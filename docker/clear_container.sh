check_result=`docker container ls -a|grep tieba_sign |awk '{print $1}'`
#docker image ls -a -q

docker container stop $check_result
docker container rm $check_result