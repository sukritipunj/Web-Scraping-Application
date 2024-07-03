#### url : http://localhost:8080/

from flask import Flask, request, render_template
import aiohttp
import asyncio
import certifi
import ssl

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
async def index():
    data = None
    error = None

    if request.method == 'POST':
        api_key = request.form.get('api_key')
        api_url = request.form.get('api_url')
        params = request.form.get('params')
        page = request.form.get('page')
        
        if api_key and api_url:
            try:
                data = await fetch_data(api_key, api_url, params, page)
                if not data:
                    error = "No data found for the provided parameters."
            except Exception as e:
                error = f"Error fetching data: {e}"
        else:
            error = "API key and API URL are required."

    return render_template('index.html', data=data, error=error)

async def fetch_data(api_key, api_url, params, page):
    params_dict = {}
    if params:
        params_list = params.split('&')
        for param in params_list:
            key, value = param.split('=')
            params_dict[key] = value
    
    # Add the API key to the parameters if needed
    if 'appid' not in params_dict and 'api_key' not in params_dict:
        params_dict['api_key'] = api_key

    # Add pagination parameters if present
    if page:
        params_dict['page'] = page
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, params=params_dict, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.json()
            else:
                response_text = await response.text()
                raise Exception(f"Failed to fetch data: {response.status} {response_text}")

if __name__ == '__main__':
    app.run(debug=True, port=8080)
