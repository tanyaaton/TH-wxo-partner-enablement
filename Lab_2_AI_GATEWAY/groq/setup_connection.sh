set -a  # Automatically export all variables
source .env
set +a

orchestrate connections add -a groq_creds
orchestrate connections configure -a groq_creds --env draft -k key_value -t team
orchestrate connections configure -a groq_creds --env live -k key_value -t team
orchestrate connections set-credentials -a groq_creds --env draft \
  -e "api_key=$GROQ_API_KEY"
orchestrate connections set-credentials -a groq_creds --env live \
  -e "api_key=$GROQ_API_KEY"