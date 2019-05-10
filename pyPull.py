#!/opt/rh/rh-python36/root/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 15:51:42 2018
PURPOSE : Check details on a tenancy , reset password, fecth in Excel compatible format and 

@author: PRANAKUM ( Pranay  Kumar )

Usage :
  reset password     |+ pyPull.py --proxy --reset-pwd user@mydom.com -p TENANCYNAME
  list all details   |+ pyPull.py --proxy -o -p TENANCYNAME
  list all in Exls   |+ pyPull.py --proxy -p TENANCYNAME

Modifyproxy details before execution
"""


import sys,os,argparse,tempfile
#from dateutil import tz
from datetime import datetime
from pytz import timezone
import oci
import subprocess
import configparser



def main():
    global config
    
    ## Setting basepath for logs
    global basepath
    basepath=os.path.dirname(sys.argv[0])
    if not basepath or basepath =='.':
        basepath=os.getcwd()
    basepath=os.path.join(basepath,'output')
    if not os.path.exists(basepath):
        os.makedirs(basepath)
    ## setting of basepath completed
    msg=sys.argv[0] +"""
     -c config file Name
      |-> Default value is ~/.oci/config
     -p profilename
      |-> Default value is  [DEFAULT]
     -r region name like us-ashburn-1,
      |-> default will be picked up from config file
     -reset to be used only to reset userid/password
     """
    parser = argparse.ArgumentParser(prog='PROG', usage=msg)
    parser.add_argument('-c','--config-file',metavar='', help='[OPTIONAL] Full path to configfile')
    parser.add_argument('-p','--profile',metavar='', help='[OPTIONAL] Profile Name')
    parser.add_argument('-r','--region-name',metavar='', help='[OPTIONAL] Region name')
    parser.add_argument('-proxy','--proxy',action='store_true', help='[OPTIONAL] For settign proxy')
    parser.add_argument('-all','--all',action='store_true', help='[OPTIONAL] For settign proxy')
    parser.add_argument('-debug','--debug',action='store_true', help='[OPTIONAL] For saving Json details')
    parser.add_argument('-reset','--reset-pwd',metavar='', help='[OPTIONAL] For resettign password')
    parser.add_argument('-o','--output',action='store_true', help='[OPTIONAL] For saving log')
    args = parser.parse_args()
    #print("=========================")
    #print(args)
    #print("=========================")
    #print(args.all)

    #sys.exit(1)
    config=default_values(args.config_file,args.profile,args.proxy,args.debug,args.output,args.all)
    if args.reset_pwd:
        identity=oci.identity.IdentityClient(config)
        tenancy_name=identity.get_compartment(config['tenancy']).data.name
        region_name=str(config['region'])
        userlist=identity.list_users(config['tenancy'],limit=5000).data
        userocid=''
        for eachuser in userlist:
            if eachuser.name==args.reset_pwd:
                userocid=eachuser.id
        if userocid:
             new_password=identity.create_or_reset_ui_password(userocid).data
             print("[INFO] : New Password for ", args.reset_pwd, " : ", new_password.password)
             URL_login='https://console.'+region_name+'.oraclecloud.com/?tenant='+tenancy_name
             print("URL : ", URL_login)
        else:
             print("[ERROR]: No user found")
        sys.exit(0) 

    #print(config)

def default_values(config_file='',profile='',proxy='',debug_info='',output='',all_values=''):
    global debug
    global logging_file
    homedir= os.getenv("HOME")  if sys.platform.upper().find('LINUX')>=0  else  os.getenv("USERPROFILE")
    config_File_path=os.path.join(homedir,'.oci','config')
    profile_tobeused= 'DEFAULT' if not profile else profile
    configfile=config_File_path if not config_file else config_file
    config=oci.config.from_file(configfile , profile_tobeused)
    #setting proxy
    if proxy:
        os.environ["HTTP_PROXY"]='myproxyserer:80'
        os.environ["HTTPS_PROXY"]=os.environ["HTTP_PROXY"]
        os.environ["http_proxy"]=os.environ["HTTP_PROXY"]
        os.environ["https_proxy"]=os.environ["HTTP_PROXY"]
        #print("[INFO] : Setting proxy")
        
    if debug_info:
        debug='true'
        ## reove the debug file
        tempfile_name=os.path.join(tempfile.gettempdir(),'tempfile_debug')
        print("[INFO]   : Detailed debug will be written to file ", tempfile_name)
        try:
            os.rmdir(tempfile_name)
        except:
            pass

    if all_values:
        basepath = os.path.dirname(sys.argv[0])
        file_name=os.path.basename(sys.argv[0])
        if not basepath or basepath == '.':
            basepath = os.getcwd()
        script_name=os.path.join(basepath,file_name)
        config_data = configparser.ConfigParser()
        config_data.read(configfile)
        all_Sections=config_data.sections()
        for eachin in all_Sections:
            print("Executing for ",eachin )
            command = script_name + ' --proxy -o -p ' + eachin
            print(command)
            subprocess.check_output(command,shell=True)


    logging_file='true' if output  else 'False'
    return(config)

def debug_print(comments,data):
    global debug
    if debug.upper()=='TRUE':
        tempfile_name=os.path.join(basepath,'tempfile_debug')
        f=open(tempfile_name,'a')
        print("START - ", comments,file=f)
        print(data,file=f)
        print("END   - ", comments,file=f)
        print("\n\n",file=f)
        f.close()

def shape_details(shape_name):
    # https://cloud.oracle.com/compute/virtual-machine/features
    # https://docs.cloud.oracle.com/iaas/Content/Database/Concepts/exaoverview.htm?Highlight=Exadata.Quarter2.92
    # returns (GPU, OCPU, Memory in GB)
    if shape_name.upper() == 'VM.STANDARD1.1': return (0, 1, 7)
    if shape_name.upper() == 'VM.STANDARD1.2': return (0, 2, 14)
    if shape_name.upper() == 'VM.STANDARD1.4': return (0, 4, 28)
    if shape_name.upper() == 'VM.STANDARD1.8': return (0, 8, 56)
    if shape_name.upper() == 'VM.STANDARD1.16': return (0, 16, 112)
    if shape_name.upper() == 'VM.STANDARD2.1': return (0, 1, 15)
    if shape_name.upper() == 'VM.STANDARD2.2': return (0, 2, 30)
    if shape_name.upper() == 'VM.STANDARD2.4': return (0, 4, 60)
    if shape_name.upper() == 'VM.STANDARD2.8': return (0, 8, 120)
    if shape_name.upper() == 'VM.STANDARD2.16': return (0, 16, 240)
    if shape_name.upper() == 'VM.STANDARD2.24': return (0, 24, 320)

    if shape_name.upper() == 'VM.DENSEIO1.4': return (0, 4, 60)
    if shape_name.upper() == 'VM.DENSEIO1.8': return (0, 8, 120)
    if shape_name.upper() == 'VM.DENSEIO1.16': return (0, 16, 240)
    if shape_name.upper() == 'VM.DENSEIO2.8': return (0, 8, 120)
    if shape_name.upper() == 'VM.DENSEIO2.16': return (0, 16, 240)
    if shape_name.upper() == 'VM.DENSEIO2.24': return (0, 24, 320)
    if shape_name.upper() == 'BM.STANDARD1.36': return (0, 36, 512)

    if shape_name.upper() == 'BM.STANDARD2.52': return (0, 52, 768)
    if shape_name.upper() == 'BM.HIGHIO1.36': return (0, 36, 512)

    if shape_name.upper() == 'BM.DENSEIO1.36': return (0, 36, 512)
    if shape_name.upper() == 'BM.DENSEIO2.52': return (0, 52, 768)

    if shape_name.upper() == 'VM.GPU2.1': return (1, 12, 104)
    if shape_name.upper() == 'BM.GPU2.2': return (2, 28, 192)
    if shape_name.upper() == 'VM.GPU3.1': return (1, 6, 90)
    if shape_name.upper() == 'VM.GPU3.2': return (2, 12, 180)
    if shape_name.upper() == 'VM.GPU3.4': return (4, 24, 360)
    if shape_name.upper() == 'BM.GPU3.8': return (8, 52, 768)

    if shape_name.upper() == 'EXADATA.QUARTER2.92': return (0, 92 , 1440 )
    if shape_name.upper() == 'EXADATA.HALF2.184'  : return (0, 184, 2880 )
    if shape_name.upper() == 'EXADATA.FULL2.368'  : return (0, 368, 5760 )
    if shape_name.upper() == 'EXADATA.QUARTER1.84': return (0, 84 , 1440 )
    if shape_name.upper() == 'EXADATA.HALF1.168'  : return (0, 168, 2880 )
    if shape_name.upper() == 'EXADATA.FULL1.336'  : return (0, 336, 5760 )
    
    if shape_name.upper() == 'VM.STANDARD.E2.1' : return (0,1,8)
    if shape_name.upper() == 'VM.STANDARD.E2.2' : return (0,2,16)
    if shape_name.upper() == 'VM.STANDARD.E2.4' : return (0,4,32)
    if shape_name.upper() == 'VM.STANDARD.E2.8' : return (0,8,64)




def tenancy_regiondetails(dict_config):
    global all_regions
    global all_active_compartments
    global logging_file
    global basepath
    global file_path
    all_active_compartments={}
    all_ADs=[]
    all_regions={}
    current_config=dict_config
    all_regions={} if not all_regions else all_regions
    
    identity = oci.identity.IdentityClient(current_config)
    user=identity.get_user(current_config["user"]).data.name
    tenancy_name=identity.get_tenancy(current_config["tenancy"]).data.name
    tenancy_ocid=identity.get_tenancy(current_config["tenancy"]).data.id
    root_compartment=tenancy_name+'(root)'
    all_active_compartments[root_compartment]=tenancy_ocid
    
    if logging_file.upper()=='TRUE':
        file_path=os.path.join(basepath,tenancy_name)
        sys.stdout = open(file_path,'w')
    print(" ( Logged in as  ", user,")")
    print("\n\n")
    print("Tenancy Name|Tenancy OCID")
    print(tenancy_name,tenancy_ocid,sep='|')
    print("\n\n")
    print("Region|Home Region|Availability Domains|Tenancy OCID")
    subscription_details=identity.list_region_subscriptions(tenancy_ocid).data
    debug_print('Section : Subscription Details',subscription_details)
    for eachregion in subscription_details:
        current_config['region']=eachregion.region_name
        current_identity=''
        all_ADs=[]
        current_identity = oci.identity.IdentityClient(current_config)
        all_ADs.append(eachregion.region_name) ## placing region name as well as First entry in AD list
        #print(current_config["region"])
        ad_details=current_identity.list_availability_domains(tenancy_ocid).data
        debug_print('Section: AD details', ad_details)
        for eachad in ad_details:
            all_ADs.append(eachad.name)
        print(eachregion.region_name,eachregion.is_home_region,' ; '.join(all_ADs[1:]),tenancy_ocid,  sep='|')
        all_regions[eachregion.region_key]=all_ADs
        
    # printing compartment details
    print("\n\n")
    print("->Compartment Details")
    print("Compartment Name|Compartment OCID|Status|creation Time" )
    compartment_details=identity.list_compartments(compartment_id=current_config["tenancy"],limit=5000).data

    debug_print('Section: compartment Details',compartment_details)
    for eachcompartment in compartment_details:
        if eachcompartment.lifecycle_state=="ACTIVE":
            all_active_compartments[eachcompartment.name]=eachcompartment.id
        print(eachcompartment.name,eachcompartment.id,eachcompartment.lifecycle_state,eachcompartment.time_created,sep='|')

def list_users(identity):
    print("\n\n")
    print("->User Credetnails Details")
    print("Username or EMAIL | Groups | Status|Creation Date|User OCID")
    tenancy_ocid=config["tenancy"]
    identity = oci.identity.IdentityClient(config)
    user_config_details=identity.list_users(compartment_id=config["tenancy"],limit=5000).data

    debug_print('Section: User Details',user_config_details)
    for eachuser in user_config_details:
        username=eachuser.name
        username_ocid=eachuser.id
        username_status=eachuser.lifecycle_state
        username_creation=eachuser.time_created
        groupids=identity.list_user_group_memberships(compartment_id=tenancy_ocid,user_id=username_ocid,limit=5000).data
        
        groupname=''
        for eachgid in groupids:
            groupname=identity.get_group(eachgid.group_id).data.name +' ; '+ groupname 
        
        print(username,groupname,username_status,username_creation,username_ocid,  sep='|')
""" start : Compute Section """
def list_compute_vnic_details(compartment_id='',instance_id='',region_config=''):
    hostDomain=''
    inst_vnics=''
    inst_privips=''
    inst_pubips=''
    inst_subnets=''
    inst_vcns=''
    r_vms=oci.core.ComputeClient(region_config)
    r_vnics=oci.core.VirtualNetworkClient(region_config)
    #print(c_vms.list_vnic_attachments(compartment_id=compartment_id,instance_id=instance_id).data)
    for eachvnicid_data in r_vms.list_vnic_attachments(compartment_id=compartment_id,instance_id=instance_id,limit=5000).data:
        eachvnicid=eachvnicid_data.vnic_id
        #print(eachvnicid)
        eachvnic=r_vnics.get_vnic(eachvnicid).data
        inst_hostname=eachvnic.hostname_label
        inst_privips=str(inst_privips) +' '+str(eachvnic.private_ip)  if eachvnic.private_ip not in inst_privips else inst_privips
        if not eachvnic.public_ip:  # Added the condition if a private NIC is attached to a VM
            eachvnic.public_ip="NoPubIP"
        inst_pubips=str(inst_pubips)+' '+str(eachvnic.public_ip)      if eachvnic.public_ip not in inst_pubips else inst_pubips
        inst_vnics=inst_vnics+' '+eachvnic.display_name               if eachvnic.display_name not in inst_vnics else inst_vnics
        subnet=r_vnics.get_subnet(eachvnic.subnet_id).data
        inst_subnets= inst_subnets +' '+ subnet.display_name          if subnet.display_name not in inst_subnets else inst_subnets
        inst_vcns=inst_vcns +' '+ r_vnics.get_vcn(subnet.vcn_id).data.display_name   if r_vnics.get_vcn(subnet.vcn_id).data.display_name not in inst_vcns else inst_vcns
        if eachvnic.is_primary:
            hostDomain=subnet.subnet_domain_name
    #all_data=hostDomain+'|'+inst_privips+'|'+inst_pubips+'|'+inst_vnics+'|'+inst_subnets+'|'+inst_vcns
    inst_fqdn=str(inst_hostname)+'.'+str(hostDomain)
    return(inst_fqdn,inst_privips,inst_pubips,inst_vnics,inst_subnets,inst_vcns)


def list_compute(r_config):
    #print("compute Details ",r_config)
    global all_regions
    global compute_ocpu
    global compute_memgb
    global compute_gpu
    r_vms=oci.core.ComputeClient(r_config)
    #for eachcomp in r_identity.list_compartments( r_config['tenancy']).data:
    for compname,compid in all_active_compartments.items():
        #compname=eachcomp.name
        #compid=eachcomp.id
        allvm_details=r_vms.list_instances(compartment_id = compid, limit = 5000).data
        debug_print('Section: Compute Details',allvm_details)
        for eachinstance in allvm_details:
            inst_name=eachinstance.display_name
            inst_id=eachinstance.id
            if eachinstance.display_name.find('|dbaas|') != -1  or compname=='ManagedCompartmentForPaaS':
                inst_image="MANAGEDPASSVM"
            else:
                inst_image=r_vms.get_image(eachinstance.image_id).data.display_name
            #print("===================================")
            #print(eachinstance.display_name,eachinstance.id,eachinstance.image_id,compid,eachinstance.availability_domain)
            #print("===================================")
            #inst_image=r_vms.get_image(eachinstance.image_id).data.display_name
            inst_ad=eachinstance.availability_domain
            # the region comes incroect in london and  hence we should compute region from global ADs list  variable :
            for eachkey,eachvalue in all_regions.items():
                if inst_ad in eachvalue:
                    inst_region=all_regions[eachkey][0]
            inst_lifecycle=eachinstance.lifecycle_state
            inst_shape=eachinstance.shape
            creation_time=eachinstance.time_created
            #print("===",eachinstance.shape,"----")
            gpu,ocpu,memgb=shape_details(eachinstance.shape)
            
            
            if inst_lifecycle == "RUNNING":
                compute_gpu=compute_gpu+gpu
                compute_ocpu=compute_ocpu+ocpu
                compute_memgb=compute_memgb+memgb
                FQDNhost,inst_privips,inst_pubips,inst_vnics,inst_subnets,inst_vcns = list_compute_vnic_details(compartment_id=compid,instance_id=inst_id,region_config=r_config)
                #FQDNhost=inst_name+'.'+hostDomain
                inst_network=str(inst_vcns)+'/'+str(inst_subnets)
                print("Compute",compname,inst_region,inst_ad,inst_network,inst_name,FQDNhost,inst_privips,inst_pubips, inst_shape,ocpu,memgb,inst_lifecycle,inst_image,creation_time, inst_id,compid,sep='|')
            else:
                inst_status="NO Further DETAILS To SHOW as the instance is: "+inst_lifecycle
                print("Compute",compname,inst_region,inst_ad,inst_name,inst_status ,sep='|')

def list_compute_allregions(config):
    global all_regions
    #print("INsode now",all_regions)
    print("\n\n")
    #print("-> Compute IaaS Details")
    print("Tier|Compartment Name|Region|Availability Domain|VCN/Subnet|Instance Name |FQDN|PrivIPs|PubIPS|Shape|OCPU|MEM(GB)|Status|Image|CreationDate|Instance ocid|compartment OCID")
    for eachregion in all_regions.values():
        config['region']=eachregion[0]
        list_compute(config)
    print("Total OCPU      |", compute_ocpu)
    print("Total Memory GB |", compute_memgb)

""" end : Compute Section """

""" start : Database  Section """
def list_dbs(current_config):
    global all_regions
    global db_ocpu
    global db_memgb
    #print(current_config,"=======")
    db=oci.database.DatabaseClient(current_config)
    vnics=oci.core.VirtualNetworkClient(current_config)
    
    for compname,compid in all_active_compartments.items():
        #compname=eachcomp.name
        #compid=eachcomp.id
        db_system_details=db.list_db_systems(compartment_id = compid,limit=5000).data
        debug_print('Section: DBSystem Details',db_system_details)
        for eachdb in db_system_details :
            db_name=eachdb.display_name
            #
            db_domain=eachdb.domain
            data_size=str(eachdb.data_storage_size_in_gbs)+" GB"
            #db_fqdn=db_hostname+'.'+db_domain
            db_ad=eachdb.availability_domain
            db_subnet_name=vnics.get_subnet(eachdb.subnet_id).data.display_name
            vcn_name=vnics.get_vcn(vnics.get_subnet(eachdb.subnet_id).data.vcn_id).data.display_name
            for eachkey,eachvalue in all_regions.items():
                if db_ad in eachvalue:
                    db_region=all_regions[eachkey][0]
            db_license=eachdb.database_edition +' ('+ eachdb.license_model +')'
            db_version=str(eachdb.version)
            db_id=eachdb.id
            db_lifecycle=eachdb.lifecycle_state
            db_shape=eachdb.shape
            db_creation_time=eachdb.time_created
            gpu,ocpu,memgb=shape_details(eachdb.shape)
            #Fetch DB version and name details
            dblist_details=[]
            for eachdb_home in db.list_db_homes(compartment_id = compid,db_system_id = db_id).data:
                dbhomeid=eachdb_home.id
                db_version=str(eachdb_home.db_version)
                for eachdbindbhome in db.list_databases(compartment_id = compid,db_home_id=dbhomeid).data:
                 db_details=eachdbindbhome.db_name+'-'+eachdbindbhome.db_unique_name+'-'+eachdbindbhome.character_set+'-'+eachdbindbhome.ncharacter_set+'-'+str(eachdbindbhome.pdb_name)+'-'+str(db_version)
                 dblist_details.append(db_details)
                  
            dblist_details=str(dblist_details)
            for eachvnic in db.list_db_nodes(compartment_id = compid,db_system_id = db_id, limit  =5000).data:
                db_hostname=eachvnic.hostname
                if db_lifecycle == "AVAILABLE":
                    db_fqdn=str(db_hostname)+'.'+str(db_domain)
                    db_memgb=db_memgb+memgb
                    db_ocpu=db_ocpu+ocpu
                    
                    IPS=vnics.get_vnic(eachvnic.vnic_id).data
                    #print db_license to get details on BYOL etc
                    db_details=str(dblist_details)+'-'+str(db_license)+'-'+data_size
                    db_networks=str(vcn_name)+'/'+str(db_subnet_name)
                    print("DB",compname,db_region,db_ad,db_networks,db_name,db_fqdn,IPS.private_ip,IPS.public_ip,db_shape,ocpu,memgb, db_lifecycle,db_details,db_creation_time,db_id,compid,sep='|')
                else:
                    db_status="NO Further DETAILS To SHOW as the database is: "+db_lifecycle
                    print("DB",compname,db_region,db_ad,db_name,db_hostname,db_status,sep='|')

def list_db_allregions(config):
    global all_regions
    #print("INsode now",all_regions)
    #print("\n\n")
    #print("->DB SYSTEM Details")
    print("Tier|Compartment Name | Region|Availability Domain|VCN/Subnet|DB System Name|DB FQDN|Priv IP|Pub IP|Shape|OCPU|MEM(GB)|Status|DBNAME-UNQNAME-CHAR-NCHAR-PDBNAME-DBVERSION-LICENSE-DATASIZE|CreationTime|DB system OCID|Compartment OCID")
    for eachregion in all_regions.values():
        config['region']=eachregion[0]
        list_dbs(config)
    print("Total OCPU      |", db_ocpu)
    print("Total Memory GB |", db_memgb)

""" END  : Database  Section """

def vncs_subnets(current_config):
    vcns=oci.core.VirtualNetworkClient(config)
    
    for compname,compid in all_active_compartments.items():
        compartment_vnc_details=vcns.list_vcns(compartment_id = compid,limit=5000).data
        debug_print('Section: VCN Details',compartment_vnc_details)
        for eachvcn in compartment_vnc_details:
            vcn_name=eachvcn.display_name
            vcn_id=eachvcn.id
            vcn_status=eachvcn.lifecycle_state
            vcn_domain_name=eachvcn.vcn_domain_name
            vcn_cidr=eachvcn.cidr_block
            if vcn_status == "AVAILABLE":
                for eachsunet in vcns.list_subnets(compartment_id = compid,vcn_id = vcn_id,limit=5000).data:
                    subnet_name=eachsunet.display_name
                    subnet_id=eachsunet.id
                    subnet_status=eachsunet.lifecycle_state
                    subnt_ad=eachsunet.availability_domain
                    subnet_cidr = eachsunet.cidr_block
                    for eachkey,eachvalue in all_regions.items():
                        if subnt_ad in eachvalue:
                            subnet_region=all_regions[eachkey][0]
                    print(compname,vcn_name,vcn_domain_name,subnet_region,subnt_ad,subnet_name,subnet_cidr,subnet_status,vcn_id,subnet_id,compid,sep='|')
            else:
                print(compname,vcn_name,vcn_domain_name,"The VCN may not be active",sep='|')



def vcns_subnets_allregions (current_config):
    global all_regions
    #print("INsode now",all_regions)
    #print("\n\n")
    print("->VCN Details")
    print("Compartment Name | VCN NAME|VCN domain|Region|Availability Domain|Subnet Name|VCN CIDR|SubnetStatus|VCN OCID|SUBNET OCID|Compartment OCID")
    for eachregion in all_regions.values():
        config['region']=eachregion[0]
        vncs_subnets(config)



def list_load_balancer(current_config):
    lbs=oci.load_balancer.LoadBalancerClient(current_config)
    vcn=oci.core.VirtualNetworkClient(current_config)	

    for compname,compid in all_active_compartments.items():
        lb_details_data=lbs.list_load_balancers(compartment_id = compid, limit = 5000).data
        debug_print('Section: LBaaS Details',lb_details_data)
        for eachlbs in lb_details_data:
            lbs_name=eachlbs.display_name
            lbs_id=eachlbs.id
            lbs_status=eachlbs.lifecycle_state
            lbs_ip_address=eachlbs.ip_addresses[0].ip_address
            lbs_shape=eachlbs.shape_name
            lbs_subnets=[]
            for eachsubnet in eachlbs.subnet_ids:
               lbs_subnets.append(vcn.get_subnet(eachsubnet).data.display_name) 
            lbs_vcn=vcn.get_vcn(vcn.get_subnet(eachsubnet).data.vcn_id).data.display_name
            lbs_networks=str(lbs_vcn)+'/'+str(lbs_subnets)
            lbs_region=current_config["region"]
            # find private or public
            if eachlbs.is_private:
                lbaas_type='Private'
            else:
                lbaas_type='Public'
            
            # find if sslcert is deployed
            if eachlbs.certificates:
                certs_deployed=list (eachlbs.certificates.keys())
            else:
                certs_deployed="NO Certs deployed"
            
            if lbs_status == "ACTIVE":
                print("LBR",compname,lbs_region,lbs_networks,lbs_name,lbs_shape,certs_deployed,lbs_ip_address,lbaas_type,lbs_id,compid,sep='|')
            else:
                print("LBR",compname,lbs_region,lbs_name,lbs_shape,certs_deployed,lbs_ip_address,"The LBAAS may not be active",sep='|')

def load_balancers_all_region(current_config):
    global all_regions
    #print("INsode now",all_regions)
    print("\n\n")
    print("->Load Balancers")
    print("Tier|Compartment Name | Region|LbaaS Name |Capacity|SSL|IP Address|Pvt or Pub| LBR OCI|COmpartment OCID")
    for eachregion in all_regions.values():
        config['region']=eachregion[0]
        list_load_balancer(config)


def list_fss(current_config)    :
    fss=oci.file_storage.FileStorageClient(current_config)
    vnic = oci.core.VirtualNetworkClient(current_config)
    region_name=config["region"]
    
    for eachkey,eachvalue in all_regions.items():
        if current_config["region"] in eachvalue or current_config["region"] in eachkey:
            ad_in_this_region=eachvalue[1:]
            
    for compname,compid in all_active_compartments.items():
        for eachad in ad_in_this_region:
            ad_name=eachad
            all_fss=fss.list_file_systems(compartment_id = compid,availability_domain = eachad,limit =5000).data
            all_mount_targets=fss.list_mount_targets(compartment_id =compid,availability_domain =eachad, limit = 5000).data
            if all_fss:
                for eachfss in all_fss:
                    fss_name=eachfss.display_name
                    fss_id=eachfss.id
                    fss_status=eachfss.lifecycle_state
                    fss_metered_bytes=eachfss.metered_bytes
                    fss_GB=round(fss_metered_bytes/1024/1024/1024,1)
                    #print(fss_metered_bytes)
                    export_paths=[]
                    mounttarget_names=[]
                    mounttarget_ips=[]
                    for eachexportpath in fss.list_exports(file_system_id=fss_id,limit=5000).data:
                        export_paths.append(eachexportpath.path)
                        export_id=eachexportpath.id
                        export_set_id=fss.get_export(export_id).data.export_set_id
                        for eachmttarget in all_mount_targets:
                            if export_set_id==eachmttarget.export_set_id:
                                mounttarget_names.append(eachmttarget.display_name)
                                mounttarget_ips.append(vnic.get_private_ip(eachmttarget.private_ip_ids).data.ip_address)
                    #export_paths=''.join(export_paths)
                    #mounttarget_names=''.join(mounttarget_names)
                    #mounttarget_ips=''.join(mounttarget_ips)
                    print(compname,ad_name,region_name,fss_name,fss_status,export_paths,fss_GB,mounttarget_names,mounttarget_ips,fss_id,sep='|')
            debug_print("Section: FSS details", all_fss)



def fss_all_regions(currentconfig):
    global all_regions
    #print("INsode now",all_regions)
    print("\n\n")
    print("[INFO]: FSS Details")
    print("Compartment Name | AD NAME|Region Name|FSS NAME|FSS Status|export paths|FSS GB Used|Mount TargetNames|MOUNT IP|FSS OCID")
    for eachregion in all_regions.values():
        config['region']=eachregion[0]
        list_fss(config)

def create_user(current_config):
    identity=oci.config.from_file(current_config)
    #identity.

global all_active_compartments
global config
global debug
global logging_file
conifg=''
debug='FALSE'

global all_regions
all_regions={}

global compute_gpu
compute_gpu=0
global compute_ocpu
compute_ocpu=0
global compute_memgb
compute_memgb=0

global db_ocpu
db_ocpu=0
global db_memgb
db_memgb=0


#print("Started Execution, Awaiting Completion..... It may take couple of minutes")
if __name__ == "__main__":
    main()

#if logging_file.upper()=='TRUE':
#sys.stdout = open('/tmp/filename','w')
#print("choosing" ,config['key_file'] )
#sys.exit(1)

###initializing  all global variables
"""START  :  Initializing all the methods needed"""
#identity = oci.identity.IdentityClient(config)
#vms=oci.core.ComputeClient(config)
#vnics=oci.core.VirtualNetworkClient(config)
#db=oci.database.DatabaseClient(config)
"""END  :  Initializing all the methods needed"""

""" Calling Functions"""

tenancy_regiondetails(config)

list_users(config)

list_compute_allregions(config)

list_db_allregions(config)

#vcns_subnets_allregions(config)

load_balancers_all_region(config)

fss_all_regions(config)


#no API as of now - not doable#list_service_limits(config)
#

if logging_file.upper()=='TRUE':
    filepath_name=file_path+'.html'
    filepath_name=os.path.os.path.abspath(filepath_name)    
    try:
        os.remove(filepath_name)
    except:
        pass    
    sys.stdout = open(filepath_name,'a')
    
    format = '%d-%B-%Y %H:%M:%S'
    now_utc = datetime.now(timezone('UTC'))
    now_india = now_utc.astimezone(timezone('Asia/Kolkata')) # Convert to Asia/Kolkata time zone  
    
    print("Execution time (india Time ) : ", now_india.strftime(format))
    with open(file_path,'r') as output_file:
        print(output_file.read().replace('\n\n\n', '</td></tr></table><br><br>     \r <table border=1>').replace('\n','<tr><td>').replace('|','</td><td>'))
        
    try:
        #os.remove(file_path)
        print("")
    except:
        pass


