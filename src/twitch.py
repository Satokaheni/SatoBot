import requests as req

def top(limit=25):
    return req.get('https://api.twitch.tv/kraken/streams/', params={'limit':limit, 'client_id':'s7ka1ne3rrzngcxr3pmd0zlpw2bvgcn'}).json()

def featured(limit=25):
    return req.get('https://api.twitch.tv/kraken/streams/featured/', params={'limit':limit}).json()

def channel(name):
    return req.get('https://api.twitch.tv/kraken/streams/'+name, params={'client_id':'ns0maf26acxxso12n8s536zv1enugli'}).json()


def getchannel(name):
    return req.get('https://api.twitch.tv/kraken/channels/'+name, params={'client_id':'ns0maf26acxxso12n8s536zv1enugli'}).json()	
	
def getfollowers(name):
    return req.get('https://api.twitch.tv/kraken/channels/'+name+'/follows', params={'client_id':'ns0maf26acxxso12n8s536zv1enugli', 'limit': 100}).json()		

def getmorefollowers(name, cursor):
    return req.get('https://api.twitch.tv/kraken/channels/'+name+'/follows', params={'client_id':'ns0maf26acxxso12n8s536zv1enugli', 'limit': 100, 'cursor': cursor}).json()		

	
def panel(name):
    return req.get('https://api.twitch.tv/api/channels/'+name+'/panels', params={'client_id':'ns0maf26acxxso12n8s536zv1enugli'}).json()

class API:
    id = ''

    def __init__(self, id):
        self.id = id

    def top(self, limit=25):
        return req.get('https://api.twitch.tv/kraken/streams/', params={'limit':limit, 'client_id':self.id}).json()

    def featured(self, limit=25):
        return req.get('https://api.twitch.tv/kraken/streams/featured/', params={'limit':limit, 'client_id':self.id}).json()

    def stream(self, name):
        return req.get('https://api.twitch.tv/kraken/streams/'+name, params={'client_id':self.id}).json()
		
    def getfollowers(self, name):
        return req.get('https://api.twitch.tv/kraken/channels/'+name+'/follows', params={'client_id': self.id, 'limit': 100}).json()		

    def getmorefollowers(self, name, cursor):
        return req.get('https://api.twitch.tv/kraken/channels/'+name+'/follows', params={'client_id': self.id, 'limit': 100, 'cursor': cursor}).json()		