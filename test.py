import unittest
import json
from datetime import datetime
from io import BytesIO
from app import application

class TestWSGIApp(unittest.TestCase):
    def setUp(self):
        self.environ = {}
        self.start_response = self._start_response
    
    def _start_response(self, status, headers):
        self.status = status
        self.headers = headers

    def test_get_current_time_gmt(self):
        #Getting time in GMT
        self.environ['PATH_INFO'] = '/'
        self.environ['REQUEST_METHOD'] = 'GET'
        
        result = application(self.environ, self.start_response)
        self.assertEqual(self.status, '200 OK')
        self.assertIn(b'Current time in GMT', result[0])

    def test_get_current_time_specific_tz(self):
        #Getting time in in required timezone
        self.environ['PATH_INFO'] = '/Europe/Moscow'
        self.environ['REQUEST_METHOD'] = 'GET'
        
        result = application(self.environ, self.start_response)
        self.assertEqual(self.status, '200 OK')
        self.assertIn(b'Current time in Europe/Moscow', result[0])
    
    def test_convert_time(self):
        #Converting time to equal format 
        self.environ['PATH_INFO'] = '/api/v1/convert'
        self.environ['REQUEST_METHOD'] = 'POST'
        self.environ['CONTENT_LENGTH'] = '100'
        self.environ['wsgi.input'] = BytesIO(json.dumps({
            'date': {'date': '12.20.2021 22:21:05', 'tz': 'EST'},
            'target_tz': 'Europe/Moscow'
        }).encode('utf-8'))
        
        result = application(self.environ, self.start_response)
        self.assertEqual(self.status, '200 OK')
        response_data = json.loads(result[0])
        self.assertIn('converted_date', response_data)
    
    def test_datediff(self):
        #Getting difference
        self.environ['PATH_INFO'] = '/api/v1/datediff'
        self.environ['REQUEST_METHOD'] = 'POST'
        self.environ['CONTENT_LENGTH'] = '200'
        self.environ['wsgi.input'] = BytesIO(json.dumps({
            'first_date': '12.06.2024 22:21:05',
            'first_tz': 'EST',
            'second_date': '12:30pm 2024-02-01',
            'second_tz': 'Europe/Moscow'
        }).encode('utf-8'))
        
        result = application(self.environ, self.start_response)
        self.assertEqual(self.status, '200 OK')
        response_data = json.loads(result[0])
        self.assertIn('difference_seconds', response_data)
    
    def test_invalid_convert_time(self):
        #Filtering invalid time convertion
        self.environ['PATH_INFO'] = '/api/v1/convert'
        self.environ['REQUEST_METHOD'] = 'POST'
        self.environ['CONTENT_LENGTH'] = '50'
        self.environ['wsgi.input'] = BytesIO(json.dumps({
            'date': {'date': 'invalid date', 'tz': 'EST'},
            'target_tz': 'Europe/Moscow'
        }).encode('utf-8'))
        
        result = application(self.environ, self.start_response)
        self.assertEqual(self.status, '400 Bad Request')
        response_data = json.loads(result[0])
        self.assertIn('error', response_data)
    
    def test_invalid_datediff(self):
        #Filtering invalid difference calculation 
        self.environ['PATH_INFO'] = '/api/v1/datediff'
        self.environ['REQUEST_METHOD'] = 'POST'
        self.environ['CONTENT_LENGTH'] = '50'
        self.environ['wsgi.input'] = BytesIO(json.dumps({
            'first_date': 'invalid date',
            'first_tz': 'EST',
            'second_date': '12:30pm 2024-02-01',
            'second_tz': 'Europe/Moscow'
        }).encode('utf-8'))
        
        result = application(self.environ, self.start_response)
        self.assertEqual(self.status, '400 Bad Request')
        response_data = json.loads(result[0])
        self.assertIn('error', response_data)

if __name__ == '__main__':
    unittest.main()
