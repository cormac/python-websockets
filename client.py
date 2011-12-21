import simpleserver

client = simpleserver.mysocket()
client.connect( '', 9999 )
client.startclient()
