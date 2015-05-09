# Installing Hadoop Ambari Framework

1. Spin up Ubuntu 12.04 HVM (ubuntu/images/hvm/ubuntu-precise-12.04-amd64-server-20140927):
	* 1x r3.large, 30GB General Purpose SSD (for Ambari Master)
	* 2x t2.small, 30GB General Purpose SSD (for Ambari Slaves)

For production, separate Name Node from other services. In this case, we will be having r3.large contain the Name Node and all other services as well.

For our sake, we kept the .pem file for all three instances the same. We call it env1pem.pem.

2. Create a security group with the following settings:
	* Ambari needs 8080 from everywhere
	* TCP/ICMP/UDP from all instances within security group
	* 22, 80 open
	* 8800-8820 for RVI
	* If we need storm, we will need to add their respective ports as well

3. ssh into master
4. sudo apt-get update
5. sudo apt-get install lamp-server^ -y, sudo apt-get install ntp -y
6. leave password blank for MySQL prompts (we will not be using MySQL)
7. sudo su
8. cd ~
9. ssh-keygen -t rsa
	* name it "id_rsa"
10. copy the env1pem.pem into the master, in the same directory as ambari
11. ssh into a slave, from master
12. sudo apt-get update, sudo apt-get install ntp -y
13. sudo su
14. vi /root/.ssh/id_rsa.pub and copy in the pub
15. cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
16. repeat 11 to 15 for other slaves
17. go back to master
18. vi /etc/hosts
19. append this below 127.0.0.1 localhost:
	172.31.6.147 ip-172-31-6-147.us-west-2.compute.internal slave1
	172.31.3.44 ip-172-31-3-44.us-west-2.compute.internal slave2
	172.31.42.145 ip-172-31-42-145.us-west-2.compute.internal master

	where <<Private IP>> <<Private DNS/Fully Qualified Domain Name (FQDN)>> <<nickname>>

20. check if you can ssh root@slave1 from master.
21. wget -nv http://public-repo-1.hortonworks.com/ambari/ubuntu12/2.x/updates/2.0.0/ambari.list -O /etc/apt/sources.list.d/ambari.list
22. apt-key adv --recv-keys --keyserver keyserver.ubuntu.com B9733A7A07513CAD
23. apt-get update
24. apt-get install ambari-server -y
25. ambari-server setup
	* daemon? no
	* jdk choice? Oracle JDK 1.7
	* agree to jdk? y
	* advanced db config? n
26. ambari-server start
27. open browser to port 8080 of master instance
28. sign in with username=admin, password=admin191
	* you can change password if needed
29. click launch install wizard
30. in get started: name the cluster ucsdkthxbai, click next
31. stack: HDP 2.2, click next
32. install options:
		* target hosts: put all your private DNS (masters and slaves)
		* host registration info: copy in env1pem.pem, and ssh user account is ubuntu
		* click next
		* note: sometimes the next arrow doesn't work. click back and redo
33. Choose services: choose all services, and click next. ignore spark warning.
34. assign masters: put all services onto master, except zookeeper server, which each node requires one.
35. assign slaves and clients: put data nodes on slaves ONLY, put rest on master ONLY.
36. customize services:
	* in hive, enter database password: hivepassword
	* in oozie, enter database password: ooziepassword
	* in knox, enter master secret: knoxpassword
37. review: next
38. wait for installation (will take ~30 minutes)
39. press finish to go to dashboard

# Setting up RVI to feed into Apache Kafka
1. ssh into master instance
2. sudo su
3. cd /root
4. mkdir rvi
5. apt-get install git -y
6. wget http://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb
7. dpkg -i erlang-solutions_1.0_all.deb
8. apt-get update
9. apt-get install erlang -y
10. run erl -v and check its version is on 6.20
11. git clone https://github.com/PDXostc/rvi_core.git
12. cd rvi_core/
13. vi rvi_sample.config
	* (line 66) change lager_console_backend, notice to lager_console_backend, info
	* (line 93) add the public IP of master instance to node_address:8817
	* (line 112) change node_service_prefix to jlr.com/backend
14. apt-get install make
15. make deps
16. make compile
17. ./scripts/setup_rvi_node.sh -d -n hdpbackend -c rvi_sample.config
18. ./scripts/rvi_node.sh -n hdpbackend
19. open new terminal tab
20. git clone https://github.com/PDXostc/rvi_backend
TBA after pull request complete; code for apache kafka is currently on our own repo