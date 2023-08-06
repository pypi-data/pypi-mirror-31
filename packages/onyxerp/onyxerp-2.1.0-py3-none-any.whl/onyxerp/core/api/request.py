"""
Created on 4 de jan de 2017

@author: rinzler
"""
import json

import requests
from builtins import BaseException

from rinzler import Rinzler

from onyxerp.core.api.response import Response


class Request(object):
    """
    Classe responsável pela abstração das requisições api
    """

    method = str()
    base_url = str()
    jwt = None
    jwt_data = dict()
    payload = dict()
    headers = dict()
    app: Rinzler = None

    # classes auxiliares
    response = None

    def __init__(self, app: Rinzler, base_url="http://localhost"):
        """
        Constructor
        """
        # setting some vales
        self.set_base_uri(base_url)
        self.app = app

    def get(self, end_point='/') -> Response:
        """
        Envia uma requisição do tipo GET de acordo com as configurações setadas
        :param end_point: str
        :return: Response
        """
        self.__set_method("GET")
        return self.__request(end_point)

    def post(self, end_point='/') -> Response:
        """
        Envia uma requisição do tipo POST de acordo com as configurações setadas
        :param end_point: str
        :return: Response
        """
        self.__set_method("POST")
        return self.__request(end_point)

    def put(self, end_point='/') -> Response:
        """
        Envia uma requisição do tipo PUT de acordo com as configurações setadas
        :param end_point: str
        :return: Response
        """
        self.__set_method("PUT")
        return self.__request(end_point)

    def patch(self, end_point='/') -> Response:
        """
        Envia uma requisição do tipo PATCH de acordo com as configurações setadas
        :param end_point: str
        :return: Response
        """
        self.__set_method("PATCH")
        return self.__request(end_point)

    def delete(self, end_point='/') -> Response:
        """
        Envia uma requisição do tipo DELETE de acordo com as configurações setadas
        :param end_point: str
        :return: Response
        """
        self.__set_method("DELETE")
        return self.__request(end_point)

    def __request(self, end_point) -> Response:
        """
        executa a requisição montada
        :rtype: Response
        """
        # final url
        url = self.get_base_uri() + end_point

        # configuration
        conf = self.config()

        try:
            method = self.get_method()
            self.app.log.info("<< External request {0} {1}".format(method, url))
            if method == 'GET':
                request = requests.get(url, headers=conf['headers'])
            elif method == 'POST':
                request = requests.post(url, headers=conf['headers'], data=conf['payload'])
            elif method == 'PATCH':
                request = requests.patch(url, headers=conf['headers'], data=conf['payload'])
            elif method == 'DELETE':
                request = requests.delete(url, headers=conf['headers'], data=conf['payload'])
            else:
                request = requests.put(url, data=conf['payload'], headers=conf['headers'])

            self.app.log.info(">> External request {0}".format(request.status_code))

            # Response object
            response = Response(self.app)

            # Set Response properies
            response.set_content(request.text)
            response.set_status_code(request.status_code)
            response.set_headers(request.headers)

            # return Response() Object
            return response
        except BaseException as e:
            self.app.log.error(str(e), exc_info=True)
            return Response(self.app).set_status_code(0)

    def config(self):
        """
        monta a configuração da request
        @return: dict
        """
        conf = dict()
        headers = self.get_headers()
        payload = self.get_payload()
        jwt = self.get_jwt()

        # Inicializando...
        conf['headers'] = dict()
        conf['payload'] = dict()

        if len(headers) > 0:
            conf['headers'] = headers

        if jwt is not None:
            conf['headers']['Authorization'] = 'Bearer ' + jwt

        if self.method != 'GET' and self.method != 'HEAD':
            conf['payload'] = json.dumps(payload)

        return conf

    def get_response_decode(self):
        """

        :return:
        """
        if self.response is None:
            raise BaseException("No request has been sent.")
        else:
            return self.response.json()

    def set_base_uri(self, base_url):
        """

        :param base_url:
        :return:
        """
        self.base_url = base_url
        return self

    def get_base_uri(self):
        """

        :return:
        """
        return self.base_url

    def set_jwt(self, jwt):
        """

        :param jwt:
        :return:
        """
        self.jwt = jwt
        return self

    def get_jwt(self):
        """

        :return:
        """
        return self.jwt

    def set_jwt_data(self, jwt_data):
        """

        :param jwt_data:
        :return:
        """
        self.jwt_data = jwt_data
        return self

    def get_jwt_data(self):
        """

        :return:
        """
        return self.jwt_data

    def set_response(self, response):
        """

        :param response:
        :return:
        """
        self.response = response
        return self

    def get_response(self):
        """

        :return:
        """
        return self.response

    def set_payload(self, payload):
        """

        :param payload:
        :return:
        """
        self.payload = payload
        return self

    def get_payload(self):
        """

        :return:
        """
        return self.payload

    def set_headers(self, headers):
        """

        :param headers:
        :return:
        """
        self.headers = headers
        return self

    def get_headers(self):
        """

        :return:
        """
        return self.headers

    def __set_method(self, method):
        self.method = method
        return self

    def get_method(self):
        """

        :return:
        """
        return self.method
