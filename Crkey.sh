#!/bin/ksh
# |- Author : Pranay Kumar
# |- 
# |- Purpose : Create dirkeys and update config file with basic information which will be created on Tenancy later
tenancy=${1}

if [ "x${tenancy}" = "x" ]; then
echo " No tenancy entered"
exit
fi 

cur_dir=`dirname $0`
#echo $cur_dir
#keyloc=`echo ${cur_dir}/../dirkeys/${tenancy}`
#echo $keyloc
#exit
keyloc=`echo ~/.oci/dirkeys/${tenancy}`

mkdir ${keyloc}
openssl genrsa -out  ${keyloc}/f 2048
openssl rsa -pubout -in ${keyloc}/f
finger_print=`openssl rsa -pubout -outform DER -in ${keyloc}/f | openssl md5 -c|awk '{print $NF}'`


echo "
[${tenancy}]
user=
fingerprint=${finger_print}
tenancy=
region=
key_file=${keyloc}/f

">>~/.oci/config


echo
echo
echo "vi ../config "
#;python  pyPull.py --proxy --reset-pwd ernam@exampledomaincom -p ${tenancy}"

