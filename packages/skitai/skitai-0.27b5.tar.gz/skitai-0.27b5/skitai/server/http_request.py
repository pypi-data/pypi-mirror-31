from . import http_response, counter
import time
import re
import json
from aquests.lib.attrdict import CaseInsensitiveDict
from aquests.protocols.http import http_util

class http_request:
	version = "1.1"
	collector = None
	producer = None
	request_count = counter.counter()
	
	def __init__ (self, *args):
		self.request_number = self.request_count.inc()		
		(self.channel, self.request,
		 self.command, self.uri, self.version,
		 self.header) = args
		self.logger = self.channel.server.server_logger
		self.server_ident = self.channel.server.SERVER_IDENT
		self.body = None
		self.multipart = None
		self.reply_code = 200
		self.reply_message = ""		
		self.loadbalance_retry = 0
		self.rbytes = 0
		self.created = time.time ()
		self.gzip_encoded = False
		self._split_uri = None
		self._headers_cache = None
		self._header_cache = {}
		self._is_stream_ended = False
		self._is_async_streaming = False
		self._is_promise = False		
		self.args = {}
		self.set_log_info ()
		self.make_response ()
	
	def set_args (self, args):
		self.args = args
		if "defaults" in self.routable:
			for k, v in self.routable ["defaults"].items ():
				if k not in self.args:
					self.args [k] = v
					
	@property
	def method (self):
		return self.command.upper ()
	
	@property
	def scheme (self):
		return self.get_scheme ()
		
	@property
	def headers (self):
		if self._headers_cache:
			return self._headers_cache						
		h = CaseInsensitiveDict ()
		for line in self.header:
			k, v = line.split (":", 1)
			h [k] = v.strip ()
		self._headers_cache = h	
		return h
	
	@property
	def payload (self):
		return self.get_body ()
	
	def json (self):		
		return json.loads (self.body.decode ('utf8'))		
	
	def set_multipart (self, dict):
		self.multipart = dict
	
	def get_multipart (self):
		return self.multipart
			
	def set_body (self, body):
		self.body = body
	
	def get_body (self):
		return self.body
	get_payload = get_body
	
	def form (self, ct = None):
		if not ct:
			ct = self.get_header ('content-type', '')			
		if self.multipart:
			return self.multipart
		elif ct.startswith ("application/x-www-form-urlencoded"):
			return http_util.crack_query (self.body)
	
	def dict (self):
		if not self.body:
			return		
		ct = self.get_header ('content-type', '')
		if ct.startswith ("application/json"):
			return self.json ()
		return self.form (ct)
	
	def is_promise (self):
		return self._is_promise
		
	def make_response (self):
		self.response = http_response.http_response (self)
	
	def set_streaming (self):
			self._is_async_streaming = True
	
	def is_async_streaming (self):
		return self._is_async_streaming
	
	def set_stream_ended (self):	
		self._is_stream_ended = True
	
	def is_stream_ended (self):
		return self._is_stream_ended
			
	def set_log_info (self):
		self.gtxid = self.get_header ("X-Gtxn-Id")
		if not self.gtxid:
			self.gtxid = "%s-%s-%s" % (
				self.channel.server.hash_id,
				self.channel.channel_number, 
				self.request_count
			)
			self.ltxid = 1000
		else:			
			self.ltxid = self.get_header ("X-Ltxn-Id")
			if not self.ltxid:
				raise ValueError ("Local txn ID missing")
			self.ltxid = int (self.ltxid) + 1000
			
		self.token = None
		self.claim = None
		self.user = None
		self.host = self.get_header ("host")
		self.user_agent = self.get_header ("user-agent")
	
	def get_gtxid (self):
		return self.gtxid
		
	def get_ltxid (self, delta = 1):
		self.ltxid += delta
		return str (self.ltxid)
			
	def get_scheme (self):	
		from .https_server import https_channel		
		return isinstance (self.channel, https_channel) and "https" or "http"
		
	def get_raw_header (self):
		return self.header
	get_headers = get_raw_header
		
	path_regex = re.compile (r'([^;?#]*)(;[^?#]*)?(\?[^#]*)?(#.*)?')
	def split_uri (self):
		if self._split_uri is None:
			m = self.path_regex.match (self.uri)
			if m.end() != len(self.uri):
				raise ValueError("Broken URI")
			else:
				self._split_uri = m.groups()				
		return self._split_uri

	def get_header_with_regex (self, head_reg, group):
		for line in self.header:
			m = head_reg.match (line)
			if m.end() == len(line):
				return head_reg.group (group)
		return ''
	
	def set_header (self, name, value):
		self.header.append ("%s: %s" % (name, value))		
	
	def get_header (self, header = None, default = None):		
		if header is None:
			return self.header
		header = header.lower()
		hc = self._header_cache
		if header not in hc:
			h = header + ':'
			hl = len(h)
			for line in self.header:
				if line [:hl].lower() == h:
					r = line [hl:].strip ()
					hc [header] = r
					return r
			hc [header] = None
			return default
		else:
			return hc[header] is not None and hc[header] or default
	
	def get_header_params (self, header, default = None):
		d = {}
		v = self.get_header (header, default)
		if v is None:
			return default, d
			
		v2 = v.split (";")
		for each in v2 [1:]:
			each = each.strip ()
			if not each: continue
			try:
				a, b = each.split ("=", 1)
			except ValueError:
				a, b = each, None
			d [a.lower ()] = b
		return v2 [0], d		
	get_header_with_attr = get_header_params
	
	def get_header_noparam (self, header, default = None):
		return self.get_header_params (header, default) [0]
	
	def get_charset (self):
		return self.get_attr ("content-type", "charset")
				
	def get_attr (self, header, attrname = None, default = None):
		value, attrs = self.get_header_params (header, None)
		if not value:
			return default
		if not attrname:	
			return attrs
		return attrs.get (attrname, default)
					
	def get_content_length (self):
		try: return int (self.get_header ("content-length"))
		except: return None
					
	def get_content_type (self):
		return self.get_header_with_attr ("content-type") [0]
				
	def get_main_type (self):
		ct = self.get_content_type ()
		if ct is None:
			return
		return ct.split ("/", 1) [0]
	
	def get_sub_type (self):
		ct = self.get_content_type ()
		if ct is None:
			return
		return ct.split ("/", 1) [1]
		
	def get_user_agent (self):
		return self.get_header ("user-agent")
	
	MAYBE_BACKENDS = ("127.0.0.", "192.168.")
	def get_remote_addr (self):
		remote_addr = self.channel.addr [0]
		if remote_addr [:8] in self.MAYBE_BACKENDS:
			return self.get_header ("X-Forwarded-For", "")
		return remote_addr
			
	def collect_incoming_data (self, data):
		if self.collector:
			self.rbytes += len (data)
			self.collector.collect_incoming_data (data)			
		else:
			self.logger.log (
				'dropping %d bytes of incoming request data' % len(data),
				'warn'
				)

	def found_terminator (self):		
		if self.collector:
			self.collector.found_terminator()			
		else:
			self.logger.log (
				'unexpected end-of-record for incoming request',
				'warn'
				)
			
	def response_finished (self):
		if self.response:
			self.response.request = None
	
	def xmlrpc_serialized (self):
		# for compat with client request
		return False
