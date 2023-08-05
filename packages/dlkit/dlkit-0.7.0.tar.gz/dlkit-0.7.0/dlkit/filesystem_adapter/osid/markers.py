"""AWS Adapter marker implementations."""
# pylint: disable=no-init
#    most markers will not be initted
# pylint: disable=too-few-public-methods
#    they are markers

from ...abstract_osid.osid import markers as abc_osid_markers
from ..types import FILESYSTEM_ASSET_CONTENT_RECORD_TYPE


class OsidPrimitive(abc_osid_markers.OsidPrimitive):
    """A marker interface for an interface that behaves like a language primitive.

    Primitive types, such as numbers and strings, do not encapsulate
    behaviors supplied by an OSID Provider. More complex primitives are
    expressed through interface definitions but are treated in a similar
    fashion as a language primitive. OSID Primitives supplied by an OSID
    Consumer must be consumable by any OSID Provider.

    """


class Identifiable(abc_osid_markers.Identifiable):
    """A marker interface for objects uniquely identified with an OSID ``Id``."""

    def __init__(self):
        self._payload = None

    def get_id(self):
        """Gets the Id associated with this instance of this OSID object.

        Persisting any reference to this object is done by persisting
        the Id returned from this method. The Id returned may be
        different than the Id used to query this object. In this case,
        the new Id should be preferred over the old one for future
        queries.

        return: (osid.id.Id) - the ``Id``
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: The ``Id`` is intended to be constant
        and persistent. A consumer may at any time persist the ``Id``
        for retrieval at any future time. Ideally, the Id should
        consistently resolve into the designated object and not be
        reused. In cases where objects are deactivated after a certain
        lifetime the provider should endeavor not to obliterate the
        object or its ``Id`` but instead should update the properties of
        the object including the deactiavted status and the elimination
        of any unwanted pieces of data. As such, there is no means for
        updating an ``Id`` and providers should consider carefully the
        identification scheme to implement.  ``Id`` assignments for
        objects are strictly in the realm of the provider and any errors
        should be fixed directly with the backend supporting system.
        Once an Id has been assigned in a production service it should
        be honored such that it may be necessary for the backend system
        to support Id aliasing to redirect the lookup to the current
        ``Id``. Use of an Id OSID may be helpful to accomplish this task
        in a modular manner.

        """
        return self._payload.get_id()

    id_ = property(fget=get_id)

    ident = property(fget=get_id)

    def is_current(self):
        """Tests to see if the last method invoked retrieved up-to-date data.

        Simple retrieval methods do not specify errors as, generally,
        the data is retrieved once at the time this object is
        instantiated. Some implementations may provide real-time data
        though the application may not always care. An implementation
        providing a real-time service may fall back to a previous
        snapshot in case of error. This method returns false if the data
        last retrieved was stale.

        return: (boolean) - ``true`` if the last data retrieval was up
                to date, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: Providers should return false unless all
        getters are implemented using real-time queries, or some trigger
        process keeps the data in this object current. Providers should
        populate basic data elements at the time this object is
        instantiated, or set an error, to ensure some data availability.

        """
        return False


