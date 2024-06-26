import json
from datetime import datetime
from pytz import timezone, all_timezones, utc
from wsgiref.simple_server import make_server

def application(environ, start_response):
    path = environ.get('PATH_INFO', '')
    method = environ.get('REQUEST_METHOD', 'GET')
    
    if path.startswith('/api/v1/convert') and method == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            date_str = data['date']['date']
            tz_from = data['date']['tz']
            tz_to = data['target_tz']
            
            #Converting string to datetime
            dt = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
            from_zone = timezone(tz_from)
            to_zone = timezone(tz_to)
     
            dt = from_zone.localize(dt)
            converted_dt = dt.astimezone(to_zone)
            
            #JSON responce
            response = json.dumps({'converted_date': converted_dt.strftime('%m.%d.%Y %H:%M:%S')})
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [response.encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]
    
    elif path.startswith('/api/v1/datediff') and method == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            first_date_str = data['first_date']
            first_tz = data['first_tz']
            second_date_str = data['second_date']
            second_tz = data['second_tz']
            
            #From string to datetime
            first_dt = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
            second_dt = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
            
            first_zone = timezone(first_tz)
            second_zone = timezone(second_tz)
            
            first_dt = first_zone.localize(first_dt)
            second_dt = second_zone.localize(second_dt)
            
            diff_seconds = int((second_dt - first_dt).total_seconds())
            
            response = json.dumps({'difference_seconds': diff_seconds})
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [response.encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'application/json')])
            return [json.dumps({'error': str(e)}).encode('utf-8')]
    
    elif path.startswith('/'):
        #Getting timezone name
        tz_name = path[1:] if len(path) > 1 else 'GMT'
        if tz_name not in all_timezones:
            tz_name = 'GMT'
        
        #Getting current time in requested timezone
        current_time = datetime.now(timezone(tz_name))
        response = f"<html><body><h1>Current time in {tz_name} is {current_time.strftime('%Y-%m-%d %H:%M:%S')}</h1></body></html>"
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response.encode('utf-8')]
    
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']
    
    #Starting server
if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()

