import json
import falcon


def _read_stream(req, logger):
    try:
        logger.debug("Reading body...")
        raw_json = req.stream.read(size=req.content_length)
        logger.debug("Done reading data: {0}".format(raw_json))
    except Exception, e:
        logger.error("error: {0}".format(e))
        # todo use a named tuple for http errors?
        raise falcon.HTTPError(falcon.HTTP_748,
                               'Read Error',
                               'Could not read the request body. Must be '
                               'them ponies again.')
    return raw_json

def _raw_to_dict(raw_json, logger):
    try:
        logger.debug("Parsing json...")
        parsed_json = json.loads(raw_json, 'utf-8')
        logger.debug("Done parsing json...")
    except ValueError:
        # todo use a named tuple for http errors?
        raise falcon.HTTPError(falcon.HTTP_753,
                               'Malformed JSON',
                               'Could not decode the request body. The '
                               'JSON was incorrect.')

    return parsed_json