import site
site.addsitedir('/app/python/lib/python2.7/site-packages')
import sys
sys.path.append("/app/share")
sys.path.append("/app/share/python/site-packages")
import web

from api.restresource import RestResource
from ni.network_traffic.snapshot import NetworkTrafficSnapshot


urls = [
    '/snapshot', 'Snapshot',
    '/snapshot/([0-9a-f]{24})', 'Snapshot',
    '/snapshot/([0-9a-f]{24}/[a-z_]+)', 'Snapshot',
    '/snapshotupload', 'SnapshotUpload'
]


class Snapshot(RestResource):
    collection_name = 'snapshots'
    supported_methods = ['GET', 'DELETE']
    relations = {
        'networkmessages': {
            'collection': 'networkmessages',
            'field': 'snapshot_id',
            'sort': 'index'
        }
    }


class SnapshotUpload:

    def __init__(self):
        self.snapshot = NetworkTrafficSnapshot()

    def POST(self):
        try:
            title = web.input().title
            filename = web.input().logfile_name
            description = web.input().description
            content = web.input().logfile_content
        except AttributeError:
            pass
        else:
            # Process the logfile
            self.snapshot.upload(title, description, filename, content)
            id = self.snapshot.save()
            self.snapshot.generate_statistics()
            return id


application = web.application(urls, globals()).wsgifunc()
