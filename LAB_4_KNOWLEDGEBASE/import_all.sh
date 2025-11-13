# git lfs install
# orchestrate env activate metro-internal
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for kb_file in "${SCRIPT_DIR}"/group_policy/*.yaml; do
    [ -f "$kb_file" ] && orchestrate knowledge-bases import -f "$kb_file"
done

for agent_file in "${SCRIPT_DIR}"/agents/*.yaml; do
    [ -f "$agent_file" ] && [[ "$agent_file" != *"METRO_general_agent.yaml" ]] && orchestrate agents import -f "$agent_file"
done

# [ -f "${SCRIPT_DIR}/agents/METRO_general_agent.yaml" ] && orchestrate agents import -f "${SCRIPT_DIR}/agents/METRO_general_agent.yaml"
