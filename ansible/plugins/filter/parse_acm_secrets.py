import json
from base64 import b64decode

# These are the labels of an acm secret
# labels:
#   apps.open-cluster-management.io/cluster-name: local-cluster
#   apps.open-cluster-management.io/cluster-server: api.mcg-hub.blueprints.rhecoeng.com
#   apps.open-cluster-management.io/secret-type: acm-cluster
def get_cluster_name(d):
    if 'metadata' in d and 'labels' in d['metadata']:
        return d['metadata']['labels'].get('apps.open-cluster-management.io/cluster-name', None)
    return None

def get_cluster_fqdn(d):
    if 'metadata' in d and 'labels' in d['metadata']:
        server = d['metadata']['labels'].get('apps.open-cluster-management.io/cluster-server', None)
        # It is rather hard to override this in an OCP deployment so we are okay in just dropping 'api.'
        return server.removeprefix('api.')
    return None

# Takes a list of resources like:
# ...
def parse_acm_secrets(secrets):
    ret = {}
    for secret in secrets:
        cluster = get_cluster_name(secret)
        if cluster is None:
            continue

        ret[cluster] = {}
        ret[cluster]['name'] = b64decode(secret['data']['name'])
        ret[cluster]['server_api'] = b64decode(secret['data']['server'])
        ret[cluster]['cluster_fqdn'] = get_cluster_fqdn(secret)

        config = b64decode(secret['data']['config'])
        parsed_config = json.loads(config)
        ret[cluster]['bearerToken'] = parsed_config['bearerToken']
        ret[cluster]['tlsClientConfig'] = parsed_config['tlsClientConfig']

    return ret


class FilterModule(object):
    def filters(self):
      return {'parse_acm_secrets': parse_acm_secrets}
