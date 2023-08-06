2. Edit the ``/etc/os_vif_bigswitch/os_vif_bigswitch.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://os_vif_bigswitch:OS_VIF_BIGSWITCH_DBPASS@controller/os_vif_bigswitch
