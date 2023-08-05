Flask AuthNZ LDAP RBAC
=======================

Uses AuthN/AuthZ environment variables from Apache mod_authnz_ldap to enforce access controls

Usage
-----

`flask_authnz_ldap_rbac` provides a single GroupRBAC class that enforces LDAP group membership.

    class GroupRBAC(app, groups_variable, write_methods, read_methods, write_groups, read_groups)
     |  Enforces membership in a given LDAP group.
     |
     |  :param app: The Flask app to be protected
     |  :param groups_variable: The environment variable that contains a list of the autenticated user's groups. Default: AUTHENTICATE_MEMBEROF
     |  :param write_methods: HTTP 'write' methods. Default: 'PUT', 'POST', 'DELETE', 'PATCH'
     |  :param read_methods: HTTP 'read' methods. Default: 'OPTIONS', 'GET', 'HEAD'
     |  :param write_groups: Groups allowed to make requests with 'write' methods. Default: None.
     |  :param read_groups: Groups allowed to make requests with 'read' methods. Default: ANY.
     |
     |  The special group names 'ANY' and 'ANONYMOUS' allow any authenticated user, or unauthenticated users, respectively.

Any LDAP attributes that will be used for RBAC decisions must be exposed as environment variables by Apache. By default, Apache exposes only the `uid` attribute; you probably want `memberOf` and maybe `sAMAccountName` as well. Consult the [mod_authnz_ldap documentation](https://httpd.apache.org/docs/2.4/mod/mod_authnz_ldap.html#exposed) for more information.

Example
-------
First, configure mod_authnz_ldap in your apache.conf:

```apache_conf
LDAPConnectionPoolTTL 600
LDAPConnectionTimeout 2
LDAPTimeout 2

<AuthnProviderAlias ldap ad-ldap>
        AuthLDAPBindDN "CN=MyApp,OU=Service Accounts,DC=contoso,DC=com"
        AuthLDAPBindPassword ChangeMe
        AuthLDAPURL "ldaps://dc1.contoso.com dc2.contoso.com/OU=Users,DC=contoso,DC=com?sAMAccountName,memberOf?sub?(objectClass=user)"
</AuthnProviderAlias>

<VirtualHost *:80>
    # ProxyProtocol on
    RewriteEngine on
    RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>

<VirtualHost *:443>
    ErrorLog logs/ssl_error_log
    TransferLog logs/ssl_access_log
    LogLevel warn

    # ProxyProtocol on
    SSLEngine on

    SSLProtocol all -SSLv3
    SSLProxyProtocol all -SSLv3
    SSLHonorCipherOrder on

    SSLCertificateFile /etc/pki/tls/certs/localhost.crt
    SSLCertificateKeyFile /etc/pki/tls/private/localhost.key

    ServerAdmin admin@localhost

    WSGIDaemonProcess myapp python-home=/opt/myapp/venv/ display-name=%{GROUP}
    WSGIScriptAlias /myapp /opt/myapp/myapp.wsgi

    <Location /myapp>
        AuthName "MyApp LDAP Auth"
        AuthType basic
        AuthBasicProvider ad-ldap

        Require valid-user

        Session On
        SessionMaxAge 1800
        SessionCookieName appsession path=/
        SessionCryptoPassphrase ChangeMe
        SessionCookieRemove On
    </Location>
</VirtualHost>
 
```

Then, configure RBAC and bind it to your app:

```python
from flask import Flask
from flask_authnz_ldap_rbac import GroupRBAC 


app = Flask(__name__)
rbac = GroupRBAC(read_groups=['CN=MyApp Users,OU=Groups,DC=contoso,DC=com'],
                 write_groups=['CN=MyApp Admins,OU=Groups,DC=contoso,DC=com'])
rbac.init_app(app)
```
