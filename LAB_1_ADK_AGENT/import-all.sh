set -x

for tool_file in tools/*.py; do
  orchestrate tools import \
    -k python \
    -f "$tool_file" \
    -r "tools/requirements.txt"
done

for agent_file in agents/*.yaml; do
  orchestrate agents import -f "$agent_file" 
done