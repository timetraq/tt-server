"""
Static Server implementation
"""

import cherrypy


class StaticServer(object):
    """
    Simple Static call-up
    """

    @staticmethod
    @cherrypy.expose
    def index():
        """
        Redirect to static page

        :return: Redirect to index web page
        """
        response = cherrypy.response
        response.headers['Location'] = 'static/index.html'
        response.status = 302
        return ['Moved Temporarily']
