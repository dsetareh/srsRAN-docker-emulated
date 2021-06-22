# startFuzzEnv.py
import yaml, sys

if len(sys.argv) != 2:
    print("./startFuzzEnv.py [test to run] [subnet]")
    quit(1)

with open("docker-compose-template.yml", 'r') as ymlfile:
    try:
        docker_config = yaml.safe_load(ymlfile)
    except yaml.YAMLError as exc:
        print(exc)

test_number = str(sys.argv[0])  # ! current test iteration
subnet = str(sys.argv[1]) + '0/24'  # ! '10.80.95.0/24' subnet
epc_ip = str(sys.argv[1]) + '10'  # ! '10.80.95.10'
enb_ip = str(sys.argv[1]) + '11'  # ! '10.80.95.11'

docker_config['x-srsue'][
    'command'] = 'stdbuf -oL srsue /etc/srsran/ue.conf.fauxrf -f' + test_number

docker_config['services']['srsepc'][
    'command'] = 'stdbuf -oL srsepc /etc/srsran/epc.conf --mme.mme_bind_addr=' + epc_ip + ' --spgw.gtpu_bind_addr=' + epc_ip

docker_config['services']['srsepc']['networks']['corenet'][
    'ipv4_address'] = epc_ip

docker_config['services']['srsenb'][
    'command'] = 'srsenb /etc/srsran/enb.conf.fauxrf --enb.mme_addr=' + epc_ip + ' --enb.gtp_bind_addr=' + enb_ip + ' --enb.s1c_bind_addr=' + enb_ip + ' --enb_files.sib_config=/etc/srsran/sib.conf --pcap.filename = /srsran/enb_' + test_number + '.pcap'

docker_config['services']['srsenb']['networks']['corenet'][
    'ipv4_address'] = enb_ip

docker_config['networks']['corenet']['ipam']['config'][0]['subnet'] = subnet

with open("docker-compose_new.yml", 'w') as newconf:
    yaml.dump(docker_config, newconf, default_flow_style=False)