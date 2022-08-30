import json
from shared import raw_parser, run_cmd

def get_all_accounts_per_tenant(tenant, name_filter):
    print(f"Getting all accounts for tenant {tenant}" )
    cmd_to_run = f'az account list --query "[?tenantId == \'{tenant}\'].id"'

    if name_filter:
        cmd_to_run = f'az account list --query "[?tenantId == \'{tenant}\' && contains(name, \'{name_filter}\')].id"'
    print(cmd_to_run)
    return run_cmd(
        cmd_to_run,
        to_json = True
    )

def get_all_vmss_per_subscription(subscription):
    print(f"Retrieving all Virtual Machine Scale Sets for Subscription ID: {subscription}")
    return run_cmd(
        'az vmss list --subscription ' + subscription + ' --query "[].{vmss_name:name,resource_group:resourceGroup}"',
        to_json=True
    )

def get_all_instance_ids_from_vmss(vmss_name, vmss_rg, subscription):
    print(f"Retrieving all Virtual Machines within: {vmss_name}")
    return run_cmd(
        'az vmss list-instances --subscription ' + subscription
        + ' -n ' + vmss_name
        + ' -g ' + vmss_rg
        + ' --query "[].instanceId"',
        to_json=True
    )

def run_command_on_instance_id_from_vmss(vmss_name, vmss_rg, instance_id, subscription, command):
    print(f"Running command '{command}' on {vmss_name} instance id {instance_id}")
    command_output = run_cmd(
        'az vmss run-command invoke -g ' + vmss_rg
        + ' -n ' + vmss_name + ' --command-id RunShellScript'
        + ' --instance-id ' + instance_id
        + ' --subscription ' + subscription
        + f' --scripts "{command}"'
    )
    return [(command["displayStatus"], command["message"]) for command in json.loads(command_output)["value"]]

def main():
    parser = raw_parser()
    required_opts = parser.add_argument_group('required arguments')
    required_opts.add_argument('--command', type=str.lower, required=True, help='Command to run on all AKS clusters and nodes')
    required_opts.add_argument('--tenant', type=str.lower, required=True, help='Tenant ID')
    parser.add_argument('--filter', type=str.upper, required=False, help='Filter subscriptions a string contained in the name')

    args = parser.parse_args()
    subscription_ids = get_all_accounts_per_tenant(tenant=args.tenant, name_filter=args.filter)
    for subscription_id in subscription_ids:
        vmss_list = get_all_vmss_per_subscription(subscription=subscription_id)
        for vmss in vmss_list:
            instance_ids_list = get_all_instance_ids_from_vmss(
                vmss_name=vmss["vmss_name"],
                vmss_rg=vmss["resource_group"],
                subscription=subscription_id
            )
            for instance_id in instance_ids_list:
                command_output = run_command_on_instance_id_from_vmss(
                    vmss_name=vmss["vmss_name"],
                    vmss_rg=vmss["resource_group"],
                    instance_id=instance_id,
                    subscription=subscription_id,
                    command=args.command
                )
                print(command_output)
    print(args.command)


if __name__ == '__main__':
    main()
