set -a  # Automatically export all variables
source .env
set +a

orchestrate connections add -a gg_creds_2
orchestrate connections configure -a gg_creds_2 --env draft -k key_value -t team
orchestrate connections configure -a gg_creds_2 --env live -k key_value -t team
orchestrate connections set-credentials -a gg_creds_2 --env draft \
  -e "api_key=$GOOGLE_API_KEY"
orchestrate connections set-credentials -a gg_creds_2 --env live \
  -e "api_key=$GOOGLE_API_KEY"