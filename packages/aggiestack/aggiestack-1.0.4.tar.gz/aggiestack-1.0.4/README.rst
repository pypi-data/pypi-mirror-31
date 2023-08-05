        Purpose
        -------
        
        This is a demo program towards satisfying the course requirements for CSE - 689-607 SPTP: Cloud Computing Individual Project.

        Description of the project can be found at: 

        https://tamu.blackboard.com/bbcswebdav/pid-4279770-dt-content-rid-31058440_1/courses/CSCE.689.1811.M1/P1.pdf

        
        Usage
        -----

        pip install aggiestack cli

        First time you use the command you will be asked the mongodb host URL and database_name in order to connect

        Usage:
  		
  		aggiestack server create [--image=<IMAGE> --flavor=<FLAVOR_NAME>] <INSTANCE_NAME>
  		aggiestack server delete <INSTANCE_NAME>
  		aggiestack server list
  		aggiestack admin show hardware 
  		aggiestack admin show instances
  		aggiestack admin can_host <MACHINE_NAME> <FLAVOR>
  		aggiestack admin show imagecaches <RACK_NAME>
  		aggiestack admin evacuate <RACK_NAME>
  		aggiestack admin remove <MACHINE>
  		aggiestack admin clear_all
  		aggiestack admin add -mem MEM -disk NUM_DISKS -vcpus VCPU -ip IP -rack RACK_NAME MACHINE
  		aggiestack show hardware
  		aggiestack show images
  		aggiestack show flavors 
  		aggiestack show all 
  		aggiestack show logs 
  		aggiestack config [--images=<IMAGES_PATH> | --flavors=<FLAVORS_PATH> | --hardware=<HARDWARE_PATH> ] 
  		aggiestack config load <CONGFIG_PATH>  
  		aggiestack -h | --help
  		aggiestack --version
