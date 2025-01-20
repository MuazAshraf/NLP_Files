from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/callback'):
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            
            # Check for error parameters
            if 'error' in query_params:
                error = query_params['error'][0]
                error_description = query_params.get('error_description', ['Unknown error'])[0]
                print(f"Error: {error}")
                print(f"Error description: {error_description}")
                
                # Send error response to browser
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"Authorization failed: {error_description}".encode())
                return

            # Handle successful authorization
            code = query_params.get('code', [None])[0]
            if code:
                print(f"Authorization code: {code}")
            else:
                print("No authorization code received.")
            
            # Send a response back to the browser
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Authorization code received! Check the console for the code.')
        else:
            # Return a 404 error if the path doesn't match '/callback'
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
