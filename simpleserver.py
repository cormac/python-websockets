import base64
import socket
import sys
import threading
import hashlib
class mysocket:
  '''
  class to wrap webserver socket functionality
  '''

  def __init__( self, sock = None ):
    if sock is None:
      self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    else: 
      self.sock = sock

  def initserver( self ):
    self.sock.bind( ( '', 9999 ) )
    self.sock.listen( 5 )
    print( 'listening on port 9999' )

  def connect( self, host, port ):
    self.sock.connect( ( host, port ) )

  def startserver( self ):
    while 1:
      self.clientsock, self.address= self.sock.accept()
      print 'connected' 
      server = echoserver( self.clientsock, self.address )
      server.start()
      #self.echodata()
    self.clientsock.close()
    self.sock.close()

  def echodata( self ):
    while 1:
      data = self.clientsock.recv( 1024 )
      if not data: break 
      self.clientsock.send( data + ' from server' )


  def startclient( self ):
    while 1:
      data = raw_input( '> ')

      if not data: break
      self.sock.send( data )
      data = self.sock.recv( 1024 )
      if not data: break
      print data
    self.sock.close()


class echoserver( threading.Thread ):

  def __init__( self, clientsock, address):
    threading.Thread.__init__( self )
    self.clientsock = clientsock
    self.address = address
    self.handshaken = False

  def run( self ):
    while 1:
      if self.handshaken == False:
        self.handshake()
      else:
        validated = []
        data = self.clientsock.recv( 1024 )
        if not data: break 
        msgs = data.split('\xff')
        print msgs[0]
        print len( msgs )
        for msg in msgs:
          if msg[0] == '\x00':
            validated.append(msg[1:])

        for v in validated:
          print v
          client.send('\x00' + v + '\xff')
        self.clientsock.send( '\x00%s from server %s\xff' % ( 'data', self.getName() ) )

  
  def handshake( self ):
    """
    NB handshake cannot have any spqaces at the beginning of each line
    """
    handshake = 'HTTP/1.1 101 Switching Protocols\r\n'
    handshake += 'Upgrade: websocket\r\n'
    handshake += 'Connection: Upgrade\r\n'
    handshake += 'Sec-WebSocket-Accept: %s\r\n\r\n'

    header = ''
    header += self.clientsock.recv( 1024 )
    print header
    if header.find( '\r\n\r\n' ) != -1:
      key = self.getHeaderValue( header, 'Sec-WebSocket-Key' ) 
      myhash = self.generateHash( key )
      handshake = handshake% ( myhash ) 
      self.handshaken = True
      print handshake
      self.clientsock.send( handshake )
    else:
      self.handshaken = True
      self.clientsock.send( 'hello mr testy' )

  def generateHash( self, key ):
    magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    key += magic_string
    print key
    my_sha = hashlib.sha1( key )
    mykey = base64.b64encode( my_sha.digest() )
    return mykey


  def getHeaderValue( self, request, header):
    """ Returns the value of a header specified header field. """
    delim = ': '
    start = request.index(header.strip() + ': ')
    end = request.index('\r\n', start)
    return request[start+len(header)+len(delim):end]

