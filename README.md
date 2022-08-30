# Script to run command on al Virtual Machine Scale Sets (Azure)
## Requirements
* You need to have AZ cli installed
* You need to be logged in into Azure
* You need to know your Tenant ID

## Usage
```shell
python3 main.py --command "nslookup www.google.com" --tenant <tenant-id> --filter [<filter>]
```

