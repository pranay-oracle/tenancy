# How to fetch details of a OCI Tenancy
Introduction :
To be used only for Oracle Cloud infrastructure

1. Scripts 
   1. prov_pyPull.py
   | - Use prov_pyPull.py to print readable CSV pip '|' delimited output file 
   | --> usage : `<python prov_pyPull.py  -p tenancyname >`

   2. pyPull.py
   | - Use pyPull.py to generate a html out put under ouput folder in current directory
   | --> usage : `<python pyPull.py  -p tenancyname >`

###Prereqs:
make sure $HOME/.oci/config file is created and populated : check below link for help
https://docs.cloud.oracle.com/iaas/Content/API/Concepts/sdkconfig.htm 
you can use Crkey.sh as well to create the Entry in config
usage : `<sh Crkey tenancyname >`
