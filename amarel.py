import paramiko
import time

output_file = "paramiko.org"


class Amarel:
    def __init__(self, net_id, password):
        self.net_id: str = net_id
        self.password: str = password

    def get_net_id(self) -> str:
        return self.net_id

    def get_password(self) -> str:
        return self.password

    def set_net_id(self, net_id) -> str:
        self.net_id = net_id
        return self.net_id

    def set_password(self, password) -> str:
        self.password = password
        return self.password

    def run_many(self, client, commands):
        out = []
        shell = client.invoke_shell()
        time.sleep(0.5)

        # clear login banner
        while shell.recv_ready():
            shell.recv(10000)

        for command in commands:
            shell.send((command + "\n").encode())

            # wait until *some* output arrives
            while not shell.recv_ready():
                time.sleep(0.1)

            # collect everything currently available
            chunk = shell.recv(100000).decode()
            print(chunk)
            out.append(chunk)

        print("--------")
        print(out)
        print("--------")

        return out[-1]

    def run_file(self, file, filename):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect("amarel.hpc.rutgers.edu", 22, self.net_id, self.password)

        time.sleep(1)

        sftp = client.open_sftp()
        remote_path = f"/scratch/{self.net_id}/{filename}"
        remote_script_path = f"/scratch/{self.net_id}/main.sh"
        remote_build_pipfile_path = f"/scratch/{self.net_id}/build_pipfile.py"

        with sftp.file(remote_path, "wb") as f:
            f.write(file.read())

        with sftp.file(remote_script_path, "wb") as f:
            lines = []
            with open("main.sh", "rb") as s:
                lines = s.readlines()

            f.writelines(lines)

        with sftp.file(remote_build_pipfile_path, "wb") as f:
            lines = []
            with open("build-pipfile.py", "rb") as s:
                lines = s.readlines()

            f.writelines(lines)

        return self.run(
            client,
            f"cd /scratch/{self.net_id} && chmod u+x main.sh && ./main.sh {filename}",
        )

    def run(self, client, command: str):
        (_, stdout, _) = client.exec_command(command)

        cmd_output = stdout.read().decode()
        print(f"Command: {command} \n Output: {cmd_output} \n")

        return cmd_output
