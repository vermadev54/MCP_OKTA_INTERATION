Copyright 2025 jainendra
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

# Streamlit Okta OAuth2.0 Authorization Code Flow 
This is an okta authentication wrapper library to implement oauth2.0 authentication & authorization in your streamlit application.

## Pre-requisites
- create uv enviroment with : uv venv
- activate env source .venv/bin/activate
- install uv pip install -r requirements.txt
- Install node + npm, to build the _custom component_
- Build the _custom component_
 ```
cd streamlit_okta/components/oauth
npm install 
npm run build
```
- Register Client Application in your Okta
    Before you can implement authorization, you need to register your app in Okta by creating an app integration from the Admin Console.
    - In the Admin Console, go to Applications > Applications.
    - Click Create App Integration.
    - Select OIDC - OpenID Connect as the Sign-in method.
    - Select Web Application as the Application type, then click Next.
    - Specify the App integration name.
    - Specify the Sign-in redirect URIs to redirect the user with their authorization code.
    - Fill in the remaining details for your app integration, then click Save.
    
    From the General tab of your app integration, save the generated Client ID and Client secret values to implement your authorization flow.


## Getting started
- Clone the repository
```
git clone <git_repo_url>
```
- Move _streamlit_okta_ folder to your project directory
- Import _okta_login_wrapper_ function into your code
```python
from streamlit_okta import okta_login_wrapper

okta_config = {
            provider_url=https://integrator-dhgdgd.okta.com/oauth2/default/.well-known/openid-configuration
            client_id=""
            client_serret=""
            base_url=https://integrator-dhgdgd.okta.com/oauth2/default/v1
            redirect_uri=http://localhost:7001
            mcpclient_url=http://localhost:7001
            mcpserver_url=http://localhost:8080
}


## running mcp server and client

1. run mcpserver: fastmcp run mcpserver.py:mcp --transport http --port 8080 --host 0.0.0.0
2. run mcp client: streamlit run mcpclient.py --server.port 7001

