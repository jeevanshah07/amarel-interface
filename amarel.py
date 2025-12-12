import paramiko
import time
import sqlite3
import re

output_file = "paramiko.org"


class Amarel:
    def __init__(self, net_id: str, password: str):
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

    def check_status(self, job_name: str) -> list:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect("amarel.hpc.rutgers.edu", 22, self.net_id, self.password)

        cmd = f"cd /scratch/$USER && ls | grep {job_name}"

        res = self.run(client, cmd)
        print(res == "")

        if res == "":
            return []

        out = self.run(client, f"cd /scratch/$USER && cat {job_name}.out")
        return out.splitlines()

    def authenticate(self) -> bool:
        if self.net_id == "" or self.password == "":
            return False

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect("amarel.hpc.rutgers.edu", 22, self.net_id, self.password)
            client.close()
            return True
        except Exception:
            return False

    def create_table(self) -> bool:

        create_table = f"""CREATE TABLE IF NOT EXISTS {self.net_id} (
            job_name text PRIMARY KEY,
            status text
        );"""

        try:
            with sqlite3.connect("amarel.db") as conn:
                cursor = conn.cursor()
                cursor.execute(create_table)
                conn.commit()

                return True
        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)
            return False

    def write_job(self, job_name: str, status: str) -> bool:
        if job_name == "":
            return False

        insert_str = f"""INSERT INTO {self.net_id}(job_name, status)
        VALUES("{job_name}", "{status}")"""

        try:
            with sqlite3.connect("amarel.db") as conn:
                cursor = conn.cursor()
                cursor.execute(insert_str)
                conn.commit()
                return True
        except sqlite3.OperationalError as e:
            print("Failed to write data: ", e)
            return False

    def get_jobs(self) -> list[dict]:
        try:
            with sqlite3.connect("amarel.db") as conn:
                res = []
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {self.net_id}")
                rows = cursor.fetchall()

                for row in rows:
                    row_dict = {"name": row[0], "status": row[1]}
                    res.append(row_dict)

                return res
        except sqlite3.OperationalError as e:
            return []

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

        return out[-1]

    def rewrite(self, partition, filename, nodes, tasks, cpus, mem, time):
        with open("job.sh", "r") as f:
            template = f.read()

        replacements = {
            "{{ partition }}": str(partition),
            "{{ filename }}": str(filename),
            "{{ nodes }}": str(nodes),
            "{{ tasks }}": str(tasks),
            "{{ cpus }}": str(cpus),
            "{{ mem }}": str(mem),
            "{{ time }}": str(time),
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        return result

    def run_file(self, file, filename, nodes, tasks, cores, mem, runtime, partition):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect("amarel.hpc.rutgers.edu", 22, self.net_id, self.password)

        time.sleep(1)

        sftp = client.open_sftp()
        remote_path = f"/scratch/{self.net_id}/{filename}.py"
        remote_script_path = f"/scratch/{self.net_id}/main.sh"
        remote_build_pipfile_path = f"/scratch/{self.net_id}/build_pipfile.py"
        remote_job_path = f"/scratch/{self.net_id}/job.sh"

        with sftp.file(remote_path, "wb") as f:
            f.write(file.read())

        with sftp.file(remote_script_path, "wb") as f:
            lines = []
            with open("main.sh", "rb") as s:
                lines = s.readlines()

            f.writelines(lines)

        with sftp.file(remote_job_path, "wb") as f:
            f.write(
                self.rewrite(partition, filename, nodes, tasks, cores, mem, runtime)
            )

        with sftp.file(remote_build_pipfile_path, "wb") as f:
            lines = []
            with open("build-pipfile.py", "rb") as s:
                lines = s.readlines()

            f.writelines(lines)

        return self.run(
            client,
            f"cd /scratch/{self.net_id} && chmod u+x job.sh && sbatch job.sh",
        )

    def run(self, client, command: str):
        (_, stdout, _) = client.exec_command(command)

        cmd_output = stdout.read().decode()
        print(f"Command: {command} \n Output: {cmd_output} \n")

        return cmd_output
