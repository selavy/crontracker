from shared_connection import SharedConnection
import sys
import datetime
from db_queries import *

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
