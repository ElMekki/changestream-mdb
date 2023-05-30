import os
import pymongo
import json
import time
from bson.timestamp import Timestamp


class Trace:
    def __init__(self, _id, coll, op, created):
        self._id = _id
        self.coll = coll
        self.op = op
        self.created = created

    def __str__(self):
        return json.dumps(self.__dict__, separators=(',', ': '))


def change_stream():
    client = pymongo.MongoClient(os.environ['CHANGE_STREAM_DB'])
    aggregate = "{'$project':{'$operationType':1'}}";

    '''
    streams = client.test.watch()
    for change in streams:
        fichier = open("journal_change.log", "a")
        # print(dumps(change))
        # print("op:%s;coll:%s;id:%s" % (change["operationType"], change["ns"]["coll"], change["fullDocument"]["_id"]))
        time = ""
        bts = change["clusterTime"]
        if isinstance(bts, Timestamp):
            time = bts.as_datetime()

        #
        operation = Trace(str(change["fullDocument"]["_id"]), change["ns"]["coll"], change["operationType"], str(time))
        print(operation)
        client['report'].operations.insert_one(json.loads(str(operation)))
        fichier.write(str(operation))
        fichier.write("\n")
        fichier.close()
    '''
    #
    with client.test.collection.watch() as stream:
        while stream.alive:
            change = stream.try_next()
            # Note that the ChangeStream's resume token may be updated
            # even when no changes are returned.
            print("Current resume token: %r" % (stream.resume_token,))
            if change is not None:
                print("Change document: %r" % (change,))
                continue
            # We end up here when there are no recent changes.
            # Sleep for a while before trying again to avoid flooding
            # the server with getMore requests when no changes are
            # available.
            time.sleep(10)


if __name__ == '__main__':
    #

    change_stream()
