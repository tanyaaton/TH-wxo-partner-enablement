#!/bin/bash

# orchestrate env activate trial-env
orchestrate tools import -k flow -f tool/text2sql_flow_7147ce.json
orchestrate agents import -f agent/st_gabriel_text2sql_flow.yaml