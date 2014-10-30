from openstack import connection
conn = connection.Connection(auth_url="http://openstack:5000/v3",
                             project_name="big_project",
                             user_name="SDK_user",
                             password="Super5ecretPassw0rd")

