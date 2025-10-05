# Copyright 2024 Snowflake Inc. 
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit_okta.utils import string_utils
from streamlit.components.v1 import html
from streamlit_okta.components import onunload_component, oauth_component
from streamlit_okta.auth.okta import Okta
import time
import logging
import requests
import asyncio


def validate_access_token(okta, access_token):
    """
    Validates the access token using Okta's introspect endpoint.
    """
    OKTA_INTROSPECT_ENDPOINT = f"{okta.okta_base_url}/introspect"

    data = {
        "token": access_token,
        "token_type_hint": "access_token",
    }

    response = requests.post(url=OKTA_INTROSPECT_ENDPOINT, data=data, headers=okta.headers)

    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("active"):
            return True
        else:
            st.warning("Access token is invalid or expired.")
            return False
    else:
        st.error("Failed to validate access token.")
        return False


async def app(okta, tokens, callback):
    # Removed the incorrect usage of `st.query_params(**{})`.
    # Streamlit does not currently support clearing query parameters directly with `st.query_params`.
    oauth_component(event='REMOVE_STATE')

    decoded_token = okta.get_user_context()

    # expiry epoch time in UTC
    exp_time = float(decoded_token['exp'])

    # current epoch time in UTC
    current_time = time.time()

    diff = (exp_time - current_time)
    if diff < 0:
        okta.verify_tokens_from_okta(
            access_token=tokens['access_token'], refresh_token=tokens['refresh_token'])

    # Use the existing `verify_tokens_from_okta` method from `okta.py` to validate the access token.
    #st.info(okta.verify_tokens_from_okta(access_token=tokens['access_token'], refresh_token=tokens['refresh_token']))

    
    

    # Browser / Tab Close Event
    st.button("revoke", on_click=okta.invalidate_token_from_okta,
              kwargs=st.session_state['token'])
    oauth_component(event='HIDE_REVOKE_BUTTON')

    # Check if the callback is asynchronous and await it if necessary.
    if asyncio.iscoroutinefunction(callback):
        await callback()
    else:
        callback()

    # Hide empty blocks
    hide_empty_blocks_html = '''<script>
            const iframeElements = window.parent.document.getElementsByTagName('iframe');

            Array.from(iframeElements)
            .filter(item=>item.title==='st.iframe')
            .forEach(item=>item.parentElement.style.display="none");

            Array.from(iframeElements)
            .filter(item=>item.title==='streamlit_okta.components.oauth_component')
            .forEach(item=>item.parentElement.style.display="none");

            const markdownElement = window.parent.document.getElementsByClassName('stMarkdown');
            Array.from(markdownElement)
            .forEach(item=>item.parentElement.style.display="block");
        </script>
        '''
    html(hide_empty_blocks_html, height=0)


async def okta_login_wrapper(config, callback):
    okta = Okta(config)

    onunload_component()
    if 'token' not in st.session_state:
        local_storage = oauth_component(event='GET_LOCAL_STORAGE')
        if local_storage:
            if 'error' in st.query_params:
                st.warning(st.query_params['error_description'][0])
                st.stop()

            if "code" in st.query_params and "state" in st.query_params:
                st.info('Please Wait...')
                authorization_code = st.query_params["code"]

                authorization_state = st.query_params["state"]


                if 'state' in local_storage and authorization_state == local_storage['state']:
                    tokens = okta.get_tokens_from_okta(authorization_code)

                    print('Login Successful!', tokens)


                    st.session_state['token'] = tokens

                

                    st.rerun()
                else:
                    st.warning(
                        "Something wrong. Please try to login again..")
                    st.stop()
            else:
                state = string_utils.generate_random_cryptographic_string()
                oauth_component(event='SET_STATE', params={'state': state})
                okta.login_with_okta_component(state)
                st.stop()
    else:
        logging.debug('User logged in successfully!')
        await app(okta, st.session_state['token'], callback)
