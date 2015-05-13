from collections import defaultdict

def combine(templates, jobs):
    def match(template, job):
        try:
            return template['name'] == job['template']
        except:
            return false
    ret = defaultdict(list)
    for template in templates:
        toremove = []
        for job in jobs:
            if match(template, job):
                temp = dict(job)
                temp.update(template)
                ret[template['name']].append(temp)
                toremove.append(job)
        for job in toremove:
            jobs.remove(job)
    # anything left
    for job in jobs:
        ret['unmatched'].append(job)
    return ret
    
