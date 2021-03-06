﻿#
# Set the environment locations used in the build.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- ------------------------------------------------------
# Mar 11, 2015  4221     dlovely     Migration from AWIPS2_baseline plus added INNO Support
# Jun 26, 2015  4295     dlovely     Removed AlertViz and CAVE zip file variables
#

# Set AWIPS2_VERSION conditionally.
Set-Variable -name AWIPS2_VERSION -value "1.0.0.0"
if ( "${JENKINS_BUILD_VERSION}" -ne "" ) { Set-Variable -name AWIPS2_VERSION -value ${JENKINS_BUILD_VERSION} }

# Set the location of the Java JDK. Override if the Jenkins job provided a different path.
Set-Variable -name JAVA_JDK_DIR -value "C:\Program Files\Raytheon\AWIPS II\Java"
if ( "${JENKINS_BUILD_JAVA_JDK_LOC}" -ne "" ) { Set-Variable -name JAVA_JDK_DIR -value ${JENKINS_BUILD_JAVA_JDK_LOC} }

Set-Variable -name A2_SCRIPTS_DIR -value "${A2_WORKSPACE_DIR}\installers\Windows\x86_64\Scripts"

Set-Variable -name A2_START_DIR -value "${A2_WORKSPACE_DIR}\START"
Set-Variable -name A2_PREPARE_CAVE_DIR -value "${A2_WORKSPACE_DIR}\Prepare"

# Tool Locations
Set-Variable -name A2_TOOLS_DIR -value "${A2_WORKSPACE_DIR}\installers\Windows\Tools"
Set-Variable -name INNO_ZIP_FILE -value "Inno 5.5.4.zip"
Set-Variable -name INNO_EXE_DIR -value "${A2_TOOLS_DIR}\Inno"
Set-Variable -name INNO_LIC_DIR -value "${A2_TOOLS_DIR}"

# Setup the Get/Put locations only if the build will use it
if ( "${JENKINS_BUILD_NO_SSH}" -eq "" ) { 
  Set-Variable -name SSH_SERVER_GET -value ${JENKINS_BUILD_SSH_SERVER_GET}
  Set-Variable -name SSH_SERVER_PUT -value ${JENKINS_BUILD_SSH_SERVER_PUT}
  Set-Variable -name SSH_PRIVATE_KEY -value ${JENKINS_BUILD_PRIVATE_KEY_LOC}
  Set-Variable -name PSCP_EXE_DIR -value "${A2_TOOLS_DIR}"
}
