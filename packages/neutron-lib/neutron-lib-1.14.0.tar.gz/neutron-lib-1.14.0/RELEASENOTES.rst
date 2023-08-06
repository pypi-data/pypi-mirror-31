===========
neutron-lib
===========

.. _neutron-lib_1.14.0:

1.14.0
======

.. _neutron-lib_1.14.0_Prelude:

Prelude
-------

.. releasenotes/notes/change_placement_client_method_names_b26bb71425f42db3.yaml @ f0a9959a7fd98b091a17a29544eacdbd6dd37337

Change create_inventory in placement client to update_resource_provider_inventories and update_inventory to update_resource_provider_inventory


.. _neutron-lib_1.14.0_New Features:

New Features
------------

.. releasenotes/notes/add-is_filter-keyword-to-attribute-maps-3fa31e91c353d033.yaml @ 0abe67c6ebb07eeb02236cb373b7c42cde03b3ec

- Add a new keyword ``is_filter`` to attribute maps. This keyword indicates
  that the attribute can be used for filtering result on list requests.

.. releasenotes/notes/add-is_sort_key-keyword-to-attribute-map-75342446d99f4490.yaml @ b03226d59739fafe036bc60c62f165da598ca947

- Add a new keyword ``is_sort_key`` to attribute maps. This keyword indicates
  that the attribute can be used as a sort key for sorting list result.

.. releasenotes/notes/add-ovo-registry-27cb7d4ac76d4dc8.yaml @ 6f94faf64ee2fe48457ad799172555cc84c2812f

- The ``neutron_lib.utils.runtime.NamespacedPlugins`` class is now available and wraps a stevedore namespace of plugins.

.. releasenotes/notes/add-ovo-registry-27cb7d4ac76d4dc8.yaml @ 6f94faf64ee2fe48457ad799172555cc84c2812f

- The ``neutron_lib.objects.registry`` module is now available for loading neutron versioned object classes registered as entry points with the ``NEUTRON_OBJECT_NAMESPACE`` namespace therein. This global registry can be used by consumers to access references to neutron versioned object classes and instances so there's no need to import ``neutron.objects``.

.. releasenotes/notes/add-port_details-to-floatingip-a2a3c95cc54737ac.yaml @ 24a0877d1d234830a36794388bb342d3d91b9230

- Add ``fip-port-details`` API extension. This extension add ``port_details``
  attribute to the Floating IP resource.

.. releasenotes/notes/callback_priority-2ded960e17bd5db9.yaml @ 217efe0a7ba192017612fffd99a16e50e1bd8b8e

- Introduced priority to callback subscription. An integer value can be
  associated with each callback so that callbacks can be executed in
  specified order for same resources and events. Every callback will have
  priority value by default. To execute callbacks in specified order, priorities
  should be defined explicitly, lower priority value would be executed first.

.. releasenotes/notes/default_overrides_none-ecc8dcf2c9c37e5d.yaml @ 478c4d85b0f2c7384b4018d373e4fa3b72aeaa82

- A new flag can be used in API definition: ``default_overrides_none``.
  When enabled, the default value for the attribute will
  be used, including if the attribute was explicitly defined
  as ``null``.

.. releasenotes/notes/placement-resource-provider-functions-17ec45f714ea2b23.yaml @ 874cf4f550e9c10c8b03af6d735642bc61a589e6

- Added ``list_resource_providers`` function to the Placement API client, which allows to retrieve a list of Resource Providers filtering by UUID or parent UUID. It requires at least version ``1.3`` of placement API for listing resource providers that are members of any of the list of aggregates provided. It requires at least version ``1.14`` of placement API for listing nested resource providers.

.. releasenotes/notes/placement-resource-provider-functions-17ec45f714ea2b23.yaml @ 874cf4f550e9c10c8b03af6d735642bc61a589e6

- Added ``get_resource_provider`` function to the Placement API client, which allows to retrieve an specific Resource Provider by its UUID.

.. releasenotes/notes/placement-resource-provider-functions-17ec45f714ea2b23.yaml @ 874cf4f550e9c10c8b03af6d735642bc61a589e6

- Added ``PlacementAPIVersionIncorrect`` exception class which can be raised when requested placement API version is incorect and doesn't support requested API feature.

.. releasenotes/notes/populate-dict-defaults-3f205c414f21bf54.yaml @ c8e1389a5590c2a4c779a19b740ecf2ec6346aa7

