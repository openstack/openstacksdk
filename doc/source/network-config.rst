==============
Network Config
==============

There are several different qualities that networks in OpenStack might have
that might not be able to be automatically inferred from the available
metadata. To help users navigate more complex setups, `os-client-config`
allows configuring a list of network metadata.

.. code-block:: yaml

  clouds:
    amazing:
      networks:
      - name: blue
        routes_externally: true
      - name: purple
        routes_externally: true
        default_interface: true
      - name: green
        routes_externally: false
      - name: yellow
        routes_externally: false
        nat_destination: true
      - name: chartreuse
        routes_externally: false
        routes_ipv6_externally: true
      - name: aubergine
        routes_ipv4_externally: false
        routes_ipv6_externally: true

Every entry must have a name field, which can hold either the name or the id
of the network.

`routes_externally` is a boolean field that labels the network as handling
north/south traffic off of the cloud. In a public cloud this might be thought
of as the "public" network, but in private clouds it's possible it might
be an RFC1918 address. In either case, it's provides IPs to servers that
things not on the cloud can use. This value defaults to `false`, which
indicates only servers on the same network can talk to it.

`routes_ipv4_externally` and `routes_ipv6_externally` are boolean fields to
help handle `routes_externally` in the case where a network has a split stack
with different values for IPv4 and IPv6. Either entry, if not given, defaults
to the value of `routes_externally`.

`default_interface` is a boolean field that indicates that the network is the
one that programs should use. It defaults to false. An example of needing to
use this value is a cloud with two private networks, and where a user is
running ansible in one of the servers to talk to other servers on the private
network. Because both networks are private, there would otherwise be no way
to determine which one should be used for the traffic. There can only be one
`default_interface` per cloud.

`nat_destination` is a boolean field that indicates which network floating
ips should be attached to. It defaults to false. Normally this can be inferred
by looking for a network that has subnets that have a gateway_ip. But it's
possible to have more than one network that satisfies that condition, so the
user might want to tell programs which one to pick. There can be only one
`nat_destination` per cloud.
