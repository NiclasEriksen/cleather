from app import app
from config import SSL_CERT, SSL_KEY
#from OpenSSL import SSL

# Create SSL context
context = (SSL_CERT, SSL_KEY)
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file(SSL_KEY)
# context.use_certificate_file(SSL_CERT)
# context.load_cert_chain(SSL_CERT, SSL_KEY)

app.run(debug=True, ssl_context=context, threaded=True)
