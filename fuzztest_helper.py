# fuzztest_helper.py
import yaml, sys
from pathlib import Path


def mass_generate_compose(startNum, endNum, templateFilename, outputDir):
    """generates composes from [startNum - endNum]

    Args:
        startNum (int): start val for range
        endNum (int): end val for range
    """
    for test in range(startNum, endNum):
        generate_compose(templateFilename, outputDir, test)


def generate_compose(templateFilename, outputDir, testNumber):
    """generates and writes to file a docker-compose for fuzz testing from template

    Args:
        templateFilename (str): template file for docker-compose generation
        outputDir (str): output directory for docker-compose outputs
        testNumber (int): current test number
    """
    with open(templateFilename, 'r') as ymlfile:
        try:
            docker_config = yaml.safe_load(ymlfile)
        except yaml.YAMLError as exc:
            print(exc)

    test_number = str(testNumber)  # ! current test iteration

    subnet = generate_subnet_string(testNumber)  # ! this iterations subnet

    epc_ip = generate_ip(testNumber, 1)  # ! 'ip 1'
    enb_ip = generate_ip(testNumber, 2)  # ! 'ip 2'

    output_folder = Path(outputDir)
    output_filename = output_folder / ("docker-compose_" + test_number +
                                       ".yml")

    docker_config['services']['srsue'][
        'command'] = 'stdbuf -oL srsue /etc/srsran/ue.conf.fauxrf -f' + test_number

    docker_config['services']['srsepc'][
        'command'] = 'stdbuf -oL srsepc /etc/srsran/epc.conf --mme.mme_bind_addr=' + epc_ip + ' --spgw.gtpu_bind_addr=' + epc_ip

    docker_config['services']['srsepc']['networks']['corenet'][
        'ipv4_address'] = epc_ip

    docker_config['services']['srsenb'][
        'command'] = 'srsenb /etc/srsran/enb.conf.fauxrf --enb.mme_addr=' + epc_ip + ' --enb.gtp_bind_addr=' + enb_ip + ' --enb.s1c_bind_addr=' + enb_ip

    docker_config['services']['srsenb']['volumes'][
        0] = './pcaps/' + test_number + ':/pcaps/'

    docker_config['services']['srsenb']['networks']['corenet'][
        'ipv4_address'] = enb_ip

    docker_config['networks']['corenet']['ipam']['config'][0][
        'subnet'] = subnet

    # container_name
    docker_config['services']['srsepc'][
        'container_name'] = 'virtual-srsepc' + test_number
    docker_config['services']['srsenb'][
        'container_name'] = 'virtual-srsenb' + test_number
    docker_config['services']['srsue'][
        'container_name'] = 'virtual-srsue' + test_number

    with open(output_filename, 'w') as newconf:
        yaml.dump(docker_config, newconf, default_flow_style=False)

    print("Generated Test# " + f"{testNumber:07d}" + " | Subnet: " + subnet)


def generate_subnet_string(iterationNum):
    """
    when given current iteration, generate a subnet range.
    each subnet is comprised of a /28 block, thus the last
    4 bits of the ip address are available, along with
    10.***.*** ranges, so 20 bits are available to us,
    and about 1mil subnets can be created

     Parameters:
        iterationNum (int): Current Test Number

    Returns:
        subnet_string (str): /28 subnet for current iteration
    """
    first = str(iterationNum >> 12)  # first 8 bits [0-7]
    second = str((iterationNum & 4080) >> 4)  # middle 8 bits [8 - 15]
    third = str(
        16 * (iterationNum & 15)
    )  # final 4 bits, multiplied by 16 to obtein this iterations subnet
    if iterationNum > 1048575:  # 20 bit max val
        print(
            "generate_subnet_string doesnt support more than 1mil iterations")
        quit(1)

    return "10." + first + "." + second + "." + third + "/28"


def generate_ip(iterationNum, ipNum):
    """
        generate a valid ip within this current iteration's
        subnet. /28 blocks allow for 15 ips maximum, thus ipNum
        cannot be above 15


     Parameters:
        iterationNum (int): Current Test Number
        ipNum (int): ip needed within block, valid values are 1 thru 15

    Returns:
        ip_address (str): ip within iterations subnet
    """

    if ipNum > 16:
        print("ipNum too large for a /28 subnet!")
        quit(1)
    first = str(iterationNum >> 12)  # first 8 bits [0-7]
    second = str((iterationNum & 4080) >> 4)  # middle 8 bits [8 - 15]
    # final 4 bits, multiplied by 16 to obtein this iterations subnet,
    # then added to ipNum to obtain a unique ip
    third = str((16 * (iterationNum & 15)) + ipNum)

    return "10." + first + "." + second + "." + third


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "./fuzztest_helper.py <start index> <end index> <template file> <output dir>"
        )
        quit(1)
    mass_generate_compose(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
                          sys.argv[4])
    print("Generated docker-composes [" + sys.argv[1] + ":" +
          str(int(sys.argv[2]) - 1) + "].")
