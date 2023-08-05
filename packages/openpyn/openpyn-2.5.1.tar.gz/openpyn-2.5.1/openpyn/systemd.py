import subprocess

from openpyn import __basefilepath__


def install_service():
    openpyn_options = input("Enter Openpyn options to be stored in systemd \
service file (/etc/systemd/system/openpyn.service, \
Default(Just Press Enter) is, uk : ") or "uk"
    update_service(openpyn_options)


def update_service(openpyn_options, run=False):
    if "-f" in openpyn_options or "--force-fw-rules" in openpyn_options:
        kill_option = " --kill-flush"
    else:
        kill_option = " --kill"
    openpyn_options = openpyn_options.replace("-d ", "")
    openpyn_options = openpyn_options.replace("--daemon", "")
    openpyn_location = str(subprocess.check_output(["which", "openpyn"]))[2:-3]
    sleep_location = str(subprocess.check_output(["which", "sleep"]))[2:-3]

    service_text = "[Unit]\nDescription=NordVPN connection manager\nWants=network-online.target\n" + \
        "After=network-online.target\nAfter=multi-user.target\n[Service]\nType=simple\nUser=root\n" + \
        "WorkingDirectory=" + __basefilepath__ + "\nExecStartPre=" + sleep_location + " 5\nExecStart=" + \
        openpyn_location + " " + openpyn_options + "\nExecStop=" + openpyn_location + kill_option + \
        "\nStandardOutput=syslog\nStandardError=syslog\n[Install]\nWantedBy=multi-user.target\n"

    with open("/etc/systemd/system/openpyn.service", "w+") as service_file:
        service_file.write(service_text)
        service_file.close()

    print("\nThe Following config has been saved in openpyn.service.",
          "You can Run it or/and Enable it with: 'sudo systemctl start openpyn',",
          "'sudo systemctl enable openpyn' \n\n", service_text)

    subprocess.run(["systemctl", "daemon-reload"])
    if run:
        print("Started Openpyn by running 'systemctl start openpyn'\n\
To check VPN status, run 'systemctl status openpyn'")
        subprocess.Popen(["systemctl", "start", "openpyn"])
