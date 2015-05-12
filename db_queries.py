from shared_connection import SharedConnection
import sys

class TemplateCollector(object):
    def __init__(self, cxn=None):
        cxn = cxn or SharedConnection()
        self.templates = []
        qry = 'SELECT * FROM job_template'
        res = cxn.execute(qry)
        for row in res:
            self.templates.append(self._parseTemplate(row))
    def _parseTemplate(self, res):
        ret = {}
        ret['name'] = res['template_name']
        ret['cron'] = res['cron_entry']
        ret['cmd'] = res['cmd_line']
        ret['hardwareid'] = res['hardware_id']
        ret['sentinels'] = res['writes_sentinels']
        return ret
    def __len__(self):
        return len(self.templates)
    def __iter__(self):
        return iter(self.templates)

def templateSQL(template):
    return "('{name}', '{cron}', '{cmd}', '{hardware}', '{sentinels}')".format(name=template['name'],
                                                                               cron=template['cron'],
                                                                               cmd=template['cmd'],
                                                                               hardware=template['hardware'],
                                                                               sentinels=template['sentinels'])

def insertTemplateSQL(template):
    return 'INSERT INTO job_template (template_name, cron_entry, cmd_line, hardware_id, writes_sentinels) VALUES {values}'.format(values=templateSQL(template))
        
if __name__ == '__main__':
    from optparse import OptionParser
    templates = [ {'name':'proc_param', 'cron':'00 04 * * 1-5', 'cmd':'proc_param --env=plesslie --do-something', 'hardware':4198, 'sentinels':False},
                  {'name':'log_puller', 'cron':'00,15,30,45 10 * * 1-5', 'cmd':'log_puller --env=plesslie --do-something --else', 'hardware':2048, 'sentinels':True},
                  ]
    
    parser = OptionParser()
    parser.add_option('--user', default='jobtracker')
    options, args = parser.parse_args()

    conninfo = 'dbname=crontracker user={user}'.format(user=options.user)
    cxn = SharedConnection(conninfo=conninfo, autocommit=True)

    qry = 'DELETE FROM job_template'
    cxn.execute(qry)
    
    for template in templates:
        cxn.execute(insertTemplateSQL(template))
    
    collector = TemplateCollector(cxn=cxn)
    for template in collector:
        print template['name']