class Extensible(abc_osid_markers.Extensible):
    """A marker interface for objects that contain ``OsidRecords``."""

    def __init__(self):
        self._payload = None

    def get_record_types(self):
        """Gets the record types available in this object.

        A record ``Type`` explicitly indicates the specification of an
        interface to the record. A record may or may not inherit other
        record interfaces through interface inheritance in which case
        support of a record type may not be explicit in the returned
        list. Interoperability with the typed interface to this object
        should be performed through ``hasRecordType()``.

        return: (osid.type.TypeList) - the record types available
        *compliance: mandatory -- This method must be implemented.*

        """
        # This should  add the FILESYSTEM_ASSET_CONTENT_RECORD_TYPE to
        # self._payload.get_record_types()
        pass

    record_types = property(fget=get_record_types)

    def has_record_type(self, record_type=None):
        """Tests if this object supports the given record ``Type``.

        The given record type may be supported by the object through
        interface/type inheritence. This method should be checked before
        retrieving the record interface.

        arg:    record_type (osid.type.Type): a type
        return: (boolean) - ``true`` if a record of the given record
                ``Type`` is available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return record_type == FILESYSTEM_ASSET_CONTENT_RECORD_TYPE or \
            self._payload.has_record_type(record_type)


class Browsable(abc_osid_markers.Browsable):
    """A marker interface for objects that offer property inspection."""

    def get_properties(self):
        """Gets a list of properties.

        Properties provide a means for applications to display a
        representation of the contents of a record without understanding
        its ``Type`` specification. Applications needing to examine a
        specific property should use the extension interface defined by
        its ``Type``.

        return: (osid.PropertyList) - a list of properties
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - an authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    properties = property(fget=get_properties)

    def get_properties_by_record_type(self, record_type=None):
        """Gets a list of properties corresponding to the specified record type.

        Properties provide a means for applications to display a
        representation of the contents of a record without understanding
        its record interface specification. Applications needing to
        examine a specific propertyshould use the methods defined by the
        record ``Type``. The resulting set includes properties specified
        by parents of the record ``type`` in the case a record's
        interface extends another.

        arg:    record_type (osid.type.Type): the record type
                corresponding to the properties set to retrieve
        return: (osid.PropertyList) - a list of properties
        raise:  NullArgument - ``record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - an authorization failure occurred
        raise:  Unsupported - ``has_record_type(record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        pass


class Suppliable(abc_osid_markers.Suppliable):
    """A marker interface for OSID Provider-owned objects used to supply
    input from an OSID Consumer."""


class Temporal(abc_osid_markers.Temporal):
    """``Temporal`` is used to indicate the object endures for a period of time."""

    def is_effective(self):
        """Tests if the current date is within the start end end dates inclusive.

        return: (boolean) - ``true`` if this is effective, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    def get_start_date(self):
        """Gets the start date.

        return: (osid.calendaring.DateTime) - the start date
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    start_date = property(fget=get_start_date)

    def get_end_date(self):
        """Gets the end date.

        return: (osid.calendaring.DateTime) - the end date
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    end_date = property(fget=get_end_date)


class Subjugateable(abc_osid_markers.Subjugateable):
    """A ``Subjugateable`` is an ``OsidObject`` dependent upon another ``OsidObject``.

    A ``Subjugateable`` is created in the context of the administering
    ``OsidObject`` that may not be reassigned.

    A ``Subjugateable`` always has a fixed Id of it administering
    ``OsidObject``.

    """


class Aggregateable(abc_osid_markers.Aggregateable):
    """``Aggregateable`` is used for an ``OsidObject`` to indicate that
    some or all of the definition is based on an included set of other
    ``OsidObjects`` which are directly accessible and do not exist outside
    the context of the parent object.

    ``Aggregateables`` allow for an ``OsidObject`` to stand alone
    without knowledge of the originating service.

    An ``Asset`` is an example of an aggregate by including the
    ``AssetContents``. An Asset also contains a provider however in this
    case the provider is categorized as a simple data attribute of the
    ``Asset`` that can be changed by updating the ``Asset`` using an
    ``AssetForm``. The ``AssetContent`` differs in there exists a
    explicit mapping to the ``Asset`` managed through an ``OsidSession``
    but accessible directly within the ``Asset`` to enable its
    consumption outside the Repository OSID.

    This marker has little practicality other than to identify a service
    pattern that is neither a data attribute nor a separately accessible
    relationship or mapping.

    """


class Containable(abc_osid_markers.Containable):
    """A ``Containable`` is a kind of aggregate where an ``OsidObject`` is
    defined as a recursive composition of itself directly accessible without
    knowledge of the originating service."""

    def is_sequestered(self):
        """Tests if this ``Containable`` is sequestered in that it should not
        appear outside of its aggregated composition.

        return: (boolean) - ``true`` if this containable is sequestered,
                ``false`` if this containable may appear outside its
                aggregate
        *compliance: mandatory -- This method must be implemented.*

        """
        pass


