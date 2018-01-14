import time
import sys
import json
import os

class DDDatabase(object):
    def __init__(self, db_fn):
        self._db_fn = db_fn
        self.revert()
        self._print_keys = [
                'call', 
                'year', 'month', 'day',
                'utc',
                'band', 'mode',
                'rsts', 'rstr',
                'name', 'qth', 'st',
                'grid',
                'skcc', 'sota', 
                'mysota',
                'remark']
        self._required_keys = [
                'call', 
                'year', 'month', 'day',
                'utc',
                'band', 'mode']

    def check_record(self,record):
        for rk in self._required_keys:
            if not (rk in record):
                return False
        return True

    def revert(self):
        if os.path.isfile(self._db_fn):
            self._db = json.load(open(self._db_fn))
        else:
            print("Database does not exist; creating.")
            self._db = []

    def add(self, record):
        self._db.append(record)

    def save(self):
        with open(self._db_fn,'w') as dbf:
            n = len(self._db)
            json.dump(self._db, dbf)
            print("Wrote %d QSOs to disk."%n)
    
    def lookup_call(self, call):
        rv = []
        for record in self._db:
            if record['call'] == call:
                rv.append(record)
        return rv

    def print_table(self, records):
        print("")
        rows = [[pk.upper() for pk in self._print_keys]]
        rows += [self.record_to_row(record) for record in records]
        if len(rows) == 1:
            print("[]")
            return
        row_widths = [max([len(row[i]) for row in rows])+1 for i in range(len(rows[0]))]
        def print_row(row):
            for i in range(len(row)):
                sys.stdout.write(row[i].ljust(row_widths[i]))
            sys.stdout.write('\n')
        print_row(rows[0])
        print_row([''.join(['-' for c in v]) for v in rows[0]])
        for row in rows[1:]:
            print_row(row)
        return

    def record_to_row(self, record):
        keys = record.keys()
        row = [(record[pk] if pk in record else '-') for pk in self._print_keys]
        TRUNC_LEN = 15
        trunc = [('%s$'%e[:TRUNC_LEN-1] if (len(e)>TRUNC_LEN) else e) for e in row]
        return trunc

    def print_log(self):
        self.print_table(self._db)


class DDCLI(object):
    def __init__(self, dddb):
        self._dddb = dddb

    def loop(self):
        self._dddb.print_log()
        while True:
            print("")
            print("--------------------------")
            call = input("CALL:\t").upper().strip()
            if call == '':
                continue
            lc = self._dddb.lookup_call(call)
            self._dddb.print_table(lc)
            record = {'call': call}
            for pk in self._dddb._print_keys:
                if pk == 'call':
                    continue
                while True:
                    v = input("%s:\t"%pk.upper()).upper().strip()
                    if v == '':
                        if pk in self._dddb._required_keys:
                            print("Required field!")
                            continue
                        else:
                            break
                    break
                record[pk] = v
            if not self._dddb.check_record(record):
                print("Invalid record.")
                continue
            self._dddb.add(record)
            self._dddb.save()
            lc = self._dddb.lookup_call(call)
            self._dddb.print_table(lc)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 ditditlog.py <log.json>")
        exit(1)
    db_fn = sys.argv[1]
    dddb = DDDatabase(db_fn)
    ddcli = DDCLI(dddb)
    try:
        ddcli.loop()
    except KeyboardInterrupt:
        print("")
        print("Exiting!")
        exit(0)

