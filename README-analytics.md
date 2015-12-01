Publicamundi Analytics Plugin
=============================


Overview
--------

The `publicamundi_analytics` plugin analyzes HAProxy logs to extract usefull information on requested BBoxes, coverages etc.


Installation
------------

Add `publicamundi_analytics` to the list of `ckan.plugins`

Configuration
-------------

The following configuration options are supported:

```ini
ckanext.publicamundi.analytics.logfile_pattern = /var/log/haproxy.log* 
ckanext.publicamundi.analytics.database_url = postgresql://user:pass@localhost:5432/analytics
ckanext.publicamundi.analytics.export_date_format = %Y-%m-%d
ckanext.publicamundi.analytics.ha_proxy_datetime_format = %d/%b/%Y:%H:%M:%S
```

Use
---

Add a cron job to periodically analyze your log files. The analysis is carried out by a
Paster subcommand:

```bash
paster publicamundi --config $CKAN_CONFIG analyze-logs --from 2015-11-29 --to 2015-12-02

```

Note that the above command uses a processing window (granularity) of 1 day.