class Sourceable(abc_osid_markers.Sourceable):
    """``Sourceble`` is used for ``OsidObjects`` where information about a
    provider is appropriate.

    Examples of ``Sourceables`` are catalogs, compositions, and
    services.

    """

    def get_provider_id(self):
        """Gets the ``Id`` of the provider.

        return: (osid.id.Id) - the provider ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._payload.get_provider_id()

    provider_id = property(fget=get_provider_id)

    def get_provider(self):
        """Gets the ``Resource`` representing the provider.

        return: (osid.resource.Resource) - the provider
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._payload.get_provider()

    provider = property(fget=get_provider)

    def get_branding_ids(self):
        """Gets the branding asset ``Ids``.

        return: (osid.id.IdList) - a list of asset ``Ids``
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._payload.get_branding_ids()

    branding_ids = property(fget=get_branding_ids)

    def get_branding(self):
        """Gets a branding, such as an image or logo, expressed using the
        ``Asset`` interface.

        return: (osid.repository.AssetList) - a list of assets
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._payload.get_branding()

    branding = property(fget=get_branding)

    def get_license(self):
        """Gets the terms of usage.

        An empty license means the terms are unknown.

        return: (osid.locale.DisplayText) - the license
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._payload.get_license()

    license_ = property(fget=get_license)


class Federateable(abc_osid_markers.Federateable):
    """``Federateable`` is used to indicate an ``OsidObject`` can be federated
    using the OSID Hierarchy pattern.

    An OSID federation of ``OsidObjects`` is where it is inferred from
    the hiererarchy that any ``OsidObject`` "includes" its children.

    """


class Operable(abc_osid_markers.Operable):
    """``Operable`` is used to indicate an ``OsidObject`` performs operations.

    The active status indicates if the ``Operable`` is on or off. The
    active status is determined from the operational status and the
    enabling rules.

    The operational status indicates the Operable is functioning. This
    status is not set administratively but instead refelects suitable
    conditions for operation.

    Operables may be administratively turned on of off through the
    enabled and disabled administrative overrides. If there are no
    related ``OsidEnabler`` rules, then ``is_enabled()`` should be set
    to ``true`` and ``is_disabled()`` set to ``false`` for the
    ``Operable`` to be on and ``is_enabled()`` set to ``false`` and
    ``is_disabled()`` set to true for the ``Operable`` to be ``off``.
    ``is_enabled()`` and ``is_disabled()`` cannot both be ``tru`` e.

    If there are related ``OsidEnabler`` rules, the active status of at
    least one ``OsidEnabler`` results in a ``true`` value for
    ``isOperational()``. This active status can be overridden by setting
    ``is_disabled()`` to ``true``. If there are no active
    ``OsidEnabler`` rules, ``is_operational()`` is false resulting in an
    ``off``  ``Operable`` unless ``is_enabled()`` is ``true`` .

    For the active status to be completely determined by the
    ``OsidEnablers,`` both ``is_enabled()`` and ``is_disabled()`` should
    be ``false`` where the ``is_active()`` status is completely driven
    from ``isOperational()``.

    """

    def is_active(self):
        """Tests if this operable is active.

        ``is_active()`` is ``true`` if ``is_operational()`` is ``true``
        and ``is_disabled()`` is ``false,`` or ``is_enabled()`` is
        ``true``.

        return: (boolean) - ``true`` if this operable is on, ``false``
                if it is off
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    def is_enabled(self):
        """Tests if this operable is administravely enabled.

        Administratively enabling overrides any applied ``OsidEnabler``.
        If this method returns ``true`` then ``is_disabled()`` must
        return ``false``.

        return: (boolean) - ``true`` if this operable is enabled,
                ``false`` if the active status is determined by other
                rules
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    def is_disabled(self):
        """Tests if this operable is administravely disabled.

        Administratively disabling overrides any applied
        ``OsidEnabler``. If this method returns ``true`` then
        ``is_enabled()`` must return ``false``.

        return: (boolean) - ``true`` if this operable is disabled,
                ``false`` if the active status is determined by other
                rules
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    def is_operational(self):
        """Tests if this ``Operable`` is operational.

        This Operable is operational if any of the applied
        ``OsidEnablers`` are ``true``.

        return: (boolean) - ``true`` if this operable is operational,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        pass
