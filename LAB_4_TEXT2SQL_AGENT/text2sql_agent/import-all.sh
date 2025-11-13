#!/bin/bash

# orchestrate env activate trial-env
orchestrate tools import -k openapi -f tool/openai_query_db.json
orchestrate agents import -f agent/st_gabriel_text2sql_agent.yaml