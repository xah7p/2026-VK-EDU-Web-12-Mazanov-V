from urllib.parse import parse_qs

def application(environ, start_response):
    query_string = environ.get('QUERY_STRING', '')
    get_params = parse_qs(query_string)
    post_params = {}
    if environ.get('REQUEST_METHOD') == 'POST':
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        if content_length > 0:
            raw_body = environ['wsgi.input'].read(content_length).decode('utf-8')
            post_params = parse_qs(raw_body)
            
    response_text = f"GET параметры: {dict(get_params)}\nPOST параметры: {dict(post_params)}"
    print(response_text)
    
    response_bytes = response_text.encode('utf-8')
    status = '200 OK'
    headers = [
        ('Content-Type', 'text/plain; charset=utf-8'),
        ('Content-Length', str(len(response_bytes)))
    ]
    start_response(status, headers)
    return [response_bytes]