- A new ``dict_populate_defaults`` flag can be used in API definition for
  a dictionary attribute, which will results in default values for the keys
  to be filled in. This can also be used on values of a dictionary attribute
  if they are dictionaries as well.

.. releasenotes/notes/rehome-db-api-63300ddab6a41e28.yaml @ edab0eb770ce2313adc73a157f8a164766a001aa

- The public APIs from ``neutron.db.api`` are now available in the ``neutron_lib.db.api`` module.

.. releasenotes/notes/rehome-db-api-63300ddab6a41e28.yaml @ edab0eb770ce2313adc73a157f8a164766a001aa

- The ``CONTEXT_READER`` and ``CONTEXT_WRITER`` global database contexts are available in ``neutron_lib.db.api`` for convenient access as decorators.

.. releasenotes/notes/rehome-db-api-63300ddab6a41e28.yaml @ edab0eb770ce2313adc73a157f8a164766a001aa

- The ``DBRetryErrorsFixture`` and ``DBAPIContextManagerFixture`` test fixtures are now available in ``neutron_lib.fixture`` allowing consumers to patch out retry error values and the gobal context manager.

.. releasenotes/notes/rehome-db-model-query-234b1559f3728a5e.yaml @ 108a598252a20c9c7f4f3b87ffdc603b5de31697

- The public functions of ``neutron.db._model_query`` are now available in ``neutron_lib.db.model_query`` with the same name. While these modules can be used, forward looking projects should start moving to versioned objects and after which point we can remove this module.

.. releasenotes/notes/rehome-db-model-query-234b1559f3728a5e.yaml @ 108a598252a20c9c7f4f3b87ffdc603b5de31697

- A new fixture named ``DBQueryHooksFixture`` is provided for testing purposes allowing consumers to patch-out the model_query filter hooks.

.. releasenotes/notes/rehome-db-model-query-234b1559f3728a5e.yaml @ 108a598252a20c9c7f4f3b87ffdc603b5de31697

- The ``make_weak_ref`` and ``resolve_ref`` functions from neutron are now available in ``neutron_lib.utils.helpers``.

.. releasenotes/notes/rehome-db-model-query-234b1559f3728a5e.yaml @ 108a598252a20c9c7f4f3b87ffdc603b5de31697

- The ``TenantIdProjectIdFilterConflict`` exception is now available in ``neutron_lib.exceptions``.

.. releasenotes/notes/rehome-db-model-query-234b1559f3728a5e.yaml @ 108a598252a20c9c7f4f3b87ffdc603b5de31697

- The ``neutron.objects.utils`` module is now available in ``neutron_lib.objects.utils``.

.. releasenotes/notes/rehome-db-utils-3076bf724caa31ef.yaml @ 2042d18d1f5c476079c777bfd945ee9bbc396b30

- The database utility functions ``get_marker_obj``, ``filter_non_model_columns``, ``model_query_scope_is_project`` and ``resource_fields`` are now available in ``neutron_lib.db.utils``.

.. releasenotes/notes/rehome-dhcpagentscheduler-apidef-1f7729fb5834dcd2.yaml @ 23f6f8c50f6236b3eb787c6c4527d87e55b365c1

- The ``dhcp_agent_scheduler`` extension's API defintion is now available in ``neutron_lib.api.definitions.dhcpagentscheduler`` and the corresponding exceptions in ``neutron_lib.exceptions.dhcpagentscheduler``.

.. releasenotes/notes/rehome-getphysmtu-plugin-fn-5875e352e3a14af3.yaml @ 93fb08870f74f716f1ecdda64846037b6b139e0b

- The ``neutron.plugins.common.utils.get_deployment_physnet_mtu`` function is now available in ``neutron_lib.plugins.utils`` with the same name.

.. releasenotes/notes/rehome-plugin-utils-create-fns-9b8591f5222bff66.yaml @ ebf776ac85bb559d9e8f275b47f3b6b34dd033f5

- The ``create_network``, ``create_subnet`` and ``create_port`` functions from ``neutron.plugins.common.utils`` are now available in ``neutron_lib.plugins.utils``.

.. releasenotes/notes/rehome-qosbwldir-apidef-f0e3f778f2f980c0.yaml @ 2dc9675f0f1cc55f988dfa4ff78a459785ce6b2f

- The ``qos-bw-limit-direction`` extension's API definition is now available in ``neutron_lib.api.definitions.qos_bw_limit_direction``.

