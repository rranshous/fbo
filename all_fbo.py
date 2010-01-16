#!/usr/bin/python
import pull
print "Content-Type: application/atom+xml\n\n"
print pull.update_atom(pull.read_feed_archive(),'/dev/null')
