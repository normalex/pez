import json
import logging
import falcon

from sqlalchemy.exc import DBAPIError
from pg8000 import InterfaceError

from .models import session_scope, forward_sequence, backward_sequence
from .config import configuration


logger = logging.getLogger(__name__)


class NumberPezV1(object):
    '''
    Number generator using Postresql/Oracle sequence objects.

    The sequence objects will advance according to the predefined step
    either forward or backwards.

    '''
    def __init__(self, sequence):
        self.sequence = sequence

    def get_next_number(self):
        with session_scope() as sess:
            next_uint = sess.execute(self.sequence)
        return next_uint

    def return_as_json(self, resp, result):
        resp.body = json.dumps(result)
        resp.content_type = 'application/json'
        resp.status = falcon.HTTP_200

    def on_get(self, req, resp):
        number = self.get_next_number()
        self.return_as_json(resp, number)


class NumberPezV2(NumberPezV1):

    def on_get(self, req, resp):
        '''
        Generates next batch of unique numbers with an optional "count" parameter.

        Returns a list of uints.

        '''
        count = req.get_param_as_int('count', min=1, max=configuration['max_count']) or 1
        numbers = [self.get_next_number() for i in range(count)]
        self.return_as_json(resp, numbers)

    def on_options(self, req, resp, **kwargs):
        '''
        Returns a json wrapped help usage information for this resource.

        Example: curl -s -X OPTIONS <route url> | python -m json.tool
        to see the help output. Could be done as a simple text or an extract from sphinx.
        TODO: create a func wrapper with inspect module to generate help automatically

        '''
        resp.set_header('Allow', 'GET')
        self.return_as_json(
            resp,
            dict(
                description='Generate a list of unique UINTs.',
                verbs=[
                    {'GET':
                        {'parameters':
                            [{'count':
                                'URL parameter min value is 0; maximum is {0}'\
                                .format(configuration['max_count'])
                            }
                            ]
                        }
                    }
                ]
            )
        )


def handle_dbapi_error(ex, req, resp, params):
    logger.exception(ex)
    raise falcon.HTTPServiceUnavailable(
        'Database connection error',
        'Database is temporary unavailable',
        3600
    )


application = falcon.API()
application.add_route('/v1/forward', NumberPezV1(forward_sequence))
application.add_route('/v1/reverse', NumberPezV1(backward_sequence))
application.add_route('/v2/forward', NumberPezV2(forward_sequence))
application.add_route('/v2/reverse', NumberPezV2(backward_sequence))

application.add_error_handler(DBAPIError, handle_dbapi_error)
application.add_error_handler(InterfaceError, handle_dbapi_error)

