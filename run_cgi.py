from http.server import CGIHTTPRequestHandler, ThreadingHTTPServer
import os


class SimpleCGI(CGIHTTPRequestHandler):
    cgi_directories = ["/cgi-bin"]
    have_python = True

    def is_python(self, path):
        return path.lower().endswith(".cgi")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = ThreadingHTTPServer(("localhost", 8000), SimpleCGI)
    print("Serving at http://localhost:8000/cgi-bin/main.cgi")
    server.serve_forever()