#!/bin/sh

JYTHON_URL="http://search.maven.org/remotecontent?filepath=org/python/jython-installer/$JYTHON_VERSION/jython-installer-$JYTHON_VERSION.jar"

wget $JYTHON_URL -O jython_installer.jar

java -jar jython_installer.jar --silent --directory $HOME/jython
