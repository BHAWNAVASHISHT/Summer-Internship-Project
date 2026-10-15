import base64, os
def get_logo_data_uri():
    p = os.path.join(os.path.dirname(__file__), 'dp_logo.png')
    if os.path.exists(p):
        with open(p, 'rb') as f:
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')
    return ''
