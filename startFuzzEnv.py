# startFuzzEnv.py
import yaml

with open("docker-compose-template.yml", 'r') as ymlfile:
    docker_config = yaml.load(ymlfile)

docker_config['x-srsue'][
    'command'] = 'stdbuf -oL srsue /etc/srsran/ue.conf.fauxrf -f20'

docker_config['services']['srsepc'][
    'command'] = 'stdbuf -oL srsepc /etc/srsran/epc.conf --mme.mme_bind_addr=10.80.95.10 --spgw.gtpu_bind_addr=10.80.95.10'

docker_config['services']['srsepc']['networks']['corenet'][
    'ipv4_address'] = '10.80.95.10'

docker_config['services']['srsenb'][
    'command'] = 'srsenb /etc/srsran/enb.conf.fauxrf --enb.mme_addr=10.80.95.10 --enb.gtp_bind_addr=10.80.95.11 --enb.s1c_bind_addr=10.80.95.11 --enb_files.sib_config=/etc/srsran/sib.conf'

docker_config['services']['srsenb']['networks']['corenet'][
    'ipv4_address'] = '10.80.95.11'

docker_config['services']['srsenb']['volumes'] = ['./pcaps:/pcaps']

docker_config['networks']['corenet']['ipam']['config'][0][
    'subnet'] = '10.80.95.0/24'

with open("docker-compose_new.yml", 'w') as newconf:
    yaml.dump(docker_config, newconf, default_flow_style=False)