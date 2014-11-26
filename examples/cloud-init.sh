#!/bin/bash -x
echo '*** start cloud-init ***'
wget -q -O - https://jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -
echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list
apt-get update
apt-get install -y jenkins
echo 'JENKINS_ARGS="${JENKINS_ARGS} --argumentsRealm.passwd.jenkins=demo --argumentsRealm.roles.jenkins=admin"' >> /etc/default/jenkins
cat >/var/lib/jenkins/config.xml <<!
<?xml version='1.0' encoding='UTF-8'?>
<hudson>
  <disabledAdministrativeMonitors/>
  <version>1.0</version>
  <numExecutors>2</numExecutors>
  <mode>NORMAL</mode>
  <useSecurity>true</useSecurity>
  <authorizationStrategy class="hudson.security.LegacyAuthorizationStrategy"/>
  <securityRealm class="hudson.security.LegacySecurityRealm"/>
  <disableRememberMe>false</disableRememberMe>
  <projectNamingStrategy class="jenkins.model.ProjectNamingStrategy\$DefaultProjectNamingStrategy"/>
  <workspaceDir>\${ITEM_ROOTDIR}/workspace</workspaceDir>
  <buildsDir>\${ITEM_ROOTDIR}/builds</buildsDir>
  <markupFormatter class="hudson.markup.EscapedMarkupFormatter"/>
  <jdks/>
  <viewsTabBar class="hudson.views.DefaultViewsTabBar"/>
  <myViewsTabBar class="hudson.views.DefaultMyViewsTabBar"/>
  <clouds/>
  <slaves/>
  <scmCheckoutRetryCount>0</scmCheckoutRetryCount>
  <views>
    <hudson.model.AllView>
      <owner class="hudson" reference="../../.."/>
      <name>All</name>
      <filterExecutors>false</filterExecutors>
      <filterQueue>false</filterQueue>
      <properties class="hudson.model.View\$PropertyList"/>
    </hudson.model.AllView>
  </views>
  <primaryView>All</primaryView>
  <slaveAgentPort>0</slaveAgentPort>
  <label></label>
  <nodeProperties/>
  <globalNodeProperties/>
</hudson>
!
cat >/var/lib/jenkins/jenkins.security.QueueItemAuthenticatorConfiguration.xml <<!
<?xml version='1.0' encoding='UTF-8'?>
<jenkins.security.QueueItemAuthenticatorConfiguration>
  <authenticators/>
</jenkins.security.QueueItemAuthenticatorConfiguration>
!
service jenkins restart
echo "*** stop cloud-init ***\n"

