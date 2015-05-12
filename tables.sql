-- Job Templates
CREATE TABLE job_template (
       id SERIAL PRIMARY KEY,
       template_name VARCHAR NOT NULL,
       cron_entry VARCHAR NOT NULL,
       cmd_line VARCHAR NOT NULL,
       hardware_id INTEGER NOT NULL, -- references hardware(id)
       writes_sentinels BOOLEAN NOT NULL DEFAULT FALSE,
       wiki_link VARCHAR NOT NULL DEFAULT '',
       job_owner INTEGER -- REFERENCES users(id)
       );

-- Job Instances
CREATE TABLE job_instance (
       id SERIAL PRIMARY KEY,
       template INTEGER REFERENCES job_template(id), -- null indicates non-template job
       warnings INTEGER NOT NULL DEFAULT 0,
       errors INTEGER NOT NULL DEFAULT 0,
       status VARCHAR NOT NULL DEFAULT 'running', -- { "running", "failed", "finished" }
       acknowledged INTEGER, -- REFERENCES users(id)
       log_file VARCHAR NOT NULL DEFAULT '',
       start_ts TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
       last_event_ts TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
       last_event VARCHAR NOT NULL DEFAULT ''
       );
       
       
       
       
       
       	 
