Prerequisites
-------------

Before you install and configure the os-vif-bigswitch service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``os_vif_bigswitch`` database:

     .. code-block:: none

        CREATE DATABASE os_vif_bigswitch;

   * Grant proper access to the ``os_vif_bigswitch`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON os_vif_bigswitch.* TO 'os_vif_bigswitch'@'localhost' \
          IDENTIFIED BY 'OS_VIF_BIGSWITCH_DBPASS';
        GRANT ALL PRIVILEGES ON os_vif_bigswitch.* TO 'os_vif_bigswitch'@'%' \
          IDENTIFIED BY 'OS_VIF_BIGSWITCH_DBPASS';

     Replace ``OS_VIF_BIGSWITCH_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``os_vif_bigswitch`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt os_vif_bigswitch

   * Add the ``admin`` role to the ``os_vif_bigswitch`` user:

     .. code-block:: console

        $ openstack role add --project service --user os_vif_bigswitch admin

   * Create the os_vif_bigswitch service entities:

     .. code-block:: console

        $ openstack service create --name os_vif_bigswitch --description "os-vif-bigswitch" os-vif-bigswitch

#. Create the os-vif-bigswitch service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        os-vif-bigswitch public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        os-vif-bigswitch internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        os-vif-bigswitch admin http://controller:XXXX/vY/%\(tenant_id\)s
