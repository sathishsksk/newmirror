import re
import requests
from lxml import etree

url = "" # file url

XSRF_TOKEN = "eyJpdiI6InhaN3NDT3pqbHRsc3J1XC84cFd0YnJRPT0iLCJ2YWx1ZSI6Im1ra3BUQVwvOGVBZGt1YXFUdVdORXNTXC9mWkY0SnB4cFNCY3F5Unc4ak1nV3lIRGtCZ21WNVRYZXRWV2lVQnRCVCIsIm1hYyI6IjQzMzFhYTA2NjMxYjc1MzhmMGM0ZTkxYWViMmFmMGM5Y2JlM2M5MDNkNzExNmE1YTNjNTExZmUxN2NjMWQwYzgifQ%3D%3D" # XSRF-TOKEN cookie
laravel_session = "eyJpdiI6IlZBUzdqY05EdVwvWW5WalVOdnFNZFpBPT0iLCJ2YWx1ZSI6Ik9XcDQwcjVcLzB2QzdXM2hBVGgwYzI5aVhkbnp5amNWdkRyd2paZTFrYjBcLzNacHhCZWFTeXZTRHUzXC93Z3ZyQjgiLCJtYWMiOiIxYTk4ZTNlMTc3NzJhNzMxZmIxYTA5OWJiNzU0MmJiYzI2ZTI4MzA3OWMzMjY1ZDE2YzM4ZWRiZDczOGZkMjI1In0%3D" # laravel_session cookie

'''
404: Exception Handling Not Found :(

NOTE:
DO NOT use the logout button on website. Instead, clear the site cookies manually to log out.
If you use logout from website, cookies will become invalid.
'''

# ===================================================================

def parse_info(res):
    f = re.findall(">(.*?)<\/td>", res.text)
    info_parsed = {}
    for i in range(0, len(f), 3):
        info_parsed[f[i].lower().replace(' ', '_')] = f[i+2]
    return info_parsed

def sharer_pw_dl(url, forced_login=False):
    client = requests.Session()
    
    client.cookies.update({
        "XSRF-TOKEN": XSRF_TOKEN,
        "laravel_session": laravel_session
    })
    
    res = client.get(url)
    token = re.findall("_token\s=\s'(.*?)'", res.text, re.DOTALL)[0]
    
    ddl_btn = etree.HTML(res.content).xpath("//button[@id='btndirect']")

    info_parsed = parse_info(res)
    info_parsed['error'] = True
    info_parsed['src_url'] = url
    info_parsed['link_type'] = 'login' # direct/login
    info_parsed['forced_login'] = forced_login
    
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    data = {
        '_token': token
    }
    
    if len(ddl_btn):
        info_parsed['link_type'] = 'direct'
    if not forced_login:
        data['nl'] = 1
    
    try: 
        res = client.post(url+'/dl', headers=headers, data=data).json()
    except:
        return info_parsed
    
    if 'url' in res and res['url']:
        info_parsed['error'] = False
        info_parsed['gdrive_link'] = res['url']
    
    if len(ddl_btn) and not forced_login and not 'url' in info_parsed:
        # retry download via login
        return sharer_pw_dl(url, forced_login=True)
    
    return info_parsed

# ===================================================================

out = sharer_pw_dl(url)
print(out)

# ===================================================================

'''
SAMPLE OUTPUT:
{
    file_name: xxx, 
    type: video/x-matroska, 
    size: 880.6MB, 
    added_on: 2022-02-04, 
    error: False, 
    link_type: direct/login
    forced_login: False (True when script retries download via login if non-login dl fails for any reason)
    src_url: https://sharer.pw/file/xxxxxxxx, 
    gdrive_link: https://drive.google.com/...
}
'''
