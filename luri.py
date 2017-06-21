
import json
import re

class LURI():
  URL_PATTERN = (r'^'
               r'((?P<scheme>.+?)://)?'
               r'((?P<user>.+?)(:(?P<password>.*?))?@)?'
               r'(?P<host>.*?)'
               r'(:(?P<port>\d+?))?'
               r'(?P<path>/.*?)?'
               r'(?P<query>[?].*?)?'
               r'(#(?P<fragment>.*?))?'
               r'$'
               )

  def __init__(self, uri=None):
    if uri:
      parsed_uri = self.parse(uri.strip())
      for key in parsed_uri:
        setattr(self, key, parsed_uri[key])

  def __str__(self):
    uri = ''
    authority = self.get_authority()
    if self.scheme:
      uri +=  "{}://".format(self.scheme)
    if self.user:
      uri += "{}:{}@".format(self.user, self.password)
    if authority:
      uri += authority
    if self.path:
      uri += self.path
    if self.query:
      uri += self.query
    if self.fragment:
      uri += '#' + self.fragment
    return uri

  def equal(uri1, uri2):
    return True

  def append_query_var(self, key, val):
    if key:
      parsed_qs = self.parse_qs()
      parsed_qs.update({key: val})
      self.query = self.create_qs(parsed_qs)
    return self

  def create_qs(self, qp_dict):
    if len(qp_dict) > 0:
      qs = '?' + ''.join(
        {"{}={}&".format(key, val) for key, val in qp_dict.items()})
      return qs[:-1]
    return None

  def remove_query_var(self, key):
    if key:
      parsed_qs = self.parse_qs()
      if key in parsed_qs:
        del parsed_qs[key]
        self.query = self.create_qs(parsed_qs)

  def get_authority(self):
    if self.host:
      if self.port:
        return "{}:{}".format(self.host, self.port)
      return self.host
    return None

  def json(self):
    return json.dumps(self.__dict__, sort_keys=True, indent=2)

  def uri_matches(self, uri):
    regex = re.compile(LURI.URL_PATTERN)
    return regex.match(uri)

  def parse(self, uri):
    matches = self.uri_matches(uri)
    return matches.groupdict() if matches is not None else None

  def parse_qs(self):
    if self.query:
      params = self.query.split("?")
      if params and params[1]:
        return {x.split('=')[0]:x.split('=')[1] for x in params[1].split("&")}
    return None

import unittest

class TestLURI(unittest.TestCase):
    def setUp(self):
        self.test_urls = [
          'https://www.example.com:8080/some-path.html?a=b',
          'www.example.com/some-path.html?a=b',
          'http://www.example.com/some-path.html?a=b',
          'ftp://example.com',
          'ftp://loktra:lokpass@example.com',
        ]

    def test_str(self):
      for url in self.test_urls:
        self.assertEqual(str(LURI(url)), url)
      
    def test_init(self):
        instance = LURI(self.test_urls[0])
        self.assertEqual(instance.scheme, 'https')
        self.assertEqual(instance.host, 'www.example.com')
        self.assertEqual(instance.get_authority(), 'www.example.com:8080')
        self.assertEqual(instance.port, '8080')
        self.assertEqual(instance.query, '?a=b')

    def test_append_query_var(self):
        l = LURI(self.test_urls[0])
        l.append_query_var('c', 'd')
        self.assertEqual(l.parse_qs(), {"a": "b", "c": "d"})

    def test_remove_query_var(self):
        l = LURI(self.test_urls[0])
        l.remove_query_var('a')
        self.assertEqual(l.parse_qs(), None)

    def test_parse(self):
        uri = LURI().parse(self.test_urls[0])
        self.assertEqual(uri.get("scheme"), 'https')
        self.assertEqual(uri.get("host"), 'www.example.com')
        self.assertEqual(uri.get("port"), '8080')
        self.assertEqual(uri.get("query"), '?a=b')

if __name__ == '__main__':
    unittest.main()
