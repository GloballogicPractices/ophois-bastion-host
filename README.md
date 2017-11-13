# OPHOIS SSH Bastion host (JumpServer)
![metrics.sh](https://i.imgur.com/YOlDYHW.png)

### What is OPHOIS?
OPOHIS is a Linux ssh jump/bastion host. OPHOIS would act as central point through which all DevOps and Support staff access Linux production servers. OPHOIS SSH gateway includes a lot of security features that would help you manage and administer thousands of Linux servers at ease.


### Motivation
OPHOIS named after Egyptian god Wepwawet AKA Ophois, he was God of War, Victory, Hunting, Lycopolis, Guardian of the Deceased, "Opener of the Ways" and Protector of Pharaoh and Egyptian Army [Wiki] (https://en.wikipedia.org/wiki/Wepwawet)


### Current Featuers

* MFA Authentication 
* Login Trackers
* Session Management
* Session Recording
* Recording Storage
* Session Playback
* Login/Logout Notification
* Security Thread Management

### Planned Features

* Web UI for Management
* Live Session Tracking
* SSO Login
* Session Recording
* Recording Storage

### Installation

* Manually:

	* Installing Python Libs:

		* Slacker
		~~~
		git clone https://github.com/os/slacker.git
		cd slacker
		python setup.py install
		~~~
		
		* Python-Redmine
			~~~
			git clone https://github.com/maxtepkeev/python-redmine.git
			cd python-redmine
			python setup.py install
			~~~

	* Installing Google Authenticator
	
			~~~
			git clone https://github.com/maxtepkeev/python-redmine.git
			sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
			sudo yum install google-authenticator
			google-authenticator
			vi /etc/pam.d/sshd
				auth required pam_google_authenticator.so nullok
			vi  /etc/ssh/sshd_config
				ChallengeResponseAuthentication yes
			vi /etc/ssh/sshd_config
				AuthenticationMethods publickey,password publickey,keyboard-interactive
			vi /etc/pam.d/sshd
				#auth       substack     password-auth
			~~~

	* Installing ttyrec package
	
			~~~
			git clone https://github.com/maxtepkeev/python-redmine.git
			cd python-redmine
			python setup.py install
			yum groupinstall 'Development Tools'
			git clone https://github.com/GloballogicPractices/ophois-bastion-host.git
			cd packages
			tar xvf ttyrec-1.0.8.tar.gz
			cd ttyrec-1.0.8
			./configure
			make && make install
			if it fails, use below patch and compile it again.
			https://github.com/habitat-sh/core-plans/blob/master/ttyrec/ttyrec-1.0.8.RHEL5.patch
			~~~
			
	* Installing ttyrec package
	
			~~~
			git clone https://github.com/maxtepkeev/python-redmine.git
			mkdir /etc/ophois
			mkdir /var/log/ophois
			mkdir /usr/bin/ophois
			git clone https://github.com/GloballogicPractices/ophois-bastion-host.git
			cp ophois-bastion-host/conf/ophois.ini /etc/ophois
			cp ophois-bastion-host/src/*.py /usr/bin/ophois
			cd /usr/bin/ophois 
			chmod +x *.py
			add ForceCommand in sshd_config
			add to /etc/pam.d/sshd
			~~~
			
		* Restart ssh


### Contributing
Currently I work on the code in my free time, any assistance is highly appreciated. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.
