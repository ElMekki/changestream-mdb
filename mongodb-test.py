import os
import pymongo
import json
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


if __name__ == '__main__':
    #

    change_stream()
