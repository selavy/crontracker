from shared_connection import SharedConnection
import datetime

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
        qry = 'select job_template.template_name, job_instance.* from job_instance LEFT OUTER JOIN job_template ON (job_instance.template = job_template.id)'
        res = cxn.execute(qry)
        for row in res:
            self.jobs.append(self._parseJob(row))
    def _parseJob(self, res):
        ret = {}
        ret['template'] = res['template_name']
        ret['warnings'] = res['warnings']
        ret['errors'] = res['errors']
        ret['status'] = res['status']
        ret['ack'] = res['acknowledged'] or False
        ret['log'] = res['log_file']
        ret['startts'] = res['start_ts']
        ret['lasteventts'] = res['last_event_ts']
        ret['lastevent'] = res['last_event']
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
        
