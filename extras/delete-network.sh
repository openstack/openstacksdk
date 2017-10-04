neutron router-gateway-clear router1
neutron router-interface-delete router1
for subnet in private-subnet ipv6-private-subnet ; do
    neutron router-interface-delete router1 $subnet
    subnet_id=$(neutron subnet-show $subnet -f value -c id)
    neutron port-list | grep $subnet_id | awk '{print $2}' | xargs -n1 neutron port-delete
    neutron subnet-delete $subnet
done
neutron router-delete router1
neutron net-delete private

# Make the public network directly consumable
neutron subnet-update public-subnet --enable-dhcp=True
neutron net-update public --shared=True
