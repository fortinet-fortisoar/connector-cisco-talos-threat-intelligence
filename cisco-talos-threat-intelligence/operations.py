"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

import requests
from connectors.core.connector import ConnectorError, get_logger

logger = get_logger('cisco-talos-threat-intelligence')


class CiscoTalosThreatIntelligence:
    def __init__(self, config):
        self.config = config
        logger.info("Initialized CiscoTalosThreatIntelligence with provided configuration")

    def get_token(self):
        url = f"{self.config['server_url'].rstrip('/')}/iroh/token"
        data = {
            "client_id": self.config.get("client_id"),
            "client_secret": self.config.get("client_secret")
        }
        headers = {
            "Content-Type": "application/json"
        }
        logger.info("Requesting access token from Cisco Talos")
        response = requests.post(url, json=data, headers=headers, verify=self.config.get("verify_ssl", True))
        if response.status_code == 200:
            logger.info("Access token received successfully")
            return response.json().get("access_token")
        else:
            logger.error(f"Token request failed: {response.status_code} - {response.text}")
            raise ConnectorError(f"Token request failed: {response.status_code} - {response.text}")

    def make_api_call(self, observable_type, value):
        token = self.get_token()
        url = f"{self.config['server_url'].rstrip('/')}/iroh/iroh-enrich/observe/observables"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = [
            {
                "type": observable_type,
                "value": value
            }
        ]
        logger.info(f"Making API call for observable type: {observable_type}, value: {value}")
        response = requests.post(url, json=payload, headers=headers, verify=self.config.get("verify_ssl", True))
        if response.status_code == 200:
            logger.info("API call successful")
            return response.json()
        else:
            logger.error(f"API call failed: {response.status_code} - {response.text}")
            raise ConnectorError(f"API call failed: {response.status_code} - {response.text}")

    def get_ip_reputation(self, params):
        logger.info("Getting IP reputation")
        return self.make_api_call("ip", params.get("ip_address"))

    def get_domain_reputation(self, params):
        logger.info("Getting domain reputation")
        return self.make_api_call("domain", params.get("domain"))

    def get_url_reputation(self, params):
        logger.info("Getting URL reputation")
        return self.make_api_call("url", params.get("url"))

    def get_file_hash_reputation(self, params):
        logger.info("Getting file hash reputation")
        return self.make_api_call("sha256", params.get("file_hash"))

    def check_health(self):
        try:
            logger.info("Performing health check")
            token = self.get_token()
            url = f"{self.config['server_url'].rstrip('/')}/iroh/iroh-enrich/health"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            response = requests.get(url, headers=headers, verify=self.config.get("verify_ssl", True))
            if response.status_code == 200:
                logger.info("Health endpoint responded successfully")
                modules = response.json().get("modules", [])
                for module in modules:
                    if module.get("module") == "SecureX Global Threat Intelligence" and module.get("status") == "ok":
                        logger.info("SecureX Global Threat Intelligence module is healthy")
                        return True
                logger.error("SecureX Global Threat Intelligence module is not healthy")
                raise ConnectorError("SecureX Global Threat Intelligence module is not healthy")
            else:
                logger.error(f"Health check failed: {response.status_code} - {response.text}")
                raise ConnectorError(f"Health check failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            raise ConnectorError(f"Health check error: {str(e)}")


def get_ip_reputation(config, params):
    return CiscoTalosThreatIntelligence(config).get_ip_reputation(params)


def get_domain_reputation(config, params):
    return CiscoTalosThreatIntelligence(config).get_domain_reputation(params)


def get_url_reputation(config, params):
    return CiscoTalosThreatIntelligence(config).get_url_reputation(params)


def get_file_hash_reputation(config, params):
    return CiscoTalosThreatIntelligence(config).get_file_hash_reputation(params)


def check_health(config):
    return CiscoTalosThreatIntelligence(config).check_health()


operations = {
    "get_ip_reputation": get_ip_reputation,
    "get_domain_reputation": get_domain_reputation,
    "get_url_reputation": get_url_reputation,
    "get_file_hash_reputation": get_file_hash_reputation
}
