Logging Module for Azure Log Analytics


#### Install
- add to your requirements.txt: `git+ssh://walmart@vs-ssh.visualstudio.com:22/Post%20Payment%20Audit%20Email%20Classification/_ssh/aiohttp_azure_logging`
- Build your container with valid ssh credentials

#### Implement
```
from aiohttp_azure_logging import send_to_azure

app = web.application()
settings = {
	'workspace_id': '<YOUR WORKSPACE ID>',
	'workspace_secret' '<YOUR WORKSPACE PRIMARY OR SECONDARY KEY>'
}
send_to_azure(app, settings)
```