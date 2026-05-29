import subprocess
import os

xml_content = """<service>
  <id>AiAnyCamBackend</id>
  <name>AI Any Camera Backend</name>
  <description>AI Any Camera FastAPI Backend</description>
  <executable>C:\\Users\\medarius\\AppData\\Local\\Programs\\Python\\Python312\\python.exe</executable>
  <arguments>-m uvicorn main:app --host 0.0.0.0 --port 8080</arguments>
  <workingdirectory>C:\\aianycam\\backend</workingdirectory>
  <onfailure action="restart" delay="5 sec"/>
  <onfailure action="restart" delay="10 sec"/>
  <onfailure action="restart" delay="20 sec"/>
  <logmode>rotate</logmode>
  <logpath>C:\\aianycam\\logs</logpath>
</service>"""

os.makedirs("C:\\aianycam\\logs", exist_ok=True)

with open("C:\\aianycam\\aianycam-backend.xml", "w") as f:
    f.write(xml_content)
print("XML created")

# Install service
result = subprocess.run(
    ["C:\\aianycam\\aianycam-backend.exe", "install"],
    capture_output=True, text=True
)
print("Install stdout:", result.stdout)
print("Install stderr:", result.stderr)
print("Return code:", result.returncode)
