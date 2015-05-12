from shared_connection import SharedConnection
import datetime
import sys

class TemplateCollector(object):
    def __init__(self, cxn=None):
        cxn = cxn or SharedConnection()
        self.templates = []
        qry = 'SELECT * FROM job_template'
        res = cxn.execute(qry)
        for row in res:
            self.templates.append(self._parseTemplate(row))
    def _parseTemplate(self, row):
        ret = {}
        ret['name'] = row['template_name']
        ret['cron'] = row['cron_entry']
        ret['cmd'] = row['cmd_line']
        ret['hardwareid'] = row['hardware_id']
        ret['sentinels'] = row['writes_sentinels']
        ret['owner'] = row['job_owner']
        ret['wiki'] = row['wiki_link']
        return ret
    def __len__(self):
        return len(self.templates)
    def __iter__(self):
        return iter(self.templates)

class JobRunCollector(object):
    def __init__(self, cxn=None):
        cxn = cxn or SharedConnection()
        self.jobs = []
        qry = 'SELECT * FROM job_instance'
        res = cxn.execute(qry)
        for row in res:
            self.jobs.append(self._parseJob(row))
    def _parseJob(self, res):
        ret = {}
        ret['template'] = res['template']
        ret['warnings'] = res['warnings'] or 0
        ret['errors'] = res['errors'] or 0
        ret['status'] = res['status'] or ''
        ret['ack'] = res['acknowledged'] or False
        ret['log'] = res['log'] or ''
        ret['startts'] = res['startts']
        ret['lasteventts'] = res['lasteventts']
        ret['lastevent'] = res['lastevent']
        return ret
    def __len__(self):
        return len(self.jobs)
    def __iter__(self):
        return iter(self.jobs)

def jobRunSQL(job):
    return "((select id from job_template where template_name = '{template}'), '{warnings}','{errors}','{status}','{ack}','{log}','{start}','{lasteventts}','{lastevent}')" \
        .format(template=job['template'],
                warnings=job['warnings'],
                errors=job['errors'],
                status=job['status'],
                ack=job['ack'] or '-1',
                log=job['log'],
                start=job['startts'],
                lasteventts=job['lasteventts'],
                lastevent=job['lastevent'],
                )

def insertJobRunSQL(job):
    return 'INSERT INTO job_instance (template, warnings, errors, status, acknowledged, log_file, start_ts, last_event_ts, last_event) VALUES {values}' \
        .format(values=jobRunSQL(job))
    
def templateSQL(template):
    return "('{name}', '{cron}', '{cmd}', '{hardware}', '{sentinels}', '{wiki}', '{owner}')" \
        .format(name=template['name'],
                cron=template['cron'],
                cmd=template['cmd'],
                hardware=template['hardware'],
                sentinels=template['sentinels'],
                wiki=template['wiki'],
                owner=template['owner'])

def insertTemplateSQL(template):
    return 'INSERT INTO job_template (template_name, cron_entry, cmd_line, hardware_id, writes_sentinels, wiki_link, job_owner) VALUES {values}' \
        .format(values=templateSQL(template))
        
if __name__ == '__main__':
    from optparse import OptionParser
    templates = [ {'name':'proc_param', 'cron':'00 04 * * 1-5', 'cmd':'proc_param --env=plesslie --do-something', 'hardware':4198, 'sentinels':False, 'owner':'24', 'wiki':''},
                  {'name':'log_puller', 'cron':'00,15,30,45 10 * * 1-5', 'cmd':'log_puller --env=plesslie --do-something --else', 'hardware':2048, 'sentinels':True, 'owner':'0', 'wiki':'http://google.com'},
                  ]

    today = datetime.date.today()
    now = datetime.datetime.now()
    jobTimes = [now + datetime.timedelta(minutes=-36),
                now + datetime.timedelta(minutes=-320),]
    
    jobs = [ {'template':'proc_param', 'warnings':'0', 'errors':'0', 'status':'finished', 'ack':'', 'log':'', 'startts':jobTimes[0], 'lasteventts':jobTimes[0], 'lastevent':'start'},
             {'template':'log_puller', 'warnings':'0', 'errors':'1', 'status':'finished', 'ack':'', 'log':'', 'startts':jobTimes[1], 'lasteventts':jobTimes[1]+datetime.timedelta(minutes=-5), 'lastevent':'commit'},
    ]
    
    parser = OptionParser()
    parser.add_option('--user', default='jobtracker')
    options, args = parser.parse_args()

    conninfo = 'dbname=crontracker user={user}'.format(user=options.user)
    cxn = SharedConnection(conninfo=conninfo, autocommit=True)
    
    qry = 'DELETE FROM job_instance'
    cxn.execute(qry)
    
    qry = 'DELETE FROM job_template'
    cxn.execute(qry)
    
    for template in templates:
        cxn.execute(insertTemplateSQL(template))

    for job in jobs:
        cxn.execute(insertJobRunSQL(job))    
    
    collector = TemplateCollector(cxn=cxn)
    for template in collector:
        print template['name']
