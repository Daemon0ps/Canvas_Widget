# Canvas_Widget
<h3 align="center">Desktop Canvas Widget - Homework / Calendar Events</h3>
<div align="center">
  <a href="https://github.com/Daemon0ps/Canvas_Widget">
    <img src="https://github.com/Daemon0ps/Canvas_Widget/blob/main/Canvas_Widget.jpg" alt="Logo" width="342" height="544">
  </a>

<div align="left">

### Prerequisites

*  Get an API key by logging into your student's Canvas account, go to Profile, and generate an API key.
*  Find out the Endpoint for Canvas/Instructure.
      The Endpoint should be something like:
       _**https://www.schoolname.instructure.com/api/v1/**_
*  Install Python 3.10+ https://www.python.org/downloads/
*  Or, alternatively, install MiniConda https://docs.conda.io/projects/miniconda/en/latest/


### Installation

1. Set up the python environment
2. Clone this repository
  ```sh
  git clone https://github.com/Daemon0ps/Canvas_Widget
  ```
2.  Set up the python environment
```sh
python -m venv Canvas_Widget
  ```
3.  Change Directories
```sh
cd Canvas_Widget
```
4.  Activate the environment
```sh
Scripts\activate.bat
```
5. Install required modules
```sh
pip install -r requirements.txt
```
6. Run program **or** create a Windows EXE
```sh
python Canvas_Widget.py
```
  * https://www.pysimplegui.org/en/latest/#creating-a-windows-exe-file
```sh
pyinstaller -wF Canvas_Widget.py
```
```sh
dist\Canvas_Widget.exe
```

**Manual Module Installations**
1.  Install PySimpleGUI - [https://pypi.org/project/PySimpleGUI/](https://pypi.org/project/PySimpleGUI/)
2.  Install PyInstaller - [https://pypi.org/project/pyinstaller/](https://pypi.org/project/pyinstaller/)
3.  Install Requests - [https://pypi.org/project/pyinstaller/](https://pypi.org/project/requests/)
4.  Install Keyring - [https://pypi.org/project/pyinstaller/](https://pypi.org/project/keyring/)
5.  Install Dateutil - [https://pypi.org/project/python-dateutil/](https://pypi.org/project/python-dateutil/)
6.  Command:
```sh
pip install PySimpleGUI pyinstaller requests keyring python-dateutil
```


### Usage
1. On first use, the program will ask you for the API Key, and the endpoint.
   * For the endpoint, make sure it ends with a forward slash "/" eg:  _**https://www.schoolname.instructure.com/api/v1/**_
2. ![image](https://github.com/Daemon0ps/Canvas_Widget/assets/133270668/95423a6d-fa01-4c3c-a356-232e628f41b1)
3. The API Key/Token, and Endpoint are saved as Windows Credentials.
* If you have Windows 11, you can access the Credential Manager with this command:
```sh
%SystemRoot%\explorer.exe "shell:::{1206F5F1-0569-412C-8FEC-3204630DFB70}"
```
4. The script will check the endpoint and API token.
5. If you see a pop-up that says "SUCESS  (OK)", then validation of the API Key and Endpoint were successful.




### Linux/WSL2 - Use at your own risk.
* If you want to run under WSL2, and want to run it under headless:
```sh
sudo apt install gnome-keyring
dbus-run-session -- sh
echo 'the_secret_password_is_squeemish_ossifrage' | gnome-keyring-daemon --unlock
python -c "import keyring; keyring.set_password('canvas', 'api_token', 'APITOKENAPITOKENAPITOKENAPITOKEN'); keyring.get_password('canvas', 'endpoint', 'https://myendpointname.instructure.com/api/v1/')"
```
* daemonized with screen, etc., if you know what youn are doing
```sh
screen -dmS canvas_widget bash -c 'dbus-run-session -- /bin/bash -c 'echo 'dbus shell'; dd if=/etc/kr/.keyring_pw | gnome-keyring-daemon --unlock; echo 'keyring unlocked; /home/0x0C/miniconda3/envs/Canvas_Widget/bin/python /home/0x0C/Canvas_Widget/Canvas_Widget.py'
```



</div>
