=============
Release Notes
=============

WaiverDB 0.10
=============

Released 10 May 2018.

* Comment is now explicitly required when creating waivers (both in API and
  CLI).

* Multiple waivers can now be created with single POST request (#98). To create
  multiple waivers, POST list to "waivers/" instead of single waiver.

* When creating a waiver by referring to a result ID, WaiverDB now accepts
  results with ``'type': 'brew-build'`` as an alias for ``'koji_build'``.

* Messaging can be disabled is settings with ``MESSAGE_PUBLISHER = None``.

* The ``KERBEROS_HTTP_HOST`` setting in the server configuration is now
  ignored. This setting is no longer needed because GSSAPI will automatically
  find a key in the Kerberos keytab matching the service principal in the
  client request.

* New man pages are available for ``waiverdb-cli(1)`` and ``waiverdb(7)`` (REST
  API).

* Changed error message for bad ``since`` value. E.g.
  ``api/v1.0/waivers/?since=123`` results in HTTP 400 with message
  ``{"message": {"since": "time data '123' does not match format
  '%Y-%m-%dT%H:%M:%S.%f'"}}``.

* CORS headers are now supported for every request (#160).

* Wrong ``subject`` filter produces more user-friendly error (#162).

* Setting a keytab file is no longer required: if one is not explicitly set,
  ``/etc/krb5.keytab`` will be used (#55).

* Unused option ``resultsdb_api_url`` was removed from client.conf.

* Containers on Quay (`<https://quay.io/repository/factory2/waiverdb>`__).

WaiverDB 0.9
============

Released 1 Mar 2018.

*  The usage of ``JSONB`` has been replaced with the older ``JSON`` column
   type, in order to maintain compatibility with PostgreSQL 9.2 on RHEL7
   (#134).

WaiverDB 0.8
============

Released 16 Feb 2018.

* Removed support to SQLite in favor of PostgreSQL.

* Fixed database migration to use the correct column type for the
  ``waiver.subject`` column (#129).

* Added information on the README file on how to configure the db.

WaiverDB 0.7
============

Released 16 Feb 2018.

* Fixed the database migration strategy for Openshift deployment (#121).
  The migration step is now run in a pre-deployment hook. Previously it ran in
  a post-start pod hook which did not work correctly in some situations.

WaiverDB 0.6
============

Released 13 Feb 2018.

* Dummy authentication for CLI for developing and debugging reasons.

* Added logo in the README page.

* You can now waive the absence of a result. Now it is possible to 
  submit waivers using a subject/testcase.

* Backward compatibility for submitting a waiver using the result_id.
  This feature will be removed in the near future.

WaiverDB 0.5
============

Released 17 Jan 2018.

* Database migrations have been introduced, and will be a part of future
  releases.  Users upgrading to 0.5 will need to run these commands::

  $ waiverdb db stamp 0a27a8ad723a
  $ waiverdb db upgrade

* Error messages are now returned by the API in JSON format.

* A new authentication method: ssl auth.  See the docs for more on
  configuration.

* The API now supports a proxyuser argument.  A limited set of superusers,
  configured server-side, are able to submit waivers on behalf of other users.

WaiverDB 0.4
============

Released 08 Nov 2017.

A number of issues have been resolved in this release:

* New WaiverDB CLI for creating waivers (#82).

* New `/about` API endpoint to expose the current running version and the method
  used for authentication of the server.

* Improved the process of building docs by using sphinxcontrib.issuetracker
  extension.

WaiverDB 0.3
============

Released 26 Sep 2017.

A number of issues have been resolved in this release:

* Fixed some type errors in the API docs examples (#73).

* Updated README to recommend installing package dependencies using dnf builddep (#74).

* Fixed the health check API to return a proper error if the application is not
  able to serve requests (#75).

Other updates:

* Supports a new HTTP API `/api/v1.0/waivers/+by-result-ids`.
* Package dependencies are switched to python2-* packages in Fedora.

WaiverDB 0.2
============

Released 16 June 2017.

* Supports containerized deployment in OpenShift. ``DATABASE_PASSWORD`` and
  ``FLASK_SECRET_KEY`` can now be passed in as environment variables instead of
  being defined in the configuration file.

* Supports publishing messages over AMQP, in addition to Fedmsg.
  The ``ZEROMQ_PUBLISH`` configuration option has been renamed to
  ``MESSAGE_BUS_PUBLISH``.

* The :file:`/etc/waiverdb/settings.py` configuration file is no longer
  installed by default. For new installations, you can copy the example
  configuration from :file:`/usr/share/doc/waiverdb/conf/settings.py.example`.

* Numerous improvements to the test and build process for WaiverDB.

WaiverDB 0.1
============

Initial release, 12 April 2017.
