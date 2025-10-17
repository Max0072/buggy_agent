# pip install docker
import docker, tempfile, os, shutil
from typing import TypedDict, List, Any

class DockerCodeRunner:
    def __init__(self, image="python:3.11-slim"):
        self.client = docker.from_env()
        self.image = image

    def run(self, req):
        workdir = tempfile.mkdtemp(prefix="agent-run-")
        try:
            for name, content in (req.get("files") or {}).items():
                path = os.path.join(workdir, name)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

            entry = {
                "python": ("main.py", "python", ["main.py"]),
                "node":   ("main.mjs", "node",   ["main.mjs"]),
                "bash":   ("run.sh",  "bash",   ["run.sh"]),
            }[req["language"]]
            main_name, cmd_exec, base_args = entry

            with open(os.path.join(workdir, main_name), "w", encoding="utf-8") as f:
                f.write(req["code"])
            command = [cmd_exec] + base_args + (req.get("args") or [])

            mem = f'{req.get("memory_mb", 512)}m'
            cpus = str(req.get("cpu_limit", 1))
            timeout = int(req.get("timeout_sec", 15))

            container = self.client.containers.run(
                self.image,
                command=command,
                working_dir="/workspace",
                user="1000:1000",
                network_disabled=True,
                mem_limit=mem,
                cpuset_cpus="0",
                cpu_period=100000,
                cpu_quota=int(100000*float(cpus)),
                security_opt=["no-new-privileges"],
                read_only=True,
                detach=True,
                volumes={
                    workdir: {"bind": "/workspace", "mode": "rw"}
                }
            )
            exit_code = container.wait(timeout=timeout)["StatusCode"]
            logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
            container.remove(force=True)

            stdout, stderr = logs, ""
            produced = []
            for root, _, files in os.walk(workdir):
                for name in files:
                    rel = os.path.relpath(os.path.join(root, name), workdir)
                    produced.append(rel)

            return {
                "stdout": stdout[:100000],
                "stderr": stderr[:100000],
                "exit_code": exit_code,
                "files": produced
            }
        except Exception as e:
            return {"stdout":"", "stderr": str(e), "exit_code": 1}
        finally:
            shutil.rmtree(workdir, ignore_errors=True)