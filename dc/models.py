from __future__ import unicode_literals

import docker


from django.conf import settings
from django.db import models
import uuid
from OpenSSL import crypto
from django.core.files.base import ContentFile

def user_directory_path_key(instance, filename):
	return 'key_store/{0}/{1}/key.pem'.format(instance.user.id, instance.uuid)

def user_directory_path_cert(instance, filename):
	return 'key_store/{0}/{1}/cert.pem'.format(instance.user.id, instance.uuid)
	
class Node(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	uuid = models.UUIDField(default=uuid.uuid4, editable=False)
	created = models.DateTimeField(auto_now_add=True, editable=False)
	modified = models.DateTimeField(auto_now=True, editable=False)
	address = models.CharField(max_length=250, blank=True)
	key = models.FileField(blank=True, upload_to=user_directory_path_key)
	cert = models.FileField(blank=True, upload_to=user_directory_path_cert)
	
	def docker(self):
		tls_config = docker.tls.TLSConfig(client_cert=(self.cert.path, self.key.path))
		client = docker.Client(base_url=self.address, tls=tls_config)
		return client
	
	def generate_key(self):
		pkey = crypto.PKey()
		pkey.generate_key(crypto.TYPE_RSA, 4096)
		self.key.save(user_directory_path_key(self, ''), ContentFile(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey).decode('utf-8')))
		
	def set_cert(self, data):
		self.cert.save(user_directory_path_cert(self, ''), ContentFile(data))
		
	def createCertRequest(self, **name):
	    """
	    Create a certificate request.
	    Arguments: pkey   - The key to associate with the request
	               digest - Digestion method to use for signing, default is sha256
	               **name - The name of the subject of the request, possible
	                        arguments are:
	                          C     - Country name
	                          ST    - State or province name
	                          L     - Locality name
	                          O     - Organization name
	                          OU    - Organizational unit name
	                          CN    - Common name
	                          emailAddress - E-mail address
	    Returns:   The certificate request in an X509Req object
	    """
	    
	    pkey=crypto.load_privatekey(crypto.FILETYPE_PEM, open(self.key.path, 'rt').read())
	    
	    req = crypto.X509Req()
	    subj = req.get_subject()
	
	    for key, value in name.items():
	        setattr(subj, key, value)
	
	    req.set_pubkey(pkey)
	    req.sign(pkey, "sha256".encode('ascii','ignore'))
	    return crypto.dump_certificate_request(crypto.FILETYPE_PEM, req).decode('utf-8')