.. releasenotes/notes/rehome-unstable-test-decorator-a062301ac7d7a082.yaml @ 31f65b8f93eccdabbaef1f5b2cd6d192704aee27

- The ``unstable_test`` decorator from ``neutron.tests.base`` is now available in neutron-lib in ``neutron_lib.utils.test``.

.. releasenotes/notes/subnet_segmentid_writable-e28a85033272f05d.yaml @ 9059d0d7097e638fe0947ba964231c6ad2f75922

- Make ``segment_id`` of subnet resource writable. Enables the possibility to
  migrate a non-routed network to a routed network.

.. releasenotes/notes/vpn-api-def-52970461fac0f7d2.yaml @ 59797ca40857e2d9c2818cbf8f616c9fcaff6763

- Adds ``neutron-vpnaas`` API definitions to neutron-lib, including ``vpnaas``, ``vpn-endpoint-groups`` and ``vpn-flavors``.

.. releasenotes/notes/vpn-api-def-52970461fac0f7d2.yaml @ 59797ca40857e2d9c2818cbf8f616c9fcaff6763

- Migrate user facing exceptions into neutron-lib along with the API definitions.

.. releasenotes/notes/vpn-api-def-52970461fac0f7d2.yaml @ 59797ca40857e2d9c2818cbf8f616c9fcaff6763

- A new validator for type ``type:list_of_subnets_or_none`` to validate data is a list of subnet dicts or ``None`` is added too.


.. _neutron-lib_1.14.0_Known Issues:

Known Issues
------------

.. releasenotes/notes/change_placement_client_method_names_b26bb71425f42db3.yaml @ f0a9959a7fd98b091a17a29544eacdbd6dd37337

- Placement API has no POST method for creating resource provider inventories but instead has PUT to update the inventories of a resource provider.

.. releasenotes/notes/change_placement_client_method_names_b26bb71425f42db3.yaml @ f0a9959a7fd98b091a17a29544eacdbd6dd37337

- Placement API has method to update the inventory for a given resource_provider.


.. _neutron-lib_1.14.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/rehome-db-api-63300ddab6a41e28.yaml @ edab0eb770ce2313adc73a157f8a164766a001aa

- Consumers using the global ``context_manager`` from ``neutron.db.api`` should now use the ``get_context_manager()`` function in the ``neutron_lib.db.api`` module or the global ``CONTEXT_READER`` and ``CONTEXT_WRITER`` if needed.

.. releasenotes/notes/remove-ensure_dir-aed59b616e02a2bb.yaml @ 61ebbb7fa536dc66a3ed55294b1f8a8151c31a2c

- The deprecated ``neutron_libutils.file.ensure_dir`` function is removed. Consumers can use ``ensure_tree(path, 0o755)`` from ``oslo_utils.fileutils`` instead.

.. releasenotes/notes/rm-apiutils-fa30241be7ca5162.yaml @ fa32a3f41c29852a8bf74db2577b847ebe892ef2

- The ``neutron_lib.api.utils`` module has been removed. The single ``populate_project_info`` function therein is available in ``neutron_lib.api.attributes`` and has been marked as a moved function in the ``utils`` module for some time now.


.. _neutron-lib_1.14.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/change_placement_client_method_names_b26bb71425f42db3.yaml @ f0a9959a7fd98b091a17a29544eacdbd6dd37337

- Change the method name create_inventory in clients/placement.py to update_resource_provider_inventories as that represents what is on the placement side.

.. releasenotes/notes/change_placement_client_method_names_b26bb71425f42db3.yaml @ f0a9959a7fd98b091a17a29544eacdbd6dd37337

- Change the POST call to /resource_providers/{uuid}/inventories to PUT.

.. releasenotes/notes/change_placement_client_method_names_b26bb71425f42db3.yaml @ f0a9959a7fd98b091a17a29544eacdbd6dd37337

- Change the method name update_inventory in clients/placement.py to update_resource_provider_inventory as that represents that the method updates the inventory of a resource_provider.


.. _neutron-lib_1.14.0_Other Notes:

Other Notes
-----------

.. releasenotes/notes/remove_label-801d7a1b13f179fa.yaml @ 590664c09c53c02ccc910a57af06b77af0dc158e

- The ``LABEL`` variable, which was uselessly duplicating ``ALIAS``, has been
  removed from API definition modules.

