set -a  # Automatically export all variables
source .env
set +a

orchestrate env activate stgb-inox
orchestrate connections add -a watsonx_credentials
orchestrate connections configure -a watsonx_credentials --env draft -k key_value -t team
orchestrate connections set-credentials -a watsonx_credentials --env draft -e "api_key=${WATSONX_API_KEY}"
orchestrate connections configure -a watsonx_credentials --env live -k key_value -t team
orchestrate connections set-credentials -a watsonx_credentials --env live -e "api_key=${WATSONX_API_KEY}"