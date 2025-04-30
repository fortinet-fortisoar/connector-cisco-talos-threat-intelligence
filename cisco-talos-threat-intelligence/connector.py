"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

from connectors.core.connector import Connector
from connectors.core.connector import get_logger, ConnectorError
from .operations import operations, check_health

logger = get_logger('cisco-talos-threat-intelligence')


class CiscoTalos_ThreatIntelligence(Connector):
    def execute(self, config, operation, params, **kwargs):
        try:
            action = operations.get(operation)
            if isinstance(params, list) and len(params) == 0:
                result = action(config)
            else:
                result = action(config, **params)
            return result
        except Exception as Err:
            logger.error('Exception occurred: {}'.format(Err))
            raise ConnectorError(Err)

    def check_health(self, config):
        return check_health(config)
