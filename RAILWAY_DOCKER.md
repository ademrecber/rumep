# Rumep Docker deployment — 23 October 2026

Only ademrecber/rumep was changed. TurkishStraitsGuide was inspected read-only
to compare builders; no settings, deployments or files in that project changed.

The failing Rumep Railpack builds stopped immediately after builder startup,
with no application output. Railway diagnosis classified this as infrastructure
error. The working comparison service used Dockerfile. This difference suggested
a workaround; it does not establish the exact internal Railway failure cause.

Commit aae9af4 adds Dockerfile, a restricted Docker context, and a runtime startup
script. No environment secrets are copied into the image. Database migrations
and collectstatic run with existing runtime configuration, then Gunicorn starts.
The existing database and S3 storage configuration are unchanged.

19 Django tests passed, including startup ordering and migration failure handling.
Compressed static collection passed locally. Docker was unavailable locally, so
the actual Docker build was verified on Railway.

Deployment ea6a4f81-54e1-4e4a-82b5-11d9b7c54430 became Active. Logs show container
startup at 01:13:03 Turkey time, no pending migrations, successful static collection
and Gunicorn listening on port 8080. Site, feed, wallpapers and content notification
APIs returned HTTP 200. Feed IDs [11,10,7,6,5,4,3,2,1] and wallpaper IDs
[7,6,5,4,3,2,1] matched the pre-deployment check.

This deployment includes the webhook user-agent fix in 57b926f. New admin
publication to device delivery still needs a real end-to-end timing test;
deployment success alone does not prove immediate FCM delivery.

Separate outstanding security work: Railway's incident disclosure recommends
rotating secrets held in environment variables. No database credentials, storage
keys, Django SECRET_KEY or webhook token were rotated in this deployment.
No Firebase service account key was read or changed.
