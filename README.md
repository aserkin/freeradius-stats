# freeradius-stats
radmin FreeRADIUS statistics converter into telegraf input
This script collects client list from running freeradius instance via radmin utility  
and convers statistics per client into influxdb format so that the script can be used as  
  
    [[inputs.exec]]  
      commands = ["/usr/local/bin/fr-stats.py"]  
      timeout = "5s"  
      data_format = "influx"  
  
for telegraf
