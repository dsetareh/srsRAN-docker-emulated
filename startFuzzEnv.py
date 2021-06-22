# startFuzzEnv.py
import yaml, sys

if len(sys.argv) != 4:
    print(
        "./startFuzzEnv.py [test to run] [subnet] [output docker-compose filename]"
    )
    quit(1)

with open(
        "/home/dsetareh/docker/srsRAN-docker-emulated/docker-compose-template.yml",
        'r') as ymlfile:
    try:
        docker_config = yaml.safe_load(ymlfile)
    except yaml.YAMLError as exc:
        print(exc)

test_number = str(sys.argv[1])  # ! current test iteration
subnet = str(sys.argv[2]) + '0/24'  # ! '10.80.95.0/24' subnet
epc_ip = str(sys.argv[2]) + '10'  # ! '10.80.95.10'
enb_ip = str(sys.argv[2]) + '11'  # ! '10.80.95.11'

docker_config['services']['srsue'][
    'command'] = 'stdbuf -oL srsue /etc/srsran/ue.conf.fauxrf -f' + test_number

docker_config['services']['srsepc'][
    'command'] = 'stdbuf -oL srsepc /etc/srsran/epc.conf --mme.mme_bind_addr=' + epc_ip + ' --spgw.gtpu_bind_addr=' + epc_ip

docker_config['services']['srsepc']['networks']['corenet'][
    'ipv4_address'] = epc_ip

docker_config['services']['srsenb'][
    'command'] = 'srsenb /etc/srsran/enb.conf.fauxrf --enb.mme_addr=' + epc_ip + ' --enb.gtp_bind_addr=' + enb_ip + ' --enb.s1c_bind_addr=' + enb_ip

docker_config['services']['srsenb']['volumes'][
    0] = './pcaps/' + test_number + '.pcap:/pcaps/enb.pcap'

docker_config['services']['srsenb']['networks']['corenet'][
    'ipv4_address'] = enb_ip

docker_config['networks']['corenet']['ipam']['config'][0]['subnet'] = subnet

with open(sys.argv[3], 'w') as newconf:
    yaml.dump(docker_config, newconf, default_flow_style=False)