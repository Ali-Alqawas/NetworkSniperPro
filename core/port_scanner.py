"""
فحص المنافذ المفتوحة لجهاز محدد
"""
import subprocess
import re
import threading
from utils.logger import log
from utils.network import validate_ip
from config import DANGEROUS_PORTS, PORT_SCAN_LIST


class PortScanner:
    def __init__(self):
        self.process = None
        self.is_scanning = False

    def scan_ports(self, target_ip, on_complete=None, on_error=None):
        if not validate_ip(target_ip):
            if on_error:
                on_error("عنوان IP غير صالح!")
            return
        self.is_scanning = True
        thread = threading.Thread(
            target=self._run_port_scan, args=(target_ip, on_complete, on_error), daemon=True
        )
        thread.start()
        return thread

    def _run_port_scan(self, target_ip, on_complete, on_error):
        try:
            # -sT: TCP connect scan, -Pn: لا تتحقق من حياة الجهاز
            self.process = subprocess.Popen(
                ["sudo", "nmap", "-sT", "-Pn", "-p", PORT_SCAN_LIST,
                 "--host-timeout", "30s", target_ip],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            output, _ = self.process.communicate()

            if not self.is_scanning:
                return

            ports = self._parse_port_output(output)
            log.info(f"فحص منافذ {target_ip}: وجد {len([p for p in ports if p['state']=='open'])} منفذ مفتوح")

            if on_complete:
                on_complete(target_ip, ports)
        except Exception as e:
            log.error(f"خطأ في فحص المنافذ: {e}")
            if on_error:
                on_error(str(e))
        finally:
            self.is_scanning = False
            self.process = None

    def _parse_port_output(self, output):
        ports = []
        for line in output.split('\n'):
            match = re.match(r'(\d+)/(tcp|udp)\s+(open|closed|filtered)\s+(\S+)', line.strip())
            if not match:
                continue
            port_num = int(match.group(1))
            protocol = match.group(2)
            state = match.group(3)
            service = match.group(4)

            if port_num in DANGEROUS_PORTS:
                svc_name, risk_desc = DANGEROUS_PORTS[port_num]
                risk_level = "high" if "خطير" in risk_desc else ("medium" if "متوسط" in risk_desc else "low")
            else:
                svc_name = service
                risk_desc = "غير مصنف"
                risk_level = "unknown"

            ports.append({
                "port": port_num, "protocol": protocol, "state": state,
                "service": svc_name, "version": "",
                "risk": risk_desc, "risk_level": risk_level,
            })
        return ports

    def stop(self):
        self.is_scanning = False
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
            finally:
                self.process = None

    def cleanup(self):
        self.stop()
