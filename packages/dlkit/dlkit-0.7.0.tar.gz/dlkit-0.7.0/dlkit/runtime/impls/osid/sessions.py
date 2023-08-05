# -*- coding: utf-8 -*-

# This module contains all the Session classes used by the MIT Core Concept
# Catalog (MC3) Handcar based implementation of the OSID Learning Service.
# Note that it includes the core OsidSession typically found in the osid
# package as well as the learning package sessions for Objective, Activities
# and ObjectiveBanks.

from dlkit.abstract_osid.osid import sessions as abc_osid_sessions
from ..osid.osid_errors import *

COMPARATIVE = 0
PLENARY = 1
ISOLATED = 0
FEDERATED = 1

CREATED = True
UPDATED = True


class OsidSession(abc_osid_sessions.OsidSession):
    """The OsidSession is the top level interface for all OSID sessions.

    An OsidSession is created through its corresponding OsidManager. A
    new OsidSession should be created for each user of a service and for
    each processing thread. A session maintains a single authenticated
    user and is not required to ensure thread-protection. A typical OSID
    session defines a set of service methods corresponding to some
    compliance level as defined by the service and is generally
    responsible for the management and retrieval of OsidObjects.

    OsidSession defines a set of common methods used throughout all OSID
    sessions. An OSID session may optionally support transactions
    through the transaction interface.

    """

    def get_locale(self):
        """Gets the locale indicating the localization preferences in
        effect for this session.

        return: (osid.locale.Locale) - the locale
        compliance: mandatory - This method must be implemented.

        """
        raise Unimplemented()

    def is_authenticated(self):
        """Tests if an agent is authenticated to this session.

        return: (boolean) - true if valid authentication credentials
                exist, false otherwise
        compliance: mandatory - This method must be implemented.

        """
        return False

    def get_authenticated_agent_id(self):
        """Gets the Id of the agent authenticated to this session.
        This is the agent for which credentials are used either acquired
        natively or via an OsidProxyManager.
        return: (osid.id.Id) - the authenticated agent Id
        raise:  IllegalState - is_authenticated() is false
        compliance: mandatory - This method must be implemented.

        """
        raise IllegalState()

    def get_authenticated_agent(self):
        """Gets the agent authenticated to this session.
        This is the agent for which credentials are used either acquired
        natively or via an OsidProxyManager.
        return: (osid.authentication.Agent) - the authenticated agent
        raise:  IllegalState - is_authenticated() is false
        raise:  OperationFailed - unable to complete request
        compliance: mandatory - This method must be implemented.

        """
        raise IllegalState()

    def get_effective_agent_id(self):
        """Gets the Id of the effective agent in use by this session.
        If is_authenticated() is true, then the effective agent may be
        the same as the agent returned by get_authenticated_agent(). If
        is_authenticated() is false, then the effective agent may be a
        default agent used for authorization by an unknwon or anonymous
        user.
        return: (osid.id.Id) - the effective agent
        compliance: mandatory - This method must be implemented.

        """
        raise Unimplemented()

    def get_effective_agent(self):
        """Gets the effective agent in use by this session.
        If is_authenticated() is true, then the effective agent may be
        the same as the agent returned by get_authenticated_agent(). If
        is_authenticated() is false, then the effective agent may be a
        default agent used for authorization by an unknwon or anonymous
        user.
        return: (osid.authentication.Agent) - the effective agent
        raise:  OperationFailed - unable to complete request
        compliance: mandatory - This method must be implemented.

        """
        raise Unimplemented()

    def get_date(self):
        """Gets the service date which may be the current date or the effective date in which this session exists.

        return: (timestamp) - the service date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise Unimplemented()

    date = property(fget=get_date)

    def get_clock_rate(self):
        """Gets the rate of the service clock.

        return: (decimal) - the clock rate
        *compliance: mandatory -- This method must be implemented.*

        """
        raise Unimplemented()

    clock_rate = property(fget=get_clock_rate)

    def get_format_type(self):
        """Gets the ``DisplayText`` format ``Type`` preference in effect for this session.

        return: (osid.type.Type) - the effective ``DisplayText`` format
                ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise Unimplemented()

    format_type = property(fget=get_format_type)

    def supports_transactions(self):
        """Tests for the availability of transactions.

        return: (boolean) - true if transaction methods are available,
                false otherwise
        compliance: mandatory - This method must be implemented.

        """
        return False

    def start_transaction(self):
        """Starts a new transaction for this sesson.
        Transactions are a means for an OSID to provide an all-or-
        nothing set of operations within a session and may be used to
        coordinate this service from an external transaction manager. A
        session supports one transaction at a time. Starting a second
        transaction before the previous has been committed or aborted
        results in an IllegalState error.
        return: (osid.transaction.Transaction) - a new transaction
        raise:  IllegalState - a transaction is already open
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - transactions not supported
        compliance: optional - This method must be implemented if
                    supports_transactions() is true.
        implementation notes: Ideally, a provider that supports
        transactions should guarantee atomicity, consistency, isolation
        and durability in a 2 phase commit process. This is not always
        possible in distributed systems and a transaction provider may
        simply allow for a means of processing bulk updates.  To
        maximize interoperability, providers should honor the one-
        transaction-at-a-time rule.

        """
        raise Unsupported()

    locale = property(get_locale)
    authenticated_agent_id = property(get_authenticated_agent_id)
    authenticated_agent = property(get_authenticated_agent)
    effective_agent_id = property(get_effective_agent_id)
    effective_agent = property(get_effective_agent)
