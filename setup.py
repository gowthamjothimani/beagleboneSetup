import subprocess
import pexpect
import os

def run_command(command, password=None):
    try:
        if password:
            child = pexpect.spawn(command)
            child.expect('password')
            child.sendline(password)
            child.expect(pexpect.EOF)
            print(f"Command '{command}' executed successfully. Output:\n{child.before.decode('utf-8')}")
        else:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print(f"Command '{command}' executed successfully. Output:\n{result.stdout}")
    except (pexpect.ExceptionPexpect, subprocess.CalledProcessError) as e:
        print(f"Command '{command}' failed. Error:\n{str(e)}")

def update_and_upgrade(password):
    run_command("sudo apt update", password)
    run_command("sudo apt upgrade -y", password)

def configure_network(ip_address, gateway, dns, password):
    network_config = f"""
[Match]
Name=eth0
Type=ether

[Link]
RequiredForOnline=yes

[Network]
Address={ip_address}/24
Gateway={gateway}
DNS={dns}
"""
    with open('/tmp/eth0.network', 'w') as file:
        file.write(network_config)
    run_command(f"sudo cp /tmp/eth0.network /etc/systemd/network/eth0.network", password)

def configure_uenv(password):
    uenv_config = """
enable_uboot_overlays=1
# UART 1
uboot_overlay_addr0=/lib/firmware/BB-UART1-00A0.dtbo
# UART 2
uboot_overlay_addr1=/lib/firmware/BB-UART2-00A0.dtbo
# UART 4
uboot_overlay_addr2=/lib/firmware/BB-UART4-00A0.dtbo
# UART 5
uboot_overlay_addr3=/lib/firmware/BB-UART5-00A0.dtbo
# UART 3 (only TX). Note that in "uboot_overlay_addrX", the X need not be = UART id
uboot_overlay_addr4=/lib/firmware/BB-UART3-00A0.dtbo
"""
    with open('/tmp/uEnv.txt', 'w') as file:
        file.write(uenv_config)
    run_command(f"sudo sh -c 'cat /tmp/uEnv.txt >> /boot/uEnv.txt'", password)

def configure_gas_service(password):
    gas_service_config = """
[Unit]
Description=Gas Service

[Service]
ExecStart=/usr/bin/python3 /home/debian/emc04/main.py
Type=simple
User=root

[Install]
WantedBy=multi-user.target
"""
    with open('/tmp/gas.service', 'w') as file:
        file.write(gas_service_config)
    run_command(f"sudo cp /tmp/gas.service /lib/systemd/system/gas.service", password)

def git_clone_repo(password):
    repo_url = "https://surajpartani-ATG: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@github.com/surajpartani-ATG/emc04.git"
    run_command(f"git clone {repo_url}", password)

def install_requirements(password):
    run_command("sudo pip3 install -r requirements.txt", password)

def enable_and_start_service(service_name, password):
    run_command(f"sudo systemctl enable {service_name}", password)
    run_command(f"sudo systemctl start {service_name}", password)
    run_command(f"sudo systemctl status {service_name}", password)

def main():
    password = input("Enter your sudo password: ")

    # Set 1: Update and Upgrade
    update_and_upgrade(password)

    # Set 2: Configure Network
    ip_address = input("Enter the IP address: ")
    gateway = input("Enter the gateway address: ")
    dns = input("Enter the DNS address: ")
    configure_network(ip_address, gateway, dns, password)

    # Set 3: Configure uEnv.txt
    configure_uenv(password)

    # Set 4: Configure Gas Service
    configure_gas_service(password)

    # Set 5: Enable and Start Gas Service
    # enable_and_start_service("gas", password)

    # Set 6: Git Clone and Change Directory
    git_clone_repo(password)
    os.chdir('emc04')

    # Set 7: Install Requirements
    install_requirements(password)

    # Set 8: Enable and Start Gas Service Again
    enable_and_start_service("gas", password)

    # Set 9: Reboot
    run_command("sudo reboot", password)

    # Set 10: Run Main Python Script
    run_command("python main.py")

if __name__ == "__main__":
    main()
